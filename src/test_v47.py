"""v47 · Separate stories: in the weekly and monthly tops a shared company
name does not join two events with different CVE ids (top 5 of week 45,
9.11.2026: SonicWall SSL-VPN MFA bypass joined with SonicWall GMS)."""

import unittest

from monthly_top import different_cves, group_month


def record(title, link, cves, date="2026-11-05", score=5, source="a.com"):
    return {"title": title, "link": link, "cves": cves, "date": date, "score": score,
            "source": source, "summary": "", "related": []}


class TestSeparateStories(unittest.TestCase):
    def test_different_cves(self):
        event = [record("A", "https://a.com/1", ["CVE-2026-1"])]
        self.assertTrue(different_cves(record("B", "https://b.com/1", ["CVE-2026-2"]), event))
        self.assertFalse(different_cves(record("B", "https://b.com/1", ["CVE-2026-1", "CVE-2026-3"]), event))
        self.assertFalse(different_cves(record("B", "https://b.com/1", []), event))

    def test_same_vendor_different_cves_stay_apart(self):
        events = group_month([
            record("SonicWall warns of new SSL-VPN MFA bypass flaw exploited in attacks",
                   "https://bleepingcomputer.com/1", ["CVE-2026-19868"], source="bleepingcomputer.com"),
            record("SonicWall Won't Patch EoL GMS Flaws That Could Expose Files",
                   "https://thehackernews.com/1", ["CVE-2026-109593"], score=4, source="thehackernews.com"),
        ])
        self.assertEqual(len(events), 2)

    def test_same_vendor_same_story_still_joins(self):
        events = group_month([
            record("SonicWall warns of new SSL-VPN MFA bypass flaw exploited in attacks",
                   "https://bleepingcomputer.com/1", ["CVE-2026-19868"], source="bleepingcomputer.com"),
            record("SonicWall Patches Exploited SonicOS Bug That Weakens VPN Logins",
                   "https://securityweek.com/1", ["CVE-2026-19868"], score=4, source="securityweek.com"),
        ])
        self.assertEqual(len(events), 1)


if __name__ == "__main__":
    unittest.main()
