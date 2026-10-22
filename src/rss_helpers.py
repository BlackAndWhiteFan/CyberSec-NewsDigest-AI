import html
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime


ATOM = "{http://www.w3.org/2005/Atom}"

# Feeds of new sources (v26) also contain older articles (Krebs on Security:
# about two months). Older items are skipped, so the first run with a new
# source does not send its whole archive. Three days cover the Sunday break.
MAX_ARTICLE_AGE_DAYS = 3


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


def item_published(item):
    """Return the publication time of an RSS or Atom item (UTC), or None."""
    rss_date = (item.findtext("pubDate") or "").strip()

    if rss_date:
        try:
            published = parsedate_to_datetime(rss_date)
        except (TypeError, ValueError, IndexError):
            published = None
    else:
        published = None

    if published is None:
        atom_date = (item.findtext(f"{ATOM}published") or item.findtext(f"{ATOM}updated") or "").strip()

        if not atom_date:
            return None

        try:
            published = datetime.fromisoformat(atom_date.replace("Z", "+00:00"))
        except ValueError:
            return None

    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    return published.astimezone(timezone.utc)


def is_too_old(item, now=None, max_days=MAX_ARTICLE_AGE_DAYS):
    """True when the item is older than max_days; items without a date pass."""
    published = item_published(item)

    if published is None:
        return False

    now = datetime.now(timezone.utc) if now is None else now
    return now - published > timedelta(days=max_days)
