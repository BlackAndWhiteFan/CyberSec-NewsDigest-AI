"""Weekly top 5 events of the previous week (Monday–Sunday), v22.

Uses the same grouping and ranking as the monthly top (monthly_top.py),
over archive records from the week; a week can span two monthly archive
files. Sent on Monday to a separate Discord channel (secret
DISCORD_WEEKLY_WEBHOOK_URL); top_guard makes sure a week is sent only once.

Run: python src/weekly_top.py                  (previous week)
     WEEK=2026-10-14 python src/weekly_top.py  (week containing that date)
"""

import os
import re
from datetime import date, datetime, timedelta

from article_archive import ARCHIVE_DIR, TIMEZONE, load_archive
from monthly_top import deliver, format_event_line, rank_events
import top_guard


TOP_LIMIT = 5


def week_start(day):
    """Return the Monday of the week containing the given date."""
    return day - timedelta(days=day.weekday())


def previous_week(today=None):
    """Return the Monday of the previous week."""
    if today is None:
        today = datetime.now(TIMEZONE).date()

    return week_start(today) - timedelta(days=7)


def week_id(monday):
    """Return the ISO week, e.g. "2026-W42"."""
    year, number, _ = monday.isocalendar()
    return f"{year}-W{number:02d}"


def week_label(monday):
    """Return e.g. "12–18.10.2026" or "26.10–01.11.2026"."""
    sunday = monday + timedelta(days=6)

    if monday.month == sunday.month:
        return f"{monday.day:02d}–{sunday.day:02d}.{sunday.month:02d}.{sunday.year}"

    if monday.year == sunday.year:
        return f"{monday.day:02d}.{monday.month:02d}–{sunday.day:02d}.{sunday.month:02d}.{sunday.year}"

    return f"{monday:%d.%m.%Y}–{sunday:%d.%m.%Y}"


def week_records(monday, archive_dir=ARCHIVE_DIR):
    """Return archive records dated within the week (Monday–Sunday)."""
    sunday = monday + timedelta(days=6)
    months = sorted({f"{monday:%Y-%m}", f"{sunday:%Y-%m}"})
    first, last = monday.isoformat(), sunday.isoformat()
    records = []

    for month in months:
        records.extend(load_archive(f"{archive_dir}/{month}.json"))

    return [record for record in records if first <= record.get("date", "") <= last]


def build_week_lines(monday, records, limit=TOP_LIMIT):
    """Return the lines of the weekly message, or [] for an empty week."""
    if not records:
        return []

    lines = [f"**🗓️ Top {limit} · tydzień {week_label(monday)}**"]
    first_archived = min(record.get("date", "") for record in records)

    if first_archived > monday.isoformat():
        lines.append(
            f"*Tydzień niepełny: archiwum od {first_archived[8:10]}.{first_archived[5:7]}.*"
        )

    lines.append("")

    for number, event in enumerate(rank_events(records, limit), start=1):
        lines.append(format_event_line(number, event))

    return lines


def parse_week(text):
    """Return the Monday of the week containing a YYYY-MM-DD date."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise SystemExit(f"Nieprawidłowa data tygodnia: {text!r} (oczekiwano RRRR-MM-DD).")

    try:
        return week_start(date.fromisoformat(text))
    except ValueError:
        raise SystemExit(f"Nieprawidłowa data tygodnia: {text!r}.") from None


def run(week=None, archive_dir=ARCHIVE_DIR, marker_path=top_guard.MARKER_PATH, today=None):
    today = today or datetime.now(TIMEZONE).date()
    text = week or os.environ.get("WEEK", "").strip()
    monday = parse_week(text) if text else previous_week(today)
    period = week_id(monday)

    print("TOP TYGODNIA:", period, week_label(monday))

    if top_guard.should_skip("week", period, path=marker_path):
        print("Zestawienie za ten tydzień już poszło – ten zaplanowany start kończy się bez wysyłki.")
        return

    records = week_records(monday, archive_dir)
    print("Artykuły w archiwum:", len(records))

    complete = monday + timedelta(days=6) < today
    deliver("week", period, build_week_lines(monday, records), "DISCORD_WEEKLY_WEBHOOK_URL", marker_path, complete)


if __name__ == "__main__":
    run()
