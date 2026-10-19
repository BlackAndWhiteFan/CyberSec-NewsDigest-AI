"""Glossary conventions for AI summaries, read from the mirror of the
CyberSec Mozaika glossary (data/glosariusz_mirror.csv).

The digest never reads the Mozaika mother workbook; the mirror is exported
from it manually (tools/eksport_mirrora.py) and committed to this repository.

Conventions are enforced in three places:
1. Prompt: the AI gets the glossary entries relevant to the articles and a
   hard rule to use only the forms listed there.
2. Check: every summary is checked for forbidden forms ("unikaj" column);
   a summary that breaks the convention is sent back for correction and
   dropped if it is still wrong.
3. Explanations: code (not the AI) adds the explanation in parentheses
   ("nawias" column) at the first occurrence of a term in the whole digest,
   so it is consistent and testable.

Polish inflected forms in INFLECTED were generated with the Morfeusz 2
morphological analyzer, so explanations agree with the case of the word they
explain (e.g. "poprawce (łatce)", "poświadczeń (danych logowania)").
"""

import csv
import re
from pathlib import Path


MIRROR_PATH = Path(__file__).resolve().parent.parent / "data" / "glosariusz_mirror.csv"
PROMPT_EXTRA_LIMIT = 40

# Entries whose explanation must follow the case of the explained word.
# id: (regex with an "anchor" group, function of the match -> explanation)
SPONSORED_ENDINGS = "(?:y|ego|emu|ym|a|ej|ą|e|i|ych|ymi)"
ESCALATION = {
    # Accusative for the ambiguous nominative/accusative form (JW, 19.10.2026).
    "podwyższenie": "eskalację",
    "podwyższenia": "eskalacji",
    "podwyższeniu": "eskalacji",
    "podwyższeniem": "eskalacją",
    "podwyższeń": "eskalacji",
}
CREDENTIALS = {
    "poświadczenia": "dane logowania",
    "poświadczeń": "danych logowania",
    "poświadczeniom": "danym logowania",
    "poświadczeniami": "danymi logowania",
    "poświadczeniach": "danych logowania",
    "poświadczenie": "dane logowania",
    "poświadczeniem": "danymi logowania",
    "poświadczeniu": "danym logowania",
}
INFLECTED = {
    "H166": (r"\b(?P<anchor>popraw(?:ka|ki|ce|kę|ką|ek|kom|kami|kach))\b",
             lambda m: "łat" + m.group("anchor").lower()[6:]),
    "H182": (r"\b(?P<anchor>podwyższeni(?:e|a|u|em)|podwyższeń)\s+uprawnień\b",
             lambda m: ESCALATION.get(m.group("anchor").lower())),
    "H207": (r"\b(?P<anchor>poświadcze(?:nia|ń|niom|niami|niach|nie|niem|niu))\b",
             lambda m: CREDENTIALS.get(m.group("anchor").lower())),
    "H371-sponsored": (rf"\b(?P<anchor>opłacan(?P<ending>{SPONSORED_ENDINGS})\s+przez\s+państwo)\b",
                       lambda m: "sponsorowan" + m.group("ending").lower()),
}


def load_mirror(path=MIRROR_PATH):
    """Return mirror entries as a list of dicts (comment lines skipped)."""
    with open(path, encoding="utf-8-sig") as file:
        lines = [line for line in file if not line.startswith("#")]

    return list(csv.DictReader(lines, delimiter=";"))


ENTRIES = load_mirror()


def is_acronym(text):
    """Acronyms and mixed-case names (RCE, PoC, IoT) are matched case-sensitively."""
    letters = [ch for ch in text if ch.isalpha()]
    return bool(letters) and (text == text.upper() or sum(ch.isupper() for ch in letters) >= 2)


def term_pattern(term):
    """Regex for a term inside text: whole words, acronyms case-sensitive."""
    flags = 0 if is_acronym(term) else re.IGNORECASE
    return re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", flags)


