"""v33: weekly and monthly tops after the first live weekly top (26.10.2026)."""

import unittest

from ai_summaries import proofread_top, tidy_summary
from event_grouping import same_event, same_name
from kev import article_cves
from monthly_top import group_month, rank_events


def record(title, source, date="2026-10-22", score=2, summary="", cves=None, related=()):
    return {
        "title": title,
        "link": f"https://{source}/{abs(hash(title))}",
        "source": source,
        "date": date,
        "score": score,
        "summary": summary,
        "cves": list(cves or []),
        "related": [{"title": t, "link": f"https://x/{i}", "source": "x.com"} for i, t in enumerate(related)],
    }


def titles(event):
    return [item["title"] for item in event]


class TestNameRule(unittest.TestCase):
    def test_forms_of_one_name(self):
        self.assertTrue(same_name("Capcom", "Capcomu"))
        self.assertTrue(same_name("Fakturownia", "Fakturowni"))

    def test_different_words_with_a_shared_beginning(self):
        self.assertFalse(same_name("Fortinet", "FortiSIEM"))

    def test_platform_name(self):
        self.assertFalse(same_name("Python", "Python"))

    def test_false_pairs_of_the_weekly_top(self):
        frequency = {}
        self.assertFalse(same_event(
            "Krytyczne podatności w urządzeniach Fortinet. Łatajcie się!",
            "Critical FortiSIEM Flaw Gets Public Exploit PoC for Unauthenticated Remote Code Execution",
            frequency, rare_limit=3,
        ))
        self.assertFalse(same_event(
            "Złośliwy serwer może przechwycić dane uwierzytelniające OAuth w MCP Python SDK",
            "Critical Flaw in Python’s Popular Pillow Image Library Allows Code Execution via a Crafted Image",
            frequency, rare_limit=3,
        ))

    def test_product_type_word_is_not_a_name(self):
        self.assertFalse(same_event(
            "ClickFix Attackers Exploit Siemens Software Center Flaw to Deploy Remote Access Trojan",
            "Atlassian Patches 75 Flaws in Data Center and Server Products",
            {}, rare_limit=2, names=frozenset({"center"}),
        ))


class TestTopGrouping(unittest.TestCase):
    def test_related_title_with_event_name(self):
        records = [
            record("PHP2Shell: dwie krytyczne luki w jednym z fundamentów Internetu", "kapitanhack.pl",
                   "2026-10-24", 5, cves=["CVE-2026-109618"]),
            record("PHP warns admins of two critical flaws, emergency patches coming tomorrow",
                   "bleepingcomputer.com", "2026-10-21", 5,
                   related=["PHP2Shell: Two Unpatched Critical PHP RCE Flaws"]),
        ]
        self.assertEqual(len(group_month(records)), 1)

    def test_shared_cve_id(self):
        records = [
            record("Twórcy PHP: pierwsze sygnały o lukach pojawiły się w 2024", "cyberdefence24.pl",
                   score=5, cves=["CVE-2026-109618"]),
            record("Widespread PHP Flaw May Cause Many Site Outages Today", "krebsonsecurity.com",
                   score=5, cves=["CVE-2026-109618", "CVE-2026-109619"]),
        ]
        self.assertEqual(len(group_month(records)), 1)

    def test_events_split_by_order_are_merged(self):
        records = [
            record("Krytyczne podatności w PHP core. Wyszła łatka.", "sekurak.pl", score=5,
                   summary="Łatki usuwają CVE-2026-109618 i CVE-2026-109619."),
            record("PHP warns admins of two critical flaws", "bleepingcomputer.com", "2026-10-21", 5,
                   related=["PHP2Shell: Two Unpatched Critical PHP RCE Flaws"]),
            record("PHP2Shell: dwie krytyczne luki", "kapitanhack.pl", "2026-10-24", 2,
                   cves=["CVE-2026-109618"]),
        ]
        self.assertEqual(len(group_month(records)), 1)

    def test_roundup_record_links_nothing(self):
        records = [
            record("Luka w FortiManagerze pomogła w zainfekowaniu zapór FortiGate", "unit42.paloaltonetworks.com",
                   score=5, cves=["CVE-2024-47575"]),
            record("Weekendowa Lektura: odcinek 699 [2026-10-23]. Bierzcie i czytajcie", "zaufanatrzeciastrona.pl",
                   cves=["CVE-2024-47575", "CVE-2026-1"]),
        ]
        self.assertEqual(len(group_month(records)), 2)


