"""Export the glossary mirror for the digest from the Mozaika mother workbook.

Run manually, only when the mother workbook changes:

    pip install openpyxl
    python tools/eksport_mirrora.py path/to/glosariusz_cybersecNN_secplus.xlsx

Writes data/glosariusz_mirror.csv. The digest itself never reads the mother
workbook: it works only with the mirror.

Mirror columns:
  id       – permanent entry ID from the mother workbook (H###); entries
             from the "Hasła do dopisania" sheet get DOP-<row>
  termin_en – English term (used to find entries relevant to an article)
  haslo    – entry name exactly as in the mother workbook
  forma    – form the AI writes in the text
  nawias   – explanation added by code in parentheses at the first
             occurrence in a digest (empty = no explanation)
  regula   – extra instruction for the AI (empty for most entries)
  unikaj   – forms the AI must not use instead of "forma" (regular
             expressions separated by " | "); summaries are checked
             against them and corrected or dropped
  objasnienie – first sentence of the entry's explanation (reference only)

Default rule (decision 19.10.2026, "wariant 1"): an entry named
"X (Y)" is written as X when X is the English term or an acronym (the v32
naming rule of the mother workbook). Explanations in parentheses only for
the entries JW chose (decision 20.10.2026, option B): by default "nawias"
is empty and OVERRIDES set it. OVERRIDES hold all digest decisions.
"""

import csv
import re
import sys
from pathlib import Path

import openpyxl

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "glosariusz_mirror.csv"
COLUMNS = ["id", "termin_en", "haslo", "forma", "nawias", "regula", "unikaj", "objasnienie"]

# Digest decisions (JW, 19.10.2026). Keys: entry ID. Missing keys keep the
# default value of the column.
OVERRIDES = {
    # 22.10.2026 (v25): the AI added "(luka)" uninflected after every
    # "podatność" ("dwie krytyczne podatności (luka)"), so it is forbidden;
    # "luka" may still be used on its own.
    "H164": {"forma": "podatność", "nawias": "",
             "regula": "nie dopisuj „(luka)” w nawiasie; słowa „luka” możesz używać zamiennie",
             "unikaj": r"\(luk\w*\)"},
    "H153": {"forma": "exploit", "nawias": "kod wykorzystujący podatność",
             "regula": "nie spolszczaj", "unikaj": r"eksploit\w*"},
    "H159": {"unikaj": r"(?:podatnoś|luk)\w* dnia zerowego"},
    # 20.10.2026: "łatka" without parentheses ("wiadomo, że to poprawka");
    # 21.10.2026: "poprawka" forbidden, so the AI keeps to "łatka".
    # 22.10.2026 (v27): also anglicisms such as "patchują" (Arista test).
    "H166": {"forma": "łatka", "nawias": "",
             "unikaj": r"poprawk\w*|poprawce|poprawek | (?:s|za)?patch(?:uj|ow)\w*"},
    # 22.10.2026 (v25): also the English form left untranslated by the AI.
    "H090": {"unikaj": r"zdaln\w+ wykonani\w+ kodu | remote code execution"},
    "H182": {"forma": "podwyższenie uprawnień", "nawias": "eskalacja",
             "unikaj": r"eskalacj\w* uprawnień | podniesieni\w* uprawnień"},
    "H152": {"unikaj": r"dow[oó]d\w* koncepcji"},
    "H411": {"forma": "wyciek danych", "nawias": "",
             "regula": "„naruszenie ochrony danych”, gdy mowa o aspektach prawnych (RODO)"},
    "H207": {"forma": "poświadczenia", "nawias": "dane logowania", "unikaj": r"kredencja\w*"},
    "H028": {"unikaj": r"złośliw\w+ oprogramowa\w+"},
    "H012": {"unikaj": r"oprogramowa\w+ szpiegując\w*"},
    "H015": {"nawias": "program żądający okupu", "regula": "bez tłumaczenia"},
    "H019": {"forma": "infostealer", "nawias": "program kradnący dane",
             "regula": "bez tłumaczenia"},
    "H023": {"unikaj": r"tyln\w+ (?:furt\w+|drzwi)"},
    "H004": {"nawias": "sieć zainfekowanych urządzeń", "regula": "bez tłumaczenia"},
    "H372": {"forma": "sprawcy", "nawias": "",
             "regula": "albo „grupa” lub „cyberprzestępcy”, jeśli pasuje do kontekstu",
             "unikaj": r"aktor\w* zagroże\w*"},
    "H371": {"forma": "powiązani z państwem", "nawias": ""},
    "H365": {"unikaj": r"broker\w* pierwszego dostępu"},
    "H337": {"unikaj": r"rozbici\w* infrastruktury"},
    # 21.10.2026: MFA without parentheses ("wszyscy mamy z tym do czynienia").
    "H232": {"forma": "MFA", "nawias": "",
             "unikaj": r"uwierzytelniani\w* wieloskładnikow\w*"},
}

