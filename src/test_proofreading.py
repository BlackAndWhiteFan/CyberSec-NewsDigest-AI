import io
import json
import unittest
import urllib.error
import urllib.parse

import ai_summaries
from gemini import GEMINI_MODELS, ask_gemini, gemini_models, proofreading_models
from languagetool import grammar_hints


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def gemini_reply(texts):
    content = json.dumps({"streszczenia": [{"id": n, "tekst": t} for n, t in texts.items()]})
    return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]}).encode())


def groq_reply(texts):
    content = json.dumps({"streszczenia": [{"id": n, "tekst": t} for n, t in texts.items()]})
    return FakeResponse(json.dumps({"choices": [{"message": {"content": content}}]}).encode())


def article(summary):
    return {
        "title": "CISA Flags Two Actively Exploited Critical Flaws",
        "link": "https://thehackernews.com/a",
        "summary": summary,
        "summary_material": "CISA Flags Two Actively Exploited Critical Flaws\nCISA added two flaws to KEV.",
    }


WRONG = "CISA dodało do listy KEV dwóch podatności."
RIGHT = "CISA dodała do listy KEV dwie podatności."


class TestGemini(unittest.TestCase):
    def test_request_puts_key_in_header_and_reads_text(self):
        seen = []

        def opener(request, timeout):
            seen.append(request)
            return gemini_reply({1: RIGHT})

        text = ask_gemini("gemini-test", "secret-key", "system", "user", opener)

        self.assertIn('"tekst"', text)
        self.assertNotIn("secret-key", seen[0].full_url)
        self.assertEqual(seen[0].get_header("X-goog-api-key"), "secret-key")

    def test_models_from_variable(self):
        self.assertEqual(gemini_models({"GEMINI_MODEL": " a , b "}), ["a", "b"])
        self.assertEqual(gemini_models({}), GEMINI_MODELS)


class TestLanguageTool(unittest.TestCase):
    def test_hints_are_mapped_to_summaries_and_spelling_ignored(self):
        texts = ["Pierwsze zdanie jest dobre.", WRONG]
        joined = "\n\n".join(texts)
        offset = joined.index("dodało")
        result = {"matches": [
            {"message": "Rodzaj czasownika nie zgadza się z podmiotem.", "offset": offset, "length": 6,
             "replacements": [{"value": "dodała"}], "rule": {"category": {"id": "GRAMMAR"}}},
            {"message": "Literówka?", "offset": 0, "length": 8,
             "replacements": [], "rule": {"category": {"id": "TYPOS"}}},
        ]}

        def opener(request, timeout):
            sent = urllib.parse.parse_qs(request.data.decode())
            self.assertEqual(sent["language"], ["pl-PL"])
            return FakeResponse(json.dumps(result).encode())

        hints = grammar_hints(texts, opener)

        self.assertEqual(list(hints), [1])
        self.assertIn("„dodało”", hints[1][0])
        self.assertIn("„dodała”", hints[1][0])

    def test_unavailable_api_gives_no_hints(self):
        def opener(request, timeout):
            raise urllib.error.URLError("offline")

        self.assertEqual(grammar_hints(["Tekst."], opener), {})


class TestProofreadingOrder(unittest.TestCase):
    def setUp(self):
        self.interval = ai_summaries.MIN_REQUEST_INTERVAL
        ai_summaries.MIN_REQUEST_INTERVAL = 0

    def tearDown(self):
        ai_summaries.MIN_REQUEST_INTERVAL = self.interval

    def test_gemini_first_with_hints(self):
        articles = [article(WRONG)]
        sent = []

        def opener(request, timeout):
            sent.append(json.loads(request.data.decode()))
            return gemini_reply({1: RIGHT})

        changed = ai_summaries.proofread_summaries(
            articles, ai_summaries.PROVIDERS, {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m"}, opener,
            lambda s: None, hints_source=lambda texts, opener: {0: ["„dodało”: rodzaj"]},
        )

        self.assertEqual(changed, 1)
        self.assertEqual(articles[0]["summary"], RIGHT)
        self.assertIn("contents", sent[0])
        self.assertIn("„dodało”: rodzaj", sent[0]["contents"][0]["parts"][0]["text"])

    # v35: no correction by Groq – it made Polish worse on 28.10.2026.
    # v37a: Gemini main and lite models; Mistral only with its key.
    def test_gemini_unavailable_means_no_correction(self):
        articles = [article(WRONG)]
        urls = []
        waits = []

        def opener(request, timeout):
            urls.append(request.full_url)
            raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, None)

        changed = ai_summaries.proofread_summaries(
            articles, ai_summaries.PROVIDERS, {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m"}, opener,
            waits.append, hints_source=lambda texts, opener: {},
        )

        self.assertEqual(changed, 0)
        self.assertEqual(articles[0]["summary"], WRONG)
        self.assertTrue(all("generativelanguage" in url for url in urls))
        # v37a: three rounds over the main and the lite models.
        self.assertEqual(len(urls), 3 * len(proofreading_models({})))
        self.assertEqual(waits, list(ai_summaries.PROOFREAD_RETRY_WAITS))

    def test_second_round_after_a_temporary_error(self):
        articles = [article(WRONG)]
        calls = []

        def opener(request, timeout):
            calls.append(request.full_url)

            if len(calls) <= len(GEMINI_MODELS):
                raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, None)

            return gemini_reply({1: RIGHT})

        changed = ai_summaries.proofread_summaries(
            articles, ai_summaries.PROVIDERS, {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m"}, opener,
            lambda s: None, hints_source=lambda texts, opener: {},
        )

        self.assertEqual(changed, 1)
        self.assertEqual(articles[0]["summary"], RIGHT)

    def test_without_gemini_key_no_correction(self):
        articles = [article(WRONG)]
        urls = []

        def opener(request, timeout):
            urls.append(request.full_url)
            return groq_reply({1: RIGHT})

        changed = ai_summaries.proofread_summaries(
            articles, ai_summaries.PROVIDERS, {"GROQ_API_KEY": "g"}, opener,
            lambda s: None, hints_source=lambda texts, opener: {},
        )
        self.assertEqual((changed, urls), (0, []))


if __name__ == "__main__":
    unittest.main()
