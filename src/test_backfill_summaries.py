import json
import tempfile
import unittest
import unittest.mock
import xml.etree.ElementTree as ET
from pathlib import Path

from backfill_summaries import backfill, build_articles, feed_material


FEED = """<rss><channel>
<item><title>Old article</title><link>https://example.com/old</link>
<description>Opis z RSS.</description></item>
</channel></rss>"""


def fake_fetch(url):
    return ET.fromstring(FEED).findall(".//item")


def record(link, summary=""):
    return {"date": "2026-10-19", "title": "Old article", "link": link, "source": "example.com",
            "categories": [], "score": 3, "related": [], "continuation": False, "summary": summary}


def fake_summarize(articles):
    for article in articles:
        article["summary"] = f"Streszczenie: {article['description'] or 'z tytułu'}"


class TestBackfill(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "2026-10.json"
        self.path.write_text(json.dumps([
            record("https://example.com/old"),
            record("https://example.com/gone"),
            record("https://example.com/done", summary="Już jest."),
        ]), encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def run_backfill(self, save, branch="main"):
        with unittest.mock.patch.dict("os.environ", {"GITHUB_REF_NAME": branch}):
            return backfill("2026-10", save, self.directory.name, fake_fetch, fake_summarize)

    def saved(self):
        return {r["link"]: r["summary"] for r in json.loads(self.path.read_text(encoding="utf-8"))}

    def test_missing_summaries_are_filled_and_existing_kept(self):
        self.assertEqual(self.run_backfill(save=True), 2)
        self.assertEqual(self.saved(), {
            "https://example.com/old": "Streszczenie: Opis z RSS.",
            "https://example.com/gone": "Streszczenie: Old article",
            "https://example.com/done": "Już jest.",
        })

    def test_preview_does_not_write(self):
        before = self.path.read_text(encoding="utf-8")
        self.assertEqual(self.run_backfill(save=False), 2)
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)

    def test_branch_run_does_not_write(self):
        before = self.path.read_text(encoding="utf-8")
        self.run_backfill(save=True, branch="v23-uzupelnienie")
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)

    def test_second_run_has_nothing_to_do(self):
        self.run_backfill(save=True)
        self.assertEqual(self.run_backfill(save=True), 0)

    def test_title_only_summary_keeps_first_sentence(self):
        def two_sentences(articles):
            for article in articles:
                article["summary"] = "Pierwsze zdanie. Drugie dopowiedziane."

        with unittest.mock.patch.dict("os.environ", {"GITHUB_REF_NAME": "main"}):
            backfill("2026-10", True, self.directory.name, fake_fetch, two_sentences)

        self.assertEqual(self.saved()["https://example.com/gone"], "Pierwsze zdanie.")
        self.assertEqual(self.saved()["https://example.com/old"], "Pierwsze zdanie. Drugie dopowiedziane.")

    def test_material_from_feed_or_title_only(self):
        articles, used = build_articles(
            [record("https://example.com/old"), record("https://example.com/gone")],
            feed_material(fake_fetch, ["feed"]),
        )
        self.assertEqual(used, ["RSS", "tylko tytuł"])
        self.assertEqual(articles[0]["description"], "Opis z RSS.")
        self.assertEqual(articles[1]["description"], "Old article")


if __name__ == "__main__":
    unittest.main()
