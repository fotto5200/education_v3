## Serve Pipeline (Canonical → Serve/Submit)

### Inputs
- Canonical item JSON (schema: `schemas/item_canonical_v1.json`).
- Session context (`session_id`, user state), selection state.

### Outputs
- Serve snapshot (schema: `schemas/item_serve_v1.json`)
- Submit result (`schemas/submit_result_v1.json`)

### Steps
1) Selection picks the next canonical item for a session.
   - MVP: default to the same `item.type` as the last item served in the session; optional `type` query overrides this.
   - Dev/testing: `policy=simple` rotates to the next available `item.type` after N serves (default 3, `POLICY_N`). `policy=engine` consults a dev policy stub; by default continues same‑type; with `ENGINE_STRICT=1` rotates after N serves.
   - Future: policy engine may choose type transitions based on user performance/roadmap.
2) Construct serve snapshot:
   - Copy safe fields: `item { id, type, title?, content.html }`.
   - Transform media: `object_key` → `signed_url` + `ttl_s`, include `alt` (and optionally expose `long_alt`).
   - Steps: include `steps[] { step_id, prompt.html, choices[] { id,text } }` without correctness; set per-step `serve.choice_order`.
   - Runtime: set `session_id`, `serve.seed`, `serve.watermark`.
3) Client submits: `{ session_id, item_id, step_id?, choice_id? }`.
4) Grade on server using canonical; respond `{ correct, explanation { html }?, next_step? }`.

#### Grading (MVP)
- Minimal evaluator compares submitted choice text to canonical `final.answer_text` (string equality).
- If `final.explanation.html` exists, it is returned in the `explanation` field for client rendering.
- Older lorem items may lack aligned choices or explanations; use new TYPE_A/B/C samples for grading tests.

### Rules
- Never send correctness flags or final keys in serve snapshot.
- Randomize choice order per serve; log seed/ordering.
- Serve signed media URLs with short TTL; watermark SVGs subtly when feasible.

### Phases
- [MVP] single-step or simple multi-step; per-step submit recommended; no `serve_id/attempt_id`.
- [Later] add `serve_id`, `attempt_id` for logging/analytics; support phase submits and advanced UI hints.

### Dev-only persistence & logs
- When `DEV_PERSIST_SELECTION=1`, the server persists selection state to `dev_state/selection_state.json` and appends simple events to `dev_state/events.ndjson`.
- When `DB_PERSIST_SELECTION=1`, the server uses SQLite at `dev_state/app.db` via an env‑gated repo.
- Fields (selection state per session): `last_type`, `active_type`, `recent_ids[]`, `serves_in_current_type` (window=5).
- Events (NDJSON): `{ ts, session_id, item_id, item_type?, action: served|answered, correct? }`.

### Progress (dev-only)
- Endpoint: `GET /api/progress` returns per-session attempts/correct/accuracy by item.type and an overall rollup.
- Source: aggregates from dev events (`answered`) via the active persistence repo; if persistence is off, returns zeros.

### Events export (dev-only)
- Endpoint: `GET /api/events.csv` streams CSV for the current session using dev events.
- Columns: `ts,session_id,item_id,item_type,action,correct`.