class TestTopDisplay(unittest.TestCase):
    def test_polish_leader_with_most_related(self):
        records = [
            record("PHP warns admins of two critical flaws, emergency patches coming tomorrow",
                   "bleepingcomputer.com", "2026-10-21", 5, summary="Łatki zostaną udostępnione jutro.",
                   cves=["CVE-2026-109618"]),
            record("PHP2Shell: dwie krytyczne luki w jednym z fundamentów Internetu", "kapitanhack.pl",
                   "2026-10-24", 5, summary="Ujawniono dwie krytyczne podatności w PHP umożliwiające RCE (RCE).",
                   cves=["CVE-2026-109618"], related=["a", "b", "c"]),
        ]
        top = rank_events(records)[0]
        self.assertEqual(top["title"], "PHP2Shell: dwie krytyczne luki w jednym z fundamentów Internetu")
        self.assertEqual(top["summary"], "Ujawniono dwie krytyczne podatności w PHP umożliwiające RCE.")

    def test_english_summary_falls_back_to_the_next_article(self):
        records = [
            record("Poważne luki w Javie i Node.js", "cyberdefence24.pl", "2026-10-23", 5,
                   summary="CVE-2026-111497 in Node.js Brotli decoder enables out-of-bounds write that may "
                           "lead to RCE and allows remote exploitation without authentication.",
                   cves=["CVE-2026-111497"]),
            record("Node2Shell (CVE-2026-111497): RCE przez dekompresję Brotli w Node.js", "sekurak.pl",
                   "2026-10-24", 2, summary="Luka w dekoderze Brotli pozwala na zapis poza buforem w Node.js.",
                   cves=["CVE-2026-111497"]),
        ]
        self.assertEqual(rank_events(records)[0]["summary"],
                         "Luka w dekoderze Brotli pozwala na zapis poza buforem w Node.js.")

    def test_roundups_are_left_out(self):
        records = [
            record("ThreatsDay: AI Secrets Leak, PingCAP Source Theft + 21 More", "thehackernews.com", score=5,
                   related=["x"]),
            record("Capcom confirms data breach", "bleepingcomputer.com"),
        ]
        self.assertEqual([event["title"] for event in rank_events(records)], ["Capcom confirms data breach"])


class TestTidyAndProofread(unittest.TestCase):
    def test_tidy(self):
        self.assertEqual(tidy_summary("Wydano łatki. Łatki zostaną udostępnione jutro."), "Wydano łatki.")
        self.assertEqual(tidy_summary("exploit tych luk prowadzi do przejęcia serwera."),
                         "Exploit tych luk prowadzi do przejęcia serwera.")

    def test_proofread_without_keys_is_skipped(self):
        events = [{"title": "A", "summary": "Tekst."}]
        self.assertEqual(proofread_top(events, environ={}), 0)
        self.assertEqual(events[0]["summary"], "Tekst.")


class TestTidyLog(unittest.TestCase):
    def test_notes_of_tidy(self):
        notes = []
        tidy_summary("Wydano łatki na RCE (RCE). Łatki zostaną udostępnione jutro.", notes)
        self.assertEqual(notes[0], "autopoprawka „RCE (RCE)” → „RCE”")
        self.assertTrue(notes[1].startswith("usunięte zdanie: „Łatki zostaną udostępnione jutro.”"))

    def test_log_lines(self):
        import contextlib
        import io as text_io
        from monthly_top import log_tidy

        output = text_io.StringIO()
        with contextlib.redirect_stdout(output):
            log_tidy([{"tidy_notes": ["autopoprawka „RCE (RCE)” → „RCE”"]}, {"tidy_notes": []}])

        self.assertEqual(output.getvalue().splitlines(), [
            "PORZĄDEK: wydarzenie 1 – autopoprawka „RCE (RCE)” → „RCE”",
            "PORZĄDEK: streszczenia zmienione przez kod: 1 z 2",
        ])

    def test_english_summary_is_reported(self):
        records = [
            record("Poważne luki w Javie", "cyberdefence24.pl", score=5,
                   summary="CVE-2026-111497 in Node.js Brotli decoder enables out-of-bounds write that may "
                           "lead to RCE and allows remote exploitation without authentication."),
        ]
        notes = rank_events(records)[0]["tidy_notes"]
        self.assertEqual(notes, ["streszczenie „Poważne luki w Javie” pominięte (po angielsku) – szukam kolejnego"])


class TestLekturaCves(unittest.TestCase):
    def test_longer_page_lead_for_lektura_links(self):
        page = "x" * 900 + " CVE-2026-109618"
        self.assertEqual(article_cves({"title": "PHP", "page_text": page, "via": "ZTS"}), ["CVE-2026-109618"])
        self.assertEqual(article_cves({"title": "PHP", "page_text": page}), [])


if __name__ == "__main__":
    unittest.main()
