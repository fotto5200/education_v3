## Served Item Specification

### Purpose
End-to-end spec for how a problem is served to a student: identities, lifecycle, payloads, runtime fields, and phases.

### Identities
- Canonical (authoring): `item.id` (unique per instantiated variant), `template_id` (groups variants), `content_version`.
- Session/runtime: `session_id` (per user session), `serve_id` (per serve), `attempt_id` (per submit).
- Contract: `contract_version` (e.g., "1.0").

### Lifecycle (timeline)
1) `POST /api/session` → sets `session_id` cookie.  
2) `GET /api/item/next` → returns serve snapshot for next item.  
3) `POST /api/answer` (per-step or per-item) → returns correctness/explanation and optional `next_step`.  
4) Repeat until done; optional final summary.

### Runtime fields (server-generated)
- `serve.seed`: randomness source per serve (logging/debug).
- `serve.choice_order`: per step or per item (IDs only).
- `serve.watermark`: subtle per-user/time marker.
- `media[].signed_url` + `ttl_s`: short-lived URLs for diagrams.

### Client payloads (when each field is sent)
- Serve snapshot (GET /api/item/next):
  - `version` (contract), `session_id`, `item { id, type, title?, content.html, media[] }`,
  - optional `item.steps[] { step_id, prompt.html, choices[] { id,text, media[] }, serve { choice_order } }`,
  - `choices[]` at item level for single-step items (each choice may include `media[]`),
  - `serve { id, seed, watermark }`, `ui { layout, actions }`.
  - Never include correctness flags, tags, or authoring-only fields.
- Submit result (POST /api/answer): `{ correct, explanation { html }?, next_step?, attempt_id }`.

### Media handling (runtime)
- Canonical stores `media[].object_key` and `alt`/`long_alt`.
- On serve, backend issues `signed_url` with `ttl_s` for each media item and returns `alt` (and may expose `long_alt` via an accessible UI affordance).
- Frontend loads the image from the `signed_url` and uses `alt` for accessibility; avoid embedding text inside images.

### Accessibility
- Prompts and math are in HTML+KaTeX; images are additive.
- Every media item must have `alt`; provide `long_alt` for complex diagrams (exposed via a “more description” UI or screen reader-only text).

### Authoring-time fields (canonical, server-only)
- Content: `type`, `title`, `content.html` (HTML + LaTeX), `media[] { object_key, alt, long_alt? }`.
- Steps: `steps[] { step_id, prompt.html, choices[] { id,text, tag? }, hint?, explanation? }`.
- Final: `final { answer_text, explanation.html }` (not sent to client pre-submit).
- Provenance: `template_id`, `variant_index?`, `generated_at`, `generator_version`.
- Tags/meta: `skill`, `difficulty`, `cluster`, `status`.

### Phases
- [MVP]
  - Single-step or simple multi-step items with fixed 4 choices per step (pre-instantiated variants).
  - Serve snapshot includes item or first step; randomize order; grade via canonical.
- [Later]
  - `serve_id`, `attempt_id` in logs; phase submits; richer UI hints; analytics tags per choice.

### Security and anti-scraping
- httpOnly cookie sessions; CSRF on writes.
- No keys client-side; one-item endpoints; signed media; randomized order; watermark.

### Logging (keys)
- Log `user_id`, `session_id`, `serve_id`, `attempt_id`, `item.id`, `template_id`, `serve.seed`, chosen `choice_id`, result.
