"""Glossary conventions for AI summaries, read from the mirror of the
CyberSec Mozaika glossary (data/glosariusz_mirror.csv).

The digest never reads the Mozaika mother workbook; the mirror is exported
from it manually (tools/eksport_mirrora.py) and committed to this repository.
Since v32 every forbidden form found or replaced is kept as a language note
with the entry id (see ai_summaries.py), for the reports to Mozaika.

Conventions are enforced in three places:
1. Prompt: the AI gets the glossary entries relevant to the articles and a
   hard rule to use only the forms listed there.
2. Check: every summary is checked for forbidden forms ("unikaj" column);
   a summary that breaks the convention is sent back for correction, and
   code removes the sentences that are still wrong (v27).
3. Explanations: code (not the AI) adds the explanation in parentheses
   ("nawias" column) at the first occurrence of a term in the whole digest,
   so it is consistent and testable.

Polish inflected forms in INFLECTED were generated with the Morfeusz 2
morphological analyzer, so explanations agree with the case of the word they
explain (e.g. "poświadczeń (danych logowania)").
"""

import csv
import re
from pathlib import Path


MIRROR_PATH = Path(__file__).resolve().parent.parent / "data" / "glosariusz_mirror.csv"
PROMPT_EXTRA_LIMIT = 40

# Entries whose explanation must follow the case of the explained word.
# id: (regex with an "anchor" group, function of the match -> explanation)
ESCALATION = {
    # Accusative for the ambiguous nominative/accusative form (JW, 19.10.2026).
    "podwyższenie": "eskalację",
    "podwyższenia": "eskalacji",
    "podwyższeniu": "eskalacji",
    "podwyższeniem": "eskalacją",
    "podwyższeń": "eskalacji",
}
def escalation(match):
    """Explanation for "podwyższenie uprawnień": accusative for the ambiguous
    form, but nominative after "typu"/"rodzaju" (v29, test 25.10.2026:
    "podatności typu podwyższenie (eskalacja) uprawnień")."""
    anchor = match.group("anchor").lower()
    before = match.string[: match.start("anchor")]

    if anchor == "podwyższenie" and re.search(r"(?:typu|rodzaju)\s+$", before, re.IGNORECASE):
        return "eskalacja"

    return ESCALATION.get(anchor)


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
# English terms inflected like Polish nouns (v27, test 22.10.2026: "przed
# exploit (kod wykorzystujący podatność)"). Morfeusz 2 does not know these
# words, so their forms follow Polish model nouns generated with Morfeusz 2:
# exploit like "kotlet" (exploicie), botnet like "budżet" (botnecie),
# infostealer like "komputer" (infostealerze). The explanation phrases were
# generated with Morfeusz 2 as well ("kodem wykorzystującym podatność").
# Each form lists its possible cases; "exploita" and "infostealera" may be
# genitive or accusative (both forms are used in Polish).
def noun_forms(stem, endings):
    return {stem + ending: cases for ending, cases in endings.items()}


