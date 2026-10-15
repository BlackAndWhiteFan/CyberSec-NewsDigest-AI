import html
import urllib.parse


def is_valid_url(url):
    if not url or not url.startswith(("https://", "http://")):
        return False

    parsed_url = urllib.parse.urlparse(url)
    return bool(parsed_url.netloc)


def is_duplicate_link(link, seen_links):
    return link in seen_links


def clean_title(title):
    """Decode HTML entities left in feed titles (e.g. &#8230; -> …).

    Some feeds encode entities twice, so the XML parser leaves codes such as
    &#8230; in the text instead of the characters they stand for.
    """
    return html.unescape(title or "").strip()
