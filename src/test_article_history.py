import json
import tempfile
import unittest
from pathlib import Path

from article_history import (
    filter_unpublished_articles,
    load_history,
    save_history,
)

class TestArticleHistory(unittest.TestCase):
    def test_loads_existing_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            path.write_text(
                json.dumps({
                    "seen_links": ["https://example.com/1"],
                    "published_links": [],
                }),
                encoding="utf-8",
            )

            history = load_history(path)

            self.assertEqual(
                history,
                {
                    "seen_links": ["https://example.com/1"],
                    "published_links": [],
                },
            )

    def test_returns_empty_history_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.json"

            history = load_history(path)

            self.assertEqual(
                history,
                {
                    "seen_links": [],
                    "published_links": [],
                },
            )

    def test_saves_and_reloads_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            history = {
                "seen_links": [
                    "https://example.com/1",
                    "https://example.com/2",
                ],
                "published_links": [],
            }

            save_history(history, path)

            self.assertEqual(load_history(path), history)

    def test_removes_duplicate_links_when_saving(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            history = {
                "seen_links": [
                    "https://example.com/1",
                    "https://example.com/1",
                    "https://example.com/2",
                ],
                "published_links": []
            }

            save_history(history, path)
           
            self.assertEqual(
                load_history(path),
                {
                    "seen_links": [
                        "https://example.com/1",
                        "https://example.com/2",
                    ],
                    "published_links": [],
                },
            )

    def test_rejects_invalid_history_structure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            path.write_text('{"other": []}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_history(path)

    def test_rejects_non_string_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            path.write_text(
                json.dumps({"seen_links": [123]}),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_history(path)

    def test_keeps_seen_and_published_links_separate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            history = {
                "seen_links": [
                    "https://example.com/seen-only",
                    "https://example.com/published",
                ],
                "published_links": [
                    "https://example.com/published",
                ],
            }

            save_history(history, path)
            loaded_history = load_history(path)

            self.assertIn(
                "https://example.com/seen-only",
                loaded_history["seen_links"],
            )
            self.assertNotIn(
                "https://example.com/seen-only",
                loaded_history["published_links"],
            )
            self.assertIn(
                "https://example.com/published",
                loaded_history["published_links"],
            )
    
    def test_filters_only_published_articles(self):
        articles = [
            {"title": "Seen only", "link": "https://example.com/seen-only"},
            {"title": "Already published", "link": "https://example.com/published"},
            {"title": "New article", "link": "https://example.com/new"},
        ]
        published_links = ["https://example.com/published"]

        result = filter_unpublished_articles(articles, published_links)

        self.assertEqual(
            [article["link"] for article in result],
            [
                "https://example.com/seen-only",
                "https://example.com/new",
            ],
        )
if __name__ == "__main__":
    unittest.main()
