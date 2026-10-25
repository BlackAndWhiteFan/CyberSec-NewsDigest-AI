"""Language notes: what was corrected in the AI summaries, kept in the archive (v32).

Until v31 the corrections lived only in the run log: forbidden glossary
forms, calques from the style list, terms left uninflected, replacements
made by code (autofix) and changes made by the proofreading. The log is gone
after 90 days and cannot be counted. Since v32 each delivered article
carries a list of notes ("language" in the archive record), the material
for the weekly reports to CyberSec Mozaika (v33): which forms the AI uses
most, which entries they concern (glossary id), and how they were fixed.

A note is a small dict with "type":
- "glossary": a forbidden form ("used") instead of the required form
  ("required"), with the entry id;
- "style": a calque from data/styl_unikaj.csv ("form" is the list entry);
- "inflection": a term left in the base form ("przed exploit");
- "autofix": a replacement made by code without an AI request;
- "proofreading": a summary changed by the language correction ("before",
  "after", "model").

The first three come from the first AI draft and get "fixed_by": "ai" (the
AI correction removed the problem), "code" (code removed the sentence),
"remains" (still in the delivered summary; only calques can stay) or
"dropped" (the summary was dropped). Notes describe AI output only; they
never change the summary and never write to the glossary.
"""

from glossary import entry_by_form, violation_entries
from summary_quality import style_hits, uninflected_hits


def findings(text):
    """Return the glossary, style and inflection notes for one summary draft."""
    notes = [
        {"type": "glossary", "id": entry["id"], "used": used, "required": entry["forma"]}
        for entry, used in violation_entries(text)
    ]

    notes += [
        {"type": "style", "used": used, "form": form, "suggestion": suggestion}
        for used, form, suggestion in style_hits(text)
    ]

    for phrase, term in uninflected_hits(text):
        entry = entry_by_form(term)
        notes.append({
            "type": "inflection",
            "id": entry["id"] if entry else "",
            "used": phrase,
            "term": term.lower(),
        })

    return notes


def settle(notes, final_text, path):
    """Set "fixed_by" on draft notes: path is "ai", "code" or "dropped"."""
    for note in notes:
        if path == "dropped" or not final_text:
            note["fixed_by"] = "dropped"
        elif note["used"].lower() in final_text.lower():
            note["fixed_by"] = "remains"
        else:
            note["fixed_by"] = path

    return notes


def unique(notes):
    """Notes without repeats (the same autofix can happen in the draft and in the correction)."""
    seen = set()
    result = []

    for note in notes:
        key = tuple(sorted((name, str(value)) for name, value in note.items()))

        if key not in seen:
            seen.add(key)
            result.append(note)

    return result


TYPE_NAMES = [
    ("glossary", "słowniczek"),
    ("style", "styl"),
    ("inflection", "odmiana"),
    ("autofix", "autopoprawki"),
    ("proofreading", "korekta"),
]


def log_line(articles):
    """One log line with the number of notes of each type."""
    counts = {name: 0 for name, _ in TYPE_NAMES}

    for article in articles:
        for note in article.get("language", []):
            if note.get("type") in counts:
                counts[note["type"]] += 1

    parts = ", ".join(f"{label} {counts[name]}" for name, label in TYPE_NAMES)
    return f"JĘZYK: uwagi językowe do archiwum – {parts}"
