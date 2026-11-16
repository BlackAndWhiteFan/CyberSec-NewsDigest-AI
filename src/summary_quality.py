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

from polish_words import english_problems, grammar_problems


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
    # v34: remarks about the material in event stories (weekly top test of
    # 26.10.2026: "Materiał nie podaje żadnych ataków ani łatek", "CISA … nie
    # podaje łatek", "nie ma informacji o dalszych atakach").
    r"materiał\w* (nie|nic|jedynie|tylko)",
    r"nie podaj\w*",
    r"(nie ma|brak\w*|nie było) (żadnych |dalszych )?(informacji|danych|wzmianek|doniesień)",
    # v31: "Liczba poszkodowanych nie została podana" (test 25.10.2026).
    r"nie (został|została|zostało|zostały|zostali) (podan|ujawnion|wskazan|sprecyzowan|określon)\w*",
    # v32: "Aktualizacje … eliminują ryzyko ataków" (test 25.10.2026).
    r"eliminuj\w* (to |te |tę )?(ryzyk|zagrożeni)\w*",
    # v35: advice without content (6 of 13 summaries on 28.10.2026: "Zainstaluj
    # najnowsze wersje systemów, aby usunąć te luki", "Postępuj zgodnie z
    # zaleceniami GMO", "Zaleca się aktualizację wtyczki po jej wydaniu",
    # 27.10: "Należy zastosować udostępnione łatki").
    r"(zainstaluj\w*|zaktualizuj\w*|zastosuj\w*|zastosowa\w*|należy|powin\w+|zaleca\w*|postępuj\w*)[^.]{0,60}?"
    r"(najnowsz\w+ wersj\w*|udostępnion\w+ (łat|aktualiz|popraw)\w*|zgodnie z zalecen\w*|po (jej|ich) wydaniu|"
    r"dostępn\w+ (łat|aktualiz)\w*|wszystki\w+ aktualizacj\w*)",
    # v35: remarks about the article itself ("Artykuł opisuje serię zero-dayów…",
    # "Brak dostępnych łatek w artykule", 28.10.2026).
    r"artykuł\w* (opisuje|omawia|przedstawia|analizuje|wskazuje|podaje|mówi|dotyczy)",
    r"w (tym )?artykule",
    # v34: a moral instead of a fact ("Ta historia pokazuje, że…", "lekcja").
    r"(ta |cała )?(historia|sprawa|incydent|przypadek) (pokazuje|uczy|przypomina)\w*",
    r"lekcj\w* (z tego|z tej|dla)",
    # v34: speculation about escalation instead of a fact from the material.
    r"(sytuacja|sprawa|zagrożenie|problem|atak\w*) (może|mogą|moż\w+ będzie) (się )?(eskalować|nasilić|rozszerzyć|narastać)",
    r"(może|mogą) (dojść do )?(dalsz\w+ )?eskalacj\w*",
    # v33: "Liczba i rodzaj naruszonych danych nie są znane" (digest 26.10.2026).
    r"(nie|nadal nie) (jest|są|był|była|było|były) (jeszcze )?znan\w*",
    # v33: a bare closing formula with no concrete advice (4 of 10 summaries
    # on 26.10.2026: "Zaleca się natychmiastową aktualizację."). Advice with
    # content ("… i ograniczenie dostępu do interfejsów zarządzania") stays.
    r"zaleca się (natychmiastow\w+ |piln\w+ |niezwłoczn\w+ )?"
    r"(aktualizacj\w+|zastosowanie (łat\w+|aktualizacj\w+)|instalacj\w+ (łat\w+|aktualizacj\w+)|wgranie łat\w+)"
    r"( (systemu|oprogramowania|wszystkich wymienionych komponentów))?\.",
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

# v35: Unicode hyphens too (see kev.CVE_PATTERN).
CVE = re.compile(r"CVE[-\u2010\u2011\u2012]\d{4}[-\u2010\u2011\u2012]\d{4,7}", re.IGNORECASE)


def normalize_cve(cve):
    return re.sub(r"[\u2010\u2011\u2012]", "-", cve).upper()
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