def search_keys(entry):
    """English and Polish forms used to find entries relevant to a text."""
    keys = set()
    english = re.sub(r"\([^)]*\)", " ", entry["termin_en"])

    for part in re.split(r"\s*/\s*|,\s*|;\s*", english):
        part = part.strip()

        if len(part) >= 3 or is_acronym(part) and len(part) >= 2:
            keys.add(part)

    if len(entry["forma"]) >= 4:
        keys.add(entry["forma"])

    return keys


KEY_PATTERNS = [(entry, [term_pattern(key) for key in search_keys(entry)]) for entry in ENTRIES]
CORE_ENTRIES = [entry for entry in ENTRIES if entry["regula"] or entry["unikaj"]]


def relevant_entries(texts, limit=PROMPT_EXTRA_LIMIT):
    """Return core entries plus entries whose terms appear in the texts."""
    joined = "\n".join(texts)
    selected = list(CORE_ENTRIES)
    extra = []

    for entry, patterns in KEY_PATTERNS:
        if entry in selected:
            continue

        if any(pattern.search(joined) for pattern in patterns):
            extra.append(entry)

    # Longer English terms are more specific; keep them when over the limit.
    extra.sort(key=lambda entry: -len(entry["termin_en"]))
    return selected + extra[:limit]


def prompt_line(entry):
    line = f"- {entry['termin_en']} → {entry['forma']}"

    if entry["regula"]:
        line += f" ({entry['regula']})"

    return line


def prompt_glossary(texts):
    """Return glossary lines for the prompt, relevant to the given texts."""
    return "\n".join(prompt_line(entry) for entry in relevant_entries(texts))


def forbidden_patterns(entry):
    return [
        re.compile(rf"(?<!\w){pattern.strip()}", re.IGNORECASE)
        for pattern in entry["unikaj"].split(" | ")
        if pattern.strip()
    ]


FORBIDDEN = [(entry, forbidden_patterns(entry)) for entry in ENTRIES if entry["unikaj"]]


def convention_violations(text):
    """Return a list of (used form, required form) for forbidden forms."""
    found = []

    for entry, patterns in FORBIDDEN:
        for pattern in patterns:
            match = pattern.search(text)

            if match:
                found.append((match.group(0), entry["forma"]))
                break

    return found


def gloss_rule(entry):
    """Return (compiled regex, explanation function) for an entry with "nawias"."""
    if entry["id"] in INFLECTED:
        pattern, explain = INFLECTED[entry["id"]]
        return re.compile(pattern, re.IGNORECASE), explain

    forma = entry["forma"]
    flags = 0 if is_acronym(forma) else re.IGNORECASE
    pattern = re.compile(rf"(?<!\w)(?P<anchor>{re.escape(forma)}\w*)", flags)
    return pattern, lambda match, text=entry["nawias"]: text


GLOSS_RULES = [(entry["id"], *gloss_rule(entry)) for entry in ENTRIES if entry["nawias"]]


def apply_glossary(text, used_terms):
    """Add explanations in parentheses at the first occurrence of each term.

    used_terms is a set shared by all summaries of one digest, so a term is
    explained only once per digest. A term already followed by a parenthesis
    counts as explained.
    """
    insertions = []
    spans = []

    for key, pattern, explain in GLOSS_RULES:
        if key in used_terms:
            continue

        match = pattern.search(text)

        if not match:
            continue

        start, end = match.span("anchor")

        # Overlapping terms get only the first explanation.
        if any(start < other_end and other_start < end for other_start, other_end in spans):
            continue

        spans.append((start, end))
        used_terms.add(key)

        if text[end:].lstrip().startswith("("):
            continue

        explanation = explain(match)

        if explanation:
            insertions.append((end, f" ({explanation})"))

    for position, addition in sorted(insertions, reverse=True):
        text = text[:position] + addition + text[position:]

    return text
