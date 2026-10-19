import os
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
from rss_helpers import clean_title, is_valid_url, is_duplicate_link
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
    prioritize_article,
    relevant_articles,
    select_top_articles,
)
from discord_output import build_digest_messages, send_messages
from ai_summaries import summarize_articles
from article_archive import append_to_archive, load_recent
from event_grouping import group_events, mark_continuations


CONTENT_ENCODED = "{http://purl.org/rss/1.0/modules/content/}encoded"
ATOM = "{http://www.w3.org/2005/Atom}"

RSS_FEEDS = [
    "https://niebezpiecznik.pl/feed/",
    "https://sekurak.pl/feed/",
    "https://zaufanatrzeciastrona.pl/feed/",
    "https://cyberdefence24.pl/rss",
    "https://www.bleepingcomputer.com/feed/",
    "https://thehackernews.com/feeds/posts/default",
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

def run():
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
    print("Nieudane feedy:", failed_feeds)
    
    grouped_articles = group_events(
        relevant_articles(eligible_articles),
        pool=eligible_articles,
    )
    selected_articles = select_top_articles(grouped_articles, limit=20)

    try:
        recent_records = load_recent(days=3)
    except Exception as error:
        recent_records = []
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
    summarize_articles(selected_articles)

    print()
    print("DISCORD")

    messages = build_digest_messages(
        selected_articles,
        len(eligible_articles),
        len(RSS_FEEDS) - failed_feeds,
    )
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    delivery_failed = False
    archive_failed = False

    if not messages:
        print("Brak artykułów do wysłania.")
    elif not webhook_url:
        print("Pominięto wysyłkę: brak zmiennej DISCORD_WEBHOOK_URL.")
    else:
        try:
            send_messages(webhook_url, messages)
        except Exception as error:
            delivery_failed = True
            print(f"BŁĄD WYSYŁKI NA DISCORD: {error}")
        else:
            print("Wysłane wiadomości:", len(messages))
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

    save_history(history)

    print("Linki zapamiętane w historii:", len(history["seen_links"]))
    print("Linki opublikowane łącznie:", len(history["published_links"]))

    if delivery_failed:
        raise SystemExit("Wysyłka prasówki na Discord nie powiodła się.")

    if archive_failed:
        raise SystemExit("Zapis do archiwum nie powiódł się.")

if __name__ == "__main__":
    run()
