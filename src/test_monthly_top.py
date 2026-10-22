import json
import tempfile
import unittest
import unittest.mock
from datetime import date
from pathlib import Path

from monthly_top import (
    build_top_lines,
    format_event_line,
    month_label,
    previous_month,
    rank_events,
    run,
)


def record(title, link, source, day, score=3, related=()):
    return {
        "date": f"2026-10-{day:02d}",
        "title": title,
        "link": link,
        "source": source,
        "categories": ["critical"],
        "score": score,
        "related": [
            {"title": t, "link": l, "source": s} for t, l, s in related
        ],
        "continuation": False,
    }


FAKTUROWNIA = record(
    "(AKTUALIZACJA 2) Fakturownia.pl zhackowana – wykradziono faktury",
    "https://niebezpiecznik.pl/fakturownia",
    "niebezpiecznik.pl",
    13,
    related=[
        (
            "Nowe włamanie Fingerprinta - ofiarą firma Fakturownia.pl",
            "https://zaufanatrzeciastrona.pl/fakturownia",
            "zaufanatrzeciastrona.pl",
        )
    ],
)
FAKTUROWNIA_FOLLOW_UP = record(
    "Fakturownia.pl po ataku: wyciekły dane 2 tysięcy firm",
    "https://sekurak.pl/fakturownia",
    "sekurak.pl",
    15,
)
BEYONDTRUST = record(
    "BeyondTrust patches zero-day exploited in attacks since August",
    "https://www.bleepingcomputer.com/beyondtrust",
    "bleepingcomputer.com",
    17,
    score=5,
    related=[
        (
            "China-Linked Hackers Exploited BeyondTrust Zero-Day",
            "https://thehackernews.com/beyondtrust",
            "thehackernews.com",
        )
    ],
)
SINGLE = record(
    "Burger King Japan data breach exposes 11 million customer records",
    "https://www.bleepingcomputer.com/burger",
    "bleepingcomputer.com",
    18,
    score=6,
)



# Tests never download the CISA KEV catalog (v28).
_KEV_PATCH = unittest.mock.patch("monthly_top.load_kev", lambda: {})


def setUpModule():
    _KEV_PATCH.start()


def tearDownModule():
    _KEV_PATCH.stop()

class TestMonths(unittest.TestCase):

    def test_previous_month(self):
        self.assertEqual(previous_month(date(2026, 11, 1)), "2026-10")
        self.assertEqual(previous_month(date(2027, 1, 1)), "2026-12")

    def test_month_label_is_polish(self):
        self.assertEqual(month_label("2026-10"), "październik 2026")
        self.assertEqual(month_label("2026-01"), "styczeń 2026")


class TestRanking(unittest.TestCase):

    def test_follow_ups_join_their_event_across_days(self):
        events = rank_events([SINGLE, FAKTUROWNIA, FAKTUROWNIA_FOLLOW_UP, BEYONDTRUST])
        top = events[0]

        self.assertEqual(top["link"], "https://niebezpiecznik.pl/fakturownia")
        self.assertEqual(top["articles"], 3)
        self.assertEqual(top["sources"], 3)
        self.assertEqual(top["first_date"], "2026-10-13")

    def test_same_source_needs_a_shared_name(self):
        chess = record(
            "Poprzez SQL injection dostali się do bazy Polskiego Związku Szachów",
            "https://sekurak.pl/chess", "sekurak.pl", 19, score=3,
        )
        pesel = record(
            "admin/123456 – takim hasłem dostali się do duńskiej bazy PESEL",
            "https://sekurak.pl/pesel", "sekurak.pl", 19, score=3,
        )

        self.assertEqual(len(rank_events([chess, pesel])), 2)

    def test_more_articles_beat_higher_score(self):
        events = rank_events([SINGLE, BEYONDTRUST])

        self.assertEqual(
            [event["link"] for event in events],
            [BEYONDTRUST["link"], SINGLE["link"]],
        )

    def test_limit_is_ten(self):
        records = [
            record(f"Unique incident {name}", f"https://a.example/{i}", "a.example", 20)
            for i, name in enumerate(
                ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot",
                 "Golf", "Hotel", "India", "Juliett", "Kilo", "Lima"]
            )
        ]
        self.assertEqual(len(rank_events(records)), 10)


