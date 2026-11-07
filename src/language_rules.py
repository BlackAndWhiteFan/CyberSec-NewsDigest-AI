"""v46: the living document of Polish rules (data/reguly_jezyka.md).

JW edits the document; every line starting with "- " in the section
"## Nakazy dla modeli" goes word for word to the prompts of the writing
model, the language correction and the event stories. Other sections only
describe where the remaining rules live.
"""

from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "reguly_jezyka.md"
SECTION = "## Nakazy dla modeli"


def load_rules(path=RULES_PATH):
    """Return the bullet lines of the section SECTION (without "- ")."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []

    rules = []
    inside = False

    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == SECTION
            continue

        if inside and line.startswith("- "):
            rules.append(line[2:].strip())

    return rules


RULES = load_rules()


def prompt_rules(rules=None):
    """The rules as prompt lines, or an empty string."""
    rules = RULES if rules is None else rules
    return "\n".join(f"- {rule}" for rule in rules)