# Digest-only rows (variants recorded in the mother workbook as notes, or
# entries still waiting in "Hasła do dopisania").
EXTRA_ROWS = [
    {"id": "H371-sponsored", "termin_en": "state-sponsored", "haslo": "",
     "forma": "opłacani przez państwo", "nawias": "",
     "regula": "odmieniaj zgodnie z kontekstem", "unikaj": r"sponsorowan\w* przez państwo",
     "objasnienie": "Wariant z kolumny „Terminologia PL” hasła H371."},
]
INBOX_FORMS = {
    "wiper": ("wiper", "program niszczący lub usuwający dane", "bez tłumaczenia"),
}

ACRONYM = re.compile(r"^[A-Z0-9][A-Z0-9\-/ .]*$")


def first_sentence(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    match = re.match(r"(.+?[.!?])(\s|$)", text)
    return match.group(1) if match else text


def split_name(name):
    """Return (main part, part in the final parentheses) of an entry name."""
    match = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", name)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return name.strip(), ""


def default_forms(name, english):
    main, bracket = split_name(name)
    first = re.split(r",\s*", main)[0].strip()
    # Spaces and hyphens ignored: "DLL sideloading" = "DLL side-loading" (v84).
    def normalize(text):
        return re.sub(r"[\s\-]", "", (text or "").lower())

    english_first = bool(first) and (
        ACRONYM.match(first) or normalize(first) in normalize(english)
    )

    if english_first:
        # Option B (20.10.2026): no automatic explanation; see OVERRIDES.
        return first, ""

    # Polish entry names stay whole (e.g. "deidentyfikacja: anonimizacja, ...").
    return main, ""


def mirror_rows(path):
    workbook = openpyxl.load_workbook(path, read_only=True)
    sheet = workbook["Glosariusz"]
    rows = list(sheet.iter_rows(values_only=True))
    header = [str(value or "") for value in rows[0]]
    column = {name.split("\n")[0].strip(): index for index, name in enumerate(header)}
    id_column = next(i for i, name in enumerate(header) if name.startswith("ID hasła"))
    result = []

    for row in rows[1:]:
        name = row[column["Termin PL"]]
        entry_id = row[id_column]

        if not name or not entry_id:
            continue

        english = str(row[column["Termin EN"]] or "")
        forma, nawias = default_forms(str(name), english)
        record = {
            "id": entry_id,
            "termin_en": english,
            "haslo": str(name),
            "forma": forma,
            "nawias": nawias,
            "regula": "",
            "unikaj": "",
            "objasnienie": first_sentence(str(row[column["Wyjaśnienie"]] or "")),
        }
        record.update(OVERRIDES.get(entry_id, {}))
        result.append(record)

    inbox = workbook["Hasła do dopisania"]

    for number, row in enumerate(inbox.iter_rows(values_only=True), start=1):
        if number == 1 or not row[0] or "przeniesione" in str(row[3] or "") or "scalone" in str(row[3] or ""):
            continue

        polish, english, explanation = str(row[0]), str(row[1] or ""), str(row[2] or "")
        forma, nawias, regula = INBOX_FORMS.get(polish, (polish, "", ""))
        result.append({
            "id": f"DOP-{number}", "termin_en": english, "haslo": polish,
            "forma": forma, "nawias": nawias, "regula": regula, "unikaj": "",
            "objasnienie": first_sentence(explanation),
        })

    result.extend(EXTRA_ROWS)
    known = {record["id"] for record in result}
    missing = set(OVERRIDES) - known

    if missing:
        raise SystemExit(f"Brak haseł z OVERRIDES w matce: {sorted(missing)}")

    return result


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python tools/eksport_mirrora.py ścieżka/do/matki.xlsx")

    rows = mirror_rows(sys.argv[1])
    OUTPUT.parent.mkdir(exist_ok=True)

    # utf-8-sig: Excel on Windows shows Polish characters correctly.
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        file.write(f"# Mirror glosariusza CyberSec Mozaika – źródło: {Path(sys.argv[1]).name}\n")
        writer = csv.DictWriter(file, fieldnames=COLUMNS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Zapisano {len(rows)} haseł do {OUTPUT}")


if __name__ == "__main__":
    main()
