import json
import tempfile
import unittest
import unittest.mock
from datetime import date
from pathlib import Path

import weekly_top
from weekly_top import build_week_lines, parse_week, previous_week, run, week_id, week_label, week_records


def record(title, link, source, day_text, score=3):
    return {
        "date": day_text, "title": title, "link": link, "source": source,
        "categories": ["critical"], "score": score, "related": [], "continuation": False,
    }



# Tests never download the CISA KEV catalog (v28).
_KEV_PATCH = unittest.mock.patch("weekly_top.load_kev", lambda: {})


def setUpModule():
    _KEV_PATCH.start()


def tearDownModule():
    _KEV_PATCH.stop()

class TestWeekDates(unittest.TestCase):
    def test_previous_week_is_monday_to_sunday(self):
        self.assertEqual(previous_week(date(2026, 10, 26)), date(2026, 10, 19))
        self.assertEqual(previous_week(date(2026, 10, 28)), date(2026, 10, 19))

    def test_week_id_and_label(self):
        self.assertEqual(week_id(date(2026, 10, 19)), "2026-W43")
        self.assertEqual(week_label(date(2026, 10, 19)), "19–25.10.2026")
        self.assertEqual(week_label(date(2026, 10, 26)), "26.10–01.11.2026")
        self.assertEqual(week_label(date(2026, 12, 28)), "28.12.2026–03.01.2027")

    def test_parse_week_returns_monday(self):
        self.assertEqual(parse_week("2026-10-22"), date(2026, 10, 19))
        for text in ("2026-13-01", "../etc", "22.10.2026"):
            with self.subTest(text=text):
                with self.assertRaises(SystemExit):
                    parse_week(text)


class TestWeekRecords(unittest.TestCase):
    def test_week_spanning_two_months_reads_both_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "2026-10.json").write_text(json.dumps([
                record("Old", "https://a/1", "a.pl", "2026-10-25"),
                record("Monday", "https://a/2", "a.pl", "2026-10-26"),
            ]), encoding="utf-8")
            Path(directory, "2026-11.json").write_text(json.dumps([
                record("Sunday", "https://a/3", "a.pl", "2026-11-01"),
                record("Next", "https://a/4", "a.pl", "2026-11-02"),
            ]), encoding="utf-8")

            titles = [r["title"] for r in week_records(date(2026, 10, 26), directory)]

        self.assertEqual(sorted(titles), ["Monday", "Sunday"])


class TestWeekLines(unittest.TestCase):
    def test_empty_week_has_no_message(self):
        self.assertEqual(build_week_lines(date(2026, 10, 19), []), [])

    def test_header_incomplete_note_and_top_five(self):
        records = [
            record(f"Unique story number {n} about topic{n}", f"https://a/{n}", f"s{n}.pl", "2026-10-21")
            for n in range(8)
        ]
        lines = build_week_lines(date(2026, 10, 19), records)

        self.assertEqual(lines[0], "**🗓️ Top 5 · tydzień 19–25.10.2026**")
        self.assertEqual(lines[1], "*Tydzień niepełny: archiwum od 21.10.*")
        self.assertEqual(sum(1 for line in lines if line[:2] in {f"{n}." for n in range(1, 10)}), 5)


class TestWeeklyRun(unittest.TestCase):
    def test_week_sent_once_for_scheduled_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "2026-10.json").write_text(json.dumps([
                record("Fakturownia hacked", "https://a/1", "a.pl", "2026-10-20"),
            ]), encoding="utf-8")
            marker = Path(directory) / "last_top.json"
            sent = []

            with unittest.mock.patch("monthly_top.send_messages", lambda url, m: sent.append((url, m))), \
                 unittest.mock.patch.dict("os.environ", {
                     "DISCORD_WEEKLY_WEBHOOK_URL": "weekly", "GITHUB_REF_NAME": "main",
                     "GITHUB_EVENT_NAME": "schedule",
                 }):
                run("2026-10-20", archive_dir=directory, marker_path=marker, today=date(2026, 10, 26))
                run("2026-10-20", archive_dir=directory, marker_path=marker, today=date(2026, 10, 26))

            self.assertEqual([url for url, _ in sent], ["weekly"])
            self.assertEqual(json.loads(marker.read_text(encoding="utf-8")), {"week": "2026-W43"})

    def test_branch_run_goes_to_test_channel_and_keeps_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "2026-10.json").write_text(json.dumps([
                record("Fakturownia hacked", "https://a/1", "a.pl", "2026-10-20"),
            ]), encoding="utf-8")
            marker = Path(directory) / "last_top.json"
            sent = []

            with unittest.mock.patch("monthly_top.send_messages", lambda url, m: sent.append((url, m))), \
                 unittest.mock.patch.dict("os.environ", {
                     "DISCORD_WEEKLY_WEBHOOK_URL": "weekly", "DISCORD_TEST_WEBHOOK_URL": "test",
                     "GITHUB_REF_NAME": "v22-top-tygodnia", "GITHUB_EVENT_NAME": "workflow_dispatch",
                 }):
                run("2026-10-20", archive_dir=directory, marker_path=marker, today=date(2026, 10, 26))

            self.assertEqual(sent[0][0], "test")
            self.assertTrue(sent[0][1][0].startswith("🧪 **TEST**"))
            self.assertFalse(marker.exists())

    def test_preview_of_current_week_is_not_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "last_top.json"
            with unittest.mock.patch.dict("os.environ", {"GITHUB_REF_NAME": "main"}):
                run("2026-10-20", archive_dir=directory, marker_path=marker, today=date(2026, 10, 21))
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
