import io
import json
import unittest
import urllib.error

from discord_output import build_digest_lines, format_article_line
from kev import KEV_NOTE, article_cves, find_cves, load_kev, mark_kev, refresh_records
from monthly_top import build_top_lines


CATALOG_JSON = json.dumps({"vulnerabilities": [
    {"cveID": "CVE-2026-102764", "dateAdded": "2026-10-16"},
    {"cveID": "CVE-2026-114625", "dateAdded": "2026-10-22"},
]})


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class TestCatalog(unittest.TestCase):
    def test_catalog_is_loaded(self):
        catalog = load_kev(lambda request, timeout: FakeResponse(CATALOG_JSON.encode()))
        self.assertEqual(catalog, {"CVE-2026-102764": "2026-10-16", "CVE-2026-114625": "2026-10-22"})

    def test_mirror_is_used_when_cisa_fails(self):
        replies = [urllib.error.URLError("timeout"), FakeResponse(CATALOG_JSON.encode())]

        def opener(request, timeout):
            reply = replies.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return reply

        self.assertEqual(len(load_kev(opener)), 2)

    def test_no_catalog_means_no_markers(self):
        def opener(request, timeout):
            raise urllib.error.URLError("offline")

        self.assertEqual(load_kev(opener), {})


class TestMarking(unittest.TestCase):
    CATALOG = {"CVE-2026-102764": "2026-10-16"}

    def test_cves_found_in_all_material_and_related_articles(self):
        article = {
            "title": "Zero-day w BeyondTrust",
            "description": "<p>Luka cve-2026-102764 (CVSS 9.3)</p>",
            "page_text": "Also CVE-2026-55555 was fixed.",
            "related": [{"title": "x", "description": "CVE-2026-77777"}],
        }
        self.assertEqual(article_cves(article), ["CVE-2026-102764", "CVE-2026-55555", "CVE-2026-77777"])

    def test_only_catalog_cves_mark_the_article(self):
        articles = [
            {"title": "BeyondTrust", "description": "CVE-2026-102764"},
            {"title": "Signal", "description": "CVE-2026-113380"},
            {"title": "No CVE", "description": "Phishing campaign."},
        ]
        self.assertEqual(mark_kev(articles, self.CATALOG), 1)
        self.assertEqual(articles[0]["kev"], ["CVE-2026-102764"])
        self.assertEqual(articles[1]["kev"], [])
        self.assertEqual(articles[2]["cves"], [])

    def test_marker_and_legend_in_the_digest(self):
        article = {"title": "Zero-day w BeyondTrust", "link": "https://kapitanhack.pl/a", "kev": ["CVE-2026-102764"]}
        self.assertTrue(format_article_line(1, article).startswith("1. 🔥 [Zero-day w BeyondTrust]"))

        lines = build_digest_lines([article], 10, 1, "23.10.2026")
        self.assertEqual(lines[-1], KEV_NOTE)

    def test_no_legend_without_marked_articles(self):
        article = {"title": "Phishing", "link": "https://sekurak.pl/a"}
        self.assertNotIn(KEV_NOTE, build_digest_lines([article], 10, 1, "23.10.2026"))


class TestTops(unittest.TestCase):
    def test_records_are_checked_again_with_the_current_catalog(self):
        records = [
            {"title": "Arista patches VeloCloud zero-day", "summary": "Luka CVE-2026-114625…", "kev": []},
            {"title": "Old", "cves": ["CVE-2026-102764"], "kev": []},
        ]
        refresh_records(records, {"CVE-2026-114625": "x", "CVE-2026-102764": "y"})
        self.assertEqual(records[0]["kev"], ["CVE-2026-114625"])
        self.assertEqual(records[1]["kev"], ["CVE-2026-102764"])

    def test_marker_and_legend_in_the_monthly_top(self):
        records = [{
            "date": "2026-10-22", "title": "Arista zero-day", "link": "https://b/a",
            "source": "bleepingcomputer.com", "score": 5, "related": [], "kev": ["CVE-2026-114625"],
        }]
        lines = build_top_lines("2026-10", records)
        self.assertTrue(any(line.startswith("1. 🔥 [Arista zero-day]") for line in lines))
        self.assertEqual(lines[-1], KEV_NOTE)


class TestFindCves(unittest.TestCase):
    def test_repeats_and_case(self):
        self.assertEqual(find_cves("cve-2026-1234 and CVE-2026-1234", None), ["CVE-2026-1234"])


if __name__ == "__main__":
    unittest.main()
