"""Monthly top 10 events, built from the article archive.

On the first day of a month, the archive of the previous month is grouped
into events with the same rules as the daily digest (see event_grouping),
but across the whole month and also within one source, so follow-ups such
as "(AKTUALIZACJA 2)" join their original story. Events are ranked by the
number of articles about them, then by the number of sources, then by the
highest score, and the top 10 are sent to a separate Discord channel.

Since v22 the workflow has several scheduled attempts, and top_guard makes
sure a month is sent only once (manual runs are never blocked). The same
ranking is used by the weekly top (weekly_top.py).

Run: python src/monthly_top.py            (previous month)
     MONTH=2026-10 python src/monthly_top.py  (a chosen month)
"""

import os
import re
from datetime import datetime

from article_archive import ARCHIVE_DIR, TIMEZONE, load_archive
from article_selection import is_excluded, is_roundup
from discord_output import polish_plural, send_messages, split_into_messages
from event_grouping import SIMILARITY_THRESHOLD, document_frequency, same_event, strong_match, text_names
from kev import KEV_NOTE, MARKER as KEV_MARKER, find_cves, load_kev, refresh_records
import test_mode
import top_guard


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


def record_titles(record):
    return [record.get("title", "")] + [related.get("title", "") for related in record.get("related", [])]


def record_cves(record):
    """CVE ids saved with the record (v28) or found in its title and summary.

    A whole roundup ("Weekendowa lektura" as one item) has CVE ids from dozens
    of links, so it links nothing (as in "Ciąg dalszy", v32).
    """
    if is_roundup(record):
        return set()

    return set(record.get("cves", [])) | set(find_cves(record.get("title", ""), record.get("summary", "")))


def strongly_linked(record, event):
    """v33: a shared CVE id, or an event name with digits in any title of the
    record and any title of the event (also the titles of related articles).

    Weekly top of 26.10.2026: "PHP warns admins of two critical flaws" (21.10)
    stood apart from PHP2Shell, although its related article was "PHP2Shell:
    Two Unpatched Critical PHP RCE…", and four PHP articles with the CVE ids
    of PHP2Shell were separate events.
    """
    cves = record_cves(record)

    if any(cves & record_cves(member) for member in event):
        return True

    titles = record_titles(record)
    return any(
        strong_match(title, other)
        for member in event
        for other in record_titles(member)
        for title in titles
    )


def group_month(records):
    """Group archive records of one month into events.

    Records are taken from the highest score and earliest date; each joins
    the first event whose leading record describes the same event, or that
    shares a CVE id or an event name with digits with any of its records
    (v33).
    """
    titles = [record.get("title", "") for record in records] + [
        related.get("title", "")
        for record in records
        for related in record.get("related", [])
    ]
    frequency = document_frequency(titles)
    # v31: names shown by the summaries (see event_grouping.text_names).
    names = text_names(record.get("summary", "") for record in records)

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

            if strongly_linked(record, event) or same_event(
                event[0].get("title", ""),
                record.get("title", ""),
                frequency,
                threshold=threshold,
                rare_limit=rare_limit,
                names=names,
            ):
                event.append(record)
                break
        else:
            events.append([record])

    return merge_linked_events(events)


def merge_linked_events(events):
    """Join events that share a CVE id or an event name with digits (v33).

    The first pass compares a record only with the events formed so far, so
    an event can split in two when its linking article comes later (weekly
    top of 26.10.2026: two PHP2Shell events).
    """
    merged = []

    for event in events:
        for target in merged:
            if any(strongly_linked(record, target) for record in event):
                target.extend(event)
                break
        else:
            merged.append(list(event))

    return merged if len(merged) == len(events) else merge_linked_events(merged)


def event_summary(event):
    """Return the AI summary of the leading article, or of the first article
    in the event that has one (records archived before v22 have none).

    v33: summaries are tidied first (ai_summaries.tidy_summary): an English
    or empty one falls back to the next article of the event.
    """
    from ai_summaries import tidy_summary
    from summary_quality import repeats_title

    fallback = ""

    for record in event:
        summary = tidy_summary(record.get("summary", ""))

        # A summary that only restates its title says nothing new next to
        # the title; the next article's summary is better, if there is one.
        if summary and repeats_title(summary, record.get("title", "")):
            fallback = fallback or summary
            continue

        if summary:
            return summary

    return fallback


def leader_key(record):
    """v33: the record shown for an event – highest score, then a Polish
    source, then the most related articles (weekly top of 26.10.2026 showed
    the English announcement "… patches coming tomorrow" for PHP2Shell)."""
    return (record.get("score", 0), record.get("source", "").endswith(".pl"), len(record.get("related", [])))


