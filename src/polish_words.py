"""v42: Polish vocabulary checks with Morfeusz 2 (the SGJP dictionary).

Two checks, both without AI:

1. English words left untranslated in a summary ("komputer łączącego się
   jako viewer", "grupa threat actor", 31.10–7.11.2026). A word counts as
   English when Morfeusz does not know it, it is written in lowercase, it is
   not a glossary term or an accepted word (data/slowa_angielskie_ok.csv),
   and the English material of the article has a word with the same
   beginning ("viewer", "tenantów" ← "tenants").
2. Words that the language correction invented ("kryzycznych", "Hakeri",
   6–7.11.2026: Gemini lite wrote them, the summary before the correction
   was right). A new word is suspicious when Morfeusz does not know it and
   no unknown word of the text before the correction or of the material
   explains it (a name such as "Gartner" explains "Gartnera"; a Polish word
   such as "Hakerzy" explains nothing).

Without the morfeusz2 package both checks are skipped (the workflows install
it; locally: pip install morfeusz2).
"""

import re
from pathlib import Path

from glossary import ENTRIES

ACCEPTED_PATH = Path(__file__).resolve().parent.parent / "data" / "slowa_angielskie_ok.csv"
PREFIX_LENGTH = 5
MIN_WORD_LENGTH = 4

WORD = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")
LOWERCASE_WORD = re.compile(r"(?<![\w./@-])[a-ząćęłńóśźż]+(?:-[a-ząćęłńóśźż]+)*(?![\w/@]|\.\w)")

_analyzer = None
_missing = False


def analyzer():
    """The Morfeusz 2 analyzer, or None when the package is missing."""
    global _analyzer, _missing

    if _analyzer is None and not _missing:
        try:
            import morfeusz2
        except ImportError:
            _missing = True
            print("MORFEUSZ: brak pakietu morfeusz2 – kontrola słów pominięta.")
            return None

        _analyzer = morfeusz2.Morfeusz(generate=False)

    return _analyzer


def make_known(morfeusz):
    """known(word) for a Morfeusz analyzer: True when the dictionary has the
    word (in any case), False for unknown words ("ign")."""
    cache = {}

    def known(word):
        if word not in cache:
            cache[word] = any(
                item[2][2] != "ign"
                for form in {word, word.lower()}
                for item in morfeusz.analyse(form)
            )
        return cache[word]

    return known


def default_known():
    morfeusz = analyzer()
    return make_known(morfeusz) if morfeusz else None


def load_accepted(path=ACCEPTED_PATH):
    """Accepted English words, one per line; "*" at the end = any ending."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            lines = [line.strip() for line in file if line.strip() and not line.lstrip().startswith("#")]
    except FileNotFoundError:
        return []

    return [line.lower() for line in lines]


def glossary_words():
    """Single words of the glossary forms and English terms ("exploit",
    "payload", "sandbox"), which may carry Polish endings."""
    words = set()

    for entry in ENTRIES:
        for text in (entry.get("forma", ""), entry.get("termin_en", "")):
            words.update(word.lower() for word in WORD.findall(text) if len(word) >= MIN_WORD_LENGTH)

    return words


ACCEPTED = load_accepted()
GLOSSARY_WORDS = glossary_words()


def is_allowed(word, accepted=None):
    """Glossary terms with Polish endings ("exploitów", "payloadzie") and
    accepted words ("framework*")."""
    lower = word.lower()

    for item in ACCEPTED if accepted is None else accepted:
        if item.endswith("*") and lower.startswith(item[:-1]) or lower == item:
            return True

    return any(lower == term or lower.startswith(term[:max(PREFIX_LENGTH, len(term) - 1)]) for term in GLOSSARY_WORDS)


def unknown_parts(word, known):
    return [part for part in word.split("-") if not known(part)]


def english_leftovers(text, material, known=None, accepted=None):
    """English words left untranslated in a summary, in order of appearance."""
    known = default_known() if known is None else known

    if not known or not material:
        return []

    prefixes = {word.lower()[:PREFIX_LENGTH] for word in WORD.findall(material) if len(word) >= MIN_WORD_LENGTH}
    found = []

    for word in LOWERCASE_WORD.findall(text):
        if (
            len(word) >= MIN_WORD_LENGTH
            and word not in found
            and unknown_parts(word, known)
            and not is_allowed(word, accepted)
            and word[:PREFIX_LENGTH] in prefixes
        ):
            found.append(word)

    return found


def invented_words(before, after, material="", known=None, accepted=None):
    """Words added by the language correction that no dictionary, glossary
    or name in the texts explains ("kryzycznych", "Hakeri")."""
    known = default_known() if known is None else known

    if not known:
        return []

    old_words = set(WORD.findall(before))
    explaining = {
        word.lower()[:PREFIX_LENGTH]
        for word in old_words | set(WORD.findall(material or ""))
        if len(word) >= MIN_WORD_LENGTH and unknown_parts(word, known)
    }
    found = []

    for word in WORD.findall(after):
        if (
            word in old_words
            or word in found
            or len(word) < 3
            or word.isupper()
            or not unknown_parts(word, known)
            or is_allowed(word, accepted)
            or word.lower()[:PREFIX_LENGTH] in explaining
        ):
            continue

        found.append(word)

    return found


def english_problems(text, material, known=None):
    """Soft problems for the summary checks (they ask for a fix, never cut)."""
    return [
        f"angielskie słowo „{word}” – przetłumacz je albo opisz po polsku "
        "(nazwy własne i terminy ze słowniczka zostaw)"
        for word in english_leftovers(text, material, known)
    ]
