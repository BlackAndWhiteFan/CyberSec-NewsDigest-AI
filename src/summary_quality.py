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

Sentence case is fixed by code, not by the AI (seen 22.10.2026: "exploit
tych luk mogą…" at the start of a sentence after a glossary correction).
"""

import re
from datetime import date


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


def quality_problems(text, source=None):
    """Return descriptions of quality problems (empty list = summary is fine)."""
    problems = []

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

    if source is not None:
        problems.extend(unsupported_facts(text, source))

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
