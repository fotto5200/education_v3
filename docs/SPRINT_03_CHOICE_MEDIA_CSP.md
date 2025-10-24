# Sprint 03 — Choice‑level Media, FE Rendering, CSP/A11y

## Goals

- Add choice‑level media support end‑to‑end (canonical → serve → FE render).
- Keep item‑level media working; maintain accessibility semantics (alt/long_alt).
- Harden client security stance with an env‑driven CSP allowlist for media origins.

## Scope

- Backend
  - Canonical: allow `steps[].choices[].media[]` (id, object_key, alt, long_alt?).
  - Serve: include `choices[].media[]` with `signed_url` + `ttl_s` (similar to item.media).
  - Security: no correctness in serve; keep short‑lived URLs and watermarking (if applicable).
- Frontend
  - Render choice media (image + text) for each choice where present.
  - Preserve alt/long_alt semantics; simple affordance for long descriptions.
- Ops/Security
  - CSP: env‑driven allowlist for media origins (dev: self/localhost; prod: CDN origin).

## API & Schema Changes

- Canonical schema (server‑only):
  - `steps[].choices[].media[]` supports: `{ id, object_key, alt, long_alt? }`.
- Serve snapshot (client payload):
  - `choices[].media[]` supports: `{ id, signed_url, ttl_s, alt }` (optional `long_alt` later).
- No changes to correctness or grading fields.

## Files to Change

- Backend
  - `backend/app/util.py` — extend `canonical_to_serve` to emit choice‑level media.
  - `backend/app/store.py` — ensure canonical loader passes through choice media.
  - `backend/app/main.py` — (optional) CSP header wiring once FE domain config is set.
- Frontend
  - `frontend/src/App.tsx` — render choice images alongside text, use `alt`.
  - (Later) affordance for `long_alt` if present.
- Docs
  - `docs/API_CONTRACT.md` — document `choices[].media[]` in serve payload.
  - `docs/SERVE_PIPELINE.md` — add choice‑media handling notes.
  - `docs/CURRENT_STATUS.md` — update active target and next actions.

## Acceptance Criteria

1) A canonical item with choice‑level media serves a payload where each choice includes media with `signed_url`, `ttl_s`, and `alt`.
2) Frontend displays choice images (if any) with accessible `alt` text and the original choice text.
3) CSP is configurable via env; dev allows localhost; production restricts to CDN origin.
4) Item‑level media continues to render unchanged.

## Manual Tests

- Create/modify a sample canonical item to include `steps[0].choices[0].media[0]`.
- Start backend (file mode) and FE; GET `/api/item/next?type=...` and verify serve payload `choices[].media[]`.
- In FE, visually confirm image appears next to the corresponding choice text.
- Confirm alt text is present in the DOM and announced by screen readers (spot‑check).

## Risks & Mitigations

- Mixed legacy data: render gracefully when media arrays are missing; no crashes.
- CSP breakage: provide clear error/log when an origin is blocked; document env values.
- Over‑rendering: keep layout lightweight; avoid large images in choices by default.

## Out of Scope (Later)

- `long_alt` rendering UI beyond basic accessibility.
- Watermarking inside choice‑level SVGs.
- IDs: `serve_id` and `attempt_id` additions.


