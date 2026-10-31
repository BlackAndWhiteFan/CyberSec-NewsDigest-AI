"""Mistral as the last fallback of the language correction (v37a).

On 30 and 31.10.2026 Gemini was overloaded every morning (timeouts and
503), so both digests went out without correction. Mistral writes Polish
clearly better than the Groq models (whose correction made the text worse
on 28.10.2026) and its free plan needs no card. The key is the repository
secret MISTRAL_API_KEY; without it the correction uses Gemini only.

Model: MISTRAL_MODEL below, or the repository variable MISTRAL_MODEL.
"""

import json
import os
import urllib.request


MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
# v37c (tests of 31.10.2026): mistral-large-2512 is on the limits list but
# not in the free tier ("tier_not_allowed"); mistral-medium-latest has only
# 20 000 tokens per minute, less than one event-story request (429).
# ministral-14b-2512 (937 500 tokens per minute) wrote the first real event
# stories, e.g. PHP2Shell from the honeypot to Mirai.
MISTRAL_MODEL = "ministral-14b-2512"
REQUEST_TIMEOUT = 60


def mistral_model(environ=None):
    environ = os.environ if environ is None else environ
    return environ.get("MISTRAL_MODEL", "").strip() or MISTRAL_MODEL


def ask_mistral(model, api_key, system, user, opener=urllib.request.urlopen):
    """Return the text answer of a Mistral model (JSON mode)."""
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        MISTRAL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CyberSec-NewsDigest-AI/1.0",
        },
        method="POST",
    )

    with opener(request, timeout=REQUEST_TIMEOUT) as response:
        answer = json.loads(response.read().decode("utf-8"))

    return answer["choices"][0]["message"]["content"]
