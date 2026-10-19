import json
import tempfile
import unittest
from pathlib import Path

from article_archive import (
    append_to_archive,
    archive_path,
    build_record,
    load_archive,
    load_recent,
)


def make_article(title, link):
    return {"title": title, "link": link, "description": ""}


class TestArticleArchive(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.archive_dir = Path(self.temp_dir.name) / "archive"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_archive_file_is_chosen_by_month(self):
        path = archive_path("2026-10-19", self.archive_dir)
        self.assertEqual(path.name, "2026-10.json")

    def test_record_contains_article_details(self):
        article = make_article(
            "Wakacje.pl zhackowane", "https://www.niebezpiecznik.pl/post/x"
        )
        record = build_record(article, "2026-10-19")

        self.assertEqual(record["date"], "2026-10-19")
        self.assertEqual(record["title"], "Wakacje.pl zhackowane")
        self.assertEqual(record["link"], "https://www.niebezpiecznik.pl/post/x")
        self.assertEqual(record["source"], "niebezpiecznik.pl")
        self.assertEqual(record["categories"], ["critical"])
        self.assertEqual(record["score"], 3)

    def test_articles_are_appended_and_saved(self):
        articles = [
            make_article("Ransomware attack", "https://a.example/1"),
            make_article("Nowa podatność w routerach", "https://b.example/2"),
        ]

        added = append_to_archive(articles, "2026-10-19", self.archive_dir)
        records = load_archive(self.archive_dir / "2026-10.json")

        self.assertEqual(added, 2)
        self.assertEqual([r["link"] for r in records], [a["link"] for a in articles])

    def test_known_links_are_not_archived_twice(self):
        article = make_article("Ransomware attack", "https://a.example/1")

        append_to_archive([article], "2026-10-19", self.archive_dir)
        added = append_to_archive([article], "2026-10-20", self.archive_dir)

        self.assertEqual(added, 0)
        self.assertEqual(len(load_archive(self.archive_dir / "2026-10.json")), 1)

    def test_new_month_starts_new_file(self):
        append_to_archive(
            [make_article("Ransomware attack", "https://a.example/1")],
            "2026-10-31",
            self.archive_dir,
        )
        append_to_archive(
            [make_article("Ransomware attack 2", "https://a.example/2")],
            "2026-11-02",
            self.archive_dir,
        )

        self.assertTrue((self.archive_dir / "2026-10.json").exists())
        self.assertTrue((self.archive_dir / "2026-11.json").exists())

    def test_nothing_is_written_for_empty_list(self):
        added = append_to_archive([], "2026-10-19", self.archive_dir)

        self.assertEqual(added, 0)
        self.assertFalse((self.archive_dir / "2026-10.json").exists())

    def test_missing_archive_is_empty(self):
        self.assertEqual(load_archive(self.archive_dir / "2099-01.json"), [])

    def test_invalid_archive_is_rejected(self):
        path = self.archive_dir / "2026-10.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_archive(path)

    def test_related_sources_and_continuation_are_saved(self):
        article = make_article("Fakturownia.pl zhackowana", "https://niebezpiecznik.pl/a")
        article["related"] = [
            make_article("Ofiarą firma Fakturownia.pl", "https://zaufanatrzeciastrona.pl/b")
        ]
        article["continuation"] = True

        record = build_record(article, "2026-10-19")

        self.assertEqual(
            record["related"],
            [
                {
                    "title": "Ofiarą firma Fakturownia.pl",
                    "link": "https://zaufanatrzeciastrona.pl/b",
                    "source": "zaufanatrzeciastrona.pl",
                }
            ],
        )
        self.assertTrue(record["continuation"])

    def test_recent_records_span_months_and_skip_older_days(self):
        append_to_archive(
            [make_article("Old ransomware attack", "https://a.example/old")],
            "2026-10-27",
            self.archive_dir,
        )
        append_to_archive(
            [make_article("Ransomware attack", "https://a.example/1")],
            "2026-10-30",
            self.archive_dir,
        )
        append_to_archive(
            [make_article("Ransomware attack 2", "https://a.example/2")],
            "2026-11-01",
            self.archive_dir,
        )

        links = [r["link"] for r in load_recent(3, "2026-11-01", self.archive_dir)]

        self.assertEqual(links, ["https://a.example/1", "https://a.example/2"])

    def test_polish_characters_are_saved_readably(self):
        append_to_archive(
            [make_article("Wyciek danych pacjentów", "https://a.example/1")],
            "2026-10-19",
            self.archive_dir,
        )
        text = (self.archive_dir / "2026-10.json").read_text(encoding="utf-8")

        self.assertIn("pacjentów", text)


if __name__ == "__main__":
    unittest.main()
