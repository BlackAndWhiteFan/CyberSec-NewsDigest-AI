"""v48 · Common platforms: Polish endings on platform names ("Androida",
"Windowsa") no longer join different stories (digest of 10.11.2026: a
Telegram flaw "na Androida" joined an APT29 campaign "atakują iOS i
Androida")."""

import unittest

from event_grouping import same_event, usable_name


class TestCommonPlatforms(unittest.TestCase):
    def test_inflected_platform_names_are_not_names(self):
        for word in ("Androida", "Androidzie", "Windowsa", "Microsoftu", "Linuksa"):
            with self.subTest(word=word):
                self.assertFalse(usable_name(word))
        for word in ("Chainalysis", "Binance", "Telegramie"):
            with self.subTest(word=word):
                self.assertTrue(usable_name(word))

    def test_telegram_and_apt29_stay_apart(self):
        self.assertFalse(same_event(
            "Krytyczna luka w Telegramie na Androida pozwalała przejąć pełną kontrolę nad telefonem ofiary",
            "Trzy łańcuchy exploitów powiązane z grupą APT29 atakują iOS i Androida",
            {"andro": 3},
        ))


if __name__ == "__main__":
    unittest.main()
