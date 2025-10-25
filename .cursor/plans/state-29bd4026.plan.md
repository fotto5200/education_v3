<!-- 29bd4026-c053-4052-9153-31d01394f26b 9b05234e-29f2-4d66-85c1-bf84e9836b9b -->
# Sprint 02 — Step‑aware Grading, Health/Readiness, Error UX

## Goals

- Grade legacy multi‑step items correctly (no more false negatives).
- Add basic operability endpoints for local checks.
- Improve error UX (clear, consistent messages).

## Scope

- Backend
- Step‑aware grading (MVP): support per‑step correct choice via dev‑only `steps[].correct_choice_id`; keep `final.answer_text` fallback.
- Health endpoints:
  - `GET /api/health` → 200 OK when server is up
  - `GET /api/readiness` → checks limiter/repo init; 200 when ready, else 503 with terse JSON
- Error JSON shape (stable): `{ code: string, message: string }` for 4xx/5xx (concise, no stack traces)
- Frontend
- Error states: friendly banners for 403 (CSRF), 429 (rate limit), and network errors; brief retry guidance; accessible focus
- Accessibility quick pass on radios/buttons (labels/focus outline)
- Dev data (limited)
- Add `correct_choice_id` to 2–3 legacy LOREM items to validate step‑aware grading

## Files to Change

- `backend/app/routes/answer.py` — implement step‑aware grading (look up correct_choice_id per step)
- `backend/app/routes/health.py` (new) — `GET /api/health`, `GET /api/readiness`
- `backend/app/main.py` — include health router
- `frontend/src/App.tsx` — map error states (403/429/network) to small banners
- `data/canonical/*.json` — add `steps[].correct_choice_id` to a few legacy items (dev only)
- Docs — `docs/API_CONTRACT.md`, `docs/SERVE_PIPELINE.md`, `docs/CURRENT_STATUS.md` (brief)

## Testing (manual)

- Fetch a legacy multi‑step LOREM item; brute‑force submits should find a correct (True) when `correct_choice_id` is present
- `GET /api/health` → 200 OK; `GET /api/readiness` → 200 OK when `DEV_PERSIST_SELECTION` or `DB_PERSIST_SELECTION` is enabled
- Force 403 (omit CSRF) and 429 (fast submits) to see FE banners; verify focus/keyboard

## Risks & Mitigations

- Mixed legacy data: keep fallback to `final.answer_text` when `correct_choice_id` missing
- Over‑verbose errors: enforce terse `{ code, message }`, log details server‑side only (if enabled)

## Deliverables

- Correct grading for tagged legacy items
- Health/readiness endpoints
- FE error banners & a11y quick pass
- Docs updated

### To-dos

- [ ] Implement step-aware grading in backend/app/routes/answer.py (use steps[].correct_choice_id)
- [ ] Add GET /api/health and /api/readiness (new health.py; wire in main.py)
- [ ] Adopt stable error shape { code, message } for 4xx/5xx
- [ ] Show friendly banners for 403/429/network; ensure focus and labels
- [ ] Add steps[].correct_choice_id to 2–3 legacy LOREM items (dev only)
- [ ] Update API_CONTRACT, SERVE_PIPELINE, CURRENT_STATUS for Sprint 02