# v33: labels the AI adds on its own (digest 26.10.2026: "podatność zero-day"
# for a flaw patched five days earlier; "natychmiastowa aktualizacja" in four
# summaries). They are allowed only when the article material has them too.
ZERO_DAY = re.compile(r"(?<!\w)(?:zero|0)[-\u2011‐ ]?day\w*|(?<!\w)dni\w* zerow\w*", re.IGNORECASE)
ZERO_DAY_SOURCE = re.compile(r"(?:zero|0)[-\u2011‐ ]?days?|zeroday|dni\w* zerow\w*", re.IGNORECASE)
URGENCY = re.compile(r"(?<!\w)natychmiast\w*", re.IGNORECASE)
PHISHING = re.compile(r"(?<!\w)(?:phishing\w*|socjotechni\w*)", re.IGNORECASE)
PHISHING_SOURCE = re.compile(r"phish\w*|social engineering|socjotechni\w*|smishing|vishing", re.IGNORECASE)
# v34: the "why it matters" sentence must not dramatize: exploitation in
# attacks and a missing patch only when the material says so.
EXPLOITED = re.compile(
    r"(?<!\w)aktywnie wykorzyst\w*|(?<!\w)wykorzystywan\w* (?:w atakach|w praktyce|przez atakujących)",
    re.IGNORECASE,
)
EXPLOITED_SOURCE = re.compile(
    r"exploit(?:ed|ation|ing)|in the wild|wykorzyst\w*|CISA KEV|atak\w*|attack\w*", re.IGNORECASE
)
NO_PATCH = re.compile(
    r"(?<!\w)(?:brak\w* (?:dostępn\w+ )?łat\w*|bez łat\w*|niezałatan\w*|nie (?:ma|wydano|wydał\w*|jest dostępn\w*) (?:jeszcze )?(?:\w+ )?łat\w*)",
    re.IGNORECASE,
)
# Clear statements that there is no patch.
NO_PATCH_SOURCE = re.compile(
    r"no (?:patch|fix)|not (?:yet )?(?:been )?(?:patched|fixed)|without a (?:patch|fix)|"
    r"has(?: not|n't) (?:yet )?released a (?:patch|fix)|has yet to (?:release|patch|fix)|"
    r"zero[- ]?day|0[- ]?day|brak\w* łat\w*|nie ma (?:jeszcze )?łat\w*|bez łat\w*",
    re.IGNORECASE,
)
# "unpatched" also describes old versions when a fix exists (Signal,
# test of 26.10.2026: "versions before 2.72.0", summary "nie ma łatki").
NO_PATCH_WEAK = re.compile(r"unpatched|niezałatan\w*", re.IGNORECASE)
FIXED_VERSION = re.compile(
    r"(?:prior to|before|earlier than|below) (?:version )?v?\d|fixed in|patched in|addressed in|resolved in|"
    r"update to (?:version )?v?\d|upgrade to|starsz\w* niż (?:wersj\w* )?\d|przed wersją|"
    r"(?:naprawion|poprawion|załatan)\w* w wersji|łat\w* w wersji|poprawk\w* w wersji",
    re.IGNORECASE,
)


def no_patch_supported(source):
    if NO_PATCH_SOURCE.search(source):
        return True

    return bool(NO_PATCH_WEAK.search(source)) and not FIXED_VERSION.search(source)
URGENCY_SOURCE = re.compile(
    r"immediate\w*|urgent\w*|as soon as possible|asap|without delay|right away|imperative|"
    r"natychmiast\w*|niezwłoczn\w*|pilni\w*|jak najszybciej",
    re.IGNORECASE,
)
# Code fix when the AI correction does not remove such a label.
ZERO_DAY_AFTER_NOUN = re.compile(
    r"(?<!\w)((?:luk|podatnoś|podatnosc)\w*)(?: typu)? \(?(?:zero|0)[-\u2011‐ ]?day\)?(?!\w)", re.IGNORECASE
)
URGENCY_WORD = re.compile(r"(?<!\w)natychmiast(?:ow\w+)?\s+", re.IGNORECASE)


