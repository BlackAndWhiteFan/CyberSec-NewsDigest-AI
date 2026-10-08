import urllib.request
import xml.etree.ElementTree as ET

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
print("CyberSec NewsDigest AI")


for feed_url in RSS_FEEDS:
    print("Pobieram RSS:", feed_url)

    try:
        items = fetch_feed(feed_url)
    except Exception as error:
        print(f"BŁĄD FEEDU: {error}")
        continue

    print(f"Znaleziono artykułów: {len(items)}")

    for item in items:
        title = item.findtext("title") or item.findtext(
            "{http://www.w3.org/2005/Atom}title"
        ) or "(brak tytułu)"

        link_element = item.find("{http://www.w3.org/2005/Atom}link")

        if link_element is not None:
            link = link_element.get("href", "(brak linku)")
        else:
            link = item.findtext("link") or "(brak linku)"

        articles.append({
            "source": feed_url,
            "title": title,
            "link": link,
        })
            
        print()
        print("TYTUŁ:", title)
        print("LINK:", link)
