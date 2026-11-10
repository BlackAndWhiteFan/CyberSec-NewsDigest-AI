"""v49 · Hashes: "hash" is industry usage (JW, 10.11.2026). The calque rows
from v43 are gone; the rules document asks for "hashe (skróty haseł)" at
the first mention and "hashe" later."""

import unittest

from language_rules import RULES
from polish_words import is_allowed
from summary_quality import style_hits


class TestHashUsage(unittest.TestCase):
    def test_hash_is_not_a_calque(self):
        self.assertEqual(style_hits("Wyciekły hashe haseł, a atakujący złamali hasha administratora."), [])

    def test_hash_is_accepted_usage(self):
        for word in ("hash", "hasha", "hashe", "hashy", "hashami"):
            with self.subTest(word=word):
                self.assertTrue(is_allowed(word))

    def test_rule_for_the_first_mention(self):
        self.assertTrue(any("hashe (skróty haseł)" in rule for rule in RULES))


if __name__ == "__main__":
    unittest.main()
