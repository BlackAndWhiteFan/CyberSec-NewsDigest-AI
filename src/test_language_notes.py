import io
import json
import unittest

import ai_summaries
from ai_summaries import PROVIDERS, proofread_summaries, summarize_articles
from article_archive import build_record
from glossary import autofix, entry_by_form
from language_notes import findings, log_line, settle, unique


def setUpModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 0
    ai_summaries.PROOFREAD = False


def tearDownModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 20
    ai_summaries.PROOFREAD = True


def make_article(title, description=""):
    return {"title": title, "link": "https://example.com/" + title.replace(" ", "-"), "description": description}


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ScriptedOpener:
    """Replies with given summary texts (one reply per request)."""

    def __init__(self, replies):
        self.replies = list(replies)

    def __call__(self, request, timeout):
        texts = self.replies.pop(0)
        content = json.dumps({"streszczenia": [{"id": n, "tekst": t} for n, t in texts.items()]})
        return FakeResponse(json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8"))


def types(article):
    return [(note["type"], note.get("id", ""), note.get("fixed_by", "")) for note in article.get("language", [])]


class TestAutofixNotes(unittest.TestCase):
    def test_replacements_are_noted_with_glossary_ids(self):
        changes = []
        text = autofix("Wydano poprawkę na zdalne wykonanie kodu i eksploit.", changes)

        self.assertEqual(text, "Wydano łatkę na RCE i exploit.")
        self.assertEqual(
            [(c["id"], c["used"], c["fixed"]) for c in changes],
            [("H166", "poprawkę", "łatkę"), ("H090", "zdalne wykonanie kodu", "RCE"), ("H153", "eksploit", "exploit")],
        )

    def test_rule_without_glossary_entry_has_a_label(self):
        changes = []
        autofix("Luka typu RCE (RCE).", changes)

        self.assertEqual(changes[0]["id"], "")
        self.assertEqual(changes[0]["rule"], "powtórzenie w nawiasie")

    def test_without_list_nothing_is_noted(self):
        self.assertEqual(autofix("poprawka"), "łatka")

    def test_entry_by_form(self):
        self.assertEqual(entry_by_form("łatka")["id"], "H166")
        self.assertIsNone(entry_by_form("nie ma takiego hasła"))


class TestFindings(unittest.TestCase):
    def test_glossary_style_and_inflection(self):
        notes = findings("Luka pozwala na eskalację uprawnień. Wyciekły rekordy pacjentów. Ostrzegają przed exploit.")
        by_type = {note["type"]: note for note in notes}

        self.assertEqual(by_type["glossary"]["id"], "H182")
        self.assertEqual(by_type["glossary"]["used"], "eskalację uprawnień")
        self.assertEqual(by_type["style"]["form"], "rekordy")
        self.assertEqual(by_type["inflection"]["id"], "H153")
        self.assertEqual(by_type["inflection"]["used"], "przed exploit")

    def test_correct_text_has_no_findings(self):
        self.assertEqual(findings("Producent wydał łatkę chroniącą przed exploitem."), [])

    def test_settle(self):
        notes = [{"type": "style", "used": "rekordy"}]
        self.assertEqual(settle([dict(notes[0])], "Wyciekły dane.", "ai")[0]["fixed_by"], "ai")
        self.assertEqual(settle([dict(notes[0])], "Wyciekły rekordy.", "ai")[0]["fixed_by"], "remains")
        self.assertEqual(settle([dict(notes[0])], "Wyciekły dane.", "code")[0]["fixed_by"], "code")
        self.assertEqual(settle([dict(notes[0])], "", "dropped")[0]["fixed_by"], "dropped")

    def test_unique(self):
        note = {"type": "autofix", "used": "poprawka", "fixed": "łatka"}
        self.assertEqual(unique([note, dict(note)]), [note])


class TestNotesInSummaries(unittest.TestCase):
    def test_corrected_by_ai(self):
        articles = [make_article("A")]
        opener = ScriptedOpener([
            {1: "Luka pozwala na eskalację uprawnień."},
            {1: "Luka pozwala na podwyższenie uprawnień."},
        ])

        summarize_articles(articles, {"GROQ_API_KEY": "g"}, opener, lambda s: None)

        self.assertEqual(types(articles[0]), [("glossary", "H182", "ai")])

    def test_autofix_in_draft(self):
        articles = [make_article("A")]
        summarize_articles(articles, {"GROQ_API_KEY": "g"}, ScriptedOpener([{1: "Producent wydał poprawkę."}]),
                           lambda s: None)

        self.assertEqual(articles[0]["summary"], "Producent wydał łatkę.")
        self.assertEqual(types(articles[0]), [("autofix", "H166", "")])

    def test_dropped_summary_keeps_its_notes(self):
        articles = [make_article("A")]
        opener = ScriptedOpener([
            {1: "Wykradziono kredencjały."},
            {1: "Wykradziono kredencjały ponownie."},
        ])

        summarize_articles(articles, {"GROQ_API_KEY": "g"}, opener, lambda s: None)

        self.assertNotIn("summary", articles[0])
        self.assertEqual([note["fixed_by"] for note in articles[0]["language"]], ["dropped"])

    def test_clean_summary_has_no_notes(self):
        articles = [make_article("A")]
        summarize_articles(articles, {"GROQ_API_KEY": "g"}, ScriptedOpener([{1: "Producent wydał łatkę."}]),
                           lambda s: None)

        self.assertNotIn("language", articles[0])

    def test_proofreading_change_is_noted(self):
        articles = [make_article("A")]
        articles[0]["summary"] = "CISA dodało do katalogu KEV dwóch podatności."
        articles[0]["summary_material"] = "A\nCISA added 2 vulnerabilities to KEV."
        def opener(request, timeout):
            content = json.dumps({"streszczenia": [{"id": 1, "tekst": "CISA dodała do katalogu KEV dwie podatności."}]})
            return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]}).encode())

        proofread_summaries(articles, PROVIDERS, {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m"}, opener,
                            lambda s: None, hints_source=lambda texts, opener: {})

        note = articles[0]["language"][-1]
        self.assertEqual(note["type"], "proofreading")
        self.assertEqual(note["before"], "CISA dodało do katalogu KEV dwóch podatności.")
        self.assertEqual(note["after"], "CISA dodała do katalogu KEV dwie podatności.")
        self.assertTrue(note["model"].startswith("Gemini "))


class TestArchiveAndLog(unittest.TestCase):
    def test_archive_record_keeps_notes(self):
        article = make_article("A")
        article["language"] = [{"type": "style", "used": "rekordy", "fixed_by": "ai"}]

        self.assertEqual(build_record(article, "2026-10-26")["language"], article["language"])
        self.assertEqual(build_record(make_article("B"), "2026-10-26")["language"], [])

    def test_log_line(self):
        articles = [{"language": [{"type": "glossary"}, {"type": "autofix"}, {"type": "autofix"}]}, {}]

        self.assertEqual(
            log_line(articles),
            "JĘZYK: uwagi językowe do archiwum – słowniczek 1, styl 0, odmiana 0, autopoprawki 2, korekta 0",
        )


if __name__ == "__main__":
    unittest.main()
