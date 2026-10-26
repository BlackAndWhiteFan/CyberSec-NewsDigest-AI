"""v33: fixes after the digest of 26.10.2026 (tics, labels without support, PHP repeat)."""

import io
import json
import unittest

import ai_summaries
from ai_summaries import summarize_articles
from main import mark_continuations_by_cve
from summary_quality import quality_problems, remove_unsupported_labels


BROTLI_SOURCE = (
    "Brotli Decoder Flaw Behind Node.js RCE Also Affects Bun, Python\n"
    "A buffer overflow in Google's Brotli decoder (CVE-2026-111497) allows code execution. "
    "Patches were released on October 21."
)
PHP_SOURCE = "PHP security release\nIt is imperative that you update now."


def setUpModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 0
    ai_summaries.PROOFREAD = False


def tearDownModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 20
    ai_summaries.PROOFREAD = True


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ScriptedOpener:
    def __init__(self, replies):
        self.replies = list(replies)

    def __call__(self, request, timeout):
        texts = self.replies.pop(0)
        content = json.dumps({"streszczenia": [{"id": n, "tekst": t} for n, t in texts.items()]})
        return FakeResponse(json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8"))


def has(problems, fragment):
    return any(fragment in problem for problem in problems)


class TestFillers(unittest.TestCase):
    def test_not_known(self):
        self.assertTrue(has(quality_problems("Liczba i rodzaj naruszonych danych nie są znane."), "ogólnik"))
        self.assertTrue(has(quality_problems("Sprawca nadal nie jest znany."), "ogólnik"))

    def test_bare_closing_formula(self):
        for text in ("Zaleca się natychmiastową aktualizację.",
                     "Zaleca się natychmiastowe zastosowanie łatki.",
                     "Zaleca się aktualizację wszystkich wymienionych komponentów."):
            self.assertTrue(has(quality_problems(text), "ogólnik"), text)

    def test_concrete_advice_stays(self):
        text = "Zaleca się aktualizację do wersji 8.5.12 i ograniczenie dostępu do interfejsów zarządzania."
        self.assertFalse(has(quality_problems(text), "ogólnik"))


class TestLabels(unittest.TestCase):
    def test_zero_day_without_support(self):
        text = "Wykryto podatność zero-day CVE-2026-111497 w dekoderze Brotli."
        self.assertTrue(has(quality_problems(text, BROTLI_SOURCE), "zero-day"))

    def test_zero_day_with_support(self):
        text = "Grupa wykorzystała lukę zero-day CVE-2026-102764."
        source = "Zero-day w BeyondTrust\nARMORY CASTLE exploited CVE-2026-102764 as a 0-day."
        self.assertFalse(has(quality_problems(text, source), "zero-day"))

    def test_urgency_without_and_with_support(self):
        text = "Wydano wersję 8.5.12. Zaleca się natychmiastową aktualizację do wersji 8.5.12."
        self.assertTrue(has(quality_problems(text, "PHP release\nVersion 8.5.12 is out."), "pilności"))
        self.assertFalse(has(quality_problems(text, PHP_SOURCE + " Version 8.5.12."), "pilności"))

    def test_code_removes_only_the_label(self):
        text = "Wykryto podatność zero-day CVE-2026-111497. Natychmiastowa aktualizacja jest wymagana."
        self.assertEqual(
            remove_unsupported_labels(text, BROTLI_SOURCE),
            "Wykryto podatność CVE-2026-111497. Aktualizacja jest wymagana.",
        )

    def test_label_kept_when_source_has_it(self):
        text = "Grupa wykorzystała lukę zero-day."
        self.assertEqual(remove_unsupported_labels(text, "A zero-day was exploited."), text)


class TestRepairKeepsFacts(unittest.TestCase):
    def test_lead_sentence_survives_when_correction_fails(self):
        article = {
            "title": "Brotli Decoder Flaw Behind Node.js RCE Also Affects Bun, Python",
            "link": "https://example.com/brotli",
            "description": "A buffer overflow in Google's Brotli decoder (CVE-2026-111497) allows code execution. "
                           "Patches were released on October 21.",
        }
        opener = ScriptedOpener([
            {1: "Wykryto podatność zero-day CVE-2026-111497 w dekoderze Brotli od Google."},
            {1: "Wykryto podatność zero-day CVE-2026-111497 w dekoderze Brotli od Google."},
        ])

        summarize_articles([article], {"GROQ_API_KEY": "g"}, opener, lambda s: None)

        self.assertEqual(article["summary"], "Wykryto podatność CVE-2026-111497 w dekoderze Brotli od Google.")


class TestLekturaContinuation(unittest.TestCase):
    def test_cve_from_the_linked_page(self):
        article = {
            "title": "Dwie krytyczne luki w PHP umożliwiające zdalny dostęp do serwera",
            "summary": "Wydano wersje PHP 8.5.12 i 8.4.27, które łatają dwie krytyczne podatności.",
            "via": "Zaufana Trzecia Strona (Weekendowa lektura)",
            "page_text": "x" * 900 + " Two related critical RCE vulnerabilities: CVE-2026-109618 and CVE-2026-109619.",
        }
        records = [{"title": "PHP2Shell: dwie krytyczne luki", "cves": ["CVE-2026-109618"], "summary": ""}]

        self.assertEqual(mark_continuations_by_cve([article], records), 1)
        self.assertTrue(article["continuation"])

    def test_page_text_of_regular_articles_is_not_used(self):
        article = {
            "title": "Nowa kampania phishingowa",
            "summary": "Atakujący podszywają się pod bank.",
            "page_text": "x" * 900 + " Wcześniej opisywaliśmy CVE-2026-109618.",
        }
        records = [{"title": "PHP2Shell", "cves": ["CVE-2026-109618"], "summary": ""}]

        self.assertEqual(mark_continuations_by_cve([article], records), 0)


class TestRansomwareExplanation(unittest.TestCase):
    # Branch test of 26.10.2026: "Negocjatorzy ransomware (program żądający okupu)".
    def test_not_after_people_or_groups(self):
        from glossary import apply_glossary
        used = set()
        text = apply_glossary("Negocjatorzy ransomware pomagali grupie. Zespół wykrył ransomware w sieci.", used)
        self.assertEqual(text, "Negocjatorzy ransomware pomagali grupie. "
                               "Zespół wykrył ransomware (program żądający okupu) w sieci.")

    def test_skipped_term_can_be_explained_in_a_later_summary(self):
        from glossary import apply_glossary
        used = set()
        self.assertEqual(apply_glossary("Grupy ransomware INC i The Gentlemen.", used),
                         "Grupy ransomware INC i The Gentlemen.")
        self.assertIn("(program żądający okupu)", apply_glossary("Atak ransomware na szpital.", used))

    def test_genitive_after_verb(self):
        from glossary import apply_glossary
        self.assertEqual(apply_glossary("Grupa użyła ransomware do szyfrowania.", set()),
                         "Grupa użyła ransomware (programu żądającego okupu) do szyfrowania.")


class TestStyleV33(unittest.TestCase):
    def test_new_calques(self):
        problems = quality_problems("Panele systemu AI-hackingowego Cairn. Przygotowano 46 buildów szyfrujących.")
        self.assertTrue(has(problems, "kalka „AI-hackingowego”"))
        self.assertTrue(has(problems, "kalka „buildów”"))

    def test_product_name_is_not_a_calque(self):
        self.assertFalse(has(quality_problems("Atakujący użyli narzędzia Build Tools."), "kalka"))


if __name__ == "__main__":
    unittest.main()
