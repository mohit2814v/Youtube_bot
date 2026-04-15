"""Track past story titles so Groq never repeats a story.

Stores a simple JSON list in output/history/<channel>.json.
Works both locally and in CI (if the repo is checked out with history,
or if you commit the history file back — see workflow).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_DIR = REPO_ROOT / "output" / "history"
MAX_HISTORY = 200  # keep last N titles; enough for ~6 months daily


def _history_path(channel: str) -> Path:
    return HISTORY_DIR / f"{channel}.json"


def load_history(channel: str) -> list[str]:
    p = _history_path(channel)
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(t) for t in data]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_title(channel: str, title: str) -> None:
    history = load_history(channel)
    history.append(title.strip())
    history = history[-MAX_HISTORY:]
    p = _history_path(channel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def history_prompt_block(channel: str) -> str:
    """Returns a string to inject into the Groq prompt, or empty if no history."""
    titles = load_history(channel)
    if not titles:
        return ""
    recent = titles[-50:]
    listing = "\n".join(f"  - {t}" for t in recent)
    return (
        "\n\nIMPORTANT — Do NOT repeat any of these past stories. "
        "Pick a COMPLETELY different plot, setting, and characters:\n"
        f"{listing}\n"
    )
