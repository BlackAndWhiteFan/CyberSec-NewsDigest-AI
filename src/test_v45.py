"""v45 · Less, but better: at most DAILY_ITEMS items in the daily digest,
ranked with KEV, CVE, other sources and Polish sources; vendor content and
business news filtered out (digests of 2–6.11.2026)."""

import unittest

from article_selection import DAILY_CANDIDATES, DAILY_ITEMS, daily_rank, is_excluded, limit_daily


def item(title, link, **extra):
    return {"title": title, "link": link, "description": "", **extra}


class TestDailyLimit(unittest.TestCase):
    def test_limits(self):
        self.assertEqual(DAILY_ITEMS, 10)
        self.assertGreater(DAILY_CANDIDATES, DAILY_ITEMS)

    def test_keeps_the_best_items_in_their_order(self):
        items = [item(f"Story {number}", f"https://example.com/{number}") for number in range(12)]
        items[11]["kev"] = ["CVE-2026-1"]
        items[10]["cves"] = ["CVE-2026-2"]
        kept = limit_daily(items, limit=3)
        self.assertEqual([entry["title"] for entry in kept][1:], ["Story 10", "Story 11"])
        self.assertEqual(len(kept), 3)

    def test_rank_rewards_kev_sources_and_polish_sites(self):
        plain = item("Firma opisuje kampanię", "https://example.com/a")
        kev = item("Firma opisuje kampanię", "https://example.com/b", kev=["CVE-2026-1"], cves=["CVE-2026-1"])
        polish = item("Firma opisuje kampanię", "https://cert.pl/c")
        echoed = item("Firma opisuje kampanię", "https://example.com/d", related=[{}, {}, {}, {}])
        self.assertEqual(daily_rank(kev) - daily_rank(plain), 4)
        self.assertEqual(daily_rank(polish) - daily_rank(plain), 1)
        self.assertEqual(daily_rank(echoed) - daily_rank(plain), 3)

    def test_short_lists_stay(self):
        items = [item("A", "https://example.com/a"), item("B", "https://example.com/b")]
        self.assertIs(limit_daily(items), items)


class TestVendorContent(unittest.TestCase):
    def test_vendor_and_business_titles_are_excluded(self):
        for title in ("The 4 Elements of Exposure Prioritization and How to Operationalize Them",
                      "Is Your Exposure Management Platform Leaving You Exposed? Five Tests to Find Out",
                      "5 Active Cyber Threats That Put US Enterprises at Risk in October 2026",
                      "Northstar Security Exits Stealth With $7M to Expose Toxic Risk Combinations"):
            with self.subTest(title=title):
                self.assertTrue(is_excluded({"title": title}))

    def test_security_news_stays(self):
        for title in ("Microsoft raises the bounty for Hyper-V flaws",
                      "Hackers Target OpenSSH SSHole Flaw Within Hours of Disclosure",
                      "Cyber threats rise in Europe"):
            with self.subTest(title=title):
                self.assertFalse(is_excluded({"title": title}))


if __name__ == "__main__":
    unittest.main()
