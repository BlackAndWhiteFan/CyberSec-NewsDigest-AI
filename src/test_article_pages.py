import io
import unittest
import urllib.error
from email.message import Message

from article_pages import MIN_FEED_MATERIAL, add_page_texts, extract_text


PAGE = """<html><head><title>T</title><script>var x = "<p>not text</p>";</script></head>
<body>
<nav><p>Home · News · Security · Downloads · Deals · Forums · Contact us today</p></nav>
<p>Sidebar paragraph outside the article that is long enough to be counted as text.</p>
<article>
  <h1>PHP2Shell exploitation began 4 days before patches</h1>
  <p>Amazon Threat Intelligence says attackers began exploiting the PHP2Shell flaws on October 17, four days before patches.</p>
  <p>Short.</p>
  <p>The attempts came from an IP address of a commercial anonymizing network and targeted the MadPot honeypot.</p>
  <p>Subscribe to our newsletter to get the latest security news delivered to your inbox every day.</p>
  <aside><p>Related articles: ten more stories you should read about PHP security this week.</p></aside>
</article>
<footer><p>Copyright © 2026 Example Media. All rights reserved by the publisher of this site.</p></footer>
</body></html>"""


class FakeResponse(io.BytesIO):
    def __init__(self, body, content_type="text/html; charset=utf-8"):
        super().__init__(body.encode("utf-8"))
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class TestExtractText(unittest.TestCase):
    def test_article_paragraphs_without_furniture(self):
        text = extract_text(PAGE)

        self.assertTrue(text.startswith("Amazon Threat Intelligence says"))
        self.assertIn("MadPot honeypot.", text)
        for unwanted in ["not text", "Sidebar", "Subscribe", "Related articles", "Copyright", "Home ·"]:
            self.assertNotIn(unwanted, text)

    def test_page_without_article_tag_uses_all_paragraphs(self):
        page = "<div><p>" + "Polski tekst artykułu o wycieku danych z firmy, który ma ponad 60 znaków." + "</p></div>"
        self.assertIn("Polski tekst artykułu", extract_text(page))

    def test_text_is_limited(self):
        page = "<article>" + "".join(f"<p>{'Paragraph number %d with enough words to count. ' % i * 2}</p>" for i in range(200)) + "</article>"
        self.assertLessEqual(len(extract_text(page, limit=1000)), 1000)


class TestAddPageTexts(unittest.TestCase):
    def test_short_feed_material_gets_page_text(self):
        articles = [
            {"title": "A", "link": "https://example.com/a", "description": "Short teaser."},
            {"title": "B", "link": "https://example.com/b", "description": "x" * MIN_FEED_MATERIAL},
        ]
        requested = []

        def opener(request, timeout):
            requested.append(request.full_url)
            return FakeResponse(PAGE)

        added = add_page_texts(articles, lambda a: len(a.get("description", "")), opener)

        self.assertEqual(added, 1)
        self.assertEqual(requested, ["https://example.com/a"])
        self.assertIn("MadPot", articles[0]["page_text"])
        self.assertNotIn("page_text", articles[1])

    def test_errors_and_non_html_pages_are_skipped(self):
        articles = [
            {"title": "A", "link": "https://example.com/a", "description": ""},
            {"title": "B", "link": "https://example.com/b", "description": ""},
        ]
        replies = [
            urllib.error.HTTPError("https://example.com/a", 403, "Forbidden", {}, None),
            FakeResponse("%PDF", "application/pdf"),
        ]

        def opener(request, timeout):
            reply = replies.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return reply

        self.assertEqual(add_page_texts(articles, lambda a: 0, opener), 0)
        self.assertNotIn("page_text", articles[0])
        self.assertNotIn("page_text", articles[1])


if __name__ == "__main__":
    unittest.main()
