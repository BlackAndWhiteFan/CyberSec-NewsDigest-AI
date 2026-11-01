"""v38: data for the bridge to CyberSec Mozaika (Letters 7–11, 1.11.2026).

The private repository cybersec-most reads this repository's data, never
its code. These tests guard the data contract, so a change of shape stops
this workflow before the bridge report breaks silently.
"""

import csv
import json
import re
import tempfile
import unittest
import unittest.mock
from datetime import date
from pathlib import Path

import monthly_top
from article_archive import build_record
from glossary import matched_ids
from monthly_top import run as monthly_run

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "data" / "glosariusz_mirror.csv"

RECORD_FIELDS = {"date", "title", "link", "source", "related", "summary"}
OPTIONAL_LIST_FIELDS = {"cves", "kev", "language", "terms"}
NOTE_FIELDS = {
    "glossary": {"id", "used", "required"},
    "style": {"used", "form", "suggestion"},
    "inflection": {"id", "used", "term"},
    "autofix": {"id", "rule", "used", "fixed"},
    "proofreading": {"before", "after", "model"},
}
FIXED_BY = {"ai", "code", "remains", "dropped"}
MIRROR_COLUMNS = ["id", "termin_en", "forma", "nawias", "regula", "unikaj"]
MIRROR_HEADER = re.compile(
    r"^# Mirror glosariusza CyberSec Mozaika · plik-matka v\d+ · \d{4}-\d{2}-\d{2} · CC BY-NC-ND 4\.0 · © Jan Wolski\.$"
)


class TestTerms(unittest.TestCase):
    def test_entries_found_in_english_and_polish(self):
        ids = matched_ids("Attackers chained a privilege escalation with a web shell.\n"
                          "Napastnicy użyli DCSync i podwyższenia uprawnień.")
        for entry in ("H182", "H727", "H740"):
            self.assertIn(entry, ids)

    def test_archive_record_gets_terms(self):
        record = build_record({"title": "PHP2Shell RCE exploited", "link": "https://a.pl/1",
                               "summary": "Luka pozwala na RCE."}, "2026-11-01")
        self.assertIn("H090", record["terms"])
        self.assertEqual(record["terms"], sorted(set(record["terms"])))


class TestArchiveContract(unittest.TestCase):
    """Real archive files in data/archive (the bridge reads exactly these)."""

    def records(self):
        for path in sorted((ROOT / "data" / "archive").glob("*.json")):
            records = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(records, list, path.name)
            yield from ((path.name, record) for record in records)

    def test_record_fields(self):
        for name, record in self.records():
            self.assertTrue(RECORD_FIELDS <= set(record), f"{name}: {record.get('title')}")
            self.assertRegex(record["date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(name[:7], record["date"][:7])

            for field in OPTIONAL_LIST_FIELDS:
                self.assertIsInstance(record.get(field, []), list, f"{name}: {field}")

            for related in record["related"]:
                self.assertTrue({"title", "link", "source"} <= set(related), name)

    def test_language_notes(self):
        for name, record in self.records():
            for note in record.get("language", []):
                kind = note.get("type")
                self.assertIn(kind, NOTE_FIELDS, f"{name}: {note}")
                self.assertTrue(NOTE_FIELDS[kind] <= set(note), f"{name}: {note}")

                if "fixed_by" in note:
                    self.assertIn(note["fixed_by"], FIXED_BY, f"{name}: {note}")

                if kind == "glossary":
                    self.assertRegex(note["id"], r"^(H\d{3}|DOP-|D\d{3})")


class TestTops(unittest.TestCase):
    def test_delivered_top_is_saved_next_to_the_marker(self):
        archive = [{"date": "2026-10-2%d" % day, "title": "PHP2Shell RCE flaw exploited", "link": f"https://s{day}.pl/a",
                    "source": f"s{day}.pl", "related": [], "summary": "Luka PHP2Shell pozwala na RCE.",
                    "cves": ["CVE-2026-109618"], "kev": [], "score": 3} for day in range(1, 4)]

        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "2026-10.json").write_text(json.dumps(archive), encoding="utf-8")
            marker = Path(directory) / "last_top.json"
            with unittest.mock.patch.dict("os.environ", {"DISCORD_MONTHLY_WEBHOOK_URL": "https://x", "TRIGGER": "schedule",
                                                          "GITHUB_REF_NAME": "main"}, clear=False), \
                 unittest.mock.patch("monthly_top.send_messages"), \
                 unittest.mock.patch("monthly_top.test_mode.is_test_run", return_value=False), \
                 unittest.mock.patch("monthly_top.test_mode.webhook_url", return_value=("https://x", "X")):
                monthly_run("2026-10", archive_dir=directory, marker_path=marker, today=date(2026, 11, 1),
                            load_kev_catalog=lambda: {})

            saved = json.loads((Path(directory) / "tops" / "2026-10.json").read_text(encoding="utf-8"))

        self.assertEqual(saved[0]["rank"], 1)
        self.assertEqual(saved[0]["period"], "2026-10")
        self.assertEqual(saved[0]["kind"], "month")
        self.assertEqual(saved[0]["cves"], ["CVE-2026-109618"])
        self.assertEqual(len(saved[0]["links"]), 3)
        for field in monthly_top.TOP_FIELDS:
            self.assertIn(field, saved[0])


class TestMirrorContract(unittest.TestCase):
    def test_six_columns_and_header(self):
        lines = MIRROR.read_text(encoding="utf-8-sig").splitlines()
        self.assertRegex(lines[0], MIRROR_HEADER)
        rows = list(csv.reader([line for line in lines if not line.startswith("#")], delimiter=";"))
        self.assertEqual(rows[0], MIRROR_COLUMNS)
        self.assertTrue(all(len(row) == len(MIRROR_COLUMNS) for row in rows[1:] if row))


class TestFilePlacement(unittest.TestCase):
    """1.11.2026: the v90 mirror was uploaded to src/, the digest kept
    reading the old one from data/, and every test passed."""

    def test_src_holds_only_code(self):
        stray = sorted(path.name for path in (ROOT / "src").iterdir()
                       if path.is_file() and path.suffix != ".py" and path.name != ".gitkeep")
        self.assertEqual(stray, [], "W src/ tylko pliki .py – dane do data/: " + ", ".join(stray))

    def test_root_holds_no_code_or_data(self):
        stray = sorted(path.name for path in ROOT.iterdir()
                       if path.is_file() and path.suffix in {".py", ".csv", ".json"})
        self.assertEqual(stray, [], "Pliki w katalogu głównym – przenieś je do src/ albo data/: " + ", ".join(stray))

    def test_data_files_are_in_data(self):
        for name in ("glosariusz_mirror.csv", "styl_unikaj.csv"):
            self.assertTrue((ROOT / "data" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
