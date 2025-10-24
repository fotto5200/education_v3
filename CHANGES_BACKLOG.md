## Schema & Process Changes Backlog

Entries are lightweight; we will batch updates to docs/code at checkpoints.

- [Done] Choice-level media support
  - Extend `choices[]` to allow `{ media[] }` similar to item-level media
  - Serve pipeline to include choice media with signed URLs
  - FE to render choice buttons with text and/or images

- [Planned] Item-level media rendering in FE
  - Add rendering of `item.media[]` in `frontend/src/App.tsx`
  - Preserve alt/long_alt semantics for accessibility

- [Done] CSP policy: env-driven allowlist for media origins
  - Dev: local static (`self`, `http://localhost:*`)
  - Prod: explicit CDN origin in `img-src`

- [Planned] Accessibility: expose optional `long_alt`
  - Canonical already allows `long_alt`
  - Consider exposing via serve snapshot and UI affordance

- [Done] IDs in serve/submit flows (dev)
  - Added `serve_id` and `attempt_id` to serve & submit; updated logs and events export


- [Planned] Plan persistence snapshots
  - Maintain `docs/PLAN_HISTORY/YYYY-MM-DD.md` snapshots at milestones
  - Add brief entry per snapshot to `docs/SESSION_LOG.md` (if major)


