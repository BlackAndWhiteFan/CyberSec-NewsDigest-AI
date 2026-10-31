"""v37c: the API's reason for a refusal goes to the log (31.10.2026)."""

import io
import unittest
import urllib.error

from ai_summaries import error_detail
from mistral import mistral_model


def http_error(code, body):
    return urllib.error.HTTPError("https://api.mistral.ai/v1/chat/completions", code, "Forbidden", {},
                                  io.BytesIO(body.encode()))


class TestErrorDetail(unittest.TestCase):
    def test_403_body_is_shown(self):
        detail = error_detail(http_error(403, '{"message": "Model not available\\n on your plan"}'))
        self.assertEqual(detail, ' | odpowiedź API: {"message": "Model not available\\n on your plan"}')

    def test_long_body_is_cut(self):
        self.assertLessEqual(len(error_detail(http_error(403, "x" * 1000))), 220)

    def test_no_detail_for_other_errors(self):
        self.assertEqual(error_detail(http_error(503, "busy")), "")
        self.assertEqual(error_detail(http_error(404, "no model")), "")
        self.assertEqual(error_detail(TimeoutError("timed out")), "")


class TestDefaultModel(unittest.TestCase):
    def test_exact_free_tier_name(self):
        self.assertEqual(mistral_model({}), "mistral-large-2512")


if __name__ == "__main__":
    unittest.main()


class TestAnswerShapes(unittest.TestCase):
    def test_text_ids_and_request_key_are_read(self):
        from ai_summaries import parse_summaries
        content = '{"wydarzenia": [{"id": "1", "tekst": "Luki PHP2Shell pozwalają przejąć serwer."}]}'
        self.assertEqual(parse_summaries(content, {1}), {1: "Luki PHP2Shell pozwalają przejąć serwer."})

    def test_story_field_of_ministral(self):
        from ai_summaries import parse_summaries
        content = '{"wydarzenia": [{"id": 1, "tytuł": "PHP2Shell", "historia": "Dwie luki w PHP pozwalają przejąć serwer."}]}'
        self.assertEqual(parse_summaries(content, {1}), {1: "Dwie luki w PHP pozwalają przejąć serwer."})

    def test_empty_answer_goes_to_the_next_model(self):
        import ai_summaries
        calls = []

        def first(system, user, opener):
            calls.append("first")
            return '{"cos": []}'

        def second(system, user, opener):
            calls.append("second")
            return '{"streszczenia": [{"id": 1, "tekst": "Tekst."}]}'

        corrected, _, models = ai_summaries.correct_in_chunks(
            [{"id": 1, "tekst": "Tekst"}], [("A", first, 1), ("B", second, 1)], None, lambda s: None)
        self.assertEqual(calls, ["first", "second"])
        self.assertEqual(models, {1: "B"})