EXPLOIT_FORMS = noun_forms("exploi", {
    "t": ("sg_acc",), "ta": ("sg_acc", "sg_gen"), "towi": ("sg_dat",), "tem": ("sg_inst",),
    "cie": ("sg_loc",), "ty": ("pl_acc",), "tów": ("pl_gen",), "tom": ("pl_dat",),
    "tami": ("pl_inst",), "tach": ("pl_loc",),
})
BOTNET_FORMS = noun_forms("botne", {
    "t": ("sg_acc",), "tu": ("sg_gen",), "towi": ("sg_dat",), "tem": ("sg_inst",),
    "cie": ("sg_loc",), "ty": ("pl_acc",), "tów": ("pl_gen",), "tom": ("pl_dat",),
    "tami": ("pl_inst",), "tach": ("pl_loc",),
})
INFOSTEALER_FORMS = noun_forms("infosteale", {
    "r": ("sg_acc",), "ra": ("sg_acc", "sg_gen"), "rowi": ("sg_dat",), "rem": ("sg_inst",),
    "rze": ("sg_loc",), "ry": ("pl_acc",), "rów": ("pl_gen",), "rom": ("pl_dat",),
    "rami": ("pl_inst",), "rach": ("pl_loc",),
})
# Nominative and accusative explanations are the same for these phrases, so
# the accusative stands for both.
EXPLOIT_GLOSS = {
    "sg_acc": "kod wykorzystujący podatność", "sg_gen": "kodu wykorzystującego podatność",
    "sg_dat": "kodowi wykorzystującemu podatność", "sg_inst": "kodem wykorzystującym podatność",
    "sg_loc": "kodzie wykorzystującym podatność", "pl_acc": "kody wykorzystujące podatność",
    "pl_gen": "kodów wykorzystujących podatność", "pl_dat": "kodom wykorzystującym podatność",
    "pl_inst": "kodami wykorzystującymi podatność", "pl_loc": "kodach wykorzystujących podatność",
}
BOTNET_GLOSS = {
    "sg_acc": "sieć zainfekowanych urządzeń", "sg_gen": "sieci zainfekowanych urządzeń",
    "sg_dat": "sieci zainfekowanych urządzeń", "sg_inst": "siecią zainfekowanych urządzeń",
    "sg_loc": "sieci zainfekowanych urządzeń", "pl_acc": "sieci zainfekowanych urządzeń",
    "pl_gen": "sieci zainfekowanych urządzeń", "pl_dat": "sieciom zainfekowanych urządzeń",
    "pl_inst": "sieciami zainfekowanych urządzeń", "pl_loc": "sieciach zainfekowanych urządzeń",
}
INFOSTEALER_GLOSS = {
    "sg_acc": "program kradnący dane", "sg_gen": "programu kradnącego dane",
    "sg_dat": "programowi kradnącemu dane", "sg_inst": "programem kradnącym dane",
    "sg_loc": "programie kradnącym dane", "pl_acc": "programy kradnące dane",
    "pl_gen": "programów kradnących dane", "pl_dat": "programom kradnącym dane",
    "pl_inst": "programami kradnącymi dane", "pl_loc": "programach kradnących dane",
}

# Context that requires the genitive for a genitive/accusative form:
# prepositions, negation, verbs and verbal nouns that govern the genitive
# ("użycie exploita", "nie wykryto exploita", "do exploita").
GENITIVE_CONTEXT = re.compile(
    r"(?:^|[\s(])(?:do|od|ode|dla|bez|u|według|wokół|podczas|obok|około|zamiast|oprócz|"
    r"spośród|z|ze|brak\w*|pomocą|użyciu|wyniku|postaci|ramach|"
    r"uży\w*|używa\w*|szuka\w*|potrzeb\w*|unika\w*|\w+(?:nie|cie|cja|cji|cją))\s+(?:\w+\s+)?$"
    r"|(?:^|\s)nie\s+(?:\w+\s+){0,2}$",
    re.IGNORECASE,
)


def explain_in_case(forms, gloss):
    """Return a function giving the explanation in the case of the matched form."""
    def explain(match):
        cases = forms[match.group("anchor").lower()]
        case = cases[0]

        if "sg_gen" in cases and GENITIVE_CONTEXT.search(match.string[: match.start("anchor")]):
            case = "sg_gen"

        return gloss[case]

    return explain


def forms_pattern(forms):
    alternatives = "|".join(sorted(forms, key=len, reverse=True))
    return rf"(?<!\w)(?P<anchor>{alternatives})(?!\w)"


def ransomware_gloss(match):
    """v33: "ransomware" does not inflect, but its explanation does: genitive
    after a verb or preposition that governs it ("użyła ransomware
    (programu żądającego okupu)"), otherwise nominative/accusative."""
    if GENITIVE_CONTEXT.search(match.string[: match.start("anchor")]):
        return "programu żądającego okupu"

    return "program żądający okupu"


INFLECTED = {
    "H015": (r"(?<!\w)(?P<anchor>ransomware)(?!\w)", ransomware_gloss),
    "H182": (r"\b(?P<anchor>podwyższeni(?:e|a|u|em)|podwyższeń)\s+uprawnień\b",
             lambda m: escalation(m)),
    "H207": (r"\b(?P<anchor>poświadcze(?:nia|ń|niom|niami|niach|nie|niem|niu))\b",
             lambda m: CREDENTIALS.get(m.group("anchor").lower())),
    "H153": (forms_pattern(EXPLOIT_FORMS), explain_in_case(EXPLOIT_FORMS, EXPLOIT_GLOSS)),
    "H004": (forms_pattern(BOTNET_FORMS), explain_in_case(BOTNET_FORMS, BOTNET_GLOSS)),
    "H019": (forms_pattern(INFOSTEALER_FORMS), explain_in_case(INFOSTEALER_FORMS, INFOSTEALER_GLOSS)),
}


