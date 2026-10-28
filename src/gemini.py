"""Google Gemini for the language correction of summaries (v30).

Gemini writes Polish clearly better than the Groq models, and the
correction is one request per digest, well within the free quota. The key
is the repository secret GEMINI_API_KEY; without it the correction uses the
Groq models as before. The key is sent in a header (x-goog-api-key), never
in the URL, so it cannot appear in logs.

When Gemini fails (e.g. 429 after the free quota is used up, or a model
name that does not exist), the next model on the list is tried, and then
the Groq models: the digest never depends on Gemini.

Models: GEMINI_MODELS below, or the repository variable GEMINI_MODEL
(comma-separated) when the list needs to change without editing code.
"""

import json
import os
import urllib.request


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Read from Google AI Studio on 25.10.2026 (project PolacyNieGesi4Digest);
# the second one is a fallback if the first is renamed or withdrawn.
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash"]
# v35: 30 s instead of 90 s. A working Gemini answers in a few seconds; on
# 28.10.2026 gemini-3.8-flash timed out twice (2 × 90 s) and the branch digest
# waited over 3.5 minutes for nothing before skipping the correction.
REQUEST_TIMEOUT = 30


def gemini_models(environ=None):
    environ = os.environ if environ is None else environ
    configured = [name.strip() for name in environ.get("GEMINI_MODEL", "").split(",") if name.strip()]
    return configured or list(GEMINI_MODELS)


def ask_gemini(model, api_key, system, user, opener=urllib.request.urlopen):
    """Return the text answer of a Gemini model (JSON mode)."""
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        GEMINI_URL.format(model=model),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
            "User-Agent": "CyberSec-NewsDigest-AI/1.0",
        },
        method="POST",
    )

    with opener(request, timeout=REQUEST_TIMEOUT) as response:
        answer = json.loads(response.read().decode("utf-8"))

    parts = answer["candidates"][0]["content"]["parts"]
    return "".join(part.get("text", "") for part in parts)
