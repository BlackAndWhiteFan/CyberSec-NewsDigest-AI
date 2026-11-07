"""v41: guard of the Karton Prasówki (docs/karton.html), ecosystem rule 9
"Karton zawsze aktualny" (Letters 24–25).

The Karton keeps two version markers that the bridge report also reads:
<meta name="prasowka-wersja"> (the newest version in CHANGELOG_PL_EN.md) and
<meta name="plik-matka-wersja"> (the mother workbook version of the glossary
mirror). Every version updates the Karton in the same round; a stale Karton
turns this test red on the branch test run, before the merge.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KARTON = ROOT / "docs" / "karton.html"


def karton():
    return KARTON.read_text(encoding="utf-8")


def meta(name):
    match = re.search(rf'<meta name="{name}" content="([^"]+)">', karton())
    return match.group(1) if match else None


def changelog_version():
    text = (ROOT / "CHANGELOG_PL_EN.md").read_text(encoding="utf-8")
    return re.search(r"^## (v\d+[a-z]?)\b", text, re.MULTILINE).group(1)


def mirror_version():
    header = (ROOT / "data" / "glosariusz_mirror.csv").read_text(encoding="utf-8-sig").splitlines()[0]
    return re.search(r"plik-matka (v\d+)", header).group(1)


def visible_state():
    return re.search(r'<div class="eyebrow">(.*?)</div>', karton()).group(1)


class TestKartonMarkers(unittest.TestCase):
    def test_karton_exists_with_both_markers(self):
        self.assertTrue(KARTON.exists(), "docs/karton.html is missing")
        self.assertIsNotNone(meta("prasowka-wersja"))
        self.assertIsNotNone(meta("plik-matka-wersja"))

    def test_digest_version_matches_changelog(self):
        self.assertEqual(meta("prasowka-wersja"), changelog_version(),
                         "update docs/karton.html together with CHANGELOG_PL_EN.md")

    def test_mother_workbook_version_matches_mirror(self):
        self.assertEqual(meta("plik-matka-wersja"), mirror_version(),
                         "update docs/karton.html together with data/glosariusz_mirror.csv")

    def test_visible_state_matches_markers(self):
        state = visible_state()
        self.assertIn(f"stan na {meta('prasowka-wersja')} ", state)
        self.assertIn(f"plik-matka {meta('plik-matka-wersja')}", state)
        self.assertIn("Prasówka (CyberSec AI Daily News Digest)", state)


class TestKartonNumbers(unittest.TestCase):
    def test_test_count_matches_suite(self):
        suite = unittest.defaultTestLoader.discover(str(ROOT / "src"), pattern="test_*.py",
                                                     top_level_dir=str(ROOT / "src"))
        shown = re.search(r"<b>(\d+)</b><span>testów jednostkowych</span>", karton()).group(1)
        self.assertEqual(int(shown), suite.countTestCases(),
                         "update the test count in docs/karton.html")


if __name__ == "__main__":
    unittest.main()
