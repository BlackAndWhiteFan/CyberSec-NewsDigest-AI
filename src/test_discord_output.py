import unittest

from discord_output import (
    AI_NOTE,
    DISCORD_MESSAGE_LIMIT,
    OTHER_CATEGORY,
    build_digest_messages,
    format_article_line,
    polish_plural,
    primary_category,
    split_into_messages,
)


def make_article(title, link="https://example.com/article", description=""):
    return {"title": title, "link": link, "description": description}


class TestPolishPlural(unittest.TestCase):
    def test_plural_forms(self):
        forms = ("artykuł", "artykuły", "artykułów")

        self.assertEqual(polish_plural(1, *forms), "artykuł")
        self.assertEqual(polish_plural(3, *forms), "artykuły")
        self.assertEqual(polish_plural(22, *forms), "artykuły")
        self.assertEqual(polish_plural(5, *forms), "artykułów")
        self.assertEqual(polish_plural(12, *forms), "artykułów")
        self.assertEqual(polish_plural(20, *forms), "artykułów")


class TestPrimaryCategory(unittest.TestCase):
    def test_most_important_category_wins(self):
        article = make_article("Zero-day vulnerability actively exploited")
        self.assertEqual(primary_category(article), "🔴 NAJWAŻNIEJSZE")

    def test_article_without_category_goes_to_other(self):
        article = make_article("Weekly newsletter")
        self.assertEqual(primary_category(article), OTHER_CATEGORY)


class TestFormatArticleLine(unittest.TestCase):
    def test_line_contains_number_link_and_domain(self):
        article = make_article("Title", "https://www.example.com/post")
        line = format_article_line(3, article)

        self.assertEqual(
            line,
            "3. [Title](<https://www.example.com/post>) · example.com",
        )

    def test_square_brackets_in_title_do_not_break_link(self):
        article = make_article("Leak [UPDATED]")
        self.assertIn("[Leak (UPDATED)]", format_article_line(1, article))

    def test_long_title_is_shortened(self):
        article = make_article("A" * 1000)
        self.assertLess(len(format_article_line(1, article)), 400)


class TestRelatedAndContinuations(unittest.TestCase):
    def test_each_related_source_is_listed_once(self):
        article = {"title": "PHP2Shell", "link": "https://www.bleepingcomputer.com/a"}
        article["related"] = [
            {"title": "x", "link": "https://thehackernews.com/b"},
            {"title": "y", "link": "https://thehackernews.com/c"},
            {"title": "z", "link": "https://www.securityweek.com/d"},
            {"title": "w", "link": "https://www.bleepingcomputer.com/e"},
        ]
        line = format_article_line(1, article)
        self.assertTrue(line.endswith(
            " · także: [thehackernews.com](<https://thehackernews.com/b>), "
            "[securityweek.com](<https://www.securityweek.com/d>)"
        ))

    def test_related_sources_are_listed(self):
        article = make_article("Fakturownia.pl zhackowana", "https://niebezpiecznik.pl/a")
        article["related"] = [
            make_article("Ofiarą firma Fakturownia.pl", "https://zaufanatrzeciastrona.pl/b")
        ]

        line = format_article_line(1, article)

        self.assertIn(
            " · także: [zaufanatrzeciastrona.pl](<https://zaufanatrzeciastrona.pl/b>)",
            line,
        )

    def test_continuation_goes_to_its_own_last_section(self):
        follow_up = make_article("Ransomware attack update", "https://example.com/1")
        follow_up["continuation"] = True
        articles = [follow_up, make_article("Ransomware attack", "https://example.com/2")]

        text = "\n".join(build_digest_messages(articles, 10, 6, "19.10.2026"))

        self.assertLess(text.index("🔴 NAJWAŻNIEJSZE"), text.index("🔁 CIĄG DALSZY"))
        self.assertGreater(
            text.index("https://example.com/1"), text.index("🔁 CIĄG DALSZY")
        )


