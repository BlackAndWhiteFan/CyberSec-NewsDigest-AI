"""Quality checks for AI summaries (v25).

Besides the glossary (glossary.convention_violations), every summary is
checked for problems seen in real digests and tops:

1. Generic filler phrases instead of facts ("co podkreśla wagę…").
2. Relative time words ("jutro", "dziś"): summaries are also shown in the
   weekly and monthly tops, where "tomorrow" no longer means anything.
3. Facts not in the source: every CVE number and every number above 12 in
   the summary must appear in the article title or text (small numbers are
   often written as words in the source: "two flaws" -> "2 luki").

A summary with problems is sent back once for correction (together with
glossary violations) and dropped if it still has problems: a missing
summary is better than a wrong one.

4. English terms left in the base form after a preposition that needs
   another case ("przed exploit", "z botnet"; v27): the AI must inflect
   them like Polish nouns ("przed exploitem").

Sentence case is fixed by code, not by the AI (seen 22.10.2026: "exploit
tych luk mogą…" at the start of a sentence after a glossary correction).
"""

import csv
import re
from datetime import date
from pathlib import Path


GENERIC_PHRASES = [
    r"co podkreśla\w*",
    r"podkreśla\w* (to )?(wagę|znaczenie|potrzebę|konieczność)",
    r"pokazuj\w*,? jak (ważn|istotn)\w*",
    r"przypomina\w* o (konieczności|znaczeniu|potrzebie)",
    r"w dzisiejszym (świecie|cyfrowym)\w*",
    r"warto (pamiętać|zwrócić uwagę)",
    r"należy zachować (szczególną )?ostrożność",
    r"nie (można|należy) (tego )?lekceważyć",
    r"to kolejny (przykład|dowód)",
    r"rosnące zagrożenie",
    r"stanowi\w* (poważne |realne |duże )?zagrożenie dla",
    # What the article does not say (test 22.10.2026: "raport nie podaje
    # informacji o sprawcach ani o dostępnych środkach zaradczych").
    r"nie (podaje|podają|zawiera|wskazuje|ujawnia|precyzuje)\w* (żadnych )?(informacji|szczegółów|danych)",
    r"(raport|artykuł|tekst|źródło|komunikat)\w* nie (podaje|zawiera|wskazuje|wymienia|precyzuje|ujawnia)\w*",
    r"brak (jest )?(informacji|szczegółów|danych) (o|na temat)",
    # v29: impersonal form ("Nie podano sprawcy ani dalszych szczegółów").
    r"nie podano",
    # v31: "Liczba poszkodowanych nie została podana" (test 25.10.2026).
    r"nie (został|została|zostało|zostały|zostali) (podan|ujawnion|wskazan|sprecyzowan|określon)\w*",
]
GENERIC = [re.compile(rf"(?<!\w){pattern}(?!\w)", re.IGNORECASE) for pattern in GENERIC_PHRASES]

# Adjective endings (jutrzejszy, wczorajszej, dzisiejszych…), not nouns
# such as "dzisiejszość".
ADJECTIVE_ENDINGS = "(?:y|ego|emu|ym|a|ej|ą|e|ych|ymi)"
RELATIVE_TIME = re.compile(
    r"(?<!\w)("
    r"jutro|pojutrze|wczoraj|dziś|dzisiaj"
    rf"|(jutrzejsz|wczorajsz|dzisiejsz){ADJECTIVE_ENDINGS}"
    r"|w (przyszłym|zeszłym|ubiegłym|minionym|tym|bieżącym) tygodniu"
    r"|w tygodniu(?!\s*\d)"
    r"|w (przyszłym|zeszłym|ubiegłym|tym|bieżącym) miesiącu"
    r")(?!\w)",
    re.IGNORECASE,
)

# A weekday without a date ("przed wydaniem łatki w środę", test 22.10.2026)
# is as unclear in a weekly top as "jutro"; "w środę 21 października" is fine.
WEEKDAY = re.compile(
    r"(?<!\w)we? (poniedziałek|wtorek|środę|czwartek|piątek|sobotę|niedzielę)(?![\w,]*\s*\(?\d)",
    re.IGNORECASE,
)

