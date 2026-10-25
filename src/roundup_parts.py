"""Splitting "Weekendowa lektura" (Zaufana Trzecia Strona) into its links (v31).

The weekly roundup is a list of links to articles on other sites, each with
a short Polish comment. Instead of one line for the whole roundup, every
link becomes a candidate article: it goes through the same scoring,
threshold, deduplication and event merging as any other article, so only
the security "meat" reaches the digest (at most LEKTURA_LIMIT links per
digest, see article_selection). Such articles are shown "via Zaufana
Trzecia Strona".

A part is a list item (<li>) or paragraph (<p>) with a link to another
site; its link text is the title (or the beginning of the comment when the
link text is too short) and the whole text is the description. When no
part is found (the layout changed), the roundup stays one line with its
fixed description, as in v29.
"""

import re
import urllib.parse
from html.parser import HTMLParser


VIA_LEKTURA = "Zaufana Trzecia Strona (Weekendowa lektura)"
OWN_DOMAINS = ("zaufanatrzeciastrona.pl",)
MIN_PART_TEXT = 40
MIN_TITLE_LENGTH = 15
MAX_TITLE_LENGTH = 200


def domain(url):
    return urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")


class PartsParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.block = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("li", "p"):
            if self.block is None:
                self.block = {"text": [], "link": "", "anchor": [], "in_anchor": False}
                self.depth = 0
            else:
                self.depth += 1
        elif tag == "a" and self.block is not None:
            href = dict(attrs).get("href", "") or ""

            if not self.block["link"] and href.startswith(("http://", "https://")) and not domain(href).endswith(OWN_DOMAINS):
                self.block["link"] = href
                self.block["in_anchor"] = True

    def handle_endtag(self, tag):
        if self.block is None:
            return

        if tag == "a":
            self.block["in_anchor"] = False
        elif tag in ("li", "p"):
            if self.depth:
                self.depth -= 1
            else:
                self.finish()

    def handle_data(self, data):
        if self.block is not None:
            self.block["text"].append(data)

            if self.block["in_anchor"]:
                self.block["anchor"].append(data)

    def finish(self):
        block, self.block = self.block, None
        text = re.sub(r"\s+", " ", "".join(block["text"])).strip()

        if not block["link"] or len(text) < MIN_PART_TEXT:
            return

        anchor = re.sub(r"\s+", " ", "".join(block["anchor"])).strip()
        title = anchor if len(anchor) >= MIN_TITLE_LENGTH else text

        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH - 1].rsplit(" ", 1)[0] + "…"

        self.parts.append({"title": title, "link": block["link"], "description": text})


def extract_parts(html):
    """Return [{"title", "link", "description"}] for the links of a roundup."""
    parser = PartsParser()
    parser.feed(html or "")
    parser.close()

    if parser.block is not None:
        parser.finish()

    seen = set()
    parts = []

    for part in parser.parts:
        if part["link"] not in seen:
            seen.add(part["link"])
            parts.append(part)

    return parts