def summarize_event(event):
    """Return the figures used to rank and display one event."""
    leader = max(event, key=leader_key)
    event = [leader] + [record for record in event if record is not leader]
    sources = set().union(*(record_sources(record) for record in event))

    return {
        "title": leader.get("title", ""),
        "link": leader.get("link", ""),
        "articles": sum(record_article_count(record) for record in event),
        "sources": len(sources - {""}),
        "score": max(record.get("score", 0) for record in event),
        "first_date": min(record.get("date", "") for record in event),
        "summary": event_summary(event),
        "kev": sorted(set().union(*(set(record.get("kev", [])) for record in event))),
    }


def rank_events(records, limit=TOP_LIMIT):
    """Return the top events of a month, most important first.

    v33: roundups and promotional titles archived before their filters
    (ThreatsDay, Weekendowa lektura as one item) are left out.
    """
    records = [record for record in records if not (is_roundup(record) or is_excluded(record))]
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

    marker = KEV_MARKER if event.get("kev") else ""
    line = (
        f"{number}. {marker}[{title}](<{event['link']}>) · "
        f"{event['articles']} {articles}, {event['sources']} {sources} · od {day}.{month}"
    )

    # The summary stays in the same entry, so it is never separated from
    # its title when the message is split.
    if event.get("summary"):
        line += f"\n> {event['summary']}"

    return line


def polish_events(events):
    """v33: one language correction of the top summaries (they are tidied by
    code in event_summary, see ai_summaries.proofread_top)."""
    from ai_summaries import proofread_top

    proofread_top([event for event in events if event.get("summary")])
    return events


def build_top_lines(month, records, limit=TOP_LIMIT, polish=None):
    """Return the lines of the monthly message, or [] for an empty month.

    polish(events): optional step on the ranked events (v33: tidy and
    proofread summaries); the tests run without it.
    """
    if not records:
        return []

    lines = [f"**📅 Top {limit} · {month_label(month)}**"]

    first_archived = min(record.get("date", "") for record in records)

    if first_archived > f"{month}-01":
        lines.append(
            f"*Miesiąc niepełny: archiwum od {first_archived[8:10]}.{first_archived[5:7]}.*"
        )

    lines.append("")

    events = rank_events(records, limit)

    if polish:
        polish(events)

    for number, event in enumerate(events, start=1):
        lines.append(format_event_line(number, event))

    return lines + kev_note(events)


def kev_note(events):
    """The 🔥 legend, when any event is marked (v28)."""
    return ["", KEV_NOTE] if any(event.get("kev") for event in events) else []


def deliver(kind, period, lines, real_variable, marker_path=top_guard.MARKER_PATH, complete=True):
    """Send a top message and record the period as sent.

    An empty period is also recorded, so later scheduled attempts stop.
    Not recorded: test runs, a missing webhook (a later attempt can still
    send) and a period that has not ended yet (a manual preview of the
    current week or month must not block the full report later).
    """
    test_run = test_mode.is_test_run()

    if not lines:
        print("Brak artykułów w archiwum – nic nie wysłano.")
    else:
        for line in lines:
            print(line)

        webhook_url, webhook_variable = test_mode.webhook_url(real_variable)

        if not webhook_url:
            print(f"Pominięto wysyłkę: brak zmiennej {webhook_variable}.")
            return

        # The header is repeated with "(cd.)" in every following message, so
        # no message starts in the middle of the numbered list.
        messages = test_mode.with_banner(split_into_messages(lines, section_headers={lines[0]}))
        send_messages(webhook_url, messages)
        print("Wysłane wiadomości:", len(messages))

    if test_run:
        print("Tryb testowy: znacznik zestawień bez zmian.")
    elif not complete:
        print("Okres jeszcze trwa – podgląd bez zapisu w znaczniku.")
    else:
        top_guard.mark_sent(kind, period, marker_path)


def run(month=None, archive_dir=ARCHIVE_DIR, marker_path=top_guard.MARKER_PATH, today=None,
        load_kev_catalog=None):
    today = today or datetime.now(TIMEZONE).date()
    month = month or os.environ.get("MONTH", "").strip() or previous_month(today)

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise SystemExit(f"Nieprawidłowy miesiąc: {month!r} (oczekiwano RRRR-MM).")

    print("TOP MIESIĄCA:", month)

    if top_guard.should_skip("month", month, path=marker_path):
        print("Zestawienie za ten miesiąc już poszło – ten zaplanowany start kończy się bez wysyłki.")
        return

    records = load_archive(f"{archive_dir}/{month}.json")
    print("Artykuły w archiwum:", len(records))
    # v28: CVE ids checked again with the current CISA KEV catalog.
    refresh_records(records, (load_kev_catalog or load_kev)())

    complete = month < today.strftime("%Y-%m")
    deliver("month", month, build_top_lines(month, records, polish=polish_events), "DISCORD_MONTHLY_WEBHOOK_URL",
            marker_path, complete)


if __name__ == "__main__":
    run()
