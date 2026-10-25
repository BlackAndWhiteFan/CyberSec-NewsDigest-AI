"""Monthly archive of articles delivered in the digest.

Each successfully delivered article is stored in data/archive/YYYY-MM.json
with its title, link, source, categories, score and the digest date. The
archive is the basis for monthly summaries and other later analyses.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from article_selection import categorize_article, prioritize_article, source_domain


ARCHIVE_DIR = Path("data/archive")
TIMEZONE = ZoneInfo("Europe/Warsaw")


def today_local():
    """Return today's date in Polish time as YYYY-MM-DD."""
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")


def archive_path(date_text, archive_dir=ARCHIVE_DIR):
    """Return the monthly archive file for a YYYY-MM-DD date."""
    return Path(archive_dir) / f"{date_text[:7]}.json"


def build_record(article, date_text):
    """Return the archived form of one article."""
    return {
        "date": date_text,
        "title": article.get("title", ""),
        "link": article.get("link", ""),
        "source": source_domain(article),
        "categories": categorize_article(article),
        "score": prioritize_article(article),
        "related": [
            {
                "title": related.get("title", ""),
                "link": related.get("link", ""),
                "source": source_domain(related),
            }
            for related in article.get("related", [])
        ],
        "continuation": bool(article.get("continuation")),
        # AI summary as delivered (v22), so weekly and monthly tops can show it.
        "summary": article.get("summary", ""),
        # CVE ids and those from the CISA KEV catalog (v28); the tops check
        # the CVE ids again with the current catalog.
        "cves": article.get("cves", []),
        "kev": article.get("kev", []),
        # v31: a link from "Weekendowa lektura".
        "via": article.get("via", ""),
    }


def load_archive(path):
    """Load a monthly archive; a missing file means an empty archive."""
    path = Path(path)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Article archive must be a JSON list.")

    return records


def load_recent(days=3, date_text=None, archive_dir=ARCHIVE_DIR):
    """Return archive records from the last `days` days, including today."""
    if date_text is None:
        date_text = today_local()

    today = datetime.strptime(date_text, "%Y-%m-%d").date()
    first_day = today - timedelta(days=days)
    months = {first_day.strftime("%Y-%m"), today.strftime("%Y-%m")}

    records = []

    for month in sorted(months):
        for record in load_archive(Path(archive_dir) / f"{month}.json"):
            if first_day.isoformat() <= record.get("date", "") <= today.isoformat():
                records.append(record)

    return records


def append_to_archive(articles, date_text=None, archive_dir=ARCHIVE_DIR):
    """Add delivered articles to the monthly archive, skipping known links.

    Returns the number of newly archived articles.
    """
    if date_text is None:
        date_text = today_local()

    path = archive_path(date_text, archive_dir)
    records = load_archive(path)
    known_links = {record.get("link") for record in records}

    added = 0

    for article in articles:
        if article.get("link") in known_links:
            continue

        records.append(build_record(article, date_text))
        known_links.add(article.get("link"))
        added += 1

    if added:
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)
            file.write("\n")

    return added
