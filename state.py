"""Démo state — porté depuis localStorage (app.js) vers un fichier JSON local.

ponytail: single JSON file, no DB. Fine for a single-demo-user hackathon
prototype; swap for a real store (Supabase, sqlite) if multi-user ever matters.
"""
import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / ".demo-state.json"


def fresh_state():
    return {
        "draft": None,
        "submitted": None,
        "selected_client": "C-1042",
        "approved_drafts": [],
        "imported_records": [],
        "client_updates": {},
        # conversations : [{id, title, created, messages: [{role, content}]}]
        "conversations": [],
        "current_chat": None,
    }


def load():
    if not STATE_FILE.exists():
        return fresh_state()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {**fresh_state(), **data}
    except (json.JSONDecodeError, OSError):
        return fresh_state()


def save(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def reset():
    state = fresh_state()
    save(state)
    return state
