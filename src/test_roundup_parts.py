import unittest

from article_selection import LEKTURA_LIMIT, select_top_articles
from discord_output import format_article_line
from roundup_parts import VIA_LEKTURA, extract_parts
from summary_quality import quality_problems


LEKTURA = """
<p>Zapraszamy do nowego odcinka Weekendowej Lektury. Miłej lektury!</p>
<h2>Część bardziej technologiczna</h2>
<ul>
<li><a href="https://www.bleepingcomputer.com/news/security/new-ransomware-hits-hospitals/">Nowy ransomware atakuje szpitale</a> – analiza kampanii, która sparaliżowała trzy szpitale w Niemczech.</li>
<li>[PDF] <a href="https://research.example.org/paper.pdf">Ciekawy</a> raport o atakach na łańcuch dostaw w ekosystemie npm, z listą złośliwych paczek.</li>
<li><a href="https://zaufanatrzeciastrona.pl/post/inny-wpis/">Nasz wcześniejszy tekst</a> o tym samym temacie, do przypomnienia.</li>
<li><a href="https://example.com/x">Krótko</a></li>
</ul>
<p>Część mniej technologiczna</p>
<ul>
<li><a href="https://therecord.media/police-arrest-ransomware-negotiator">Policja zatrzymała negocjatora okupów</a>, który współpracował z grupą ransomware.</li>
<li><a href="https://therecord.media/police-arrest-ransomware-negotiator">Policja zatrzymała negocjatora okupów</a> (powtórka tego samego linku).</li>
</ul>
"""


class TestExtractParts(unittest.TestCase):
    def test_external_links_with_comment_become_parts(self):
        parts = extract_parts(LEKTURA)
        links = [part["link"] for part in parts]

        self.assertEqual(links, [
            "https://www.bleepingcomputer.com/news/security/new-ransomware-hits-hospitals/",
            "https://research.example.org/paper.pdf",
            "https://therecord.media/police-arrest-ransomware-negotiator",
        ])
        self.assertEqual(parts[0]["title"], "Nowy ransomware atakuje szpitale")
        self.assertIn("trzy szpitale", parts[0]["description"])
        # Link text too short: the comment is the title.
        self.assertTrue(parts[1]["title"].startswith("[PDF] Ciekawy raport"))

    def test_no_parts_in_other_layouts(self):
        self.assertEqual(extract_parts("<p>Tylko tekst bez linków, ale dość długi, by go rozważyć.</p>"), [])
        self.assertEqual(extract_parts(""), [])


class TestLekturaInDigest(unittest.TestCase):
    def test_at_most_three_links_from_lektura(self):
        articles = [
            {"title": f"Ransomware attack on hospital {n}", "link": f"https://site{n}.example/a",
             "description": "", "via": VIA_LEKTURA}
            for n in range(6)
        ]
        selected = select_top_articles(articles)
        self.assertEqual(len(selected), LEKTURA_LIMIT)

    def test_line_shows_via(self):
        article = {"title": "Nowy ransomware atakuje szpitale", "link": "https://www.bleepingcomputer.com/a", "via": VIA_LEKTURA}
        self.assertIn("· bleepingcomputer.com · via Zaufana Trzecia Strona", format_article_line(1, article))


