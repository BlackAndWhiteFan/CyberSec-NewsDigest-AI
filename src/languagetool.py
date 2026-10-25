"""Grammar hints from LanguageTool for the language correction (v30).

LanguageTool is an open-source grammar checker with Polish rules and a free
public API (no key). All summaries are checked in one request; only grammar
and punctuation findings are used (spelling findings are mostly technical
names such as "Envoy" or "brotlicffi"). The findings are not applied by
code: they are passed to the correction model as hints next to each
summary. When the API is unavailable, the correction runs without hints.
"""

import json
import urllib.parse
import urllib.request


LANGUAGETOOL_URL = "https://api.languagetool.org/v2/check"
REQUEST_TIMEOUT = 30
USED_CATEGORIES = {"GRAMMAR", "PUNCTUATION", "CONFUSED_WORDS", "SEMANTICS"}
SEPARATOR = "\n\n"


def grammar_hints(texts, opener=urllib.request.urlopen):
    """Return {index of text: [hint, ...]} for the texts, or {} on error."""
    if not texts:
        return {}

    joined = SEPARATOR.join(texts)
    starts = []
    position = 0

    for text in texts:
        starts.append(position)
        position += len(text) + len(SEPARATOR)

    data = urllib.parse.urlencode({"text": joined, "language": "pl-PL"}).encode("utf-8")
    request = urllib.request.Request(
        LANGUAGETOOL_URL,
        data=data,
        headers={"User-Agent": "CyberSec-NewsDigest-AI/1.0"},
        method="POST",
    )

    try:
        with opener(request, timeout=REQUEST_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print(f"LANGUAGETOOL: niedostępny – {type(error).__name__}: {str(error)[:120]}")
        return {}

    hints = {}

    for match in result.get("matches", []):
        if match.get("rule", {}).get("category", {}).get("id") not in USED_CATEGORIES:
            continue

        offset = match.get("offset", 0)
        index = max(i for i, start in enumerate(starts) if start <= offset)
        local = offset - starts[index]
        fragment = texts[index][local:local + match.get("length", 0)]
        replacements = [r.get("value", "") for r in match.get("replacements", [])[:2] if r.get("value")]
        hint = f"„{fragment}”: {match.get('message', '')}"

        if replacements:
            hint += " (propozycja: " + " / ".join(f"„{value}”" for value in replacements) + ")"

        hints.setdefault(index, []).append(hint)

    print(f"LANGUAGETOOL: uwagi do {len(hints)} z {len(texts)} streszczeń")
    return hints
