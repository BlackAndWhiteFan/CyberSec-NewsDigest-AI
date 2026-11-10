"""v43: calque dictionary (rows accepted by JW on 7.11.2026) and dates with
English or shortened month names fixed by code."""

import unittest

from glossary import autofix
from summary_quality import style_hits


class TestMonthAutofix(unittest.TestCase):
    def test_english_and_short_month_names(self):
        cases = {
            "Incydent zawieszono do 15 august.": "Incydent zawieszono do 15 sierpnia.",
            "Dostęp od 30 paź 2026 r.": "Dostęp od 30 października 2026 r.",
            "Łatka z August 2, 2026 usuwa lukę.": "Łatka z 2 sierpnia 2026 usuwa lukę.",
            "Atak trwał do 5 May.": "Atak trwał do 5 maja.",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                changes = []
                self.assertEqual(autofix(text, changes), expected)
                self.assertEqual(changes[0]["rule"], "miesiąc po polsku")

    def test_polish_dates_and_english_words_stay(self):
        for text in ("Łatka z 10 maja 2026 r.", "Raport z maj 2026 bez dnia.", "Kampania March of Lies.",
                     "Grupa may use 3 exploits."):
            with self.subTest(text=text):
                self.assertEqual(autofix(text), text)


class TestCalqueDictionary(unittest.TestCase):
    def forms(self, text):
        return [form for _, form, _ in style_hits(text)]

    def test_calques_from_the_digests(self):
        cases = {
            "Luka umożliwia nieautoryzowanemu atakującemu wykonanie kodu.": "nieautoryzowan* atakując*",
            "Łatki są dostępne w poziomach łatek 2026-11-01.": "poziom* łatek",
            "Hakerzy wytransferowali 6,3 mld USD.": "wytransferowa*",
            "Synology ostrzegło, że grupa threat actor wykorzystuje luki.": "threat actor*",
            "Grupa dokonała wycieku danych.": "dokona* wycieku",
            "PHP wydał emergency łatki.": "emergency",
        }
        for text, form in cases.items():
            with self.subTest(text=text):
                self.assertIn(form, self.forms(text))

    def test_accepted_words_stay(self):
        # JW, 7.11.2026: "wystawiony" stays (the industry says so).
        for text in ("Ponad 1000 serwerów wystawionych w internecie jest podatnych.",
                     "Nieautoryzowany dostęp do danych trwał dwa dni.",
                     "Narzędzie HashiCorp Vault przechowuje sekrety.",
                     "Wymagane jest posiadanie numeru PESEL."):
            with self.subTest(text=text):
                self.assertEqual(self.forms(text), [])


if __name__ == "__main__":
    unittest.main()
