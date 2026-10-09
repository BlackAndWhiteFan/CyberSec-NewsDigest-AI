import unittest

from deduplication import add_article


class TestAddArticle(unittest.TestCase):

    def setUp(self):
        self.articles = []
        self.seen_links = {}

    def test_adds_new_article(self):
        add_article(
            self.articles,
            self.seen_links,
            "feed_a",
            "Test article",
            "https://example.com/article"
        )

        self.assertEqual(len(self.articles), 1)
        self.assertEqual(self.articles[0]["title"], "Test article")
        self.assertEqual(
            self.articles[0]["link"],
            "https://example.com/article"
        )
        self.assertEqual(self.articles[0]["sources"], ["feed_a"])

    def test_does_not_add_duplicate_link(self):
        add_article(
            self.articles,
            self.seen_links,
            "feed_a",
            "Test article",
            "https://example.com/article"
        )
        add_article(
            self.articles,
            self.seen_links,
            "feed_b",
            "Test article",
            "https://example.com/article"
        )

        self.assertEqual(len(self.articles), 1)

    def test_tracks_all_sources_for_duplicate_link(self):
        add_article(
            self.articles,
            self.seen_links,
            "feed_a",
            "Test article",
            "https://example.com/article"
        )
        add_article(
            self.articles,
            self.seen_links,
            "feed_b",
            "Test article",
            "https://example.com/article"
        )

        self.assertEqual(
            self.articles[0]["sources"],
            ["feed_a", "feed_b"]
        )

    def test_does_not_duplicate_same_source(self):
        add_article(
            self.articles,
            self.seen_links,
            "feed_a",
            "Test article",
            "https://example.com/article"
        )
        add_article(
            self.articles,
            self.seen_links,
            "feed_a",
            "Test article",
            "https://example.com/article"
        )

        self.assertEqual(len(self.articles), 1)
        self.assertEqual(self.articles[0]["sources"], ["feed_a"])


if __name__ == "__main__":
    unittest.main()
