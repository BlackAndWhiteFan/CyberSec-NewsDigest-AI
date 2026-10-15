import unittest

from rss_helpers import clean_title, is_valid_url, is_duplicate_link


class TestIsValidUrl(unittest.TestCase):

    def test_accepts_https_url(self):
        self.assertTrue(is_valid_url("https://example.com/article"))

    def test_accepts_http_url(self):
        self.assertTrue(is_valid_url("http://example.com/article"))

    def test_rejects_empty_url(self):
        self.assertFalse(is_valid_url(""))

    def test_rejects_missing_scheme(self):
        self.assertFalse(is_valid_url("example.com/article"))

    def test_rejects_missing_host(self):
        self.assertFalse(is_valid_url("https://"))

    def test_rejects_unsupported_scheme(self):
        self.assertFalse(is_valid_url("ftp://example.com/file"))
    
    def test_duplicate_link_is_detected(self):
        seen_links = {"https://example.com/article": []}
        self.assertTrue(is_duplicate_link("https://example.com/article", seen_links))

    def test_new_link_is_not_a_duplicate(self):
        seen_links = {"https://example.com/article": []}
        self.assertFalse(is_duplicate_link("https://example.com/another-article", seen_links))


class TestCleanTitle(unittest.TestCase):

    def test_decodes_numeric_entities(self):
        self.assertEqual(clean_title("Nowy incydent&#8230;"), "Nowy incydent…")

    def test_decodes_hex_entities(self):
        self.assertEqual(clean_title("&#x1f4cc; Wykład"), "📌 Wykład")

    def test_decodes_named_entities_and_strips_spaces(self):
        self.assertEqual(clean_title("  Tom &amp; Jerry "), "Tom & Jerry")

    def test_handles_missing_title(self):
        self.assertEqual(clean_title(None), "")


if __name__ == "__main__":
    unittest.main()
