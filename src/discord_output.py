"""Formatting and delivery of the daily digest to a Discord webhook."""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from article_selection import CATEGORIES, categorize_article


DISCORD_MESSAGE_LIMIT = 2000
OTHER_CATEGORY = "📰 POZOSTAŁE"
MAX_TITLE_LENGTH = 250


def polish_plural(number, one, few, many):
    """Return the Polish noun form matching the number (1 artykuł, 2 artykuły, 5 artykułów)."""
    if number == 1:
        return one

    if number % 10 in (2, 3, 4) and number % 100 not in (12, 13, 14):
        return few

    return many


def primary_category(article):
    """Return the label of the most important category matching an article.

    The order of CATEGORIES in article_selection.py defines importance,
    so new categories added there are handled here automatically.
    """
    categories = categorize_article(article)

    for key, label in CATEGORIES.items():
        if key in categories:
            return label

    return OTHER_CATEGORY


def format_article_line(number, article):
    """Return one digest line: number, clickable title and source domain."""
    title = article["title"].replace("[", "(").replace("]", ")")

    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH - 1] + "…"

    link = article["link"]
    domain = urllib.parse.urlparse(link).netloc.removeprefix("www.")

    # <...> around the link stops Discord from showing a large preview card.
    return f"{number}. [{title}](<{link}>) · {domain}"


def build_digest_lines(articles, eligible_count, source_count, date_text):
    """Return all digest lines, grouped by category."""
    groups = {}

    for article in articles:
        groups.setdefault(primary_category(article), []).append(article)

    section_order = list(CATEGORIES.values()) + [OTHER_CATEGORY]

    selected_phrase = polish_plural(
        len(articles),
        "artykuł wybrany",
        "artykuły wybrane",
        "artykułów wybranych",
    )
    lines = [
        f"**🛡️ CyberSec NewsDigest · {date_text}**",
        f"{len(articles)} {selected_phrase} spośród {eligible_count}"
        f" · źródła: {source_count}",
    ]

    number = 1

    for section in section_order:
        if section not in groups:
            continue

        lines.append("")
        lines.append(f"**{section}**")

        for article in groups[section]:
            lines.append(format_article_line(number, article))
            number += 1

    return lines


def split_into_messages(lines, limit=DISCORD_MESSAGE_LIMIT):
    """Join lines into messages no longer than the limit, never splitting a line."""
    messages = []
    current = ""

    for line in lines:
        candidate = f"{current}\n{line}" if current else line

        if len(candidate) <= limit:
            current = candidate
        else:
            messages.append(current)
            current = line

    if current:
        messages.append(current)

    return messages


def build_digest_messages(articles, eligible_count, source_count, date_text=None):
    """Return the digest as a list of Discord-ready messages."""
    if not articles:
        return []

    if date_text is None:
        date_text = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%d.%m.%Y")

    lines = build_digest_lines(articles, eligible_count, source_count, date_text)
    return split_into_messages(lines)


def send_messages(webhook_url, messages):
    """Send messages to a Discord webhook, one request per message."""
    for index, message in enumerate(messages):
        payload = json.dumps({
            "content": message,
            # Ignore @everyone, @here and other mentions that could appear in
            # article titles taken from external feeds.
            "allowed_mentions": {"parse": []},
        }).encode("utf-8")

        request = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CyberSec-NewsDigest-AI/1.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            response.read()

        if index < len(messages) - 1:
            time.sleep(1)
