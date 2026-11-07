import os
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
from rss_helpers import MAX_ARTICLE_AGE_DAYS, clean_title, is_duplicate_link, is_too_old, is_valid_url
from article_history import (
    filter_unpublished_articles,
    load_history,
    save_history,
)

from deduplication import add_article
from article_selection import (
    MIN_PRIORITY_SCORE,
    categorize_article,
    is_excluded,
    is_roundup,
    prioritize_article,
    relevant_articles,
    select_top_articles,
)
from discord_output import build_digest_messages, send_messages
from ai_summaries import summarize_articles, summary_source
from article_pages import add_page_texts
from kev import VIA_LEAD_CHARS, find_cves, load_kev, mark_kev
from roundup_parts import VIA_LEKTURA, extract_parts
from article_archive import append_to_archive, load_recent
from event_grouping import CONTEXT_DAYS, add_context, group_events, mark_continuations, merge_by_cves, merge_by_story
from run_guard import mark_done, should_skip
import test_mode


CONTENT_ENCODED = "{http://purl.org/rss/1.0/modules/content/}encoded"
ATOM = "{http://www.w3.org/2005/Atom}"

RSS_FEEDS = [
    "https://niebezpiecznik.pl/feed/",
    "https://sekurak.pl/feed/",
    "https://zaufanatrzeciastrona.pl/feed/",
    "https://cyberdefence24.pl/rss",
    "https://www.bleepingcomputer.com/feed/",
    "https://thehackernews.com/feeds/posts/default",
    # v26: more sources (research of 22.10.2026).
    "https://cert.pl/rss.xml",
    "https://kapitanhack.pl/feed/",
    "https://www.securityweek.com/feed/",
    "https://therecord.media/feed",
    "https://krebsonsecurity.com/feed/",
]

