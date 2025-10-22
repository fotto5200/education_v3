# MVP Backlog (pre‑data)

## Backend
- Selection
  - Step-aware grading: support per-step correct choice (older items) and keep `final.answer_text` fallback.
  - Health checks: `GET /api/health` (OK) and readiness (checks key subsystems).
  - Error responses: concise 4xx/5xx with stable JSON shape.
- Persistence (dev → prod path)
  - Current: file/SQLite (env‑gated). Next: Postgres repo behind the same interface.
  - Export tools: NDJSON→CSV endpoint done; add simple filters (date/type) later.
- Security & ops
  - Rate-limit tuning; CORS tighten for known origins; CSP template in docs.
  - Structured logging fields (user/session/item/type/action).

## Frontend
- Usability
  - Type switch (dev‑only) to fetch by `?type` from a small control.
  - Error/empty states (403/429/network): friendly banners.
  - Accessibility: label radios, keyboard focus indicators, ARIA where needed.
- Feedback flow
  - Keep banner + explanation; consider auto‑advance on correct (toggle) later.

## Content/dev data
- Add 1–2 more items per `TYPE_A/B/C` for rotation tests.
- Optional: bring legacy LOREM items up to grading parity (answer/explanation).

## Docs & runbooks
- CURRENT_STATUS: summarize grading/progress/CSV and how to test.
- Short test runbook: common curl/PowerShell snippets.
- Security posture quick ref (CSRF, rate limits, CSP).

## Optional (post‑MVP prep)
- DB repo: Postgres implementation (env‑gated), tiny migrations, basic indexing.
- Simple policy rules scaffold using attempts/accuracy by type.
