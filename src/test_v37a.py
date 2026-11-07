"""v37a: language correction that runs every day (digests of 30–31.10.2026)."""

import io
import json
import unittest
import urllib.error

import ai_summaries
from gemini import proofreading_models
from mistral import MISTRAL_URL
from summary_quality import readability_problems


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def answer(request, fix):
    """Reply in the format of the API that was asked, fixing every item."""
    if request.full_url == MISTRAL_URL:
        sent = json.loads(json.loads(request.data.decode())["messages"][1]["content"])
    else:
        sent = json.loads(json.loads(request.data.decode())["contents"][0]["parts"][0]["text"])

    content = json.dumps({"streszczenia": [{"id": i["id"], "tekst": fix(i["tekst"])} for i in sent["streszczenia"]]})

    if request.full_url == MISTRAL_URL:
        return FakeResponse(json.dumps({"choices": [{"message": {"content": content}}]}).encode())

    return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": content}]}}]}).encode())


def articles(count):
    return [{
        "title": f"CISA Flags Flaw {n}",
        "link": f"https://example.com/{n}",
        "summary": f"CISA dodało do listy KEV podatność numer {n}.",
        "summary_material": f"CISA Flags Flaw {n}\nCISA added flaw {n} to KEV.",
    } for n in range(1, count + 1)]


def fix(text):
    return text.replace("dodało", "dodała")


def unavailable(request):
    return urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, None)


ENV = {"GEMINI_API_KEY": "m", "MISTRAL_API_KEY": "s"}


def run(items, opener, env=ENV, waits=None):
    return ai_summaries.proofread_summaries(items, ai_summaries.PROVIDERS, env, opener,
                                            (waits if waits is not None else []).append,
                                            hints_source=lambda texts, opener: {})


class TestChunks(unittest.TestCase):
    def test_twelve_summaries_go_in_three_requests(self):
        items = articles(12)
        sizes = []

        def opener(request, timeout):
            sent = json.loads(json.loads(request.data.decode())["contents"][0]["parts"][0]["text"])
            sizes.append(len(sent["streszczenia"]))
            return answer(request, fix)

        self.assertEqual(run(items, opener), 12)
        self.assertEqual(sizes, [5, 5, 2])

    def test_a_lost_chunk_does_not_stop_the_others(self):
        items = articles(7)
        calls = []

        def opener(request, timeout):
            calls.append(request.full_url)
            if len(calls) == 1:
                raise TimeoutError("The read operation timed out")
            return answer(request, fix)

        self.assertEqual(run(items, opener, {"GEMINI_API_KEY": "m"}), 7)


class TestFallbacks(unittest.TestCase):
    def test_lite_model_after_the_main_ones(self):
        main = proofreading_models({"GEMINI_LITE_MODEL": ""})
        self.assertTrue(main[-1].endswith("lite"))
        self.assertEqual(proofreading_models({"GEMINI_MODEL": "a", "GEMINI_LITE_MODEL": "b, a"}), ["a", "b"])

    def test_overloaded_model_is_skipped_for_the_rest_of_the_round(self):
        items = articles(10)
        urls = []

        def opener(request, timeout):
            urls.append(request.full_url)
            if "lite" not in request.full_url:
                raise unavailable(request)
            return answer(request, fix)

        self.assertEqual(run(items, opener, {"GEMINI_API_KEY": "m"}), 10)
        main_calls = [url for url in urls if "lite" not in url]
        # Each main model fails once per round, not once per chunk; v42: the
        # lite models come in the second round, so the main ones fail twice.
        self.assertEqual(len(main_calls), 4)

    def test_mistral_when_gemini_is_down(self):
        items = articles(3)
        urls = []
        waits = []

        def opener(request, timeout):
            urls.append(request.full_url)
            if request.full_url != MISTRAL_URL:
                raise unavailable(request)
            return answer(request, fix)

        self.assertEqual(run(items, opener, waits=waits), 3)
        self.assertEqual(items[0]["summary"], "CISA dodała do listy KEV podatność numer 1.")
        self.assertTrue(items[0]["language"][-1]["model"].startswith("Mistral "))
        # Gemini gets the whole first round; Mistral comes in the second.
        self.assertNotEqual(urls[0], MISTRAL_URL)
        self.assertEqual(waits, [ai_summaries.PROOFREAD_RETRY_WAITS[0]])

    def test_mistral_key_goes_in_the_header(self):
        items = articles(1)
        seen = []

        def opener(request, timeout):
            seen.append(request)
            return answer(request, fix)

        run(items, opener, {"MISTRAL_API_KEY": "klucz-xyz"})
        self.assertEqual(seen[0].full_url, MISTRAL_URL)
        self.assertEqual(seen[0].get_header("Authorization"), "Bearer klucz-xyz")
        self.assertNotIn("klucz-xyz", seen[0].full_url)

    def test_everything_down_keeps_the_summaries(self):
        items = articles(2)

        def opener(request, timeout):
            raise TimeoutError("The read operation timed out")

        self.assertEqual(run(items, opener), 0)
        self.assertEqual(items[0]["summary"], "CISA dodało do listy KEV podatność numer 1.")

    def test_no_keys_no_requests(self):
        def opener(request, timeout):
            raise AssertionError("no request expected")

        self.assertEqual(run(articles(1), opener, {"GROQ_API_KEY": "g"}), 0)


class TestOtherFlaws(unittest.TestCase):
    # Summaries of 30–31.10.2026.
    def test_empty_mention_is_a_soft_problem(self):
        for text in ("Luki CVE-2026-1 i CVE-2026-2 oraz dwie inne luki.",
                     "Dodatkowo wykryto jeszcze dwie inne luki w RTIR.",
                     "Obie podatności i trzy dodatkowe błędy naprawiono."):
            self.assertTrue(any("pusta wzmianka" in p for p in readability_problems(text)), text)

    def test_named_flaw_is_fine(self):
        text = "Naprawiono CVE-2026-1 i CVE-2026-2, a brak weryfikacji certyfikatów czeka na poprawkę."
        self.assertFalse(any("pusta wzmianka" in p for p in readability_problems(text)))

    def test_cve_hint_no_longer_suggests_it(self):
        problems = readability_problems("CVE-2026-1, CVE-2026-2 i CVE-2026-3.")
        self.assertFalse(any("inne luki" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
