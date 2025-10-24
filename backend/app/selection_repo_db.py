import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from .db import connect, ensure_tables


def is_enabled() -> bool:
    val = os.environ.get("DB_PERSIST_SELECTION", "").strip().lower()
    return val in ("1", "true", "yes", "on")


def init_db() -> None:
    if not is_enabled():
        return
    ensure_tables()


def load_selection_state() -> Dict[str, Any]:
    if not is_enabled():
        return {}
    out: Dict[str, Any] = {}
    try:
        with connect() as conn:
            cur = conn.cursor()
            for row in cur.execute("SELECT session_id, last_type, active_type_norm, serves_in_current_type, recent_ids_json FROM selection_state"):
                sid = row["session_id"]
                out[sid] = {
                    "last_type": row["last_type"],
                    "active_type": row["active_type_norm"],
                    "serves_in_current_type": row["serves_in_current_type"],
                    "recent_window": 5,
                    "recent_ids": json.loads(row["recent_ids_json"] or "[]"),
                }
    except Exception:
        return {}
    return out


def save_selection_state(state: Dict[str, Any]) -> None:
    if not is_enabled():
        return
    try:
        with connect() as conn:
            cur = conn.cursor()
            for sid, payload in state.items():
                recent_ids = payload.get("recent_ids") or []
                cur.execute(
                    """
                    INSERT INTO selection_state(session_id, last_type, active_type_norm, serves_in_current_type, recent_ids_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                      last_type=excluded.last_type,
                      active_type_norm=excluded.active_type_norm,
                      serves_in_current_type=excluded.serves_in_current_type,
                      recent_ids_json=excluded.recent_ids_json,
                      updated_at=excluded.updated_at
                    """,
                    (
                        sid,
                        payload.get("last_type"),
                        payload.get("active_type"),
                        int(payload.get("serves_in_current_type") or 0),
                        json.dumps(recent_ids, ensure_ascii=False),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
            conn.commit()
    except Exception:
        pass


def append_event(event: Dict[str, Any]) -> None:
    if not is_enabled():
        return
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO attempt_events(ts, session_id, serve_id, attempt_id, item_id, item_type, action, correct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    event.get("session_id"),
                    event.get("serve_id"),
                    event.get("attempt_id"),
                    event.get("item_id"),
                    event.get("item_type"),
                    event.get("action"),
                    1 if bool(event.get("correct")) else (None if event.get("correct") is None else 0),
                ),
            )
            conn.commit()
    except Exception:
        pass


def read_events_for_session(session_id: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not (is_enabled() and session_id):
        return rows
    try:
        with connect() as conn:
            cur = conn.cursor()
            for row in cur.execute(
                "SELECT ts, session_id, serve_id, attempt_id, item_id, item_type, action, correct FROM attempt_events WHERE session_id=? ORDER BY id ASC",
                (session_id,),
            ):
                rows.append({
                    "ts": row["ts"],
                    "session_id": row["session_id"],
                    "serve_id": row["serve_id"],
                    "attempt_id": row["attempt_id"],
                    "item_id": row["item_id"],
                    "item_type": row["item_type"],
                    "action": row["action"],
                    "correct": (True if row["correct"] == 1 else (False if row["correct"] == 0 else None)),
                })
    except Exception:
        return []
    return rows
