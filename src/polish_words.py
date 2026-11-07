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


# v46: grammar checks with Morfeusz 2 (rules D of the language observation).

_generator = None


def generator():
    """The Morfeusz 2 generator (forms of a lemma), or None."""
    global _generator

    if _generator is None and analyzer() is not None:
        import morfeusz2
        _generator = morfeusz2.Morfeusz(analyse=False)

    return _generator


def make_tags(morfeusz):
    """tags(word) -> [(lemma, tag)] for a Morfeusz analyzer."""
    cache = {}

    def tags(word):
        if word not in cache:
            cache[word] = [(item[2][1].split(":")[0], item[2][2]) for item in morfeusz.analyse(word)]
        return cache[word]

    return tags


def default_tags():
    morfeusz = analyzer()
    return make_tags(morfeusz) if morfeusz else None


def plural_genders(word, tags):
    """Genders of plural nominative/accusative noun readings ("luki": m3, f)."""
    genders = set()

    for _, tag in tags(word):
        parts = tag.split(":")

        if parts[0] in ("subst", "depr") and len(parts) > 3 and "pl" in parts[1].split(".") \
                and {"nom", "acc"} & set(parts[2].split(".")):
            for gender in parts[3].split("."):
                genders.add("f" if gender == "f" else "n" if gender == "n" else "m")

    return genders


NUMERAL = re.compile(r"(?<![\w-])(dwa|dwie|oba|obie)\s+([a-ząćęłńóśźż]+)", re.IGNORECASE)
# Nouns read as feminine in this domain although Morfeusz also knows a
# masculine homonym ("luki": "luk", a bow).
FEMININE_IN_DOMAIN = {"luki"}


def numeral_problems(text, tags=None):
    """"dwa luki" → "dwie luki", "dwie błędy" → "dwa błędy" (v46)."""
    tags = default_tags() if tags is None else tags

    if not tags:
        return []

    problems = []

    for match in NUMERAL.finditer(text):
        numeral, noun = match.group(1), match.group(2)
        genders = plural_genders(noun.lower(), tags)

        # An adjective after the numeral ("dwie inne luki") is not checked.
        if not genders or any(tag.startswith("adj") for _, tag in tags(noun.lower())):
            continue

        feminine = genders == {"f"} or noun.lower() in FEMININE_IN_DOMAIN
        wanted = None

        if numeral.lower() in ("dwa", "oba") and feminine:
            wanted = {"dwa": "dwie", "oba": "obie"}[numeral.lower()]
        elif numeral.lower() in ("dwie", "obie") and "f" not in genders:
            wanted = {"dwie": "dwa", "obie": "oba"}[numeral.lower()]

        if wanted:
            problems.append(f"liczebnik „{match.group(0)}” – popraw na „{wanted} {noun}”")

    return problems


LOCATIVE_PREPOSITION = re.compile(r"(?<![\w-])(w|we|o|przy|po)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{3,})(?![\w-])")


def locative_form(lemma, generate):
    for form, _, tag, *_ in generate(lemma):
        parts = tag.split(":")

        if parts[0] == "subst" and parts[1] == "sg" and "loc" in parts[2].split("."):
            return form

    return None


def name_case_problems(text, tags=None, generate=None):
    """Product names left in the nominative after "w", "o", "przy", "po":
    "w Linux" → "w Linuksie", "w Android" → "w Androidzie" (v46).
    Indeclinable names ("w Windows") and names Morfeusz does not know
    ("Firefox") are left alone."""
    tags = default_tags() if tags is None else tags

    if generate is None:
        morfeusz = generator()
        generate = morfeusz.generate if morfeusz else None

    if not tags or not generate:
        return []

    problems = []

    for match in LOCATIVE_PREPOSITION.finditer(text):
        word = match.group(2)
        readings = [(lemma, tag) for lemma, tag in tags(word) if tag.split(":")[0] == "subst"]

        if not readings or any("loc" in tag.split(":")[2].split(".") for _, tag in readings):
            continue

        if not all(tag.split(":")[2] == "nom" and tag.split(":")[1] == "sg" for _, tag in readings):
            continue

        form = locative_form(readings[0][0], generate)

        if form and word[0].isupper():
            form = form[0].upper() + form[1:]

        if form and form != word:
            problems.append(f"nieodmieniona nazwa „{match.group(0)}” – napisz „{match.group(1)} {form}”")

    return problems


SUBJECT_VERB = re.compile(r"(?<![\w-])([A-ZĄĆĘŁŃÓŚŹŻ][\w.-]*[A-Za-z0-9])\s+([a-ząćęłńóśźż]+ł[aoy]?)(?![\w-])")


def past_gender(verb, tags):
    for _, tag in tags(verb):
        parts = tag.split(":")

        if parts[0] == "praet" and parts[1] == "sg":
            gender = parts[2]
            return "f" if gender == "f" else "n" if gender == "n" else "m"

    return None


def gender_problems(text, tags=None):
    """One company in two genders in one summary: "Chainalysis ogłosiło …
    Chainalysis ujawnił" (digests of 2.11 and 7.11.2026)."""
    tags = default_tags() if tags is None else tags

    if not tags:
        return []

    seen = {}

    for match in SUBJECT_VERB.finditer(text):
        gender = past_gender(match.group(2), tags)

        if gender:
            seen.setdefault(match.group(1), {}).setdefault(gender, match.group(2))

    return [
        f"„{name}” raz w rodzaju {', raz w rodzaju '.join(GENDER_NAMES[gender] + ' („' + verb + '”)' for gender, verb in verbs.items())}"
        " – wybierz jeden rodzaj dla tej nazwy"
        for name, verbs in seen.items()
        if len(verbs) > 1
    ]


GENDER_NAMES = {"m": "męskim", "f": "żeńskim", "n": "nijakim"}


def grammar_problems(text):
    """All Morfeusz grammar checks (soft problems)."""
    return numeral_problems(text) + name_case_problems(text) + gender_problems(text)
