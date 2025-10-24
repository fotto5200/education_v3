## API Contract

This document shows canonical examples and links to JSON Schemas in `schemas/`.

See also: `LaTeX_Escaping_Guide.md` for escaping rules.

### Serve snapshot (GET /api/item/next)
```json
{
  "version": "1.0",
  "session_id": "s_123",
  "item": {
    "id": "i_456",
    "type": "mcq",
    "content": { "html": "Evaluate \\( y = 2x^2 + 3x - 5 \\) at \\( x = 2 \\)." },
    "media": [
      { "id": "fig1", "signed_url": "https://cdn.example/abc", "ttl_s": 120, "alt": "Quadratic diagram" }
    ]
  },
  "choices": [
    { "id": "A", "text": "9" },
    { "id": "B", "text": "11" },
    { "id": "C", "text": "13" }
  ],
  "serve": { "id": "serve_ab12cd34", "seed": "r8xz", "choice_order": ["B","C","A"], "watermark": "u_abc_2025-10-09" },
  "ui": { "layout": "question-above-choices", "actions": ["submit"] }
}
```

Schema: `schemas/item_serve_v1.json`

#### Query parameters (MVP)
- `type` (optional): when provided, the server scopes selection to items whose `item.type` matches the given value (case-insensitive). Without this parameter, selection defaults to the same type as the last item served in the session.
- `policy` (optional, dev/testing):
  - `simple`: rotate to the next available `item.type` after N serves (default N=3, env `POLICY_N`).
  - `engine`: consults a dev policy engine stub that recommends the next `item.type`. By default it continues same‑type; if env `ENGINE_STRICT=1`, it rotates after N serves (env `POLICY_N`, default 3).
  - Ignored if `type` is provided.

Examples:
- `GET /api/item/next` → next item of the same type as last served (session-scoped)
- `GET /api/item/next?type=PARALLEL_LINE_FIND_X` → next item of that type

Notes:
- `skill` is NOT used for next-item selection in the MVP; it is reserved for future remedial focus flows.
- `policy=simple|engine` are development/testing only; production policy selection will be governed by a server-side policy engine.

### Submit step (POST /api/answer)
Request:
```json
{ "session_id": "s_123", "item_id": "i_456", "step_id": "step_1", "choice_id": "B", "serve_id": "serve_ab12cd34" }
```

Response:
```json
{ "correct": true, "explanation": { "html": "Correct: 8 + 6 - 5 = 9." }, "next_step": { "id": "step_2" }, "attempt_id": "attempt_ef567890" }
```

Schemas: `schemas/submit_step_v1.json`, `schemas/submit_result_v1.json`

#### Semantics (step‑aware grading)
- If the canonical item has `steps[]` and the targeted step (by `step_id`, or the first step if omitted) includes `correct_choice_id`, the server grades by ID: `correct := (choice_id == correct_choice_id)`.
- Otherwise, the server falls back to comparing the submitted choice’s text to the canonical `final.answer_text` (exact string match; trimmed; case‑sensitive currently).
- When present, `final.explanation.html` is returned as `explanation.html`.
- For legacy/local lorem items where data may be incomplete, fallback behavior applies; use TYPE_A/B/C samples for predictable tests.

### Notes
- Never include correctness flags in the serve snapshot.
- All LaTeX in JSON must use escaped delimiters (e.g., `\\( ... \\)`).
- The client must pass credentials (cookies) and CSRF token on writes.

### Error responses (stable JSON shape)
- All 4xx/5xx errors return JSON: `{ "code": string, "message": string }`.
- Common codes:
  - `csrf_required` (403)
  - `rate_limited` (429) — includes standard rate‑limit headers
  - `bad_request`, `not_found`, `server_error`

Example 429 body:
```json
{ "code": "rate_limited", "message": "Too many requests" }
```

### Health and readiness
- `GET /api/health` → `{ "status": "ok" }` (200) when process is up.
- `GET /api/readiness` → dev‑friendly 200 with diagnostics, e.g.:
```json
{ "status": "ready", "limiter_ok": true, "persistence": { "file": true, "db": false } }
```

### Progress summary (GET /api/progress)
Response (example):
```json
{
  "session_id": "s_123",
  "by_type": {
    "TYPE_A": { "attempts": 3, "correct": 2, "accuracy": 0.6667 },
    "TYPE_B": { "attempts": 1, "correct": 0, "accuracy": 0.0 }
  },
  "overall": { "attempts": 4, "correct": 2, "accuracy": 0.5 }
}
```

Notes:
- Dev-only data source: when `DEV_PERSIST_SELECTION=1`, the server aggregates from `dev_state/events.ndjson` (answered events). With `DB_PERSIST_SELECTION=1`, aggregates from SQLite at `dev_state/app.db`. Without persistence enabled, returns zeros.
- Scope: current session only; no user identity assumptions.

### Events export (GET /api/events.csv)
Response: CSV stream with header
```
ts,session_id,serve_id,attempt_id,item_id,item_type,action,correct
```

Notes:
- Dev-only: requires `DEV_PERSIST_SELECTION=1`. Exports only events for the current session (cookie).
- Fields: `ts` (ISO 8601), `session_id`, `item_id`, `item_type` (if present), `action` (served|answered), `correct` (true|false or empty).
- Header-only is returned when no events exist for the current session.

Usage examples:
```powershell
# With WebRequestSession (recommended)
$ws = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$sess = Invoke-RestMethod -Uri "http://localhost:8000/api/session" -Method Post -WebSession $ws
Invoke-WebRequest -Uri "http://localhost:8000/api/events.csv" -WebSession $ws -OutFile events.csv
```
```bash
# With cookie jar (curl)
curl -c jar.txt -X POST http://localhost:8000/api/session
curl -b jar.txt http://localhost:8000/api/events.csv -o events.csv
```
