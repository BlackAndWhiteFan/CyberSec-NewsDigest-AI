"""v53 · Lata 90.: digests of 14–16.11.2026."""
import unittest

from article_selection import is_excluded
from language_rules import RULES
from summary_quality import baseless_patch_problems, fix_sentence_case, quality_problems


class TestOrdinals(unittest.TestCase):
    def test_no_capital_after_ordinal(self):
        text = "Już w latach 90. rozważano użycie cyberprzestrzeni."
        self.assertEqual(fix_sentence_case(text), text)

    def test_capital_after_sentence_still_added(self):
        self.assertEqual(fix_sentence_case("Atak trwał dwa dni. potem ustał."), "Atak trwał dwa dni. Potem ustał.")


class TestSelection(unittest.TestCase):
    def test_update_bugs_are_excluded(self):
        self.assertTrue(is_excluded({"title": "Microsoft says November security updates cause printing issues"}))
        self.assertTrue(is_excluded({"title": "Microsoft confirms Windows activation failures after November updates"}))
        self.assertFalse(is_excluded({"title": "PostgreSQL Patches 52 Flaws, Including 22-Year-Old Bug"}))


class TestChecks(unittest.TestCase):
    def test_not_mentioned_patch_is_empty_sentence(self):
        text = "Grupa wykorzystała lukę Log4Shell. Atak trwał od 2023 r., a w raporcie nie wspomniano o dostępnej łatce."
        self.assertTrue(baseless_patch_problems(text, "BO Team compromised a code-signing server via vCenter."))

    def test_emergency_is_an_anglicism(self):
        problems = quality_problems("Check Point wydało emergency hotfixy na lukę.")
        self.assertTrue(any("„emergency”" in p for p in problems))

    def test_rules(self):
        joined = "\n".join(RULES)
        self.assertIn("potencjalne RCE", joined)
        self.assertIn("przeciwko luce", joined)
        self.assertIn("złośliwy workflow", joined)


if __name__ == "__main__":
    unittest.main()
