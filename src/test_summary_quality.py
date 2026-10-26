import unittest

from summary_quality import fix_sentence_case, quality_problems, unsupported_facts


class TestGenericPhrases(unittest.TestCase):
    def test_filler_phrases_are_reported(self):
        cases = [
            "Atak dotknął 300 firm, co podkreśla wagę aktualizacji.",
            "Incydent podkreśla znaczenie kopii zapasowych.",
            "To kolejny przykład ataku na łańcuch dostaw.",
            "Warto pamiętać o aktualizacjach.",
            "Atak ten stanowi poważne zagrożenie dla kluczowych sektorów.",
        ]

        for text in cases:
            with self.subTest(text=text):
                problems = quality_problems(text)
                self.assertEqual(len(problems), 1)
                self.assertIn("ogólnik", problems[0])

    def test_concrete_summary_has_no_problems(self):
        text = "Microsoft wydał łatki dla 98 luk zero-day w Windows Server 2025."
        self.assertEqual(quality_problems(text), [])


class TestRelativeTime(unittest.TestCase):
    def test_relative_time_words_are_reported(self):
        for text in ["Łatki zostaną udostępnione jutro.", "Dziś CISA dodała lukę do katalogu.",
                     "W przyszłym tygodniu firma wyda poprawioną wersję.",
                     "Ataki zaczęły się cztery dni przed wydaniem łatki w środę."]:
            with self.subTest(text=text):
                problems = quality_problems(text)
                self.assertEqual(len(problems), 1)
                self.assertIn("względne określenie czasu", problems[0])

    def test_dates_and_similar_words_are_allowed(self):
        self.assertEqual(quality_problems("Łatki wydano 21 października, a dzisiejszość tego nie zmienia."), [])
        self.assertEqual(quality_problems("Łatki wydano w środę 21 października."), [])
        self.assertEqual(quality_problems("Łatki wydano we wtorek, 20 października."), [])


class TestLengthAndForm(unittest.TestCase):
    def test_long_summary_and_semicolons_are_reported(self):
        long_text = "Cisco wydał łatki dla 34 podatności w Expressway i IOS XR. " * 9
        self.assertTrue(any("znaków" in p for p in quality_problems(long_text)))
        problems = quality_problems("Splunk wydał łatki; SolarWinds także.")
        self.assertEqual(len(problems), 1)
        self.assertIn("średnikiem", problems[0])

    def test_missing_information_remarks_are_reported(self):
        problems = quality_problems("Citizen Lab potwierdził infekcję, a raport nie podaje informacji o sprawcach.")
        self.assertEqual(len(problems), 1)
        self.assertIn("ogólnik", problems[0])


class TestInflection(unittest.TestCase):
    def test_uninflected_terms_after_prepositions_are_reported(self):
        for text in ["Eksperci ostrzegają przed exploit, który krąży w sieci.",
                     "Atak przeprowadzono przy użyciu botnet Mirai.",
                     "Ochrona przed nowym infostealer."]:
            with self.subTest(text=text):
                problems = quality_problems(text)
                self.assertEqual(len(problems), 1)
                self.assertIn("nieodmieniony termin", problems[0])

    def test_inflected_terms_and_accusative_are_fine(self):
        for text in ["Eksperci ostrzegają przed exploitem.", "Opublikowano exploit.",
                     "Zainstalowali backdoor w routerze.", "Członkowie botnetu zatrzymani."]:
            with self.subTest(text=text):
                self.assertEqual(quality_problems(text), [])


