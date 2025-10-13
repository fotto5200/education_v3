## Schema & Process Changes Backlog

Entries are lightweight; we will batch updates to docs/code at checkpoints.

- [Planned] Choice-level media support
  - Extend `choices[]` to allow `{ media[] }` similar to item-level media
  - Serve pipeline to include choice media with signed URLs
  - FE to render choice buttons with text and/or images

- [Planned] Item-level media rendering in FE
  - Add rendering of `item.media[]` in `frontend/src/App.tsx`
  - Preserve alt/long_alt semantics for accessibility

- [Planned] CSP policy: env-driven allowlist for media origins
  - Dev: local static (`self`, `http://localhost:*`)
  - Prod: explicit CDN origin in `img-src`

- [Planned] Accessibility: expose optional `long_alt`
  - Canonical already allows `long_alt`
  - Consider exposing via serve snapshot and UI affordance

- [Later] IDs in serve/submit flows
  - Add `serve_id` and `attempt_id` to serve & submit schemas
  - Update logging and analytics