class TestMessage(unittest.TestCase):

    def test_event_line_shows_counts_and_first_day(self):
        event = rank_events([FAKTUROWNIA, FAKTUROWNIA_FOLLOW_UP])[0]
        line = format_event_line(1, event)

        self.assertTrue(line.startswith("1. [(AKTUALIZACJA 2) Fakturownia.pl"))
        self.assertIn("· 3 artykuły, 3 serwisy · od 13.10", line)

    def test_single_article_wording(self):
        line = format_event_line(2, rank_events([SINGLE])[0])
        self.assertIn("· 1 artykuł, 1 serwis · od 18.10", line)

    def test_header_marks_incomplete_month(self):
        lines = build_top_lines("2026-10", [FAKTUROWNIA, SINGLE])

        self.assertEqual(lines[0], "**📅 Top 10 · październik 2026**")
        self.assertEqual(lines[1], "*Miesiąc niepełny: archiwum od 13.10.*")

    def test_empty_month_produces_nothing(self):
        self.assertEqual(build_top_lines("2026-10", []), [])


class TestSummaries(unittest.TestCase):
    def test_summary_is_shown_under_the_title(self):
        item = dict(FAKTUROWNIA, summary="Wykradziono faktury klientów.")
        line = format_event_line(1, rank_events([item])[0])

        self.assertEqual(line.split("\n")[1], "> Wykradziono faktury klientów.")

    def test_summary_taken_from_another_article_of_the_event(self):
        from monthly_top import event_summary
        event = [dict(FAKTUROWNIA), dict(SINGLE, summary="Drugi artykuł.")]
        self.assertEqual(event_summary(event), "Drugi artykuł.")

    def test_old_records_without_summary_have_no_quote(self):
        line = format_event_line(1, rank_events([FAKTUROWNIA])[0])
        self.assertNotIn("\n>", line)

    def test_long_top_repeats_header_in_next_message(self):
        from discord_output import split_into_messages
        items = [
            dict(SINGLE, title=f"Unique headline {n} about distinct subject{n}", link=f"https://x/{n}",
                 source=f"s{n}.pl", summary="s" * 400)
            for n in range(10)
        ]
        lines = build_top_lines("2026-10", items)
        messages = split_into_messages(lines, section_headers={lines[0]})

        self.assertGreater(len(messages), 1)
        for message in messages[1:]:
            self.assertTrue(message.startswith("**📅 Top 10 · październik 2026 (cd.)**"))


class TestRun(unittest.TestCase):
    """Every run gets a temporary marker, so tests never touch data/."""

    def test_run_without_webhook_does_not_fail_and_keeps_period_open(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "2026-10.json"
            path.write_text(json.dumps([FAKTUROWNIA, SINGLE]), encoding="utf-8")
            marker = Path(directory) / "last_top.json"

            with unittest.mock.patch.dict("os.environ", {"GITHUB_REF_NAME": "main"}):
                run("2026-10", archive_dir=directory, marker_path=marker, today=date(2026, 11, 1))
            self.assertFalse(marker.exists())

    def test_invalid_month_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            for month in ("2026-13", "../etc", "2026-1"):
                with self.subTest(month=month):
                    with self.assertRaises(SystemExit):
                        run(month, archive_dir=directory, marker_path=Path(directory) / "m.json")

    def test_empty_month_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "last_top.json"
            # Same result on every branch the unit tests run on in GitHub Actions.
            with unittest.mock.patch.dict("os.environ", {"GITHUB_REF_NAME": "main"}):
                run("2026-10", archive_dir=directory, marker_path=marker, today=date(2026, 11, 1))
            self.assertEqual(json.loads(marker.read_text(encoding="utf-8")), {"month": "2026-10"})

    def test_sent_month_is_recorded_and_scheduled_retry_skipped(self):
        import monthly_top
        import top_guard

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "2026-10.json"
            path.write_text(json.dumps([FAKTUROWNIA, SINGLE]), encoding="utf-8")
            marker = Path(directory) / "last_top.json"
            sent = []
            original = monthly_top.send_messages
            monthly_top.send_messages = lambda url, messages: sent.append(messages)

            try:
                with unittest.mock.patch.dict("os.environ", {
                    "DISCORD_MONTHLY_WEBHOOK_URL": "real", "GITHUB_REF_NAME": "main",
                    "GITHUB_EVENT_NAME": "schedule",
                }):
                    run("2026-10", archive_dir=directory, marker_path=marker, today=date(2026, 11, 1))
                    run("2026-10", archive_dir=directory, marker_path=marker, today=date(2026, 11, 1))
            finally:
                monthly_top.send_messages = original

            self.assertEqual(len(sent), 1)
            self.assertTrue(top_guard.should_skip("month", "2026-10", "schedule", marker))

    def test_preview_of_current_month_is_not_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "last_top.json"
            with unittest.mock.patch.dict("os.environ", {"GITHUB_REF_NAME": "main"}):
                run("2026-10", archive_dir=directory, marker_path=marker, today=date(2026, 10, 20))
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