# Declinable English terms (glossary forms) and prepositions or phrases
# after which their base form (nominative/accusative) is wrong (v27).
DECLINABLE_TERMS = (
    "exploit", "botnet", "infostealer", "backdoor", "keylogger", "rootkit",
    "loader", "dropper", "trojan", "phishing", "stealer",
)
NON_ACCUSATIVE_CONTEXT = (
    "do", "od", "ode", "dla", "bez", "u", "według", "wokół", "podczas", "obok",
    "około", "zamiast", "oprócz", "z", "ze", "przy", "przed", "nad", "między",
    "dzięki", "wobec", "przeciwko", "za pomocą", "przy użyciu", "w wyniku",
    "w postaci", "w ramach",
)
UNINFLECTED = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(c) for c in sorted(NON_ACCUSATIVE_CONTEXT, key=len, reverse=True)) + r")"
    r"\s+(?:[\w-]+\s+)?(" + "|".join(DECLINABLE_TERMS) + r")(?![\w-])",
    re.IGNORECASE,
)

CVE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
# "26 739" (Polish thousands separator) is one number.
NUMBER = re.compile(r"\d{1,3}(?:[ \u00a0]\d{3})+(?![\d.,])|\d+(?:[.,]\d+)*")
UNCHECKED_NUMBER_LIMIT = 12

# Abbreviations after which a lowercase word does not start a new sentence
# (Polish ones and company suffixes: "Nikkei Inc. poinformowało…").
ABBREVIATIONS = {
    "np", "m.in", "tj", "tzn", "ok", "itp", "itd", "tzw", "r", "godz", "ang", "dr", "prof", "nr", "wg",
    "tys", "mln", "mld", "proc", "pkt", "ust", "art", "min", "ds", "dot", "zob", "wyd",
    "inc", "ltd", "corp", "co", "llc", "plc", "gmbh", "ag", "s.a", "sp", "o.o",
}


def digits(value):
    return re.sub(r"\D", "", value)


def source_numbers(source):
    """Digit strings of all numbers in the source (separators ignored)."""
    found = set()

    for match in NUMBER.finditer(source):
        found.add(digits(match.group(0)))
        # "1,830,000" or "1.8" also count as their parts ("1", "830", "8").
        found.update(digits(part) for part in re.split(r"[.,]", match.group(0)) if digits(part))

    return found


def is_unchecked_number(number, year):
    value = int(number)
    return value <= UNCHECKED_NUMBER_LIMIT or year - 1 <= value <= year + 1


def unsupported_facts(text, source, year=None):
    """Return CVE numbers and numbers above 12 that are not in the source."""
    problems = []
    source_cves = {cve.upper() for cve in CVE.findall(source)}

    for cve in CVE.findall(text):
        if cve.upper() not in source_cves:
            problems.append(f"numer {cve.upper()} nie występuje w artykule – usuń go albo popraw")

    year = date.today().year if year is None else year
    known = source_numbers(source)
    text_without_cves = CVE.sub(" ", text)

    for match in NUMBER.finditer(text_without_cves):
        value = match.group(0)
        number = digits(value)

        if not number or is_unchecked_number(number, year):
            continue

        if number not in known:
            problems.append(f"liczba „{value}” nie występuje w artykule – użyj liczby z artykułu albo ją usuń")

    return problems


# v29: style list (data/styl_unikaj.csv), edited by JW: calques and
# anglicisms with a suggestion ("rekordy" -> "wpisy, dane").
STYLE_PATH = Path(__file__).resolve().parent.parent / "data" / "styl_unikaj.csv"