# Forbidden forms that code can replace safely (v27, third branch test of
# 22.10.2026: most correction requests were for "poprawki" and "zdalne
# wykonanie kodu", and a rate-limited correction round lost five
# summaries). Replacing them in code saves AI requests. "łatka" inflects
# like "poprawka" (poprawce -> łatce), RCE does not inflect, and "eksploit"
# forms map to the same "exploit" forms.
AUTOFIX = [
    # (pattern, replacement, required glossary form or a label of the rule)
    (re.compile(r"(?<!\w)([Pp])opraw(ka|ki|kę|ką|ce|ek|kom|kami|kach)(?!\w)"),
     lambda m: ("Ł" if m.group(1) == "P" else "ł") + "at" + m.group(2), "łatka"),
    (re.compile(r"(?<!\w)zdaln\w+ wykonani\w+ (?:dowolnego )?kodu(?!\w)", re.IGNORECASE), lambda m: "RCE", "RCE"),
    (re.compile(r"(?<!\w)remote code execution(?!\w)", re.IGNORECASE), lambda m: "RCE", "RCE"),
    # v29: reversed order ("wykonanie kodu zdalnie", test 25.10.2026).
    (re.compile(r"(?<!\w)wykonani\w+ (?:dowolnego )?kodu zdalnie(?!\w)", re.IGNORECASE), lambda m: "RCE", "RCE"),
    (re.compile(r"(?<!\w)([Ee])ksploi(t|ta|ty|tem|tów|tom|tami|tach|towi|cie)(?!\w)"),
     lambda m: m.group(1) + "xploi" + m.group(2), "exploit"),
    # v29: "zdalne wykonanie kodu (RCE)" became "RCE (RCE)" (24.10.2026);
    # a word repeated in parentheses right after itself is removed.
    (re.compile(r"(?<!\w)(\w+) \(\1\)"), lambda m: m.group(1), "powtórzenie w nawiasie"),
    (re.compile(r"(?<!\w)iPhoneie(?!\w)"), lambda m: "iPhonie", "odmiana"),
    # v35: "we"/"ze" before a word starting with w/f (we) or s/z/ś/ź/ż/w (ze)
    # followed by a consonant: "w wtyczce" → "we wtyczce" (28.10.2026),
    # "z wsparciem" → "ze wsparciem" (27.10.2026). "w wersji", "z wykorzystaniem"
    # (vowel after the first letter) stay.
    # Only before lowercase words: names and acronyms keep "w"/"z" ("z SQL",
    # "z SharePointem").
    (re.compile(r"(?<!\w)([Ww]) (?=[wf][bcdfghjklłmnprstwzćńśźż])"),
     lambda m: m.group(1) + "e ", "przyimek we"),
    # The digraphs sz, rz, cz, dz count as one consonant: "z szybkiego" stays,
    # "ze szkoły", "ze wsparciem", "ze zdjęcia" change.
    # v36: before "w" only when a sibilant follows ("ze wsparciem", "ze
    # wszystkimi", "ze względu"), not "z włączoną", "z wnukiem" (29.10.2026).
    (re.compile(r"(?<!\w)([Zz]) (?=(?:sz|rz|cz|dz)[bcdfghjklłmnprstwzćńśźż]|s(?!z)[bcdfghjklłmnprstwzćńśźż]"
                r"|z(?!z)[bcdfghjklłmnprstwzćńśźż]|[śźż][bcdfghjklłmnprstwzćńśźż]|w(?:sz|rz|[szśźż]))"),
     lambda m: m.group(1) + "e ", "przyimek ze"),
    # v35: "łata" is not the glossary form ("ponowne wprowadzenie łaty", 28.10.2026).
    (re.compile(r"(?<!\w)([Łł])at(a|y|ę|ą|om|ami|ach)(?!\w)"),
     lambda m: m.group(1) + {"a": "atka", "y": "atki", "ę": "atkę", "ą": "atką", "om": "atkom",
                             "ami": "atkami", "ach": "atkach"}[m.group(2)], "łatka"),
]


