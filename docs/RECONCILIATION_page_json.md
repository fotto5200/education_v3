## Reconciliation: partner `page.json` → Canonical & Serve

This document maps each field in `page.json` to the canonical authoring schema and/or the serve snapshot, with rationale and phase notes.

### Summary
- `page.json` mixes authoring content, a final answer, inline SVG, and step questions.
- We split into: Canonical (server-only, full truth) and Serve (client, safe subset per request).

### Field-by-field mapping

- `type` → Canonical `type` (MVP)
  - Rationale: problem category; carried into serve as `item.type`.

- `title` → Canonical `title` (MVP)
  - Carried into serve as `item.title` (optional in UI).

- `hasPicture` (bool) → Replace with Canonical `media[]` presence (MVP)
  - Rationale: presence inferred by `media` array length.

- `svg` (inline SVG) → Canonical `media[] { id, object_key, alt }` (MVP)
  - Serve: `media[] { id, signed_url, ttl_s, alt }` (no inline SVG).
  - Rationale: signed URLs, CDN, a11y.

- `question` (string) → Canonical `content.html` or first step `prompt.html` (MVP)
  - Serve: appears in `item.content.html` or `item.steps[0].prompt.html`.
  - Rationale: HTML+KaTeX, not SVG text.

- `answers` (flat array) → Canonical `steps[][].choices[]` or top-level `choices[]` (MVP)
  - Each choice must be `{ id, text }` (not string only).
  - Serve: only selected 4 choices per step; randomized order.

- `answerText` (final answer) → Canonical `final.answer_text` (MVP)
  - Serve: never sent pre-submit; revealed via submit result.

- `version` (203) → Canonical `content_version` (MVP)
  - Serve: uses `version: "1.0"` for contract version.

- `stepQuestions[]` → Canonical `steps[]` (MVP)
  - Map: `question` → `prompt.html`; `answers[]` → `choices[] { id,text }`; `hint` → `hint`.
  - Serve: include steps (optional) without correctness; per-step `serve.choice_order`.

### New required fields (canonical)
- `item.id` (unique per variant), `template_id` (grouping), `generated_at`, `generator_version`, `tags { skill, difficulty }`.

### New runtime fields (serve)
- `session_id`, `serve.seed`, `serve.watermark`, `media[].signed_url`, `ttl_s`.

### Phasing
- [MVP] All mappings above except analytics-only tags and IDs like `serve_id`/`attempt_id`.
- [Later] Add analytics tags to choices, richer provenance, and logging identifiers.
