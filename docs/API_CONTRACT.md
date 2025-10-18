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
  "serve": { "seed": "r8xz", "choice_order": ["B","C","A"], "watermark": "u_abc_2025-10-09" },
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
{ "session_id": "s_123", "item_id": "i_456", "step_id": "step_1", "choice_id": "B" }
```

Response:
```json
{ "correct": true, "explanation": { "html": "Correct: 8 + 6 - 5 = 9." }, "next_step": { "id": "step_2" } }
```

Schemas: `schemas/submit_step_v1.json`, `schemas/submit_result_v1.json`

#### Semantics (MVP grading)
- The server evaluates correctness by comparing the submitted choice’s text to the canonical `final.answer_text` for the item (exact text match; step‑agnostic for MVP samples).
- When present, `final.explanation.html` is returned as `explanation.html` for display by the client.
- Legacy/local lorem items may omit explanations and may not align choice text with final answers; those can grade False and/or return `explanation` absent. Use the newer TYPE_A/B/C samples for end‑to‑end grading tests.

### Notes
- Never include correctness flags in the serve snapshot.
- All LaTeX in JSON must use escaped delimiters (e.g., `\\( ... \\)`).
- The client must pass credentials (cookies) and CSRF token on writes.

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
- Dev-only data source: when `DEV_PERSIST_SELECTION=1`, the server aggregates from `dev_state/events.ndjson` (answered events). Without it, all zeros.
- Scope: current session only; no user identity assumptions.

### Events export (GET /api/events.csv)
Response: CSV stream with header
```
ts,session_id,item_id,item_type,action,correct
```

Notes:
- Dev-only: requires `DEV_PERSIST_SELECTION=1`. Exports only events for the current session (cookie).
- Fields: `ts` (ISO 8601), `session_id`, `item_id`, `item_type` (if present), `action` (served|answered), `correct` (true|false or empty).
