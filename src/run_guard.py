"""Guard against more than one scheduled digest per day (v19).

GitHub runs scheduled workflows unreliably: many scheduled starts are
skipped or come hours late. The workflow therefore has several morning
start times, and this guard makes sure only the first successful scheduled
run of the day sends a digest. Manual runs are never blocked.

Since v24 the main trigger is an external alarm clock (cron-job.org), which
starts the workflow through the API (workflow_dispatch) with the input
budzik=true. The workflow passes it on as TRIGGER=budzik, and the guards
treat it like a scheduled run, so the alarm clock and GitHub's own schedule
(kept as a backup) never send the same digest twice.

The marker data/last_digest.json is written after every completed run
(also when there was nothing to send), but not after a failed delivery, so
a later attempt can try again.
"""

import json
import os
from pathlib import Path

from article_archive import today_local


MARKER_PATH = Path("data/last_digest.json")

# Triggers that may be skipped: GitHub's schedule and the external alarm clock.
SCHEDULED_TRIGGERS = {"schedule", "budzik"}


def current_trigger():
    """Return what started this run: "budzik" for the external alarm clock,
    otherwise GitHub's event name ("schedule", "workflow_dispatch")."""
    return os.environ.get("TRIGGER", "").strip() or os.environ.get("GITHUB_EVENT_NAME", "")


def last_digest_date(path=MARKER_PATH):
    """Return the date of the last completed digest run, or None."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return None

    return data.get("date") if isinstance(data, dict) else None


def should_skip(event_name=None, today=None, path=MARKER_PATH):
    """Return True for a scheduled run when today's digest has already run."""
    event_name = current_trigger() if event_name is None else event_name
    today = today_local() if today is None else today
    return event_name in SCHEDULED_TRIGGERS and last_digest_date(path) == today


def mark_done(articles_sent, event_name=None, today=None, path=MARKER_PATH):
    """Record that today's digest run has completed."""
    event_name = current_trigger() if event_name is None else event_name
    record = {
        "date": today_local() if today is None else today,
        "trigger": event_name or "local",
        "articles": articles_sent,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
