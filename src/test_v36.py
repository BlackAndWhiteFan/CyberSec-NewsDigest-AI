"""v36: fixes after the digest of 29 October 2026."""

import io
import json
import unittest

import ai_summaries
from ai_summaries import summarize_articles
from glossary import autofix
from summary_quality import quality_problems, readability_problems


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


ORACLE = {
    "title": "Hackers Target Critical Oracle E-Business Suite RCE Flaw Days After Security Patch",
    "link": "https://example.com/oracle",
    "description": "Attackers exploit a critical SQL injection flaw in Oracle E-Business Suite days after the patch.",
}


class TestSoftProblemsNeverCut(unittest.TestCase):
    def test_draft_stays_when_the_correction_is_worse(self):
        draft = ("Atakujący wykorzystują krytyczną lukę SQL injection w Oracle E-Business Suite. "
                 "Ataki zaczęły się kilka dni po wydaniu łatki, a eksploatację widać w wielu firmach.")
        worse = ("Atakujący wykorzystują krytyczną lukę SQL injection w Oracle E-Business Suite od 2019 roku. "
                 "Luka umożliwia wstrzyknięcie kodu po jej załataniu.")
        article = dict(ORACLE)
        summarize_articles([article], {"GROQ_API_KEY": "g"}, ScriptedOpener([{1: draft}, {1: worse}]), lambda s: None)

        self.assertEqual(article["summary"], draft)


class TestFirstSentenceGuard(unittest.TestCase):
    def test_summary_without_its_first_sentence_is_dropped(self):
        draft = ("Oracle E-Business Suite ma lukę wykorzystywaną od 2019 roku. "
                 "Luka umożliwia wstrzyknięcie kodu SQL.")
        article = dict(ORACLE)
        summarize_articles([article], {"GROQ_API_KEY": "g"}, ScriptedOpener([{1: draft}, {1: draft}]), lambda s: None)

        self.assertNotIn("summary", article)


class TestPrepositionZe(unittest.TestCase):
    def test_cases(self):
        cases = {
            "urządzenie z włączoną funkcją": "urządzenie z włączoną funkcją",
            "rozmowa z wnukiem": "rozmowa z wnukiem",
            "kontakt z wsparciem": "kontakt ze wsparciem",
            "razem z wszystkimi": "razem ze wszystkimi",
            "z względu na": "ze względu na",
        }
        for before, after in cases.items():
            self.assertEqual(autofix(before), after, before)


class TestPhishing(unittest.TestCase):
    def test_added_effect_is_rejected(self):
        text = "Wyciekły dane 11 mln użytkowników, co może umożliwić kampanie phishingowe."
        source = "Burger King Japan\nData of 11 million users leaked, including names and emails."
        self.assertTrue(any("phishingu" in p for p in quality_problems(text, source)))

    def test_phishing_from_the_article_stays(self):
        text = "Atakujący użyli phishingu i złośliwego załącznika."
        source = "Russian hackers\nThe attackers used phishing emails with a malicious attachment."
        self.assertFalse(any("phishingu" in p for p in quality_problems(text, source)))


class TestSentenceLength(unittest.TestCase):
    def test_threshold_30_words(self):
        words_28 = " ".join(["słowo"] * 27) + " koniec."
        words_32 = " ".join(["słowo"] * 31) + " koniec."
        self.assertFalse(any("podziel" in p for p in readability_problems(words_28)))
        self.assertTrue(any("podziel" in p for p in readability_problems(words_32)))


if __name__ == "__main__":
    unittest.main()
