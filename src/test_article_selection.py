
import unittest

from article_selection import (
    categorize_article,
    is_excluded,
    prioritize_article,
    select_top_articles,
)


def make_article(title, link="https://example.com/article", description=""):
    return {"title": title, "link": link, "description": description}


class TestArticleSelection(unittest.TestCase):
    
    def test_selects_articles_by_priority(self):
        articles = [
            {"title": "Technology company announces results", "description": ""},
            {"title": "New CVE-2026-12345 vulnerability disclosed", "description": ""},
            {"title": "Ransomware attack actively exploited in the wild", "description": ""},
        ]

        selected = select_top_articles(articles)

        self.assertEqual(selected[0]["title"], "Ransomware attack actively exploited in the wild")
        self.assertEqual(selected[1]["title"], "New CVE-2026-12345 vulnerability disclosed")

    def test_respects_article_limit(self):
        articles = [
            make_article("First ransomware attack", "https://a.example/1"),
            make_article("Second ransomware attack", "https://b.example/2"),
            make_article("Third ransomware attack", "https://c.example/3"),
        ]

        selected = select_top_articles(articles, limit=2)

        self.assertEqual(len(selected), 2)

    def test_zero_limit_returns_no_articles(self):
        articles = [
            {"title": "Ransomware attack reported", "description": ""},
        ]

        self.assertEqual(select_top_articles(articles, limit=0), [])

    def test_detects_critical_article(self):
        article = {
            "title": "Ransomware attack hits a major company",
            "description": "Investigators are examining the incident.",
        }

        self.assertIn("critical", categorize_article(article))

    def test_detects_vulnerability(self):
        article = {
            "title": "New CVE-2026-12345 vulnerability disclosed",
            "description": "A security patch is available.",
        }

        self.assertIn("vulnerabilities", categorize_article(article))

    def test_detects_poland_related_article(self):
        article = {
            "title": "New cybersecurity alert issued in Poland",
            "description": "Authorities published a security advisory.",
        }

        self.assertIn("poland", categorize_article(article))

    def test_article_can_have_multiple_categories(self):
        article = {
            "title": "Critical vulnerability affects Polish organizations",
            "description": "A new CVE has been disclosed.",
        }

        categories = categorize_article(article)

        self.assertIn("critical", categories)
        self.assertIn("vulnerabilities", categories)
        self.assertIn("poland", categories)

    def test_priority_score_combines_categories(self):
        article = {
            "title": "Ransomware exploits a new CVE in Poland",
            "description": "A major incident has been reported.",
        }

        self.assertEqual(prioritize_article(article), 6)

    def test_unmatched_article_has_no_categories(self):
        article = {
            "title": "Technology company announces quarterly results",
            "description": "The company reported its latest financial results.",
        }

        self.assertEqual(categorize_article(article), [])
        self.assertEqual(prioritize_article(article), 0)

    def test_handles_missing_title_and_description(self):
        self.assertEqual(categorize_article({}), [])
        self.assertEqual(prioritize_article({}), 0)



class TestPolishKeywords(unittest.TestCase):

    def test_inflected_forms_are_recognized(self):
        critical_titles = [
            "Wyciek danych pacjentów",
            "Kolejny wyciekiem zagrożone dane",
            "ENEL-MED informuje o kradzieży danych pacjentów",
            "Wakacje.pl zhackowane",
            "Sklep internetowy został zhakowany",
            "Przestępcy włamali się do systemu",
            "Grupa hakerska atakuje urzędy",
            "Duży cyberatak na sklepy",
            "Krytycznej podatności nie załatano",
        ]

        for title in critical_titles:
            with self.subTest(title=title):
                self.assertIn("critical", categorize_article(make_article(title)))

    def test_vulnerability_forms_are_recognized(self):
        titles = [
            "Nowa podatność w routerach",
            "Błąd w luce bezpieczeństwa",
            "Producent wydał łatkę",
            "Poprzez SQL injection dostali się do bazy",
            "Podatność XSS w komentarzach",
        ]

        for title in titles:
            with self.subTest(title=title):
                self.assertIn(
                    "vulnerabilities",
                    categorize_article(make_article(title)),
                )

    def test_stems_do_not_match_inside_other_words(self):
        article = make_article("Lukratywny kontrakt dla niepolskich firm")
        self.assertEqual(categorize_article(article), [])

    def test_polish_locative_form_is_recognized(self):
        self.assertIn("poland", categorize_article(make_article("Atak w Polsce")))