def autofix(text, changes=None):
    """Replace forbidden forms that have a safe automatic replacement.

    v32: when `changes` is a list, every replacement is added to it as a
    language note (type "autofix", glossary id when the rule follows a
    glossary entry), so the archive keeps what code corrected.
    """
    for pattern, replacement, target in AUTOFIX:
        def replace(match, replacement=replacement, target=target):
            fixed = replacement(match)

            if changes is not None and fixed != match.group(0):
                entry = entry_by_form(target)
                changes.append({
                    "type": "autofix",
                    "id": entry["id"] if entry else "",
                    "rule": target,
                    "used": match.group(0),
                    "fixed": fixed,
                })

            return fixed

        text = pattern.sub(replace, text)

    return text


def load_mirror(path=MIRROR_PATH):
    """Return mirror entries as a list of dicts (comment lines skipped)."""
    with open(path, encoding="utf-8-sig") as file:
        lines = [line for line in file if not line.startswith("#")]

    return list(csv.DictReader(lines, delimiter=";"))


ENTRIES = load_mirror()
ENTRIES_BY_FORM = {entry["forma"].lower(): entry for entry in ENTRIES}


def entry_by_form(form):
    """Return the mirror entry with this required form ("łatka", "RCE"), or None."""
    return ENTRIES_BY_FORM.get((form or "").lower())


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
    # Without parentheses: the AI copied "exploit (kit)" literally (test 19.10).
    english = re.sub(r"\s*\([^)]*\)", "", entry["termin_en"]).strip()
    line = f"- {english} → {entry['forma']}"

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


def violation_entries(text):
    """Return a list of (entry, used form) for forbidden forms (v32: with the entry)."""
    found = []

    for entry, patterns in FORBIDDEN:
        for pattern in patterns:
            match = pattern.search(text)

            if match:
                found.append((entry, match.group(0)))
                break

    return found


def convention_violations(text):
    """Return a list of (used form, required form) for forbidden forms."""
    return [(used, entry["forma"]) for entry, used in violation_entries(text)]


def gloss_rule(entry):
    """Return (compiled regex, explanation function) for an entry with "nawias"."""
    if entry["id"] in INFLECTED:
        pattern, explain = INFLECTED[entry["id"]]
        return re.compile(pattern, re.IGNORECASE), explain

    forma = entry["forma"]

    if is_acronym(forma):
        # Acronyms only as whole words, optionally inflected after a hyphen
        # ("IAB-ów"): "NAT" must not match inside "NATO" (20.10.2026).
        pattern = re.compile(rf"(?<!\w)(?P<anchor>{re.escape(forma)}(?:-\w+)?)(?!\w)")
    else:
        pattern = re.compile(rf"(?<!\w)(?P<anchor>{re.escape(forma)}\w*)", re.IGNORECASE)

    return pattern, lambda match, text=entry["nawias"]: text


# Longer terms first: "DLL sideloading" must win over "sideloading", whose
# explanation ("instalacja spoza sklepu") means something else (20.10.2026).
GLOSS_RULES = [
    (entry["id"], *gloss_rule(entry))
    for entry in sorted(
        (entry for entry in ENTRIES if entry["nawias"]),
        key=lambda entry: -len(entry["forma"]),
    )
]


# v33: an indeclinable term used as an attribute of a person or group
# ("negocjatorzy ransomware", "grupy ransomware INC") cannot take the
# explanation: "Negocjatorzy ransomware (program żądający okupu)" reads as if
# the negotiators were a program (test 26.10.2026). Such an occurrence is
# skipped; the explanation goes to a later one, or to a later summary of the
# digest. "Atak ransomware (program żądający okupu)" stays as before.
ATTRIBUTIVE_BEFORE = re.compile(
    r"(?<!\w)(?:negocj|grup|gang|operator|afiliant|ugrupowani|kartel|cyberprzestęp|przestęp|"
    r"twórc|autor|członk|lider|ofiar)\w*\s+$",
    re.IGNORECASE,
)
ATTRIBUTIVE_TERMS = {"H015"}


def first_usable_match(key, pattern, text):
    """First match of a term that can take an explanation."""
    for match in pattern.finditer(text):
        if key in ATTRIBUTIVE_TERMS and ATTRIBUTIVE_BEFORE.search(text[: match.start("anchor")]):
            continue

        return match

    return None


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

        match = first_usable_match(key, pattern, text)

        if not match:
            continue

        start, end = match.span("anchor")

        # A term that is itself inside parentheses (e.g. "wykonanie kodu (RCE)")
        # gets no nested explanation: "(RCE (zdalne ...))" seen in test 19.10.
        before = text[:start]
        if before.count("(") > before.count(")"):
            continue

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
