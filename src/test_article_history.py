import json
import tempfile
import unittest
from pathlib import Path

from article_history import load_history, save_history


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
                    ]
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


if __name__ == "__main__":
    unittest.main()