class TestFacts(unittest.TestCase):
    SOURCE = "Nikkei discloses third data breach, 1.83M records exposed. CVE-2026-41234 was used. 14:00 UTC"

    def test_numbers_and_cves_from_the_source_pass(self):
        text = "Nikkei ujawniło 1,83 mln rekordów; użyto CVE-2026-41234 o 14:00 UTC."
        self.assertEqual(unsupported_facts(text, self.SOURCE, year=2026), [])

    def test_number_with_space_thousands_separator(self):
        source = "Up to 26,739 VPS servers affected."
        self.assertEqual(unsupported_facts("Dotyczy to 26 739 serwerów VPS.", source, year=2026), [])
        self.assertEqual(len(unsupported_facts("Dotyczy to 27 000 serwerów.", source, year=2026)), 1)

    def test_invented_number_is_reported(self):
        problems = unsupported_facts("Ujawniono 2,5 mln rekordów.", self.SOURCE, year=2026)
        self.assertEqual(len(problems), 1)
        self.assertIn("„2,5”", problems[0])

    def test_invented_cve_is_reported(self):
        problems = unsupported_facts("Użyto CVE-2026-99999.", self.SOURCE, year=2026)
        self.assertEqual(len(problems), 1)
        self.assertIn("CVE-2026-99999", problems[0])

    def test_small_numbers_and_current_year_are_not_checked(self):
        text = "Dwie luki (2) załatano 21 października 2026 r. w 3 produktach."
        self.assertEqual(unsupported_facts(text, "Two flaws patched on October 21.", year=2026), [])

    def test_no_source_means_no_fact_check(self):
        self.assertEqual(quality_problems("Ujawniono 2,5 mln wpisów."), [])


class TestSentenceCase(unittest.TestCase):
    def test_sentences_start_with_capital_letter(self):
        self.assertEqual(
            fix_sentence_case("CISA ostrzega przed lukami. exploit tych luk pozwala przejąć serwer."),
            "CISA ostrzega przed lukami. Exploit tych luk pozwala przejąć serwer.",
        )
        self.assertEqual(fix_sentence_case("exploit krąży w sieci."), "Exploit krąży w sieci.")

    def test_abbreviations_do_not_start_a_sentence(self):
        for text in ["Dotyczy to m.in. routerów, np. modeli ASUS, i ok. 300 firm.",
                     "Nikkei Inc. poinformowało o wycieku.",
                     "Skradziono dane ponad 321 tys. kont."]:
            with self.subTest(text=text):
                self.assertEqual(fix_sentence_case(text), text)


class TestLanguageV29(unittest.TestCase):
    """Examples from the digests of 23–24.10.2026."""

    def test_calques_from_the_style_list(self):
        cases = {
            "Mogły zostać ujawnione rekordy pacjentów.": "rekordy",
            "Grupy używały AI‑zarządzanego frameworka.": "AI‑zarządzanego",
            "Framework służył do intruzji.": "intruzji",
            "Napastnicy eksploatując FortiClient przejęli serwery.": "eksploatując",
        }
        for text, calque in cases.items():
            with self.subTest(text=text):
                problems = quality_problems(text)
                self.assertTrue(any(f"„{calque}”" in p and "kalka" in p for p in problems))

    def test_number_of_data_is_a_calque(self):
        self.assertTrue(any("kalka" in p for p in quality_problems("Mogło to narazić nieokreśloną liczbę danych pacjentów.")))

    def test_record_numbers_are_not_calques(self):
        self.assertEqual(quality_problems("Odnotowano rekordową liczbę ataków."), [])

    def test_style_problems_are_soft(self):
        self.assertEqual(quality_problems("Ujawniono rekordy pacjentów.", soft=False), [])

    def test_english_summary_is_reported(self):
        text = ("Hackers compromised the LiteLLM project and published malicious Docker images "
                "with a payload that steals credentials from the affected systems.")
        self.assertIn("streszczenie nie jest po polsku – napisz je po polsku", quality_problems(text))

    def test_polish_summary_with_english_names_is_fine(self):
        text = "Splunk wydał łatki dla Enterprise i SOAR, a SolarWinds dla Observability i Patch Manager."
        self.assertEqual(quality_problems(text), [])

    def test_summary_repeating_the_title(self):
        source = "Node2Shell (CVE-2026-111497): RCE przez dekompresję Brotli w Node.js\ntekst"
        problems = quality_problems("Node2Shell (CVE-2026-111497) umożliwia RCE przez dekompresję Brotli w Node.js.", source)
        self.assertTrue(any("powtarza tytuł" in p for p in problems))

    def test_impersonal_missing_information_and_bare_week(self):
        self.assertTrue(quality_problems("Infekcję potwierdzono. Nie podano sprawcy ani dalszych szczegółów."))
        self.assertTrue(quality_problems("W tygodniu zgłoszono ponad 4 500 przejętych kont."))
        self.assertEqual(quality_problems("Ataki trwały w tygodniu 12–18 października."), [])

if __name__ == "__main__":
    unittest.main()