class TestSelectionRules(unittest.TestCase):

    def test_poland_alone_does_not_reach_threshold(self):
        article = make_article("Polskie modele AI na zakręcie")
        self.assertEqual(select_top_articles([article]), [])

    def test_unmatched_article_is_not_selected(self):
        article = make_article("Roboty zyskają zmysł dotyku?")
        self.assertEqual(select_top_articles([article]), [])

    def test_promotional_title_is_excluded(self):
        article = make_article(
            "Jak reagować na wyciek danych? Bezpłatne szkolenie od sekuraka"
        )

        self.assertTrue(is_excluded(article))
        self.assertEqual(select_top_articles([article]), [])

    def test_webinar_is_excluded(self):
        article = make_article(
            "(Webinar) How to Stop AI-Driven Privilege Escalation"
        )
        self.assertTrue(is_excluded(article))

    def test_training_mentioned_in_incident_is_not_excluded(self):
        article = make_article("Phishing podszywa się pod szkolenie BHP")
        self.assertFalse(is_excluded(article))

    def test_lecture_announcement_is_excluded(self):
        article = make_article(
            "Jak nie dać się zhackować? Ruszamy w Polskę z kolejną edycją "
            "naszego kultowego wykładu"
        )
        self.assertTrue(is_excluded(article))

    def test_weekly_roundups_are_not_excluded(self):
        self.assertFalse(is_excluded(make_article("Weekendowa lektura: odcinek 697")))

    def test_default_source_limit_is_four(self):
        articles = [
            make_article(f"Ransomware attack {i}", f"https://www.thehackernews.com/{i}")
            for i in range(10)
        ]

        self.assertEqual(len(select_top_articles(articles)), 4)

    def test_niebezpiecznik_limit_is_two(self):
        articles = [
            make_article(f"Wyciek danych {i}", f"https://niebezpiecznik.pl/post/{i}")
            for i in range(5)
        ]

        self.assertEqual(len(select_top_articles(articles)), 2)

    def test_source_limit_leaves_room_for_other_sources(self):
        articles = [
            make_article(f"Ransomware attack {i}", f"https://thehackernews.com/{i}")
            for i in range(6)
        ] + [make_article("Nowa podatność w routerach", "https://sekurak.pl/x")]

        selected = select_top_articles(articles)

        self.assertEqual(len(selected), 5)
        self.assertEqual(selected[-1]["link"], "https://sekurak.pl/x")



class TestContextAndTitleOnlyKeywords(unittest.TestCase):

    def test_incident_in_title_is_critical(self):
        article = make_article(
            "Kolejni pacjenci mogą mieć duży problem, czyli nowy incydent "
            "w branży medycznej"
        )

        self.assertIn("critical", categorize_article(article))
        self.assertEqual(len(select_top_articles([article])), 1)

    def test_incident_only_in_description_is_not_critical(self):
        article = make_article(
            "Nowe przepisy dla operatorów",
            description="W razie incydentu operator ma 24 godziny.",
        )
        self.assertNotIn("critical", categorize_article(article))

    def test_cyberattack_in_conference_context_is_not_selected(self):
        article = make_article(
            "AI przyspiesza cyberataki, a firmowe systemy pozostają na "
            "celowniku. Eksperci Sprint Cyber Forum o rosnącej skali zagrożeń"
        )
        self.assertEqual(select_top_articles([article]), [])

    def test_cyberattack_trend_report_is_not_selected(self):
        article = make_article(
            "Firmy widzą wzrost cyberataków. Droga do odporności jest jednak daleka"
        )
        self.assertEqual(select_top_articles([article]), [])

    def test_advice_article_is_not_selected(self):
        article = make_article(
            "Jak używać AI do ochrony przed atakami, wykrywania włamań "
            "i analizy incydentu?"
        )
        self.assertEqual(select_top_articles([article]), [])

    def test_concrete_cyberattack_is_selected(self):
        article = make_article("Duży cyberatak na lodówki i zamrażarki sklepowe")
        self.assertEqual(len(select_top_articles([article])), 1)

    def test_strong_signals_survive_context_penalty(self):
        article = make_article(
            "Na konferencji ujawniono krytyczną podatność CVE-2026-1234"
        )
        self.assertEqual(len(select_top_articles([article])), 1)

    def test_vulnerability_in_admin_panel_is_not_penalized(self):
        article = make_article("Podatność w panelu administracyjnym routera")
        self.assertEqual(prioritize_article(article), 2)


if __name__ == "__main__":
    unittest.main()
