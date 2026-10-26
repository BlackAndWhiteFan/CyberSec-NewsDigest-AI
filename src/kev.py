"""🔥 marker for vulnerabilities from the CISA KEV catalog (v28).

CISA's Known Exploited Vulnerabilities catalog lists vulnerabilities with
confirmed exploitation in real attacks (245 were added in 2025). The marker
is set by code, not by the AI: the catalog (JSON) is downloaded once per run,
CVE ids are found in the title and the lead (first 600 characters) of the
feed text and page text, also of the related articles of the same event,
and compared with the catalog (v29: only the lead, see LEAD_CHARS).

The catalog is downloaded from CISA, with CISA's GitHub mirror as a
fallback. When neither works, the digest goes out without markers.

The weekly and monthly tops download the catalog again and check the CVE ids
saved in the archive, because CISA often adds a vulnerability a few days
after the first articles about it.
"""

import json
import re
import urllib.request

from article_selection import is_roundup


KEV_URLS = [
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json",
]
FETCH_TIMEOUT = 30
CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
MARKER = "🔥 "
KEV_NOTE = "-# 🔥 luka z katalogu CISA KEV – potwierdzone wykorzystywanie w atakach."


def load_kev(opener=urllib.request.urlopen, urls=KEV_URLS):
    """Return {CVE id: date added} from the catalog, or {} when unavailable."""
    for url in urls:
        request = urllib.request.Request(url, headers={"User-Agent": "CyberSec-NewsDigest-AI/1.0"})

        try:
            with opener(request, timeout=FETCH_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))

            catalog = {
                item["cveID"].upper(): item.get("dateAdded", "")
                for item in data.get("vulnerabilities", [])
                if isinstance(item, dict) and item.get("cveID")
            }
        except Exception as error:
            print(f"CISA KEV: {url} – {type(error).__name__}: {str(error)[:120]}")
            continue

        if catalog:
            print(f"CISA KEV: {len(catalog)} pozycji katalogu ({url.split('/')[2]})")
            return catalog

    print("CISA KEV: katalog niedostępny – bez znaczników 🔥")
    return {}


def find_cves(*texts):
    """Return the CVE ids found in the texts, sorted and without repeats."""
    found = set()

    for text in texts:
        found.update(cve.upper() for cve in CVE_PATTERN.findall(text or ""))

    return sorted(found)


# v29: only CVE ids from the title and the beginning of the text count.
# Articles often mention older vulnerabilities further on (Arista article of
# 23.10.2026 got the marker for earlier VeloCloud CVE ids).
LEAD_CHARS = 600
# v33: for a link from "Weekendowa lektura" the description is a short ZTS
# comment and the page is the linked publication itself, whose CVE ids often
# come after its first 600 characters (PHP Foundation post, 26.10.2026).
VIA_LEAD_CHARS = 2000


def plain_text(value):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value or "")).strip()


def article_cves(article):
    """CVE ids in the title and the lead of the article and of its related
    articles (same event)."""
    texts = []

    for item in [article] + list(article.get("related", [])):
        texts.append(item.get("title", ""))
        texts.extend(plain_text(item.get(field, ""))[:LEAD_CHARS] for field in ("description", "content"))
        page_lead = VIA_LEAD_CHARS if item.get("via") else LEAD_CHARS
        texts.append(plain_text(item.get("page_text", ""))[:page_lead])

    return find_cves(*texts)


def mark_kev(articles, catalog):
    """Set "cves" and "kev" (CVE ids from the catalog) on each article."""
    marked = 0

    for article in articles:
        # A roundup lists CVE ids of many stories (v29).
        if is_roundup(article):
            article["cves"], article["kev"] = [], []
            continue

        article["cves"] = article_cves(article)
        article["kev"] = [cve for cve in article["cves"] if cve in catalog]
        marked += bool(article["kev"])

    print(f"CISA KEV: oznaczone artykuły {marked} z {len(articles)}")
    return marked


def refresh_records(records, catalog):
    """Update "kev" of archive records with the current catalog (for tops)."""
    for record in records:
        cves = set(record.get("cves", [])) | set(find_cves(record.get("title", ""), record.get("summary", "")))
        record["kev"] = sorted(set(record.get("kev", [])) | {cve for cve in cves if cve in catalog})

    return records
