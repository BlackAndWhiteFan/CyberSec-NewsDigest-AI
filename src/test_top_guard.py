import tempfile
import unittest
from pathlib import Path

from top_guard import load_marker, mark_sent, should_skip


class TestTopGuard(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "data" / "last_top.json"

    def tearDown(self):
        self.directory.cleanup()

    def test_kinds_are_independent(self):
        mark_sent("week", "2026-W43", self.path)
        mark_sent("month", "2026-10", self.path)

        self.assertEqual(load_marker(self.path), {"week": "2026-W43", "month": "2026-10"})
        self.assertTrue(should_skip("week", "2026-W43", "schedule", self.path))
        self.assertFalse(should_skip("week", "2026-W44", "schedule", self.path))

    def test_manual_run_is_never_skipped(self):
        mark_sent("month", "2026-10", self.path)
        self.assertFalse(should_skip("month", "2026-10", "workflow_dispatch", self.path))

    def test_alarm_clock_run_is_skipped_after_period_was_sent(self):
        mark_sent("week", "2026-W43", self.path)
        self.assertTrue(should_skip("week", "2026-W43", "budzik", self.path))
        self.assertFalse(should_skip("week", "2026-W44", "budzik", self.path))

    def test_missing_or_damaged_marker_does_not_block(self):
        self.assertFalse(should_skip("month", "2026-10", "schedule", self.path))
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{bad", encoding="utf-8")
        self.assertFalse(should_skip("month", "2026-10", "schedule", self.path))


if __name__ == "__main__":
    unittest.main()
