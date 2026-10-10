import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
from rss_helpers import is_valid_url, is_duplicate_link
from article_history import load_history, save_history

from deduplication import add_article
from article_selection import (
    categorize_article,
    prioritize_article,
    select_top_articles,
)


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

articles = []
seen_links = {}
history = load_history()
previously_seen_links = set(history["seen_links"])
print("Linki wczytane z historii:", len(previously_seen_links))

total_feed_items = 0
skipped_invalid_items = 0
duplicate_items = 0
previously_seen_items = 0
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
        title = (
            item.findtext("title")
            or item.findtext(
                "{http://www.w3.org/2005/Atom}title"
            )
            or ""
        ).strip()
        
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

        if link in previously_seen_links:
            previously_seen_items += 1
            print("POMINIĘTO: artykuł był widziany wcześniej")
            continue

        if is_duplicate_link(link, seen_links):
            duplicate_items += 1

        add_article(
            articles,
            seen_links,
            feed_url,
            title,
            link,
            description
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

print()
print("PODSUMOWANIE RSS")
print("Wpisy znalezione w feedach:", total_feed_items)
print("Unikalne artykuły:", len(articles))
print("Duplikaty w bieżącym uruchomieniu:", duplicate_items)
print("Artykuły widziane wcześniej:", previously_seen_items)
print("Pominięte nieprawidłowe wpisy:", skipped_invalid_items)
print("Nieudane feedy:", failed_feeds)

new_links = [
    article["link"]
    for article in articles
]

history["seen_links"] = list(
    dict.fromkeys(
        history["seen_links"] + new_links
    )
)

save_history(history)

print("Zapamiętane linki w historii:", len(history["seen_links"]))
    
