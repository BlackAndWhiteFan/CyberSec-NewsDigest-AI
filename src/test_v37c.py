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