def unsupported_labels(text, source):
    """Return "zero-day" and "natychmiast…" when the source does not say so."""
    problems = []
    match = ZERO_DAY.search(text)

    if match and not ZERO_DAY_SOURCE.search(source):
        problems.append(
            f"„{match.group(0)}” – artykuł nie nazywa tej luki zero-day; usuń to określenie"
        )

    match = URGENCY.search(text)

    if match and not URGENCY_SOURCE.search(source):
        problems.append(
            f"„{match.group(0)}” – artykuł nie mówi o pilności; usuń to słowo albo całe zalecenie"
        )

    # v36: possible effects the AI adds on its own ("co może umożliwić
    # kampanie phishingowe", 29.10.2026; "zwiększa ryzyko phishingu", 27.10).
    match = PHISHING.search(text)

    if match and not PHISHING_SOURCE.search(source):
        problems.append(f"„{match.group(0)}” – artykuł nie pisze o phishingu ani socjotechnice; usuń to")

    match = EXPLOITED.search(text)

    if match and not EXPLOITED_SOURCE.search(source):
        problems.append(f"„{match.group(0)}” – artykuł nie mówi o wykorzystywaniu w atakach; usuń to")

    match = NO_PATCH.search(text)

    if match and not no_patch_supported(source):
        problems.append(f"„{match.group(0)}” – artykuł nie mówi o braku łatki (albo podaje wersję z poprawką); usuń to")

    if match and FIXED_VERSION.search(text):
        problems.append(f"„{match.group(0)}” – sprzeczność: streszczenie podaje też wersję z poprawką; usuń to")

    return problems


def remove_unsupported_labels(text, source):
    """Remove "zero-day" after luka/podatność and "natychmiast…" when the source lacks them."""
    if not ZERO_DAY_SOURCE.search(source):
        text = ZERO_DAY_AFTER_NOUN.sub(lambda m: m.group(1), text)

    if not URGENCY_SOURCE.search(source):
        text = URGENCY_WORD.sub("", text)

    return fix_sentence_case(text)


def unsupported_facts(text, source, year=None):
    """Return CVE numbers and numbers above 12 that are not in the source."""
    problems = unsupported_labels(text, source)
    source_cves = {normalize_cve(cve) for cve in CVE.findall(source)}

    for cve in CVE.findall(text):
        if normalize_cve(cve) not in source_cves:
            problems.append(f"numer {normalize_cve(cve)} nie występuje w artykule – usuń go albo popraw")

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
# anglicisms with a suggestion ("intruzja" -> "włamanie").
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


def style_hits(text, rules=None):
    """Return [(used text, form from the list, suggestion)] for calques (v32)."""
    hits = []

    for pattern, form, suggestion in STYLE_RULES if rules is None else rules:
        match = pattern.search(text)

        if match:
            hits.append((match.group(0), form, suggestion))

    return hits


def suggestion_text(suggestion):
    """v33: "wersji, kompilacji" as alternatives, not a phrase to paste (test of
    26.10.2026: "46 własnych wersji, kompilacji szyfrujących")."""
    depth = 0
    parts = [""]

    for char in suggestion:
        depth += {"(": 1, ")": -1}.get(char, 0)

        if char == "," and depth == 0:
            parts.append("")
        else:
            parts[-1] += char

    parts = [part.strip() for part in parts if part.strip()]

    if len(parts) < 2:
        return suggestion

    return " albo ".join(parts) + " (wybierz jedno słowo, nie wpisuj obu)"


def style_problems(text, rules=None):
    """Calques and anglicisms from the style list, with suggestions."""
    return [f"kalka „{used}” – użyj: {suggestion_text(suggestion)}" for used, _, suggestion in style_hits(text, rules)]


def uninflected_hits(text):
    """Return [(phrase, term)] for terms left in the base form ("przed exploit", v32)."""
    return [(match.group(0), match.group(1)) for match in UNINFLECTED.finditer(text)]


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
# v34: three short sentences (what, why it matters, what to do) need a bit
# more room than 350 characters; the prompt asks for at most 420.
MAX_SUMMARY_LENGTH = 480


