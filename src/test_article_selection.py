
import unittest

from article_selection import (
    categorize_article,
    prioritize_article,
    select_top_articles,
)

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
            {"title": "First article", "description": ""},
            {"title": "Second article", "description": ""},
            {"title": "Third article", "description": ""},
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


if __name__ == "__main__":
    unittest.main()
