## Serve Pipeline (Canonical → Serve/Submit)

### Inputs
- Canonical item JSON (schema: `schemas/item_canonical_v1.json`).
- Session context (`session_id`, user state), selection state.

### Outputs
- Serve snapshot (schema: `schemas/item_serve_v1.json`)
- Submit result (`schemas/submit_result_v1.json`)

### Steps
1) Selection picks the next canonical item for a session (respect playlists/skill/difficulty).
2) Construct serve snapshot:
   - Copy safe fields: `item { id, type, title?, content.html }`.
   - Transform media: `object_key` → `signed_url` + `ttl_s`, include `alt` (and optionally expose `long_alt`).
   - Steps: include `steps[] { step_id, prompt.html, choices[] { id,text } }` without correctness; set per-step `serve.choice_order`.
   - Runtime: set `session_id`, `serve.seed`, `serve.watermark`.
3) Client submits: `{ session_id, item_id, step_id?, choice_id? }`.
4) Grade on server using canonical; respond `{ correct, explanation { html }?, next_step? }`.

### Rules
- Never send correctness flags or final keys in serve snapshot.
- Randomize choice order per serve; log seed/ordering.
- Serve signed media URLs with short TTL; watermark SVGs subtly when feasible.

### Phases
- [MVP] single-step or simple multi-step; per-step submit recommended; no `serve_id/attempt_id`.
- [Later] add `serve_id`, `attempt_id` for logging/analytics; support phase submits and advanced UI hints.