# v34: filler without a known phrase ("Atak ten stanowi poważne zagrożenie
# dla kluczowych sektorów"): a sentence with no concrete detail – no digit,
# CVE id, acronym, name or number word – but with evaluative words. Checked
# on 140 sentences of the October archive: 8 found, all filler; sentences
# that state an effect without names ("Luka umożliwia wykonanie dowolnego
# kodu bez uwierzytelnienia") have no evaluative words and stay.
CONCRETE = re.compile(r"\d|CVE-|[A-ZĄĆĘŁŃÓŚŹŻ]{2,}|[a-ząćęłńóśźż][A-ZĄĆĘŁŃÓŚŹŻ]")
NUMBER_WORDS = re.compile(
    r"(?<!\w)(?:jed[ne]\w*|dw[aie]\w*|trz[eiy]\w*|czter\w*|pię[ćc]\w*|sześ\w*|siedem\w*|osiem\w*|"
    r"dziesię\w*|kilk\w*|setk\w*|tysi[ąę]c\w*|milion\w*|miliard\w*|pierwsz\w*|drug[aiy]\w*|trzeci\w*|"
    r"połow\w*)(?!\w)",
    re.IGNORECASE,
)
EVALUATIVE = re.compile(
    r"(?<!\w)(?:pokaz\w*|pokazuj\w*|podkreśl\w*|wyzwa\w*|konsekwencj\w*|zagrożeni\w*|ryzyk\w*|"
    r"skuteczn\w*|istotn\w*|znaczeni\w*|kluczow\w*|poważn\w*|współprac\w*|ekspert\w*|dochodzeni\w*|"
    r"protok\w* reagowania|sytuacj\w*|wektor\w*|świadomoś\w*|czujnoś\w*|ostrożnoś\w*|bezpieczeństw\w*)(?!\w)",
    re.IGNORECASE,
)


def has_concrete(sentence):
    if CONCRETE.search(sentence) or NUMBER_WORDS.search(sentence):
        return True

    # A capitalized word after the first one is a name (firm, product, group).
    return any(word[0].isupper() for word in re.findall(r"[\w-]+", sentence)[1:])


def empty_sentences(text):
    """Sentences without a concrete detail but with evaluative words (v34)."""
    return [sentence for sentence in split_sentences(text)
            if not has_concrete(sentence) and EVALUATIVE.search(sentence)
            # Already reported as a known filler phrase.
            and not any(pattern.search(sentence) for pattern in GENERIC)]


# v34: readable for a busy reader ("żeby mózg się nie pocił", JW): long
# sentences and stacks of CVE ids go back for correction as soft problems,
# which never cut or drop a summary.
# v36: 30 instead of 25 – the split requests made the digest choppy
# (JW, 29.10.2026: "rwane").
MAX_SENTENCE_WORDS = 30
MAX_CVE_IDS = 2


IMPERATIVE_ADVICE = re.compile(
    r"(?:^|(?<=[.!?]\s))(?:Zainstaluj|Zaktualizuj|Zastosuj|Wyłącz|Włącz|Sprawdź|Postępuj|Usuń|Zmień|Zresetuj)\b"
)


OTHER_FLAWS = re.compile(
    r"\b(?:dwie|dwóch|trzy|trzech|cztery|czterech|kilka|kilku|\d+)\s+(?:inne|innych|dodatkowe|dodatkowych|"
    r"pozostałe|pozostałych)\s+(?:luki|luk|podatności|błędy|błędów)\b",
    re.I,
)


