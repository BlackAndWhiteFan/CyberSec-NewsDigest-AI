import unittest

from glossary import (
    CORE_ENTRIES,
    ENTRIES,
    apply_glossary,
    convention_violations,
    prompt_glossary,
    relevant_entries,
)


def gloss(text):
    return apply_glossary(text, set())


def entry(entry_id):
    return next(item for item in ENTRIES if item["id"] == entry_id)


class TestMirror(unittest.TestCase):
    def test_mirror_has_unique_ids_and_required_columns(self):
        ids = [item["id"] for item in ENTRIES]

        self.assertGreater(len(ENTRIES), 700)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item["forma"] for item in ENTRIES))

    def test_digest_decisions_are_in_the_mirror(self):
        expected = {
            "H028": ("malware", "złośliwe oprogramowanie"),
            "H090": ("RCE", "zdalne wykonanie kodu"),
            "H152": ("PoC", "dowód słuszności koncepcji"),
            "H153": ("exploit", "kod wykorzystujący podatność"),
            "H159": ("zero-day", "luka dnia zerowego"),
            "H166": ("poprawka", "łatka"),
            "H182": ("podwyższenie uprawnień", "eskalacja"),
            "H207": ("poświadczenia", "dane logowania"),
            "H365": ("IAB", "broker dostępu początkowego"),
            "H023": ("backdoor", "tylna furtka"),
        }

        for entry_id, (forma, nawias) in expected.items():
            with self.subTest(entry_id=entry_id):
                self.assertEqual((entry(entry_id)["forma"], entry(entry_id)["nawias"]), (forma, nawias))

    def test_polish_entry_without_english_first_has_no_explanation(self):
        self.assertEqual(entry("H063")["forma"], "atak na łańcuch dostaw")
        self.assertEqual(entry("H063")["nawias"], "")


class TestExplanations(unittest.TestCase):
    def test_english_first_entries_get_polish_explanation(self):
        cases = {
            "Rozsyłano malware.": "Rozsyłano malware (złośliwe oprogramowanie).",
            "Luka pozwala na RCE.": "Luka pozwala na RCE (zdalne wykonanie kodu).",
            "Badacze opublikowali PoC.": "Badacze opublikowali PoC (dowód słuszności koncepcji).",
            "Napastnicy zostawili backdoor w routerze.":
                "Napastnicy zostawili backdoor (tylna furtka) w routerze.",
            "Atak ransomware sparaliżował szpital.":
                "Atak ransomware (oprogramowanie wymuszające okup) sparaliżował szpital.",
            "Dostęp sprzedał IAB.": "Dostęp sprzedał IAB (broker dostępu początkowego).",
            "Grupa użyła exploita.": "Grupa użyła exploita (kod wykorzystujący podatność).",
        }

        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(gloss(text), expected)

    def test_explanation_agrees_with_case(self):
        cases = {
            "Producent wydał poprawkę.": "Producent wydał poprawkę (łatkę).",
            "W poprawce brakuje zmian.": "W poprawce (łatce) brakuje zmian.",
            "Luka umożliwia podwyższenie uprawnień.":
                "Luka umożliwia podwyższenie (eskalację) uprawnień.",
            "Doszło do podwyższenia uprawnień.": "Doszło do podwyższenia (eskalacji) uprawnień.",
            "Wykradziono poświadczenia.": "Wykradziono poświadczenia (dane logowania).",
            "Użyto skradzionych poświadczeń.": "Użyto skradzionych poświadczeń (danych logowania).",
            "Grupa opłacana przez państwo zaatakowała.":
                "Grupa opłacana przez państwo (sponsorowana) zaatakowała.",
        }

        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(gloss(text), expected)

    def test_term_explained_once_per_digest(self):
        used = set()
        first = apply_glossary("Atak ransomware na szpital.", used)
        second = apply_glossary("Kolejny atak ransomware na urząd.", used)

        self.assertIn("(oprogramowanie wymuszające okup)", first)
        self.assertEqual(second, "Kolejny atak ransomware na urząd.")

    def test_existing_parenthesis_counts_as_explained(self):
        used = set()
        text = "Malware (szkodnik) się rozprzestrzenia."

        self.assertEqual(apply_glossary(text, used), text)
        self.assertIn("H028", used)

    def test_acronyms_are_case_sensitive(self):
        self.assertEqual(gloss("Klient zamówił poc."), "Klient zamówił poc.")


class TestConventionViolations(unittest.TestCase):
    def test_forbidden_forms_are_detected(self):
        cases = {
            "Luka pozwala na eskalację uprawnień.": "podwyższenie uprawnień",
            "Badacze opublikowali eksploit.": "exploit",
            "Producent wydał łatkę.": "poprawka",
            "Za atakiem stoją aktorzy zagrożeń.": "sprawcy",
            "Rozsyłano złośliwe oprogramowanie.": "malware",
            "Możliwe jest zdalne wykonanie kodu.": "RCE",
            "Opublikowano dowód koncepcji.": "PoC",
            "Wykradziono kredencjały.": "poświadczenia",
            "Grupa sponsorowana przez państwo.": "opłacani przez państwo",
        }

        for text, required in cases.items():
            with self.subTest(text=text):
                violations = convention_violations(text)
                self.assertEqual([forma for _, forma in violations], [required])

    def test_correct_text_has_no_violations(self):
        text = (
            "Luka umożliwia RCE i podwyższenie uprawnień; badacze opublikowali PoC, "
            "a producent wydał poprawkę."
        )
        self.assertEqual(convention_violations(text), [])

    def test_explanations_added_by_code_are_not_checked(self):
        # The check runs on the AI text before explanations are added.
        self.assertEqual(convention_violations("Producent wydał poprawkę."), [])


class TestPrompt(unittest.TestCase):
    def test_core_conventions_are_always_in_the_prompt(self):
        text = prompt_glossary(["Zupełnie inny tekst."])

        for item in CORE_ENTRIES:
            self.assertIn(f"- {item['termin_en']} → {item['forma']}", text)

    def test_entries_found_in_article_text_are_added(self):
        selected = relevant_entries(["Attackers used password spraying against VPN."])
        ids = {item["id"] for item in selected}

        self.assertIn("H134", ids)  # password spraying

    def test_prompt_size_is_limited(self):
        long_text = " ".join(item["termin_en"] for item in ENTRIES)
        self.assertLessEqual(len(relevant_entries([long_text])), len(CORE_ENTRIES) + 40)


if __name__ == "__main__":
    unittest.main()
