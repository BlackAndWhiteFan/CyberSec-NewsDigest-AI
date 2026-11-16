import unittest

from glossary import (
    gloss_rule,
    GLOSS_RULES,
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

    def test_only_chosen_entries_have_explanations(self):
        """Option B (20.10.2026): parentheses only where JW decided.
        v40 (Letter 18, decision of 2.11.2026): only H182 and H207 remain."""
        expected = {
            "H182": ("podwyższenie uprawnień", "eskalacja"),
            "H207": ("poświadczenia", "dane logowania"),
        }
        with_explanation = {item["id"] for item in ENTRIES if item["nawias"]}

        self.assertEqual(with_explanation, set(expected))
        for entry_id, (forma, nawias) in expected.items():
            with self.subTest(entry_id=entry_id):
                self.assertEqual((entry(entry_id)["forma"], entry(entry_id)["nawias"]), (forma, nawias))

    def test_english_first_entries_keep_english_form_without_explanation(self):
        for entry_id, forma in {"H153": "exploit", "H004": "botnet", "H015": "ransomware",
                                "H019": "infostealer", "H028": "malware", "H090": "RCE", "H152": "PoC",
                                "H023": "backdoor", "H365": "IAB", "H726": "DLL sideloading"}.items():
            with self.subTest(entry_id=entry_id):
                self.assertEqual((entry(entry_id)["forma"], entry(entry_id)["nawias"]), (forma, ""))

    def test_polish_entry_without_english_first_has_no_explanation(self):
        self.assertEqual(entry("H063")["forma"], "atak na łańcuch dostaw")
        self.assertEqual(entry("H063")["nawias"], "")


class TestExplanations(unittest.TestCase):
    def test_chosen_entries_get_explanation(self):
        cases = {
            "Wykradziono poświadczenia.": "Wykradziono poświadczenia (dane logowania).",
            "Luka umożliwia podwyższenie uprawnień.":
                "Luka umożliwia podwyższenie (eskalację) uprawnień.",
        }

        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(gloss(text), expected)

    def test_other_terms_get_no_explanation(self):
        text = (
            "Rozsyłano malware, luka daje RCE, badacze opublikowali PoC i backdoor w NATO przez NAT; "
            "producent wydał łatkę, a grupa opłacana przez państwo zaatakowała."
        )
        self.assertEqual(gloss(text), text)

    def test_terms_without_explanation_since_v40(self):
        # Letter 18: exploit, botnet, ransomware, infostealer and wiper stay bare.
        text = ("Grupa użyła exploita i ransomware, przejęła botnet, rozsyłała infostealera "
                "i uruchomiła wiper.")
        self.assertEqual(gloss(text), text)

    def test_explanation_agrees_with_case(self):
        cases = {
            "Luka umożliwia podwyższenie uprawnień.":
                "Luka umożliwia podwyższenie (eskalację) uprawnień.",
            "Doszło do podwyższenia uprawnień.": "Doszło do podwyższenia (eskalacji) uprawnień.",
            "Wykradziono poświadczenia.": "Wykradziono poświadczenia (dane logowania).",
            "Użyto skradzionych poświadczeń.": "Użyto skradzionych poświadczeń (danych logowania).",
        }

        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(gloss(text), expected)

    def test_term_explained_once_per_digest(self):
        used = set()
        first = apply_glossary("Wykradziono poświadczenia.", used)
        second = apply_glossary("Znów wykradziono poświadczenia.", used)

        self.assertIn("(dane logowania)", first)
        self.assertEqual(second, "Znów wykradziono poświadczenia.")

    def test_existing_parenthesis_counts_as_explained(self):
        used = set()
        text = "Wykradziono poświadczenia (loginy i hasła)."

        self.assertEqual(apply_glossary(text, used), text)
        self.assertIn("H207", used)

    def test_term_inside_parentheses_gets_no_nested_explanation(self):
        text = "Przejęto dane logowania (poświadczenia) w trzech krajach."
        self.assertNotIn("(poświadczenia (", gloss(text))

    def test_term_after_parentheses_is_still_explained(self):
        used = set()
        apply_glossary("Przejęto dane logowania (poświadczenia).", used)
        self.assertIn("poświadczenia (dane logowania)", apply_glossary("Wykradziono poświadczenia.", used))

    def test_mfa_has_no_explanation(self):
        self.assertEqual(gloss("Firma wymaga MFA."), "Firma wymaga MFA.")

    def test_longer_terms_are_checked_first(self):
        lengths = [len(next(item for item in ENTRIES if item["id"] == key)["forma"]) for key, *_ in GLOSS_RULES]
        self.assertEqual(lengths, sorted(lengths, reverse=True))

    # No chosen explanation is an acronym any more (MFA without parentheses
    # since 21.10.2026), so acronym matching is tested on a sample entry.
    ACRONYM_ENTRY = {"id": "TEST", "forma": "NAT", "nawias": "translacja adresów"}

    def test_acronym_is_not_matched_inside_a_longer_word(self):
        pattern, _ = gloss_rule(self.ACRONYM_ENTRY)
        self.assertIsNone(pattern.search("Zaatakowano członków NATO."))

    def test_inflected_acronym_after_hyphen_is_matched(self):
        pattern, _ = gloss_rule(self.ACRONYM_ENTRY)
        self.assertEqual(pattern.search("Router z NAT-em.").group("anchor"), "NAT-em")

    def test_acronyms_are_case_sensitive(self):
        pattern, _ = gloss_rule(self.ACRONYM_ENTRY)
        self.assertIsNone(pattern.search("Słowo nat w zdaniu."))


class TestConventionViolations(unittest.TestCase):
    def test_forbidden_forms_are_detected(self):
        cases = {
            "Luka pozwala na eskalację uprawnień.": "podwyższenie uprawnień",
            "Badacze opublikowali eksploit.": "exploit",
            "Za atakiem stoją aktorzy zagrożeń.": "sprawcy",
            "Rozsyłano złośliwe oprogramowanie.": "malware",
            "Możliwe jest remote code execution.": "RCE",
            "Opublikowano dowód koncepcji.": "PoC",
            "Wykradziono kredencjały.": "poświadczenia",
            "Grupa sponsorowana przez państwo.": "opłacani przez państwo",
            "Załatano dwie podatności (luka) RCE.": "podatność",
            "Błąd może umożliwić remote code execution.": "RCE",
            "Aktualizacje patchują zero-day.": "łatka",
        }

        for text, required in cases.items():
            with self.subTest(text=text):
                violations = convention_violations(text)
                self.assertEqual([forma for _, forma in violations], [required])

    def test_correct_text_has_no_violations(self):
        text = (
            "Luka umożliwia RCE i podwyższenie uprawnień; badacze opublikowali PoC, "
            "a producent wydał łatkę."
        )
        self.assertEqual(convention_violations(text), [])

    def test_explanations_added_by_code_are_not_checked(self):
        # The check runs on the AI text before explanations are added.
        self.assertEqual(convention_violations("Producent wydał łatkę."), [])

    def test_list42_poprawka_and_expansion_are_allowed(self):
        # v52 (List 42, mirror build 102): "poprawka" and "zdalne wykonanie
        # kodu" are correct; "patchować" stays forbidden.
        self.assertEqual(convention_violations("Firma wydała poprawki; możliwe jest zdalne wykonanie kodu."), [])
        self.assertEqual([forma for _, forma in convention_violations("Firma spatchowała lukę.")], ["łatka"])


class TestPrompt(unittest.TestCase):
    def test_core_conventions_are_always_in_the_prompt(self):
        text = prompt_glossary(["Zupełnie inny tekst."])

        for item in CORE_ENTRIES:
            english = item["termin_en"].split(" (")[0]
            self.assertIn(f"- {english} → {item['forma']}", text)

    def test_entries_found_in_article_text_are_added(self):
        selected = relevant_entries(["Attackers used password spraying against VPN."])
        ids = {item["id"] for item in selected}

        self.assertIn("H134", ids)  # password spraying

    def test_prompt_shows_english_terms_without_parentheses(self):
        text = prompt_glossary([""])
        self.assertIn("- exploit → exploit", text)
        self.assertNotIn("exploit (kit)", text)

    def test_prompt_size_is_limited(self):
        long_text = " ".join(item["termin_en"] for item in ENTRIES)
        self.assertLessEqual(len(relevant_entries([long_text])), len(CORE_ENTRIES) + 40)


class TestAutofixV29(unittest.TestCase):
    def test_duplicate_acronym_and_iphone(self):
        from glossary import autofix
        self.assertEqual(
            autofix("Luki umożliwiają remote code execution (RCE) na iPhoneie."),
            "Luki umożliwiają RCE na iPhonie.",
        )

    def test_list42_correct_forms_stay(self):
        # v52 (List 42): "poprawka" and "zdalne wykonanie kodu" are correct.
        from glossary import autofix
        text = "Wydano poprawkę bezpieczeństwa; luka pozwalała na zdalne wykonanie kodu."
        self.assertEqual(autofix(text), text)
        self.assertEqual(autofix("Luka pozwala na wykonanie kodu zdalnie."), "Luka pozwala na wykonanie kodu zdalnie.")

    def test_escalation_after_typu_is_nominative(self):
        self.assertEqual(
            gloss("Osiem luk typu podwyższenie uprawnień."),
            "Osiem luk typu podwyższenie (eskalacja) uprawnień.",
        )
        self.assertEqual(
            gloss("Luka umożliwia podwyższenie uprawnień."),
            "Luka umożliwia podwyższenie (eskalację) uprawnień.",
        )

if __name__ == "__main__":
    unittest.main()