def fetch_feed(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "CyberSec-NewsDigest-AI/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data.lstrip())

    items = root.findall(".//item") or root.findall(
        ".//{http://www.w3.org/2005/Atom}entry"
    )

    return items

def mark_continuations_by_cve(articles, recent_records):
    """Mark articles whose summary shares a CVE id with a recent record.

    v32: records of a whole roundup ("Weekendowa lektura" delivered as one
    item) are skipped: their CVE ids come from dozens of different links, so
    a new analysis of one of them is not a follow-up (v32 test, 25.10.2026:
    Unit 42 on FortiManager marked by CVE-2024-47575 from roundup 699).
    """
    recent = set()

    for record in recent_records:
        if is_roundup(record):
            continue

        recent.update(record.get("cves", []))
        recent.update(find_cves(record.get("title", ""), record.get("summary", "")))

    marked = 0

    for article in articles:
        if article.get("continuation"):
            continue

        texts = [article.get("title", ""), article.get("summary", "")]

        # v33: for a lektura link the ZTS comment is short and the CVE ids are
        # in the linked page, often after its first 600 characters (digest of
        # 26.10.2026: PHP 8.5.12 release, CVE-2026-109618 in the PHP
        # Foundation post, shown again in "Najważniejsze").
        if article.get("via"):
            texts.append(article.get("page_text", "")[:VIA_LEAD_CHARS])

        if set(find_cves(*texts)) & recent:
            article["continuation"] = True
            marked += 1

    print("Ciąg dalszy po numerach CVE ze streszczeń:", marked)
    return marked


def run():
    if should_skip():
        print("Dzisiejsza prasówka już poszła – ten zaplanowany start kończy się bez wysyłki.")
        return

    articles = []
    seen_links = {}
    history = load_history()
    previously_published_links = set(history["published_links"])
    print("Linki opublikowane wcześniej:", len(previously_published_links))
    
    total_feed_items = 0
    skipped_invalid_items = 0
    duplicate_items = 0
    previously_published_items = 0
    failed_feeds = 0
    too_old_items = 0
    
    print("CyberSec NewsDigest AI")
    
    
    for feed_url in RSS_FEEDS:
        print("Pobieram RSS:", feed_url)
    
        try:
            items = fetch_feed(feed_url)
        except Exception as error:
            failed_feeds += 1
            print(f"BŁĄD FEEDU: {error}")
            continue
    
        print(f"Znaleziono artykułów: {len(items)}")
        total_feed_items += len(items)
    
        for item in items:
            title = clean_title(
                item.findtext("title")
                or item.findtext(
                    "{http://www.w3.org/2005/Atom}title"
                )
            )
            
            description = (
                item.findtext("description")
                or item.findtext(
                    "{http://www.w3.org/2005/Atom}summary"
                )
                or item.findtext(
                    "{http://www.w3.org/2005/Atom}content"
                )
                or ""
            ).strip()

            # Full article text, when the feed provides it (RSS content:encoded
            # or Atom content). Used only as material for AI summaries.
            content = (
                item.findtext(CONTENT_ENCODED)
                or item.findtext(f"{ATOM}content")
                or ""
            ).strip()
    
            link_element = item.find("{http://www.w3.org/2005/Atom}link")
    
            if link_element is not None:
                link = link_element.get("href", "")
            else:
                link = item.findtext("link") or ""
    
            link = link.strip()
    
            
            if not title or not is_valid_url(link):
                print("POMINIĘTO: brak prawidłowego tytułu lub linku")
                skipped_invalid_items += 1
                continue

            if is_too_old(item):
                too_old_items += 1
                continue
    
            
            # v31: "Weekendowa lektura" is split into its links; each link is
            # a candidate article ("via Zaufana Trzecia Strona").
            if is_roundup({"title": title}):
                parts = extract_parts(content or description)
                print(f"WEEKENDOWA LEKTURA: {len(parts)} pozycji – {title}")

                for part in parts:
                    print("  LEKTURA:", part["title"][:100], "|", part["link"])

                    if part["link"] in seen_links:
                        continue

                    add_article(articles, seen_links, feed_url, part["title"], part["link"], part["description"])
                    articles[-1]["via"] = VIA_LEKTURA

                if parts:
                    continue

            if is_duplicate_link(link, seen_links):
                duplicate_items += 1
    
            add_article(
                articles,
                seen_links,
                feed_url,
                title,
                link,
                description,
                content,
            )
            article = {
                "title": title,
                "description": description,
                "link": link,
            }
    
            categories = categorize_article(article)
            priority = prioritize_article(article)
    
            print("KATEGORIE:", categories)
            print("PRIORYTET:", priority)
    
            print()
            print("TYTUŁ:", title)
            print("ŹRÓDŁO:", feed_url)
            print("LINK:", link)
            
    eligible_articles = filter_unpublished_articles(
        articles,
        history["published_links"],
    )
    
    previously_published_items = len(articles) - len(eligible_articles)
    
    print()
    print("PODSUMOWANIE RSS")
    print("Wpisy znalezione w feedach:", total_feed_items)
    print("Unikalne artykuły:", len(articles))
    print("Duplikaty w bieżącym uruchomieniu:", duplicate_items)
    print("Artykuły opublikowane wcześniej (pominięte):", previously_published_items)
    print("Pominięte nieprawidłowe wpisy:", skipped_invalid_items)
    print(f"Pominięte jako starsze niż {MAX_ARTICLE_AGE_DAYS} dni:", too_old_items)
    print("Nieudane feedy:", failed_feeds)
    
    grouped_articles = group_events(
        relevant_articles(eligible_articles),
        pool=eligible_articles,
    )
    selected_articles = select_top_articles(grouped_articles, limit=20)

    try:
        recent_records = load_recent(days=3)
        # v34: a longer look back for the story of an event (context only).
        context_records = load_recent(days=CONTEXT_DAYS)
    except Exception as error:
        recent_records = []
        context_records = []
        print(f"BŁĄD ODCZYTU ARCHIWUM (pominięto ciąg dalszy): {error}")

    mark_continuations(
        selected_articles,
        recent_records,
        pool_titles=[article["title"] for article in eligible_articles],
    )
    
    print()
    print("SELEKCJA ARTYKUŁÓW")
    print("Artykuły dostępne do selekcji:", len(eligible_articles))
    print("Artykuły wybrane do digestu:", len(selected_articles))
    print(
        "Połączone powtórzenia (dodatkowe źródła):",
        sum(len(article.get("related", [])) for article in selected_articles),
    )
    print(
        "Ciąg dalszy wcześniejszych wydarzeń:",
        sum(1 for article in selected_articles if article.get("continuation")),
    )
    print(
        "Odrzucone jako promocja:",
        sum(1 for article in eligible_articles if is_excluded(article)),
    )
    print(
        "Poniżej progu trafności:",
        sum(
            1
            for article in eligible_articles
            if not is_excluded(article)
            and prioritize_article(article) < MIN_PRIORITY_SCORE
        ),
    )
    
    for article in selected_articles:
        print("WYBRANO:", article["title"])
        print("PRIORYTET:", prioritize_article(article))
        print("LINK:", article["link"])
        print()
        
    new_links = [
        article["link"]
        for article in articles
    ]
    
    history["seen_links"] = list(
        dict.fromkeys(
            history["seen_links"] + new_links
        )
    )
    
    print()
    print("STRESZCZENIA AI")
    # v27: short feed teasers are completed with text from the article page.
    add_page_texts(selected_articles, lambda article: len(summary_source(article)))
    # v28: 🔥 for vulnerabilities from the CISA KEV catalog (set by code).
    mark_kev(selected_articles, load_kev())
    # v35: one vulnerability, one item – merge by CVE ids known from the pages.
    selected_articles = merge_by_cves(selected_articles)
    add_context(selected_articles, context_records, pool_titles=[article["title"] for article in eligible_articles])
    summarize_articles(selected_articles)
    # v31: a story already delivered in recent days is a continuation also
    # when only the summaries share a CVE id (the ZTS comment of a lektura
    # link has none; PHP2Shell, test 25.10.2026).
    # v35: second pass with CVE ids from the summaries (Apple, 28.10.2026).
    selected_articles = merge_by_cves(selected_articles, use_summaries=True)
    # v44: one story, one item – the same amounts in the summaries (bug bounty, 4.11.2026).
    selected_articles = merge_by_story(selected_articles)
    mark_continuations_by_cve(selected_articles, recent_records)

    print()
    print("DISCORD")

    messages = build_digest_messages(
        selected_articles,
        len(eligible_articles),
        len(RSS_FEEDS) - failed_feeds,
    )
    test_run = test_mode.is_test_run()
    messages = test_mode.with_banner(messages)
    webhook_url, webhook_variable = test_mode.webhook_url("DISCORD_WEBHOOK_URL")

    if test_run:
        print(f"TRYB TESTOWY (gałąź {test_mode.branch_name()}): kanał testowy, bez zapisu historii i archiwum.")

    delivery_failed = False
    archive_failed = False
    articles_sent = 0

    if not messages:
        print("Brak artykułów do wysłania.")
    elif not webhook_url:
        print(f"Pominięto wysyłkę: brak zmiennej {webhook_variable}.")
    else:
        try:
            send_messages(webhook_url, messages)
        except Exception as error:
            delivery_failed = True
            print(f"BŁĄD WYSYŁKI NA DISCORD: {error}")
        else:
            print("Wysłane wiadomości:", len(messages))

        # A test run records nothing as published or archived.
        if not test_run and not delivery_failed:
            articles_sent = len(selected_articles)
            history["published_links"] = list(
                dict.fromkeys(
                    history["published_links"]
                    + [article["link"] for article in selected_articles]
                    + [
                        related["link"]
                        for article in selected_articles
                        for related in article.get("related", [])
                    ]
                )
            )
            try:
                archived = append_to_archive(selected_articles)
            except Exception as error:
                archive_failed = True
                print(f"BŁĄD ARCHIWUM: {error}")
            else:
                print("Zarchiwizowane artykuły:", archived)

    # A test run saves nothing, so the branch keeps the data of main.
    if test_run:
        print("Tryb testowy: historia, archiwum i znacznik dnia bez zmian.")
    else:
        save_history(history)

        # After a failed delivery the marker is not written, so a later
        # scheduled attempt the same day can try again.
        if not delivery_failed:
            mark_done(articles_sent)

    print("Linki zapamiętane w historii:", len(history["seen_links"]))
    print("Linki opublikowane łącznie:", len(history["published_links"]))

    if delivery_failed:
        raise SystemExit("Wysyłka prasówki na Discord nie powiodła się.")

    if archive_failed:
        raise SystemExit("Zapis do archiwum nie powiódł się.")

if __name__ == "__main__":
    run()
