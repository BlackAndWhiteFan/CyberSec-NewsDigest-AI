"""v50 · One Tuesday: Microsoft's monthly update is one item, an item
without a summary goes last in the daily limit, continuations look back 7
days, and the zero-day number rule is backed by the calque list (digests
of 11–12.11.2026)."""

import unittest

from article_selection import daily_rank
from event_grouping import CONTINUATION_DAYS, is_patch_tuesday, strong_match
from summary_quality import style_hits


class TestPatchTuesday(unittest.TestCase):
    def test_monthly_update_titles_match(self):
        self.assertTrue(strong_match("Microsoft November 2026 Patch Tuesday fixes 1,235 flaws, Outlook zero-day",
                                     "Microsoft Fixes Nearly 1,100 Security Vulnerabilities"))
        self.assertTrue(is_patch_tuesday("Microsoft’s Patch Tuesday surpasses 1,000 bugs for second month in a row"))

    def test_other_microsoft_news_stays_apart(self):
        for title in ("Microsoft patches Outlook zero-day exploited in attacks",
                      "Microsoft finally fixes VPN issues caused by September updates"):
            with self.subTest(title=title):
                self.assertFalse(is_patch_tuesday(title))


class TestDailyRankAndWindow(unittest.TestCase):
    def test_missing_summary_ranks_lower(self):
        with_summary = {"title": "A", "link": "https://example.com/a", "description": "", "summary": "Tekst."}
        without = {"title": "A", "link": "https://example.com/a", "description": "", "summary": ""}
        self.assertEqual(daily_rank(with_summary) - daily_rank(without), 3)

    def test_continuation_window(self):
        self.assertEqual(CONTINUATION_DAYS, 7)


class TestZeroDayNumbers(unittest.TestCase):
    def test_zero_day_plural_is_flagged(self):
        forms = [form for _, form, _ in style_hits("Badacz ujawnił 33 zero-dayów i dwa zero-daye.")]
        self.assertEqual(forms, ["zero-dayów", "zero-daye"])


if __name__ == "__main__":
    unittest.main()
