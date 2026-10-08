import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = "https://niebezpiecznik.pl/feed/"

print("CyberSec NewsDigest AI")
print("Pobieram RSS:", RSS_URL)

with urllib.request.urlopen(RSS_URL, timeout=20) as response:
    xml_data = response.read()

root = ET.fromstring(xml_data.lstrip())

items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

print(f"Znaleziono artykułów: {len(items)}")

for item in items[:5]:
    title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "(brak tytułu)"
    link_element = item.find("link")
    link = link_element.get("href", "(brak linku)") if link_element is not None else "(brak linku)"

    print()
    print("TYTUŁ:", title)
    print("LINK:", link)
