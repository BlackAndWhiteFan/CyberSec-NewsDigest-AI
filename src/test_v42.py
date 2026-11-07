"""v42: clean Polish – English words left in summaries, words invented by
the language correction, and the lite Gemini models at the end of the
correction queue (digests of 31.10–7.11.2026)."""

import importlib.util
import json
import unittest
import urllib.error

import ai_summaries
from polish_words import english_leftovers, english_problems, invented_words, is_allowed, load_accepted
from summary_quality import quality_problems

POLISH = {
    "komputer", "łączącego", "się", "jako", "grupa", "przejęła", "konta", "luka", "pozwala", "przejąć",
    "kontrolę", "nad", "systemem", "krytycznych", "podatności", "łatki", "firma", "wydała", "hakerzy",
    "zaatakowali", "serwery", "dane", "klientów", "według",
}


def known(word):
    return word.lower() in POLISH


class TestEnglishLeftovers(unittest.TestCase):
    def test_untranslated_words_from_the_material(self):
        text = "Luka pozwala przejąć komputer łączącego się jako viewer."
        material = "TeamViewer flaw lets a remote host attack the viewer."
        self.assertEqual(english_leftovers(text, material, known), ["viewer"])

    def test_polish_endings_on_english_words(self):
        text = "Hakerzy przejęli konta tenantów."
        self.assertEqual(english_leftovers(text, "attackers logged into tenants", known), ["tenantów"])

    def test_glossary_terms_and_accepted_words_stay(self):
        text = "Grupa użyła exploitów, payloadu i frameworka."
        material = "The group used exploits, a payload and a framework."
        self.assertEqual(english_leftovers(text, material, known, accepted=["framework*"]), [])

    def test_names_paths_and_words_missing_from_the_material_stay(self):
        text = "Hakerzy zaatakowali serwery GitLab i plik wp-content/upgrade według kontrolę."
        self.assertEqual(english_leftovers(text, "GitLab servers wp-content upgrade", known), [])
        # Not in the material: a Polish word Morfeusz does not know, not English.
        self.assertEqual(english_leftovers("Firma wydała łatki wieloagentowe.", "patches", known), [])

    def test_soft_problem_asks_for_a_fix(self):
        problems = english_problems("Grupa przejęła konta jako viewer.", "the viewer side", known)
        self.assertEqual(len(problems), 1)
        self.assertIn("„viewer”", problems[0])

    def test_accepted_list_file(self):
        accepted = load_accepted()
        self.assertIn("framework*", accepted)
        self.assertTrue(all(item == item.lower() and " " not in item for item in accepted))
        self.assertTrue(is_allowed("frameworku", accepted))


class TestInventedWords(unittest.TestCase):
    def test_typos_from_the_correction(self):
        # 6–7.11.2026: Gemini lite wrote "kryzycznych" and "Hakeri".
        self.assertEqual(invented_words("Firma wydała łatki krytycznych podatności.",
                                        "Firma wydała łatki kryzycznych podatności.", "", known), ["kryzycznych"])
        self.assertEqual(invented_words("Hakerzy zaatakowali serwery.", "Hakeri zaatakowali serwery.", "", known),
                         ["Hakeri"])

    def test_names_and_terms_are_explained(self):
        before = "Według Gartner firma wydała łatki."
        after = "Według Gartnera firma wydała łatki exploitów."
        self.assertEqual(invented_words(before, after, "", known), [])
        self.assertEqual(invented_words("Grupa przejęła konta.", "Grupa przejęła konta tenantów.",
                                        "accounts of tenants", known), [])

    def test_acronyms_and_short_words_pass(self):
        self.assertEqual(invented_words("Luka pozwala przejąć konta.", "Luka RCE pozwala przejąć konta w r.",
                                        "", known), [])


@unittest.skipUnless(importlib.util.find_spec("morfeusz2"), "morfeusz2 not installed")
class TestRealMorfeusz(unittest.TestCase):
    def test_dictionary_knows_polish_and_not_the_typos(self):
        self.assertEqual(invented_words("Firma wydała łatki dla krytycznych podatności.",
                                        "Firma wydała łatki dla kryzycznych podatności.", ""), ["kryzycznych"])
        self.assertEqual(english_leftovers("Luka pozwala zaatakować komputer łączącego się jako viewer.",
                                           "the viewer computer"), ["viewer"])


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def gemini_reply(text):
    def opener(request, timeout):
        content = json.dumps({"streszczenia": [{"id": 1, "tekst": text}]})
        return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]}).encode())
    return opener


class TestCorrectionGuard(unittest.TestCase):
    def setUp(self):
        self.interval = ai_summaries.MIN_REQUEST_INTERVAL
        ai_summaries.MIN_REQUEST_INTERVAL = 0
        self.invented = ai_summaries.invented_words

    def tearDown(self):
        ai_summaries.MIN_REQUEST_INTERVAL = self.interval
        ai_summaries.invented_words = self.invented

    def run_correction(self, before, after):
        article = {"title": "A", "link": "https://a.pl/1", "summary": before, "summary_material": "A\nmaterial"}
        ai_summaries.invented_words = lambda old, new, material: invented_words(old, new, material, known)
        ai_summaries.proofread_summaries([article], ai_summaries.PROVIDERS, {"GEMINI_API_KEY": "m"},
                                         gemini_reply(after), lambda s: None, hints_source=lambda texts, opener: {})
        return article["summary"]

    def test_correction_with_an_invented_word_is_rejected(self):
        before = "Firma wydała łatki krytycznych podatności."
        self.assertEqual(self.run_correction(before, "Firma wydała łatki kryzycznych podatności."), before)


class TestCorrectionOrder(unittest.TestCase):
    def test_lite_after_mistral_from_the_second_round(self):
        correctors = ai_summaries.language_correctors({"GEMINI_API_KEY": "g", "MISTRAL_API_KEY": "m"})
        names = [name for name, _, _ in correctors]
        rounds = {name: first for name, _, first in correctors}
        mistral = next(index for index, name in enumerate(names) if name.startswith("Mistral"))
        lite = [index for index, name in enumerate(names) if name.endswith("lite")]

        self.assertTrue(lite and all(index > mistral for index in lite))
        self.assertTrue(all(rounds[names[index]] == 2 for index in lite))
        self.assertTrue(all(rounds[name] == 1 for name in names[:mistral]))

    def test_lite_alone_still_works(self):
        correctors = ai_summaries.language_correctors({"GEMINI_API_KEY": "g", "GEMINI_MODEL": "x-lite",
                                                       "GEMINI_LITE_MODEL": "x-lite"})
        self.assertEqual([(name, first) for name, _, first in correctors], [("Gemini x-lite", 1)])


class TestQualityHook(unittest.TestCase):
    def test_quality_problems_include_english_words(self):
        problems = quality_problems("Luka pozwala przejąć komputer łączącego się jako viewer.",
                                    "TeamViewer flaw\nThe viewer computer is attacked.")
        # With morfeusz2 installed the word is reported; without it the check
        # is skipped and nothing breaks.
        if importlib.util.find_spec("morfeusz2"):
            self.assertTrue(any("„viewer”" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
