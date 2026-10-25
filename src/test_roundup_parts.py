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


class TestQualityV31(unittest.TestCase):
    def test_not_given_remark(self):
        problems = quality_problems("Doszło do wycieku danych. Liczba poszkodowanych nie została podana.")
        self.assertTrue(any("ogólnik" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
