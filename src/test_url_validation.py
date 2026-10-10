import unittest

from rss_helpers import is_valid_url, is_duplicate_link


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


if __name__ == "__main__":
    unittest.main()
