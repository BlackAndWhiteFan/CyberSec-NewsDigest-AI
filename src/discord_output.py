"""Formatting and delivery of the daily digest to a Discord webhook."""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from article_selection import CATEGORIES, categorize_article


# Discord allows 2000 characters per message; the margin covers differences
# in how emoji and other special characters are counted.
DISCORD_MESSAGE_LIMIT = 1900
OTHER_CATEGORY = "📰 POZOSTAŁE"
CONTINUATION_CATEGORY = "🔁 CIĄG DALSZY"
MAX_TITLE_LENGTH = 250
CONTINUATION_SUFFIX = " (cd.)"


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
    if article.get("continuation"):
        return CONTINUATION_CATEGORY

    categories = categorize_article(article)

    for key, label in CATEGORIES.items():
        if key in categories:
            return label

    return OTHER_CATEGORY


def section_labels():
    """Return section labels in display order: categories, other, continuations."""
    return list(CATEGORIES.values()) + [OTHER_CATEGORY, CONTINUATION_CATEGORY]


def section_header(label):
    """Return the bold header line for a section label."""
    return f"**{label}**"


def format_article_line(number, article):
    """Return one digest line: number, clickable title and source domain."""
    title = article["title"].replace("[", "(").replace("]", ")")

    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH - 1] + "…"

    link = article["link"]
    domain = urllib.parse.urlparse(link).netloc.removeprefix("www.")

    # <...> around the link stops Discord from showing a large preview card.
    line = f"{number}. [{title}](<{link}>) · {domain}"

    related = article.get("related", [])

    if related:
        others = ", ".join(
            f"[{source_label(item)}](<{item['link']}>)" for item in related
        )
        line += f" · także: {others}"

    return line


def source_label(article):
    return urllib.parse.urlparse(article["link"]).netloc.removeprefix("www.")


def build_digest_lines(articles, eligible_count, source_count, date_text):
    """Return all digest lines, grouped by category."""
    groups = {}

    for article in articles:
        groups.setdefault(primary_category(article), []).append(article)

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

    for section in section_labels():
        if section not in groups:
            continue

        lines.append("")
        lines.append(section_header(section))

        for article in groups[section]:
            lines.append(format_article_line(number, article))
            number += 1

    return lines


def split_into_messages(lines, limit=DISCORD_MESSAGE_LIMIT, section_headers=()):
    """Join lines into messages no longer than the limit, never splitting a line.

    When a section continues in the next message, its header is repeated
    there with a "(cd.)" suffix, so each message can be read on its own.
    """
    messages = []
    current = ""
    current_header = None

    for line in lines:
        if line in section_headers:
            current_header = line

        candidate = f"{current}\n{line}" if current else line

        if len(candidate) <= limit:
            current = candidate
            continue

        messages.append(current)

        if current_header and line not in ("", current_header):
            continued = current_header[:-2] + CONTINUATION_SUFFIX + "**"
            current = f"{continued}\n{line}"
        else:
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
    headers = {section_header(label) for label in section_labels()}
    return split_into_messages(lines, section_headers=headers)


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
