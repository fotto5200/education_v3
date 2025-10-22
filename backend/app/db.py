import os
import sqlite3
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
DEV_DIR = ROOT / "dev_state"
DB_PATH = DEV_DIR / "app.db"


def _get_db_path() -> Path:
    DEV_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def connect() -> sqlite3.Connection:
    path = _get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables() -> None:
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS selection_state (
                  session_id TEXT PRIMARY KEY,
                  last_type TEXT,
                  active_type_norm TEXT,
                  serves_in_current_type INTEGER,
                  recent_ids_json TEXT,
                  updated_at TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS attempt_events (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ts TEXT NOT NULL,
                  session_id TEXT NOT NULL,
                  item_id TEXT,
                  item_type TEXT,
                  action TEXT NOT NULL CHECK(action IN ('served','answered')),
                  correct INTEGER
                )
                """
            )
            conn.commit()
    except Exception:
        # Dev-only; fail silently
        pass