def readability_problems(text):
    problems = []

    # v35: advice in the imperative reads like a list of orders (28.10.2026).
    if IMPERATIVE_ADVICE.search(text):
        problems.append(
            "zalecenie w trybie rozkazującym – napisz je opisowo jako fakt "
            "(np. „Poprawka jest w wersji 1.6.0.”) albo pomiń, jeśli nie ma konkretu"
        )

    for sentence in split_sentences(text):
        words = len(re.findall(r"[\w-]+", CVE.sub("CVE", sentence)))

        if words > MAX_SENTENCE_WORDS:
            problems.append(
                f"zdanie ma {words} słów – podziel je na dwa krótsze zdania "
                f"(najwyżej {MAX_SENTENCE_WORDS} słów): „{sentence[:60]}…”"
            )

    cves = {normalize_cve(cve) for cve in CVE.findall(text)}

    if len(cves) > MAX_CVE_IDS:
        problems.append(
            f"{len(cves)} numery CVE – zostaw najwyżej {MAX_CVE_IDS} najważniejsze; pozostałe luki nazwij "
            "typem z artykułu (np. „i luka XXE”) albo pomiń"
        )

    # v37a: "oraz dwie inne luki" said nothing and came back in 5 summaries
    # on 30–31.10.2026 (the hint above used to suggest it).
    for match in OTHER_FLAWS.finditer(text):
        problems.append(
            f"pusta wzmianka „{match.group(0)}” – nazwij typ tych luk z artykułu "
            "(np. „i brak weryfikacji certyfikatów”) albo ją pomiń"
        )

    return problems


# v51: sentences about a missing patch or CVE where the article says
# nothing about patches ("Luka nie jest jeszcze wykorzystywana w atakach i
# nie istnieje łatka" about eBPF rootkits, "Firma nie podała informacji o
# łatce" about a breach at Notion, 12.11.2026).
NO_PATCH_SENTENCE = re.compile(
    r"[^.]*\b(?:nie (?:istnieje|ma|podał\w*|ujawnił\w*|poinformował\w*|wydał\w*)[^.]*\b(?:łatk\w*|CVE)"
    r"|brak łatki|łatka nie (?:jest|została|istnieje)|bez łatki|o łatce)[^.]*\.?",
    re.IGNORECASE,
)
PATCH_WORDS = re.compile(
    r"patch|fix|update|upgrade|łatk|poprawk|aktualizac|firmware|mitigat|advisory|cve-|no fix|unpatched|version",
    re.IGNORECASE,
)


def baseless_patch_problems(text, source):
    """Soft problem: a sentence about a missing patch or CVE although the
    article mentions no patch, update or CVE at all (v51)."""
    if not source or PATCH_WORDS.search(source):
        return []

    match = NO_PATCH_SENTENCE.search(text)

    if not match:
        return []

    return [f"zdanie o łatce lub CVE bez podstaw w artykule („{match.group(0).strip()[:80]}”) – usuń je, "
            "artykuł nie mówi o łatce"]


def quality_problems(text, source=None, soft=True):
    """Return descriptions of quality problems (empty list = summary is fine).

    soft=False leaves out style problems (calques from the style list): the
    AI is asked to fix them, but a summary is never cut or dropped for them.
    """
    problems = []

    if len(text) > MAX_SUMMARY_LENGTH:
        problems.append(
            f"streszczenie ma {len(text)} znaków – skróć je do najwyżej 420 znaków "
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

    for sentence in empty_sentences(text):
        problems.append(
            f"zdanie bez konkretu („{sentence[:70]}”) – zastąp je faktem z artykułu "
            "(kto, co, ile, kiedy) albo usuń"
        )

    if soft:
        problems.extend(style_problems(text))
        problems.extend(readability_problems(text))
        # v46: Morfeusz 2 grammar checks (numerals, product names, genders).
        problems.extend(grammar_problems(text))

    if looks_english(text):
        problems.append("streszczenie nie jest po polsku – napisz je po polsku")

    if source is not None:
        problems.extend(unsupported_facts(text, source))

        if repeats_title(text, source.split("\n", 1)[0]):
            problems.append("streszczenie powtarza tytuł – dodaj konkret z tekstu artykułu (kto, ile, skutki)")

        # v42: English words left untranslated (soft: asks for a fix).
        if soft:
            problems.extend(english_problems(text, source))
            # v51: no sentences about a patch the article does not mention.
            problems.extend(baseless_patch_problems(text, source))

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
