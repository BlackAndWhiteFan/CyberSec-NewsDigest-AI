"""🔥 marker for vulnerabilities from the CISA KEV catalog (v28).

CISA's Known Exploited Vulnerabilities catalog lists vulnerabilities with
confirmed exploitation in real attacks (245 were added in 2025). The marker
is set by code, not by the AI: the catalog (JSON) is downloaded once per run,
CVE ids are found in the article material (title, feed text, page text and
the related articles of the same event) and compared with the catalog.

The catalog is downloaded from CISA, with CISA's GitHub mirror as a
fallback. When neither works, the digest goes out without markers.

The weekly and monthly tops download the catalog again and check the CVE ids
saved in the archive, because CISA often adds a vulnerability a few days
after the first articles about it.
"""

import json
import re
import urllib.request


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


def article_cves(article):
    """CVE ids in the article material and in the related articles."""
    texts = [
        item.get(field, "")
        for item in [article] + list(article.get("related", []))
        for field in ("title", "description", "content", "page_text")
    ]
    return find_cves(*texts)


def mark_kev(articles, catalog):
    """Set "cves" and "kev" (CVE ids from the catalog) on each article."""
    marked = 0

    for article in articles:
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
