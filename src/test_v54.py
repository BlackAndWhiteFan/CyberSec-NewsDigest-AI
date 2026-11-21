"""v54 · Uwagi dla korektora (List 43): style findings reach the corrector."""
import json
import unittest

import ai_summaries
from summary_quality import load_style
from test_proofreading import gemini_reply


class TestStyleHintsForCorrector(unittest.TestCase):
    def setUp(self):
        self.interval = ai_summaries.MIN_REQUEST_INTERVAL
        ai_summaries.MIN_REQUEST_INTERVAL = 0

    def tearDown(self):
        ai_summaries.MIN_REQUEST_INTERVAL = self.interval

    def test_calque_goes_to_the_corrector(self):
        wrong = "Check Point wydało emergency hotfixy na lukę CVE-2026-123039."
        right = "Check Point wydało awaryjne hotfixy na lukę CVE-2026-123039."
        articles = [{
            "title": "Check Point warns of zero-day flaw exploited for root access",
            "link": "https://www.bleepingcomputer.com/a",
            "summary": wrong,
            "summary_material": "Check Point released emergency hotfixes for CVE-2026-123039.",
        }]
        sent = []

        def opener(request, timeout):
            sent.append(json.loads(request.data.decode()))
            return gemini_reply({1: right})

        ai_summaries.proofread_summaries(
            articles, ai_summaries.PROVIDERS, {"GROQ_API_KEY": "g", "GEMINI_API_KEY": "m"}, opener,
            lambda s: None, hints_source=lambda texts, opener: {},
        )

        prompt = sent[0]["contents"][0]["parts"][0]["text"]
        self.assertIn("„emergency”", prompt)
        self.assertIn("awaryjny", prompt)
        self.assertEqual(articles[0]["summary"], right)


class TestStyleList(unittest.TestCase):
    def test_no_duplicate_forms(self):
        forms = [form.lower() for _, form, _ in load_style()]
        self.assertEqual(len(forms), len(set(forms)))


if __name__ == "__main__":
    unittest.main()
