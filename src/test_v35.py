"""v35: fixes after the digests of 27 and 28 October 2026."""

import unittest

from ai_summaries import clean_summary
from article_selection import has_context_title, prioritize_article
from event_grouping import merge_by_cves
from glossary import autofix
from kev import find_cves
from summary_quality import quality_problems, readability_problems


def has(problems, fragment):
    return any(fragment in problem for problem in problems)


def article(title, source, cves=(), summary="", score_title=None):
    return {
        "title": title,
        "link": f"https://{source}/{abs(hash(title))}",
        "description": "",
        "cves": list(cves),
        "kev": [],
        "summary": summary,
        "related": [],
    }


class TestMergeByCves(unittest.TestCase):
    def test_brotli_three_times_becomes_one_item(self):
        articles = [
            article("Microsoft releases emergency .NET patches for critical Brotli flaw", "bleepingcomputer.com",
                    ["CVE-2026-111497"]),
            article("Attackers Use Microsoft Teams IT Support Scams", "thehackernews.com"),
            article("Critical 'HTTP2Shell' Brotli vulnerability triggers emergency patches", "bleepingcomputer.com",
                    ["CVE-2026-111497"]),
            article("PHP Issues Second Windows Security Update to Fix Brotli Code Execution Flaw",
                    "thehackernews.com", ["CVE-2026-111497"]),
        ]
        merged = merge_by_cves(articles)

        self.assertEqual(len(merged), 2)
        brotli = [item for item in merged if item.get("related")][0]
        self.assertEqual(len(brotli["related"]), 2)
        self.assertEqual(merged[1]["title"], "Attackers Use Microsoft Teams IT Support Scams")

    def test_second_pass_uses_summaries_with_unicode_hyphens(self):
        articles = [
            article("Apple backports CoreGraphics zero-day patches", "bleepingcomputer.com", ["CVE-2026-86950"]),
            article("iOS, macOS 27.2 Patch 286 Bugs", "securityweek.com",
                    summary="Apple naprawiło 286 podatności, w tym CVE‑2026‑86950."),
        ]
        self.assertEqual(len(merge_by_cves([dict(item) for item in articles])), 2)
        self.assertEqual(len(merge_by_cves(articles, use_summaries=True)), 1)

    def test_articles_without_cves_are_not_merged(self):
        self.assertEqual(len(merge_by_cves([article("A", "a.pl"), article("B", "b.pl")])), 2)

    def test_roundup_is_never_merged(self):
        articles = [
            article("Weekendowa Lektura: odcinek 700", "zaufanatrzeciastrona.pl", ["CVE-2026-111497"]),
            article("Brotli flaw", "bleepingcomputer.com", ["CVE-2026-111497"]),
        ]
        self.assertEqual(len(merge_by_cves(articles)), 2)


class TestUnicodeHyphens(unittest.TestCase):
    def test_find_cves(self):
        self.assertEqual(find_cves("Luka CVE‑2026‑86950 i CVE-2026-1234"), ["CVE-2026-1234", "CVE-2026-86950"])

    def test_fact_check_sees_the_cve(self):
        text = "Luka CVE‑2026‑99999 pozwala na RCE."
        self.assertTrue(has(quality_problems(text, "Title\nCVE-2026-86950 allows RCE."), "CVE-2026-99999"))

    def test_clean_summary_normalizes(self):
        self.assertEqual(clean_summary("Luka CVE‑2026‑86950 – opis."), "Luka CVE-2026-86950 – opis.")


class TestCleanSummary(unittest.TestCase):
    def test_underscore_inside_a_name_stays(self):
        self.assertEqual(clean_summary("Wtyczka twofactor_gauthenticator dla Roundcube."),
                         "Wtyczka twofactor_gauthenticator dla Roundcube.")

    def test_markdown_underscores_go(self):
        self.assertEqual(clean_summary("To jest _ważne_ zdanie."), "To jest ważne zdanie.")


class TestAdvice(unittest.TestCase):
    # Summaries of 27 and 28 October 2026.
    GENERIC = [
        "Zainstaluj najnowsze wersje systemów, aby usunąć te luki.",
        "Postępuj zgodnie z zaleceniami GMO i wyłącz zainfekowane maszyny.",
        "Zaleca się aktualizację wtyczki po jej wydaniu.",
        "Należy zastosować udostępnione łatki.",
    ]

    def test_generic_advice_is_filler(self):
        for text in self.GENERIC:
            self.assertTrue(has(quality_problems(text), "ogólnik"), text)

    def test_concrete_advice_stays(self):
        for text in ("Poprawka jest w wersji 6.2606.4246.", "Problem rozwiązano w wersji 1.6.0."):
            self.assertFalse(has(quality_problems(text), "ogólnik"), text)

    def test_imperative_is_a_soft_problem(self):
        text = "Zaktualizuj PHP do wersji 8.5.12."
        self.assertTrue(has(readability_problems(text), "trybie rozkazującym"))
        self.assertFalse(has(quality_problems(text, soft=False), "trybie rozkazującym"))


class TestRemarksAboutTheArticle(unittest.TestCase):
    def test_article_remarks(self):
        for text in ("Artykuł opisuje serię zero-dayów w Citrix NetScaler.",
                     "Brak dostępnych łatek w artykule."):
            self.assertTrue(has(quality_problems(text), "ogólnik"), text)


class TestPrepositions(unittest.TestCase):
    CASES = {
        "Luka w wtyczce.": "Luka we wtyczce.",
        "Kontakt z wsparciem.": "Kontakt ze wsparciem.",
        "Atak w francuskich sklepach.": "Atak we francuskich sklepach.",
        "Dane ze szkoły i z szkoły.": "Dane ze szkoły i ze szkoły.",
        "Ruch z szybkiego serwera.": "Ruch z szybkiego serwera.",
        "Atak z SQL injection.": "Atak z SQL injection.",
        "Błąd w wersji 2.1.": "Błąd w wersji 2.1.",
        "Atak z wykorzystaniem phishingu.": "Atak z wykorzystaniem phishingu.",
        "Ponowne wprowadzenie łaty.": "Ponowne wprowadzenie łatki.",
    }

    def test_cases(self):
        for before, after in self.CASES.items():
            self.assertEqual(autofix(before), after, before)


class TestSelection(unittest.TestCase):
    def test_loophole_in_the_law_is_context(self):
        self.assertTrue(has_context_title({"title": "Bezpłatne e-dzienniki z lukami w przepisach"}))

    def test_commentary_is_context(self):
        self.assertTrue(has_context_title(
            {"title": "This is Fine: What NetScaler Zero-Days Tell Us About the New Normal"}))

    def test_real_vulnerability_keeps_its_score(self):
        self.assertGreaterEqual(prioritize_article({"title": "Krytyczna luka w routerach TP-Link", "description": ""}), 2)


if __name__ == "__main__":
    unittest.main()
