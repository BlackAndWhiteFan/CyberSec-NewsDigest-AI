import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = "https://niebezpiecznik.pl/feed/"

print("CyberSec NewsDigest AI")
print("Pobieram RSS:", RSS_URL)

with urllib.request.urlopen(RSS_URL, timeout=20) as response:
    xml_data = response.read()

print(xml_data[:500])

root = ET.fromstring(xml_data)

items = root.findall(".//item")

print(f"Znaleziono artykułów: {len(items)}")

for item in items[:5]:
    title = item.findtext("title", default="(brak tytułu)")
    link = item.findtext("link", default="(brak linku)")

    print()
    print("TYTUŁ:", title)
    print("LINK:", link)
