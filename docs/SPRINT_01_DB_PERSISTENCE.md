# Sprint 01 — Dev DB Persistence (SQLite)

## Goals
- Add SQLite‑backed persistence for selection state and attempts behind existing repo interfaces; default remains file/in‑memory. No API changes.

## Scope
- Tables
  - `selection_state(session_id PK, last_type, active_type_norm, serves_in_current_type, recent_ids_json, updated_at)`
  - `attempt_events(id PK, ts, session_id, item_id, item_type, action CHECK('served'|'answered'), correct)`
- Env flags
  - `DB_PERSIST_SELECTION=1` (enable SQLite)
  - File path: `dev_state/app.db` (gitignored)

## Files to add/change
- Add `backend/app/db.py`: connector + ensure tables
- Add `backend/app/selection_repo_db.py`: DB repo (load/save state; append/read events)
- Update `backend/app/selection_repo.py`: env‑gate to DB, else file; add init + read helper
- Update `backend/app/routes/session.py`: `/progress` and `/events.csv` use repo abstraction; call `init_if_needed()`
- Docs: note DB dev option in `docs/SERVE_PIPELINE.md` and `docs/API_CONTRACT.md`; update `state.plan.md`

## Tests (manual)
- File mode (default): flags off; verify `selection_state.json` changes; `/api/progress` and `/api/events.csv` respond
- DB mode: set `DB_PERSIST_SELECTION=1`; verify `dev_state/app.db` exists; progress survives restart; CSV exports rows

## Risks & mitigations
- DB unavailable: silently fallback to file repo
- Schema drift: ensure tables at startup; dev‑only

## Deliverables
- Working DB persistence env‑gated; docs updated; short runbook snippet
