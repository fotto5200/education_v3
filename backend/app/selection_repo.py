import os
from typing import Any, Dict, List

from . import selection_repo_db as db_repo

# File-based fallback implemented here (existing functions)
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
DEV_DIR = ROOT / "dev_state"
STATE_PATH = DEV_DIR / "selection_state.json"
EVENTS_PATH = DEV_DIR / "events.ndjson"


def _file_is_enabled() -> bool:
    val = os.environ.get("DEV_PERSIST_SELECTION", "").strip().lower()
    return val in ("1", "true", "yes", "on")


def is_enabled() -> bool:
    # Enabled if either file or DB persistence is enabled
    return _file_is_enabled() or db_repo.is_enabled()


def init_if_needed() -> None:
    # Ensure dirs/tables
    if db_repo.is_enabled():
        db_repo.init_db()
    if _file_is_enabled():
        try:
            DEV_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass


def load_selection_state() -> Dict[str, Any]:
    if db_repo.is_enabled():
        return db_repo.load_selection_state()
    if not _file_is_enabled():
        return {}
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_selection_state(state: Dict[str, Any]) -> None:
    if db_repo.is_enabled():
        db_repo.save_selection_state(state)
        return
    if not _file_is_enabled():
        return
    try:
        tmp = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        STATE_PATH.write_text(tmp, encoding="utf-8")
    except Exception:
        pass


def append_event(event: Dict[str, Any]) -> None:
    if db_repo.is_enabled():
        db_repo.append_event(event)
        return
    if not _file_is_enabled():
        return
    try:
        DEV_DIR.mkdir(parents=True, exist_ok=True)
        event_with_ts = {"ts": datetime.now(timezone.utc).isoformat(), **event}
        with EVENTS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event_with_ts, ensure_ascii=False) + "\n")
    except Exception:
        pass


def read_events_for_session(session_id: str) -> List[Dict[str, Any]]:
    if db_repo.is_enabled():
        return db_repo.read_events_for_session(session_id)
    rows: List[Dict[str, Any]] = []
    if not (_file_is_enabled() and session_id):
        return rows
    if not EVENTS_PATH.exists():
        return rows
    try:
        with EVENTS_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("session_id") != session_id:
                    continue
                rows.append(e)
    except Exception:
        return []
    return rows
