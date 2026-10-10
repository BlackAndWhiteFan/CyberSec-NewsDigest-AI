import json
from pathlib import Path


DEFAULT_HISTORY = {
    "seen_links": [],
    "published_links": [],
}


def load_history(path="data/seen_articles.json"):
    """Load article history from a JSON file."""
    history_path = Path(path)

    if not history_path.exists():
        return DEFAULT_HISTORY.copy()

    with history_path.open("r", encoding="utf-8") as file:
        history = json.load(file)

    if not isinstance(history, dict):
        raise ValueError("Article history must be a JSON object.")

    seen_links = history.get("seen_links")

    if not isinstance(seen_links, list):
        raise ValueError("Article history must contain a seen_links list.")

    if not all(isinstance(link, str) for link in seen_links):
        raise ValueError("All seen_links entries must be strings.")

    return {"seen_links": list(dict.fromkeys(seen_links))}


def save_history(history, path="data/seen_articles.json"):
    """Save article history to a JSON file."""
    seen_links = history.get("seen_links") if isinstance(history, dict) else None

    if not isinstance(seen_links, list):
        raise ValueError("Article history must contain a seen_links list.")

    if not all(isinstance(link, str) for link in seen_links):
        raise ValueError("All seen_links entries must be strings.")

    history_path = Path(path)
    history_path.parent.mkdir(parents=True, exist_ok=True)

    with history_path.open("w", encoding="utf-8") as file:
        json.dump(
            {"seen_links": list(dict.fromkeys(seen_links))},
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")
