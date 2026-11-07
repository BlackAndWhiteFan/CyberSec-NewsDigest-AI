"""v46 · Polish polish: Morfeusz 2 grammar checks, the living rules document
(data/reguly_jezyka.md) in the prompts, the CVSS decimal comma and "build"
moved from the calque list to industry usage."""

import importlib.util
import unittest

import ai_summaries
from glossary import autofix
from language_rules import RULES, load_rules, prompt_rules
from polish_words import gender_problems, is_allowed, name_case_problems, numeral_problems
from summary_quality import style_hits

TAGS = {
    "luki": [("luk", "subst:pl:nom.acc.voc:m3"), ("luka", "subst:pl:nom.acc.voc:f")],
    "podatności": [("podatność", "subst:pl:nom.acc.voc:f")],
    "błędy": [("błąd", "subst:pl:nom.acc.voc:m3")],
    "inne": [("inny", "adj:pl:nom.acc.voc:m2.m3.f.n:pos")],
    "Linux": [("Linux", "subst:sg:nom:m2")],
    "Windows": [("Windows", "subst:sg.pl:nom.gen.dat.acc.inst.loc.voc:m3")],
    "ogłosiło": [("ogłosić", "praet:sg:n:perf")],
    "ujawnił": [("ujawnić", "praet:sg:m1.m2.m3:perf")],
    "dodała": [("dodać", "praet:sg:f:perf")],
}


def tags(word):
    return TAGS.get(word, [])


def generate(lemma):
    return {"Linux": [("Linuksie", "Linux", "subst:sg:loc:m2")]}.get(lemma, [])


class TestNumerals(unittest.TestCase):
    def test_gender_of_the_numeral(self):
        problems = numeral_problems("Wykryto dwa luki, dwa podatności i dwie błędy.", tags)
        self.assertEqual(len(problems), 3)
        self.assertIn("„dwie luki”", problems[0])
        self.assertIn("„dwa błędy”", problems[2])

    def test_correct_forms_and_adjectives_stay(self):
        self.assertEqual(numeral_problems("Wykryto dwie luki, dwa błędy i dwie inne luki.", tags), [])


class TestNames(unittest.TestCase):
    def test_declinable_name_after_w(self):
        problems = name_case_problems("Luka w Linux pozwala na RCE.", tags, generate)
        self.assertEqual(problems, ["nieodmieniona nazwa „w Linux” – napisz „w Linuksie”"])

    def test_indeclinable_and_unknown_names_stay(self):
        self.assertEqual(name_case_problems("Luka w Windows i w Firefox.", tags, generate), [])

    def test_one_gender_per_company(self):
        problems = gender_problems("Chainalysis ogłosiło wyciek. Chainalysis ujawnił hasła. CISA dodała lukę.", tags)
        self.assertEqual(len(problems), 1)
        self.assertIn("Chainalysis", problems[0])


@unittest.skipUnless(importlib.util.find_spec("morfeusz2"), "morfeusz2 not installed")
class TestRealMorfeusz(unittest.TestCase):
    def test_real_dictionary(self):
        self.assertEqual(len(numeral_problems("Wykryto dwa luki.")), 1)
        self.assertEqual(name_case_problems("Luka w Linux."), ["nieodmieniona nazwa „w Linux” – napisz „w Linuksie”"])


class TestRulesDocument(unittest.TestCase):
    def test_rules_reach_the_prompts(self):
        self.assertGreaterEqual(len(RULES), 8)
        self.assertTrue(any("grupa Storm-0940" in rule for rule in RULES))
        self.assertIn(RULES[0], ai_summaries.PROOFREAD_PROMPT.format(rules=prompt_rules()))
        self.assertIn("{rules}", ai_summaries.SYSTEM_PROMPT)
        self.assertIn("{rules}", ai_summaries.EVENT_PROMPT)

    def test_only_the_rules_section_is_read(self, tmp=None):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as file:
            file.write("# T\n- not a rule\n## Nakazy dla modeli\n- Rule one.\n- Rule two.\n## Inne\n- not a rule\n")
        self.assertEqual(load_rules(file.name), ["Rule one.", "Rule two."])
        self.assertEqual(load_rules("missing.md"), [])


class TestAutofixAndUsage(unittest.TestCase):
    def test_cvss_decimal_comma(self):
        self.assertEqual(autofix("Ocena (CVSS 8.1) i wersja 16.7.8."), "Ocena (CVSS 8,1) i wersja 16.7.8.")
        self.assertEqual(autofix("CVSS v3.1: 9.8"), "CVSS v3.1: 9,8")

    def test_build_is_industry_usage(self):
        self.assertEqual(style_hits("Łatka jest w buildzie 11.2609 i w nowych buildach."), [])
        self.assertTrue(is_allowed("buildzie"))


if __name__ == "__main__":
    unittest.main()
