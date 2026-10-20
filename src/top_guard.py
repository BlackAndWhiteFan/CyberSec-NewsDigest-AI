"""Guard against sending the same weekly or monthly top twice (v22).

GitHub skips or delays many scheduled runs, so the top workflows have
several attempts. The marker data/last_top.json remembers the last period
sent for each kind ("week": "2026-W43", "month": "2026-10"). A scheduled
attempt for a period that was already sent ends without sending; manual
runs are never blocked. Test runs from branches do not write the marker.
"""

import json
import os
from pathlib import Path


MARKER_PATH = Path("data/last_top.json")


def load_marker(path=MARKER_PATH):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}

    return data if isinstance(data, dict) else {}


def should_skip(kind, period, event_name=None, path=MARKER_PATH):
    """True for a scheduled run when this period has already been sent."""
    event_name = os.environ.get("GITHUB_EVENT_NAME", "") if event_name is None else event_name
    return event_name == "schedule" and load_marker(path).get(kind) == period


def mark_sent(kind, period, path=MARKER_PATH):
    """Record that the top for this period has been handled."""
    data = load_marker(path)
    data[kind] = period
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
