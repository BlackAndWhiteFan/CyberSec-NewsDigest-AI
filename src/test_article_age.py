import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from rss_helpers import is_too_old, item_published


NOW = datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc)


def item(xml):
    return ET.fromstring(xml)


class TestArticleAge(unittest.TestCase):
    def test_rss_pubdate(self):
        entry = item("<item><pubDate>Wed, 21 Oct 2026 18:28:00 GMT</pubDate></item>")
        self.assertEqual(item_published(entry), datetime(2026, 10, 21, 18, 28, tzinfo=timezone.utc))
        self.assertFalse(is_too_old(entry, NOW))

    def test_old_rss_item_is_skipped(self):
        entry = item("<item><pubDate>Tue, 15 Sep 2026 10:00:00 +0200</pubDate></item>")
        self.assertTrue(is_too_old(entry, NOW))

    def test_atom_published_date(self):
        old = item('<entry xmlns="http://www.w3.org/2005/Atom"><published>2026-10-18T09:00:00.000-07:00</published></entry>')
        fresh = item('<entry xmlns="http://www.w3.org/2005/Atom"><updated>2026-10-22T09:00:00Z</updated></entry>')
        self.assertTrue(is_too_old(old, NOW))
        self.assertFalse(is_too_old(fresh, NOW))

    def test_weekend_articles_are_kept_on_monday(self):
        saturday = item("<item><pubDate>Sat, 24 Oct 2026 07:00:00 +0200</pubDate></item>")
        monday = datetime(2026, 10, 26, 5, 17, tzinfo=timezone.utc)
        self.assertFalse(is_too_old(saturday, monday))

    def test_item_without_or_with_broken_date_is_kept(self):
        self.assertFalse(is_too_old(item("<item><title>A</title></item>"), NOW))
        self.assertFalse(is_too_old(item("<item><pubDate>wczoraj</pubDate></item>"), NOW))


if __name__ == "__main__":
    unittest.main()