class TestFixesBeforeMergeV31(unittest.TestCase):
    """Lektura 699 (test of 25.10.2026)."""

    def test_question_title_loses_to_threat_analysis(self):
        from article_selection import prioritize_article
        commentary = {"title": "Najbezpieczniejsza przeglądarka 2026? Chrome, Edge i Safari – 15 zero-dayów",
                      "link": "https://my127001.pl/a", "description": "", "via": VIA_LEKTURA}
        analysis = {"title": "Bronze Sandcastle wdraża zmodyfikowane powłoki oparte na Meterpreterze",
                    "link": "https://www.sophos.com/en-us/blog/bronze-sandcastle", "description": "", "via": VIA_LEKTURA}

        self.assertLess(prioritize_article(commentary), prioritize_article(analysis))
        self.assertEqual(prioritize_article(analysis), 2)

    def test_analysis_bonus_only_for_lektura_and_matching_paths(self):
        from article_selection import is_analysis_link, prioritize_article
        self.assertTrue(is_analysis_link("https://unit42.paloaltonetworks.com/fortimanager/"))
        self.assertTrue(is_analysis_link("https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940/"))
        self.assertFalse(is_analysis_link("https://www.microsoft.com/en-us/windows/"))
        self.assertEqual(prioritize_article({"title": "Bronze Sandcastle", "link": "https://www.sophos.com/x"}), 0)

    def test_links_without_article_text_are_skipped(self):
        html = """<ul>
        <li><a href="https://z3s.pl/wl">Jeśli chcecie otrzymywać e-mailową wersję</a> Weekendowej Lektury, zapiszcie się.</li>
        <li><a href="https://www.youtube.com/watch?v=x">Cyber Legion – od społeczności do cyberobrony państwa</a> nagranie.</li>
        <li><a href="https://discord.gg/zaufana">discord.gg/zaufana</a> – zapraszamy na nasz serwer Discord.</li>
        <li><a href="https://www.netflix.com/title/1">Serial o hakerach z ciekawym wątkiem</a> do obejrzenia.</li>
        </ul>"""
        self.assertEqual([part["link"] for part in extract_parts(html)], ["https://www.netflix.com/title/1"])

    def test_continuation_by_cve_in_summary(self):
        from main import mark_continuations_by_cve
        articles = [
            {"title": "Dwie krytyczne luki w PHP", "summary": "PHP załatało CVE-2026-109618 i CVE-2026-109619."},
            {"title": "Signal", "summary": "Luka CVE-2026-113380 w RingRTC."},
        ]
        records = [{"title": "PHP2Shell: dwie krytyczne luki", "cves": ["CVE-2026-109618"], "summary": ""}]

        self.assertEqual(mark_continuations_by_cve(articles, records), 1)
        self.assertTrue(articles[0]["continuation"])
        self.assertNotIn("continuation", articles[1])


    def test_roundup_record_is_not_an_event(self):
        # v32 test, 25.10.2026: Unit 42 on FortiManager was marked by a CVE id
        # from the whole roundup 699 delivered as one item.
        from main import mark_continuations_by_cve
        articles = [{"title": "Luka w FortiManagerze", "summary": "Atakujący wykorzystali CVE-2024-47575."}]
        records = [{"title": "Weekendowa Lektura: odcinek 699 [2026-10-23]. Bierzcie i czytajcie",
                    "cves": ["CVE-2024-47575"], "summary": ""}]

        self.assertEqual(mark_continuations_by_cve(articles, records), 0)
        self.assertNotIn("continuation", articles[0])


class TestQualityV31(unittest.TestCase):
    def test_not_given_remark(self):
        problems = quality_problems("Doszło do wycieku danych. Liczba poszkodowanych nie została podana.")
        self.assertTrue(any("ogólnik" in problem for problem in problems))

    def test_v32_filler_and_calques(self):
        # v32 test, 25.10.2026 (Atlassian and HPE summaries).
        problems = quality_problems(
            "Atlassian opublikował łatki usuwające 75 unikalnych podatności. "
            "Aktualizacje obejmują wszystkie komponenty i eliminują ryzyko ataków."
        )
        self.assertTrue(any("ogólnik „eliminują ryzyko”" in problem for problem in problems))
        self.assertTrue(any("kalka „unikalnych”" in problem for problem in problems))
        self.assertTrue(any("kalka „wpływających na wersje”" in problem
                            for problem in quality_problems("Luki RCE wpływających na wersje AOS-10.")))
        self.assertEqual(quality_problems("Luka wpływa na wydajność serwera."), [])


if __name__ == "__main__":
    unittest.main()
