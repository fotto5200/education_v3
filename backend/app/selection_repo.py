import json
import os
from pathlib import Path
from typing import Any, Dict
from datetime import datetime, timezone

# Dev-only persistence toggle

def is_enabled() -> bool:
    val = os.environ.get("DEV_PERSIST_SELECTION", "").strip().lower()
    return val in ("1", "true", "yes", "on")


ROOT = Path(__file__).resolve().parents[2]
DEV_DIR = ROOT / "dev_state"
STATE_PATH = DEV_DIR / "selection_state.json"
EVENTS_PATH = DEV_DIR / "events.ndjson"


def _ensure_dir() -> None:
    try:
        DEV_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def load_selection_state() -> Dict[str, Any]:
    if not is_enabled():
        return {}
    _ensure_dir()
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_selection_state(state: Dict[str, Any]) -> None:
    if not is_enabled():
        return
    _ensure_dir()
    try:
        tmp = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        STATE_PATH.write_text(tmp, encoding="utf-8")
    except Exception:
        # Best-effort in dev
        pass


def append_event(event: Dict[str, Any]) -> None:
    if not is_enabled():
        return
    _ensure_dir()
    try:
        event_with_ts = {"ts": datetime.now(timezone.utc).isoformat(), **event}
        with EVENTS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event_with_ts, ensure_ascii=False) + "\n")
    except Exception:
        # Best-effort in dev
        pass
