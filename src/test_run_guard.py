import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from run_guard import current_trigger, last_digest_date, mark_done, should_skip


class TestRunGuard(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "data" / "last_digest.json"

    def tearDown(self):
        self.directory.cleanup()

    def test_no_marker_means_no_skip(self):
        self.assertIsNone(last_digest_date(self.path))
        self.assertFalse(should_skip("schedule", "2026-10-20", self.path))

    def test_scheduled_run_skipped_after_todays_digest(self):
        mark_done(3, "schedule", "2026-10-20", self.path)
        self.assertTrue(should_skip("schedule", "2026-10-20", self.path))

    def test_manual_run_is_never_skipped(self):
        mark_done(3, "workflow_dispatch", "2026-10-20", self.path)
        self.assertFalse(should_skip("workflow_dispatch", "2026-10-20", self.path))

    def test_manual_run_blocks_later_scheduled_run(self):
        mark_done(1, "workflow_dispatch", "2026-10-20", self.path)
        self.assertTrue(should_skip("schedule", "2026-10-20", self.path))

    def test_new_day_is_not_skipped(self):
        mark_done(3, "schedule", "2026-10-19", self.path)
        self.assertFalse(should_skip("schedule", "2026-10-20", self.path))

    def test_marker_content(self):
        mark_done(0, "schedule", "2026-10-20", self.path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data, {"date": "2026-10-20", "trigger": "schedule", "articles": 0})

    def test_alarm_clock_run_is_skipped_like_a_scheduled_run(self):
        mark_done(5, "schedule", "2026-10-20", self.path)
        self.assertTrue(should_skip("budzik", "2026-10-20", self.path))

    def test_alarm_clock_run_blocks_later_scheduled_run(self):
        mark_done(5, "budzik", "2026-10-20", self.path)
        self.assertTrue(should_skip("schedule", "2026-10-20", self.path))
        self.assertFalse(should_skip("workflow_dispatch", "2026-10-20", self.path))

    def test_trigger_variable_overrides_event_name(self):
        with mock.patch.dict("os.environ", {"TRIGGER": "budzik", "GITHUB_EVENT_NAME": "workflow_dispatch"}):
            self.assertEqual(current_trigger(), "budzik")

        with mock.patch.dict("os.environ", {"TRIGGER": "", "GITHUB_EVENT_NAME": "schedule"}):
            self.assertEqual(current_trigger(), "schedule")

    def test_damaged_marker_does_not_block(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")
        self.assertFalse(should_skip("schedule", "2026-10-20", self.path))


if __name__ == "__main__":
    unittest.main()
