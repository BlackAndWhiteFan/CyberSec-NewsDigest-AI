"""v51 · No empty sentences: no sentences about a patch or CVE the article
does not mention, no Microsoft fixes for its own update bugs, and both
parts of "hashe (skróty haseł)" inflected (digest test of 12.11.2026)."""

import unittest

import ai_summaries
from article_selection import is_excluded
from language_rules import RULES
from summary_quality import baseless_patch_problems


class TestBaselessPatchSentences(unittest.TestCase):
    def test_sentence_without_basis_is_flagged(self):
        problems = baseless_patch_problems(
            "Badacze opisali rootkity eBPF. Luka nie jest jeszcze wykorzystywana w atakach i nie istnieje łatka.",
            "eBPF rootkits are discussed on underground forums.")
        self.assertEqual(len(problems), 1)
        self.assertIn("nie istnieje łatka", problems[0])

    def test_article_about_patches_keeps_the_sentence(self):
        self.assertEqual(baseless_patch_problems("Firma nie podała numeru CVE ani dostępnej łatki.",
                                                 "D-Link has not released a patch or CVE ids yet."), [])

    def test_prompt_limits_patch_questions_to_vulnerabilities(self):
        self.assertIn("dotyczą tylko artykułów o lukach", ai_summaries.SYSTEM_PROMPT)


class TestSelectionAndRules(unittest.TestCase):
    def test_update_bug_fixes_are_excluded(self):
        self.assertTrue(is_excluded({"title": "Microsoft fixes audio issues caused by September security updates"}))
        self.assertFalse(is_excluded({"title": "Microsoft patches Outlook zero-day exploited in attacks"}))

    def test_hash_rule_inflects_both_parts(self):
        self.assertTrue(any("hashy (skrótów haseł)" in rule for rule in RULES))


if __name__ == "__main__":
    unittest.main()
