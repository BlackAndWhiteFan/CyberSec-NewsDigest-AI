"""v37b: the tops use the same correction chain as the digest (31.10.2026)."""

import io
import json
import unittest
import urllib.error
from pathlib import Path

import ai_summaries
from ai_summaries import proofread_top, summarize_events
from mistral import MISTRAL_URL


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


STORY = ("Dwie krytyczne luki PHP2Shell pozwalają przejąć serwer z PHP. "
         "Łatki wyszły 22.10 w wersjach 8.5.12 i 8.4.27.")
MATERIAL = [
    "22.10 · sekurak.pl · PHP2Shell: Dwie krytyczne luki PHP2Shell pozwalają przejąć serwer z PHP.",
    "23.10 · thehackernews.com · PHP patch: Łatki wyszły 22.10 w wersjach 8.5.12 i 8.4.27.",
]


def event():
    return {"title": "PHP2Shell", "summary": "Stare streszczenie.", "material": list(MATERIAL)}


def reply(request, text):
    content = json.dumps({"streszczenia": [{"id": 1, "tekst": text}]})
    if "generativelanguage" in request.full_url:
        return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]}).encode())
    return FakeResponse(json.dumps({"choices": [{"message": {"content": content}}]}).encode())


def setUpModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 0


def tearDownModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 20


class TestEventStories(unittest.TestCase):
    def test_mistral_before_groq_when_gemini_is_down(self):
        urls = []

        def opener(request, timeout):
            urls.append(request.full_url)
            if "generativelanguage" in request.full_url:
                raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, None)
            return reply(request, STORY)

        events = [event()]
        env = {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m", "MISTRAL_API_KEY": "s"}
        self.assertEqual(summarize_events(events, env, opener, lambda s: None), 1)
        self.assertEqual(events[0]["summary"], STORY)
        self.assertEqual([url for url in urls if "generativelanguage" not in url], [MISTRAL_URL])

    def test_gemini_answers_first(self):
        urls = []

        def opener(request, timeout):
            urls.append(request.full_url)
            return reply(request, STORY)

        env = {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m", "MISTRAL_API_KEY": "s"}
        self.assertEqual(summarize_events([event()], env, opener, lambda s: None), 1)
        self.assertEqual(len(urls), 1)
        self.assertIn("generativelanguage", urls[0])


class TestTopCorrection(unittest.TestCase):
    def test_mistral_only_is_enough(self):
        events = [{"title": "A", "link": "https://a.pl/1", "summary": "CISA dodało lukę do KEV.",
                   "summary_material": "A\nCISA added a flaw to KEV."}]

        def opener(request, timeout):
            return reply(request, "CISA dodała lukę do KEV.")

        self.assertEqual(proofread_top(events, {"MISTRAL_API_KEY": "s"}, opener, lambda s: None), 1)


class TestWorkflows(unittest.TestCase):
    def test_tops_get_the_mistral_secret(self):
        root = Path(__file__).resolve().parent.parent / ".github" / "workflows"
        for name in ("daily-digest.yml", "weekly-top.yml", "monthly-top.yml"):
            text = (root / name).read_text(encoding="utf-8")
            self.assertIn("MISTRAL_API_KEY: ${{ secrets.MISTRAL_API_KEY }}", text, name)


if __name__ == "__main__":
    unittest.main()
