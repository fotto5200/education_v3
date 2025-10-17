# Current Status — Local MVP

Date: 2025-10-13

Note: Plan persistence — `\\state.plan.md` is the single source of truth. At each session start, we print Start Gate (last updated, active next target, next actions). Session close runs the Save Protocol (plan/status/backlog/session log + external commit).

## What works now
- Backend (FastAPI)
  - Serves local media statically at `/media` (maps to repo `media/`).
  - `POST /api/session`: issues httpOnly cookie (`ev3_session`).
  - `GET /api/item/next`: builds a serve snapshot from `data/canonical/*.json` and now selects a random item per request.
    - Adds `serve.seed`, randomized `serve.choice_order`, and a per-serve `watermark`.
    - Transforms `media[].object_key` → `media[].signed_url` under `/media/items/...` with stub `ttl_s`.
  - `POST /api/answer`: returns a mock grading result (placeholder).
- Frontend (React/Vite)
  - Renders `item.content.html` with KaTeX for inline math.
  - Orders choices by `serve.choice_order`.
  - Renders optional `item.media[]` images with `alt` text.

## Contracts and data
- Uses schemas in `schemas/` (serve, submit) and local canonical JSON in `data/canonical/`.
- Serve payload excludes correctness; grading remains server-side (mocked for now).

## Run locally (external terminals)
- Backend: `uvicorn backend.app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm install && npm run dev`
- Browser app: `http://localhost:5173`
- Direct serve check: `http://localhost:8000/api/item/next` (refresh to see varying `item.id`).

## Notes
- Selection is random per request (stateless); variety depends on files present in `data/canonical/`.
- Media URLs are local (unsigned) with a short stub `ttl_s` for development.
- Startup is quiet; avoid long-running watchers inside planning steps—run them externally.

### CSRF (enforced)
- `POST /api/session` now returns `{ session_id, csrf_token }` and sets the httpOnly cookie.
- `POST /api/answer` requires header `X-CSRF-Token` matching the current session; missing/invalid → 403.
- Frontend fetches the token on mount and includes it on submit. Manual verification:
  - Network tab: normal submit has `X-CSRF-Token` and returns 200.
  - Console test (no header) returns 403.

### Rate limiting (dev)
- Library: `slowapi` with session cookie (fallback to IP) as key.
- Current dev/test limits (intentionally low for manual testing):
  - `GET /api/item/next`: 5/min
  - `POST /api/answer`: 5/min
- Exceeding returns 429 with rate-limit headers (and `Retry-After`).
- Counters reset on server restart (in-memory). Limits will be raised later.
- Cooldown UI: FE uses `X-RateLimit-Reset` (epoch) with a small safety buffer before re‑enabling the Check button. Because we use a fixed window, the first click right at the boundary can still 429; acceptable for MVP.

### Multi-step (MVP)
- Serve payload includes `item.steps[]` with `{ step_id, prompt.html, choices[] }` and per-step `serve.choice_order`.
- Frontend renders one step at a time, shows “Step X of N,” and advances on submit when `next_step` is returned.
- Single-step items still use top-level `choices` and `serve.choice_order`.
- Grading is mocked; advancement uses client index for now. Verify by seeing the step counter increase after each Check.

### Feedback UI
- After submit, the frontend renders server-provided `explanation.html` beneath the Check button (HTML + KaTeX supported).
- The last explanation remains visible when advancing to the next step, until a new submit replaces it.

## Next targets (suggested)
1) CSRF header requirement on `POST /api/answer` (server verify; FE include header).
2) Round‑robin or stateful selection (optional) and simple per-skill filters.
3) Multi-step serve/render (include `steps[]`, advance via `next_step`).
4) Basic rate limiting on submit and serve endpoints.
