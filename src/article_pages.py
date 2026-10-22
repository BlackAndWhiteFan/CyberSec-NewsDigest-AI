"""Article text from the article page, when the feed gives too little (v27).

Many feeds (BleepingComputer, The Hacker News, The Record) give only a
one- or two-sentence teaser, so the AI had little to summarize. For each
selected article whose feed material is shorter than MIN_FEED_MATERIAL, the
article page is downloaded once and its paragraphs (<p>) are extracted, with
the text inside <article> preferred. Only plain text is kept: no scripts,
links or markup. The page text is untrusted data, like the feed text, and is
used only as material for the AI summary and the fact check.

Errors never stop the digest: a page that cannot be fetched (timeout, 403
from bot protection, wrong content type) leaves the article with its feed
material.
"""

import re
import urllib.request
from html.parser import HTMLParser

from rss_helpers import is_valid_url


MIN_FEED_MATERIAL = 600
PAGE_TEXT_LIMIT = 4000
MIN_PARAGRAPH_LENGTH = 60
FETCH_TIMEOUT = 15
MAX_PAGE_BYTES = 2_000_000
USER_AGENT = "Mozilla/5.0 (compatible; CyberSec-NewsDigest-AI/1.0)"

SKIPPED_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "aside", "form", "figure", "button"}

# Paragraphs that are page furniture, not article text.
BOILERPLATE = re.compile(
    r"\b(?:we use cookies|używamy (?:plików )?cookies|cookie policy|polityk\w* (?:prywatności|cookies)|"
    r"newsletter\w*|subscribe to|sign up|zapisz się|subskrybuj\w*|all rights reserved|"
    r"udostępnij|share this|related articles|czytaj (?:też|także|również)|advertisement|reklama)\b|©",
    re.IGNORECASE,
)


class ParagraphParser(HTMLParser):
    """Collect paragraph texts, separately for paragraphs inside <article>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.article_depth = 0
        self.paragraph = None
        self.paragraph_in_article = False
        self.paragraphs = []
        self.article_paragraphs = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIPPED_TAGS:
            self.skip_depth += 1
        elif tag == "article":
            self.article_depth += 1
        elif tag == "p" and not self.skip_depth:
            self.close_paragraph()
            self.paragraph = []
            self.paragraph_in_article = self.article_depth > 0

    def handle_endtag(self, tag):
        if tag in SKIPPED_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "article" and self.article_depth:
            self.article_depth -= 1
        elif tag == "p":
            self.close_paragraph()

    def handle_data(self, data):
        if self.paragraph is not None and not self.skip_depth:
            self.paragraph.append(data)

    def close_paragraph(self):
        if self.paragraph is None:
            return

        text = re.sub(r"\s+", " ", "".join(self.paragraph)).strip()
        self.paragraph = None

        if len(text) < MIN_PARAGRAPH_LENGTH or BOILERPLATE.search(text):
            return

        self.paragraphs.append(text)

        if self.paragraph_in_article:
            self.article_paragraphs.append(text)


def extract_text(page_html, limit=PAGE_TEXT_LIMIT):
    """Return the article text of a page: its paragraphs, joined and limited."""
    parser = ParagraphParser()
    parser.feed(page_html or "")
    parser.close()
    parser.close_paragraph()

    paragraphs = parser.article_paragraphs or parser.paragraphs
    text = ""

    for paragraph in paragraphs:
        if text and len(text) + len(paragraph) + 1 > limit:
            break

        text = f"{text} {paragraph}".strip()

    return text[:limit]


def fetch_page(url, opener=urllib.request.urlopen):
    """Return the HTML of a page (text/html only, size limited)."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})

    with opener(request, timeout=FETCH_TIMEOUT) as response:
        content_type = response.headers.get("Content-Type", "")

        if "html" not in content_type.lower():
            raise ValueError(f"nie HTML: {content_type[:40]}")

        charset = response.headers.get_content_charset() or "utf-8"
        return response.read(MAX_PAGE_BYTES).decode(charset, errors="replace")


def add_page_texts(articles, material_length, opener=urllib.request.urlopen):
    """Add "page_text" to articles with too little feed material.

    material_length(article) returns the length of the feed material. Returns
    the number of articles that got a longer text from their page.
    """
    added = 0
    needed = [article for article in articles if material_length(article) < MIN_FEED_MATERIAL]

    for article in needed:
        url = article.get("link", "")

        if not is_valid_url(url):
            continue

        try:
            text = extract_text(fetch_page(url, opener))
        except Exception as error:
            print(f"PEŁNA TREŚĆ: {url} – {type(error).__name__}: {str(error)[:120]}")
            continue

        if len(text) > material_length(article):
            article["page_text"] = text
            added += 1
        else:
            print(f"PEŁNA TREŚĆ: {url} – strona nie dała dłuższego tekstu")

    print(f"Pełna treść ze stron: {added} z {len(needed)} artykułów z krótkim opisem w RSS")
    return added
