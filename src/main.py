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


print("CyberSec NewsDigest AI")


for feed_url in RSS_FEEDS:
    print("Pobieram RSS:", feed_url)

    try:
        items = fetch_feed(feed_url)
    except Exception as error:
        print(f"BŁĄD FEEDU: {error}")
        continue

    print(f"Znaleziono artykułów: {len(items)}")

    for item in items[:5]:
        title = item.findtext("title") or item.findtext(
            "{http://www.w3.org/2005/Atom}title"
        ) or "(brak tytułu)"

        link_element = item.find("{http://www.w3.org/2005/Atom}link")
        link = link_element.get("href", "(brak linku)") if link_element is not None else "(brak linku)"
        print("LINK ELEMENT:", ET.tostring(link_element, encoding="unicode") if link_element is not None else "(brak elementu)")
        print("CAŁY ITEM:", ET.tostring(item, encoding="unicode"))

        print()
        print("TYTUŁ:", title)
        print("LINK:", link)
