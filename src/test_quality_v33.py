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
    # v40 (Letter 18): "ransomware" has no explanation any more, so the v33
    # cases (test 26.10.2026) must come out unchanged.
    def test_no_explanation_after_people_verbs_or_alone(self):
        from glossary import apply_glossary
        for text in ("Negocjatorzy ransomware pomagali grupie. Zespół wykrył ransomware w sieci.",
                     "Grupa użyła ransomware do szyfrowania.", "Atak ransomware na szpital."):
            with self.subTest(text=text):
                self.assertEqual(apply_glossary(text, set()), text)


class TestStyleV33(unittest.TestCase):
    def test_new_calques(self):
        problems = quality_problems("Panele systemu AI-hackingowego Cairn. Przygotowano 46 buildów szyfrujących.")
        self.assertTrue(has(problems, "kalka „AI-hackingowego”"))
        self.assertTrue(has(problems, "kalka „buildów”"))

    def test_product_name_is_not_a_calque(self):
        self.assertFalse(has(quality_problems("Atakujący użyli narzędzia Build Tools."), "kalka"))


class TestSecondBranchTest(unittest.TestCase):
    # Second branch test of 26.10.2026 (10:50).
    def test_notes_never_get_a_continued_header(self):
        from discord_output import split_into_messages
        header = "**🔁 CIĄG DALSZY**"
        lines = ["x" * 30, header, "1. " + "a" * 27, "", "Streszczenia przygotowało AI."]
        messages = split_into_messages(lines, limit=70, section_headers={header})

        self.assertEqual(messages[-1], "Streszczenia przygotowało AI.")

    def test_section_still_continues_after_its_header_gap(self):
        from discord_output import split_into_messages
        header = "**📅 Top 10**"
        lines = [header, "", "1. " + "a" * 40, "2. " + "b" * 40]
        messages = split_into_messages(lines, limit=60, section_headers={header})

        self.assertTrue(messages[1].startswith("**📅 Top 10 (cd.)**"))

    def test_ransomware_after_a_negotiating_participle(self):
        from glossary import apply_glossary
        text = "Śledczy zidentyfikowali wykonawców firm negocjujących ransomware."
        self.assertEqual(apply_glossary(text, set()), text)

    def test_alternatives_are_not_a_phrase(self):
        from summary_quality import suggestion_text
        self.assertEqual(suggestion_text("wersji, kompilacji"),
                         "wersji albo kompilacji (wybierz jedno słowo, nie wpisuj obu)")
        self.assertEqual(suggestion_text("wpisy, dane (np. „dane pacjentów”, „1,8 mln wpisów”)"),
                         "wpisy albo dane (np. „dane pacjentów”, „1,8 mln wpisów”) "
                         "(wybierz jedno słowo, nie wpisuj obu)")
        self.assertEqual(suggestion_text("włamanie"), "włamanie")

    def test_counted_data(self):
        self.assertTrue(has(quality_problems("Pozyskał ponad 4,1 mln danych partii."), "kalka „mln danych”"))


if __name__ == "__main__":
    unittest.main()
