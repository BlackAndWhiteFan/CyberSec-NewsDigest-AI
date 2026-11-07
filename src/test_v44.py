"""v44: one story, one item – duplicates of 31.10–7.11.2026 (Chainalysis,
Binance, OpenSSH, GPT-6 Cyber, the CERT Polska bug bounty six times)."""

import unittest

from event_grouping import amounts, merge_by_story, same_event, same_story, strong_match


def frequent(*titles):
    # A big event: its name is in many titles of the day's pool.
    return {stem: 6 for stem in ("chain", "binan", "opens", "japan", "europ")}


class TestFrequentNames(unittest.TestCase):
    def test_big_events_merge_although_their_name_is_frequent(self):
        pairs = [
            ("Chainalysis says breach exposed credentials for all customers",
             "Chainalysis Breach Exposes All Users' Credentials, Forces Shutdown of Key Services"),
            ("Wiadomo już jak włamali się do Binance (i wykradli ponad 6 miliardów USD)",
             "Binance Reveals How Fake Job Interviews and AI Tool Abuse Led to $6.43 Billion Theft"),
            ("Korzystacie z OpenSSH na hostach z musl libc? Lepiej patchujcie",
             "OpenSSH flaw lets attackers log into password-disabled Linux accounts"),
        ]
        for title_a, title_b in pairs:
            with self.subTest(title=title_a):
                self.assertTrue(same_event(title_a, title_b, frequent(), names={"chainalysis"}))

    def test_places_and_word_beginnings_do_not_merge(self):
        self.assertFalse(same_event("Japan Airlines warns of data breach as country grapples",
                                    "Japan's GMO Offers $1 Million Bounty to Catch Hackers", frequent()))
        self.assertFalse(same_event("Chainalysis Confirms Intrusion Into Internal Tools",
                                    "Attackers Chain Three Ivanti Connect Secure Flaws", frequent(),
                                    names={"chainalysis"}))

    def test_product_with_a_version_number(self):
        self.assertTrue(strong_match("Nadchodzący model OpenAI – GPT 6 Cyber starł na miazgę jądro Linux",
                                     "OpenAI Launches GPT-6 Cyber After AI Helps Find 81 Firefox Flaws"))
        self.assertFalse(strong_match("AES 256 w pendrive", "AES-256 w dyskach"))


class TestSameStory(unittest.TestCase):
    def test_amounts(self):
        self.assertEqual(amounts("pula 1 mln zł, do 20 tys. zł, 20 000 zł w 2026 r."), {10 ** 6, 20000})
        self.assertEqual(amounts("CVE-2026-111497 i milion złotych"), {10 ** 6})

    def bug_bounty(self):
        return [
            {"title": "Znajdź luki w polskich systemach i zgarnij pieniądze", "link": "https://a.pl/1",
             "summary": "Program Bug Bounty uruchomiły NASK i CERT Polska, oferując do 20 tys. zł. Pula 1 mln zł."},
            {"title": "Zhakuj te rządowe systemy", "link": "https://b.pl/1",
             "summary": "Program ma pulę 1 mln zł, przy maksymalnej nagrodzie 20 tys. zł."},
            {"title": "Rusza program hackowania. Do 20 000zł za zgłoszenie; 1 000 000zł w puli", "link": "https://c.pl/1",
             "summary": "CERT Polska uruchomił program bug bounty."},
            {"title": "Binance: kradzież 6 mld USD", "link": "https://d.pl/1",
             "summary": "Binance straciło 6 mld USD w 20 minut."},
        ]

    def test_bug_bounty_articles_tell_one_story(self):
        items = self.bug_bounty()
        self.assertTrue(same_story(items[0], items[1]))
        self.assertTrue(same_story(items[1], items[2]))
        self.assertFalse(same_story(items[0], items[3]))

    def test_merge_keeps_one_item(self):
        merged = merge_by_story(self.bug_bounty())
        self.assertEqual(len(merged), 2)
        self.assertEqual(len(merged[0]["related"]), 2)

    def test_one_shared_amount_needs_a_shared_name(self):
        a = {"title": "A", "summary": "Atak dotknął 1 500 osób w szpitalu Medicover."}
        b = {"title": "B", "summary": "Wyciek objął 1 500 klientów sklepu Allegro."}
        self.assertFalse(same_story(a, b))


if __name__ == "__main__":
    unittest.main()