class TestSplitIntoMessages(unittest.TestCase):
    def test_messages_respect_limit_and_keep_lines_whole(self):
        lines = [f"line {i} " + "x" * 90 for i in range(60)]
        messages = split_into_messages(lines, limit=500)

        for message in messages:
            self.assertLessEqual(len(message), 500)

        rejoined = "\n".join(messages).split("\n")
        self.assertEqual(rejoined, lines)


    def test_section_header_is_repeated_in_next_message(self):
        lines = ["**Header**", "**🛡️ PODATNOŚCI**"] + [
            f"{i}. " + "x" * 90 for i in range(1, 13)
        ]
        messages = split_into_messages(
            lines,
            limit=500,
            section_headers={"**🛡️ PODATNOŚCI**"},
        )

        self.assertGreater(len(messages), 1)

        for message in messages[1:]:
            self.assertTrue(message.startswith("**🛡️ PODATNOŚCI (cd.)**\n"))

        for message in messages:
            self.assertLessEqual(len(message), 500)


class TestBuildDigestMessages(unittest.TestCase):
    def test_empty_selection_produces_no_messages(self):
        self.assertEqual(build_digest_messages([], 0, 6, "16.10.2026"), [])

    def test_digest_has_header_sections_and_all_articles(self):
        articles = [
            make_article("Ransomware attack", "https://example.com/1"),
            make_article("New CVE-2026-0001 patch", "https://example.com/2"),
            make_article("Weekly newsletter", "https://example.com/3"),
        ]
        messages = build_digest_messages(articles, 150, 6, "16.10.2026")
        text = "\n".join(messages)

        self.assertIn("CyberSec NewsDigest · 16.10.2026", text)
        self.assertIn("3 artykuły wybrane spośród 150", text)
        self.assertIn("🔴 NAJWAŻNIEJSZE", text)
        self.assertIn(OTHER_CATEGORY, text)

        for article in articles:
            self.assertIn(article["link"], text)

    def test_twenty_long_articles_fit_discord_limit(self):
        articles = [
            make_article("T" * 200, f"https://example.com/{'p' * 150}/{i}")
            for i in range(20)
        ]
        messages = build_digest_messages(articles, 150, 6, "16.10.2026")

        self.assertGreater(len(messages), 1)

        for message in messages:
            self.assertLessEqual(len(message), DISCORD_MESSAGE_LIMIT)


if __name__ == "__main__":
    unittest.main()


class TestSummaries(unittest.TestCase):
    def test_summary_is_quoted_under_its_title(self):
        line = format_article_line(1, make_article("Tytuł"), "Krótkie streszczenie.")
        title_line, summary_line = line.split("\n")

        self.assertIn("[Tytuł]", title_line)
        self.assertEqual(summary_line, "> Krótkie streszczenie.")

    def test_glossary_explains_term_once_per_digest_and_note_is_added(self):
        first = make_article("Credentials stolen from hospital", "https://example.com/1")
        second = make_article("Gang leaks credentials", "https://example.com/2")
        first["summary"] = "Wykradziono poświadczenia pracowników szpitala."
        second["summary"] = "Grupa opublikowała poświadczenia klientów."

        text = "\n".join(build_digest_messages([first, second], 10, 6, "19.10.2026"))

        self.assertEqual(text.count("(dane logowania)"), 1)
        self.assertIn("Wykradziono poświadczenia (dane logowania)", text)
        self.assertTrue(text.endswith(AI_NOTE))

    def test_no_note_without_summaries(self):
        text = "\n".join(build_digest_messages([make_article("Tytuł")], 10, 6, "19.10.2026"))
        self.assertNotIn(AI_NOTE, text)

    def test_twenty_articles_with_long_summaries_fit_discord_limit(self):
        articles = []

        for number in range(20):
            article = make_article("Zero-day " + "x" * 240, f"https://example.com/{number}")
            article["summary"] = "s" * 450
            articles.append(article)

        messages = build_digest_messages(articles, 150, 6, "19.10.2026")
        self.assertTrue(all(len(message) <= DISCORD_MESSAGE_LIMIT for message in messages))
        self.assertEqual(sum(message.count("\n> ") for message in messages), 20)


class TestHeaderNotOrphaned(unittest.TestCase):
    def test_section_header_never_ends_a_message(self):
        header = "**🛡️ PODATNOŚCI**"
        lines = ["a" * 1800, "", header, "1. " + "b" * 300]
        messages = split_into_messages(lines, section_headers={header})

        self.assertFalse(any(message.endswith(header) for message in messages))
        self.assertTrue(messages[1].startswith(header + "\n1. "))
        self.assertNotIn("(cd.)", messages[1])
