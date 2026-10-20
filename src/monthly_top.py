"""Monthly top 10 events, built from the article archive.

On the first day of a month, the archive of the previous month is grouped
into events with the same rules as the daily digest (see event_grouping),
but across the whole month and also within one source, so follow-ups such
as "(AKTUALIZACJA 2)" join their original story. Events are ranked by the
number of articles about them, then by the number of sources, then by the
highest score, and the top 10 are sent to a separate Discord channel.

Run: python src/monthly_top.py            (previous month)
     MONTH=2026-10 python src/monthly_top.py  (a chosen month)
"""

import os
import re
from datetime import datetime

from article_archive import ARCHIVE_DIR, TIMEZONE, load_archive
from discord_output import polish_plural, send_messages, split_into_messages
from event_grouping import SIMILARITY_THRESHOLD, document_frequency, same_event
import test_mode


TOP_LIMIT = 10
MAX_TITLE_LENGTH = 250

MONTH_NAMES = (
    "styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
    "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień",
)


def previous_month(today=None):
    """Return the previous month as YYYY-MM."""
    if today is None:
        today = datetime.now(TIMEZONE).date()

    if today.month == 1:
        return f"{today.year - 1}-12"

    return f"{today.year}-{today.month - 1:02d}"


def month_label(month):
    """Return e.g. "październik 2026" for "2026-10"."""
    year, number = month.split("-")
    return f"{MONTH_NAMES[int(number) - 1]} {year}"


def record_sources(record):
    return {record.get("source", "")} | {
        related.get("source", "") for related in record.get("related", [])
    }


def record_article_count(record):
    return 1 + len(record.get("related", []))


def group_month(records):
    """Group archive records of one month into events.

    Records are taken from the highest score and earliest date; each joins
    the first event whose leading record describes the same event.
    """
    titles = [record.get("title", "") for record in records] + [
        related.get("title", "")
        for record in records
        for related in record.get("related", [])
    ]
    frequency = document_frequency(titles)

    ordered = sorted(
        records,
        key=lambda record: (-record.get("score", 0), record.get("date", "")),
    )
    events = []

    for record in ordered:
        for event in events:
            # The event's own articles all contain its name, so a word still
            # counts as rare when it appears in up to that many titles + 1.
            rare_limit = 1 + sum(record_article_count(member) for member in event)

            # A follow-up from the same source must share a name or a CVE;
            # two common words are not enough, because one site often uses
            # similar phrasing for different stories.
            same_source = record.get("source") in {member.get("source") for member in event}
            threshold = float("inf") if same_source else SIMILARITY_THRESHOLD

            if same_event(
                event[0].get("title", ""),
                record.get("title", ""),
                frequency,
                threshold=threshold,
                rare_limit=rare_limit,
            ):
                event.append(record)
                break
        else:
            events.append([record])

    return events


def summarize_event(event):
    """Return the figures used to rank and display one event."""
    leader = event[0]
    sources = set().union(*(record_sources(record) for record in event))

    return {
        "title": leader.get("title", ""),
        "link": leader.get("link", ""),
        "articles": sum(record_article_count(record) for record in event),
        "sources": len(sources - {""}),
        "score": max(record.get("score", 0) for record in event),
        "first_date": min(record.get("date", "") for record in event),
    }


def rank_events(records, limit=TOP_LIMIT):
    """Return the top events of a month, most important first."""
    summaries = [summarize_event(event) for event in group_month(records)]
    summaries.sort(
        key=lambda item: (
            -item["articles"],
            -item["sources"],
            -item["score"],
            item["first_date"],
        )
    )
    return summaries[:limit]


def format_event_line(number, event):
    title = event["title"].replace("[", "(").replace("]", ")")

    if len(title) > MAX_TITLE_LENGTH:
        title = title[: MAX_TITLE_LENGTH - 1] + "…"

    articles = polish_plural(event["articles"], "artykuł", "artykuły", "artykułów")
    sources = polish_plural(event["sources"], "serwis", "serwisy", "serwisów")
    day, month = event["first_date"][8:10], event["first_date"][5:7]

    return (
        f"{number}. [{title}](<{event['link']}>) · "
        f"{event['articles']} {articles}, {event['sources']} {sources} · od {day}.{month}"
    )


def build_top_lines(month, records, limit=TOP_LIMIT):
    """Return the lines of the monthly message, or [] for an empty month."""
    if not records:
        return []

    lines = [f"**📅 Top {limit} · {month_label(month)}**"]

    first_archived = min(record.get("date", "") for record in records)

    if first_archived > f"{month}-01":
        lines.append(
            f"*Miesiąc niepełny: archiwum od {first_archived[8:10]}.{first_archived[5:7]}.*"
        )

    lines.append("")

    for number, event in enumerate(rank_events(records, limit), start=1):
        lines.append(format_event_line(number, event))

    return lines


def run(month=None, archive_dir=ARCHIVE_DIR):
    month = month or os.environ.get("MONTH", "").strip() or previous_month()

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise SystemExit(f"Nieprawidłowy miesiąc: {month!r} (oczekiwano RRRR-MM).")

    records = load_archive(f"{archive_dir}/{month}.json")

    print("TOP MIESIĄCA:", month)
    print("Artykuły w archiwum:", len(records))

    lines = build_top_lines(month, records)

    if not lines:
        print("Brak artykułów w archiwum – nic nie wysłano.")
        return

    for line in lines:
        print(line)

    webhook_url, webhook_variable = test_mode.webhook_url("DISCORD_MONTHLY_WEBHOOK_URL")

    if not webhook_url:
        print(f"Pominięto wysyłkę: brak zmiennej {webhook_variable}.")
        return

    messages = test_mode.with_banner(split_into_messages(lines))
    send_messages(webhook_url, messages)
    print("Wysłane wiadomości:", len(messages))


if __name__ == "__main__":
    run()
