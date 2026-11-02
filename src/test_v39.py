"""v39: guards for the two remaining data lines read by the bridge to
CyberSec Mozaika (Letter 13), and the "proofread" field (Letters 13–14).

The graph "Linie styku" in the bridge carton showed that the bridge report
reads data/tops/ (P4 · Żywe przykłady) and data/styl_unikaj.csv (P3 ·
Kalki), but no test guarded their shape.
"""

import io
import json
import re
import unittest
from pathlib import Path

import ai_summaries
import monthly_top
from article_archive import build_record

ROOT = Path(__file__).resolve().parent.parent
TOP_RECORD_FIELDS = {"period", "kind", "rank", *monthly_top.TOP_FIELDS}
PERIOD = {"week": re.compile(r"^\d{4}-W\d{2}$"), "month": re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")}


class TestTopsContract(unittest.TestCase):
    """Real files in data/tops (the bridge reads exactly these)."""

    def test_saved_tops(self):
        for path in sorted((ROOT / "data" / "tops").glob("*.json")):
            records = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(records, list, path.name)
            self.assertTrue(records, path.name)
            self.assertEqual([record["rank"] for record in records], list(range(1, len(records) + 1)), path.name)

            for record in records:
                self.assertTrue(TOP_RECORD_FIELDS <= set(record), f"{path.name}: {record.get('title')}")
                self.assertIn(record["kind"], PERIOD, path.name)
                self.assertRegex(record["period"], PERIOD[record["kind"]], path.name)
                self.assertEqual(record["period"], path.stem)
                self.assertIsInstance(record["articles"], int, path.name)
                self.assertIsInstance(record["sources"], int, path.name)

                for field in ("kev", "cves", "links"):
                    self.assertIsInstance(record[field], list, f"{path.name}: {field}")


class TestStyleListFormat(unittest.TestCase):
    """bridge_report.py reads the file with csv.DictReader, separator ";",
    skipping lines that start with "#", and expects the header forma;zamiast
    (Letter 14)."""

    def lines(self):
        text = (ROOT / "data" / "styl_unikaj.csv").read_text(encoding="utf-8-sig")
        return [line for line in text.splitlines() if line.strip() and not line.startswith("#")]

    def test_header(self):
        self.assertEqual(self.lines()[0], "forma;zamiast")

    def test_rows(self):
        for line in self.lines()[1:]:
            form, _, suggestion = line.partition(";")
            self.assertTrue(form.strip() and suggestion.strip(), line)
            self.assertNotIn(";", suggestion, line)
            # A star only at the end of a word ("rekord*"), never inside.
            self.assertNotRegex(form, r"\*\w", line)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def gemini_reply(request, timeout):
    sent = json.loads(json.loads(request.data.decode())["contents"][0]["parts"][0]["text"])
    content = json.dumps({"streszczenia": sent["streszczenia"]})
    return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]}).encode())


def articles():
    return [{"title": "A", "link": "https://a.pl/1", "summary": "CISA dodała lukę do KEV.",
             "summary_material": "A\nCISA added a flaw to KEV."}]


class TestProofreadField(unittest.TestCase):
    def setUp(self):
        self.interval = ai_summaries.MIN_REQUEST_INTERVAL
        ai_summaries.MIN_REQUEST_INTERVAL = 0

    def tearDown(self):
        ai_summaries.MIN_REQUEST_INTERVAL = self.interval

    def run_proofreading(self, items, environ, opener):
        ai_summaries.proofread_summaries(items, ai_summaries.PROVIDERS, environ, opener, lambda s: None,
                                         hints_source=lambda texts, opener: {})

    def test_model_name_when_corrected(self):
        items = articles()
        self.run_proofreading(items, {"GEMINI_API_KEY": "m"}, gemini_reply)
        self.assertTrue(items[0]["proofread"].startswith("Gemini "))
        self.assertEqual(build_record(items[0], "2026-11-02")["proofread"], items[0]["proofread"])

    def test_empty_when_no_model_answered(self):
        items = articles()

        def opener(request, timeout):
            raise TimeoutError("The read operation timed out")

        self.run_proofreading(items, {"GEMINI_API_KEY": "m"}, opener)
        self.assertEqual(items[0]["proofread"], "")

    def test_empty_without_keys(self):
        items = articles()
        self.run_proofreading(items, {}, gemini_reply)
        self.assertEqual(items[0]["proofread"], "")
        self.assertEqual(build_record(items[0], "2026-11-02")["proofread"], "")

    def test_archive_records_keep_the_distinction(self):
        # "" = no correction; a missing field = a record from before v39.
        for path in sorted((ROOT / "data" / "archive").glob("*.json")):
            for record in json.loads(path.read_text(encoding="utf-8")):
                if "proofread" in record:
                    self.assertIsInstance(record["proofread"], str, path.name)


if __name__ == "__main__":
    unittest.main()
