"""One-time backfill of AI summaries for archived articles (v23).

Articles archived before v22 have no "summary", so the weekly and monthly
tops show them without one. This script finds such records in a monthly
archive, looks the articles up again in the RSS feeds (to get the same
material the digest uses: full text or description), writes summaries with
the same AI module and mandatory glossary as the digest, and saves them in
the archive. Records that are no longer in any feed are summarized from the
title only: the title is given as the material, so the AI renders it as one
Polish sentence and adds nothing (an empty text made the model answer
"Brak dostępnych informacji…" in the preview of 2026-10-21).

Run (GitHub Actions, workflow "Backfill AI summaries"):
    MONTH=2026-10 SAVE=false python src/backfill_summaries.py   (preview)
    MONTH=2026-10 SAVE=true  python src/backfill_summaries.py   (save)

Nothing is saved in a preview, in a test run from a branch, or for records
that already have a summary. Nothing is sent to Discord.
"""

import json
import os
import re
from pathlib import Path

from ai_summaries import summarize_articles
from article_archive import ARCHIVE_DIR, load_archive
from rss_helpers import clean_title, is_valid_url
import main
import test_mode


ATOM = "{http://www.w3.org/2005/Atom}"


def feed_material(fetch=main.fetch_feed, feeds=main.RSS_FEEDS):
    """Return {link: {"description", "content"}} for all current feed items."""
    material = {}

    for url in feeds:
        try:
            items = fetch(url)
        except Exception as error:
            print(f"BŁĄD FEEDU {url}: {error}")
            continue

        for item in items:
            link_element = item.find(f"{ATOM}link")
            link = (link_element.get("href", "") if link_element is not None else item.findtext("link") or "").strip()

            if not is_valid_url(link):
                continue

            material[link] = {
                "description": (
                    item.findtext("description")
                    or item.findtext(f"{ATOM}summary")
                    or item.findtext(f"{ATOM}content")
                    or ""
                ).strip(),
                "content": (
                    item.findtext(main.CONTENT_ENCODED)
                    or item.findtext(f"{ATOM}content")
                    or ""
                ).strip(),
            }

    return material


def first_sentence(text):
    """Return the first sentence of a summary."""
    match = re.match(r"(.+?[.!?])(\s|$)", text.strip())
    return match.group(1) if match else text.strip()


def records_without_summary(records):
    return [record for record in records if not record.get("summary")]


def build_articles(records, material):
    """Return articles for the AI module and the material used for each."""
    articles, used = [], []

    for record in records:
        found = material.get(record.get("link", ""), {})
        title = clean_title(record.get("title", ""))
        articles.append({
            "title": title,
            "link": record.get("link", ""),
            # Without feed material the title itself is the material.
            "description": found.get("description", "") or title,
            "content": found.get("content", ""),
        })
        used.append("RSS" if found else "tylko tytuł")

    return articles, used


def backfill(month, save, archive_dir=ARCHIVE_DIR, fetch=main.fetch_feed, summarize=summarize_articles):
    """Fill missing summaries in one monthly archive; return the number filled."""
    path = Path(archive_dir) / f"{month}.json"
    records = load_archive(path)
    missing = records_without_summary(records)

    print("UZUPEŁNIANIE STRESZCZEŃ:", month)
    print("Artykuły w archiwum:", len(records), "· bez streszczenia:", len(missing))

    if not missing:
        print("Nic do uzupełnienia.")
        return 0

    articles, used = build_articles(missing, feed_material(fetch))
    summarize(articles)
    filled = 0

    for record, article, source in zip(missing, articles, used):
        summary = article.get("summary", "")

        # From the title alone only the first sentence is reliable; the AI
        # added an unsupported second sentence in the preview of 2026-10-21.
        if source == "tylko tytuł":
            summary = first_sentence(summary)

        print(f"- {record.get('date')} · {record.get('title', '')[:80]} [{source}]")
        print(f"  > {summary or '(brak streszczenia)'}")

        if summary:
            record["summary"] = summary
            filled += 1

    print("Streszczenia przygotowane:", filled, "z", len(missing))

    if not save:
        print("Podgląd (SAVE=false): archiwum bez zmian.")
        return filled

    if test_mode.is_test_run():
        print("Tryb testowy (gałąź): archiwum bez zmian.")
        return filled

    if filled:
        with path.open("w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print("Zapisano archiwum:", path)

    return filled


def run():
    month = os.environ.get("MONTH", "").strip()

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise SystemExit(f"Nieprawidłowy miesiąc: {month!r} (oczekiwano RRRR-MM).")

    save = os.environ.get("SAVE", "false").strip().lower() == "true"
    backfill(month, save)


if __name__ == "__main__":
    run()