def load_style(path=STYLE_PATH):
    """Return [(compiled pattern, form, suggestion)] from the style list."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            lines = [line for line in file if line.strip() and not line.lstrip().startswith("#")]
    except FileNotFoundError:
        return []

    rules = []

    for row in csv.DictReader(lines, delimiter=";"):
        form = (row.get("forma") or "").strip()

        if not form:
            continue

        # "*" at the end of a word means any ending; hyphen variants match.
        pattern = re.escape(form.replace("\u2011", "-")).replace(r"\*", r"\w*").replace(r"\-", "[-\u2011‐]")
        rules.append((
            re.compile(rf"(?<!\w){pattern}(?!\w)", re.IGNORECASE),
            form,
            (row.get("zamiast") or "").strip(),
        ))

    return rules


STYLE_RULES = load_style()


def style_problems(text, rules=None):
    """Calques and anglicisms from the style list, with suggestions."""
    problems = []

    for pattern, form, suggestion in STYLE_RULES if rules is None else rules:
        match = pattern.search(text)

        if match:
            problems.append(f"kalka „{match.group(0)}” – użyj: {suggestion}")

    return problems


# v29: English summaries (24.10.2026: four summaries in English).
ENGLISH_WORDS = frozenset(
    "the and of to in with that is was are were for by which has have from this "
    "allows affected attackers vulnerability vulnerabilities exposed data".split()
)
POLISH_LETTERS = re.compile(r"[ąćęłńóśźż]", re.IGNORECASE)


def looks_english(text):
    """True when a summary is written in English rather than Polish."""
    words = re.findall(r"[a-ząćęłńóśźż]+", text.lower())

    if len(words) < 6:
        return False

    english = sum(1 for word in words if word in ENGLISH_WORDS)
    return english / len(words) >= 0.12 and len(POLISH_LETTERS.findall(text)) < 3


def content_words(text):
    return {word for word in re.findall(r"\w{4,}", text.lower())}


def repeats_title(text, title):
    """True when the summary only restates the title (24.10.2026: "Node2Shell
    (CVE-2026-111497) umożliwia RCE przez dekompresję Brotli w Node.js.")."""
    words = content_words(text)
    title_words = content_words(title or "")

    # Short titles say too little to compare with.
    if not words or len(title_words) < 4:
        return False

    return len(words - title_words) <= 2


# v27: summaries became long single sentences joined with semicolons and
# were cut at SUMMARY_LIMIT (test 22.10.2026).
MAX_SUMMARY_LENGTH = 400


def quality_problems(text, source=None, soft=True):
    """Return descriptions of quality problems (empty list = summary is fine).

    soft=False leaves out style problems (calques from the style list): the
    AI is asked to fix them, but a summary is never cut or dropped for them.
    """
    problems = []

    if len(text) > MAX_SUMMARY_LENGTH:
        problems.append(
            f"streszczenie ma {len(text)} znaków – skróć je do najwyżej 350 znaków "
            "(2–3 krótkie zdania, najważniejsze fakty)"
        )

    if ";" in text:
        problems.append("zdania połączone średnikiem – podziel je na osobne zdania zakończone kropką")

    for pattern in GENERIC:
        match = pattern.search(text)

        if match:
            problems.append(f"ogólnik „{match.group(0)}” – zastąp go konkretem z artykułu albo usuń")
            break

    match = RELATIVE_TIME.search(text) or WEEKDAY.search(text)

    if match:
        problems.append(
            f"względne określenie czasu „{match.group(0)}” – podaj datę z artykułu albo pomiń czas "
            "(streszczenie trafia też do zestawień tygodniowych i miesięcznych)"
        )

    for match in UNINFLECTED.finditer(text):
        problems.append(
            f"nieodmieniony termin w „{match.group(0)}” – odmień „{match.group(1)}” jak polski "
            "rzeczownik (np. „przed exploitem”, „z botnetu”, „do infostealera”)"
        )

    if soft:
        problems.extend(style_problems(text))

    if looks_english(text):
        problems.append("streszczenie nie jest po polsku – napisz je po polsku")

    if source is not None:
        problems.extend(unsupported_facts(text, source))

        if repeats_title(text, source.split("\n", 1)[0]):
            problems.append("streszczenie powtarza tytuł – dodaj konkret z tekstu artykułu (kto, ile, skutki)")

    return problems


def fix_sentence_case(text):
    """Start the summary and every sentence with a capital letter."""
    def upper_after(match):
        before = match.group("before") or ""
        letter = match.group("letter")

        if before.lower() not in ABBREVIATIONS:
            letter = letter.upper()

        return before + match.group("end") + match.group("space") + letter

    text = re.sub(
        r"(?P<before>[\w.]*\w)?(?P<end>[.!?])(?P<space>\s+)(?P<letter>[a-ząćęłńóśźż])",
        upper_after,
        text,
    )

    if text[:1].islower():
        text = text[0].upper() + text[1:]

    return text


def split_sentences(text):
    """Split a summary into sentences (not after abbreviations such as "m.in.")."""
    sentences = []
    start = 0

    for match in re.finditer(r"[.!?](\s+)(?=[A-ZĄĆĘŁŃÓŚŹŻ0-9„\"])", text):
        word_before = re.search(r"([\w.]*\w)?$", text[start:match.start()]).group(0)

        if word_before.lower() in ABBREVIATIONS:
            continue

        sentences.append(text[start:match.end(1) - len(match.group(1))].strip())
        start = match.end()

    if text[start:].strip():
        sentences.append(text[start:].strip())

    return sentences


def repair_summary(text, has_problems, limit=MAX_SUMMARY_LENGTH):
    """Repair a summary by code when the AI correction failed (v27).

    Semicolons become sentence ends, sentences with problems are removed
    (has_problems(sentence) -> list) and the summary is cut to whole
    sentences within the limit. Returns "" when nothing good is left.
    """
    text = fix_sentence_case(re.sub(r"\s*;\s*", ". ", text))
    kept = []

    for sentence in split_sentences(text):
        if not sentence.endswith((".", "!", "?")):
            continue

        if has_problems(sentence):
            continue

        if len(" ".join(kept + [sentence])) > limit:
            break

        kept.append(sentence)

    return " ".join(kept)
