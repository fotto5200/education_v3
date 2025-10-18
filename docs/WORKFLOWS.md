## Core Workflows (brief)

- Authoring → Ingestion → Canonical: Author emits item JSON → ingestion validates/enriches → saves canonical item (Postgres) + media keys.
- Session Start (Login/Resume): User signs up/logs in → server sets httpOnly session cookie → client loads profile/preferences.
- Select Next Item: MVP selects by `item.type` (same as last served per session by default; optional `type` query override). Future: policy engine may apply playlists/skill/difficulty and avoids near-duplicates → returns canonical item id.
- Serve Snapshot: Backend derives safe payload (prompt, choices, signed media, randomized order, watermark) → FE renders.
- Per‑step Submit and Feedback: Client posts choice (with CSRF) → server grades from canonical → returns correctness + explanation/next step.
- Media Fetch: FE requests signed URL assets → CDN serves SVG/PNG → alt/long_alt used for accessibility.
- Onboarding Flow: First login → guided steps (verify → tutorial/assessment) → initial skill targeting.
- Content QA and Promotion: QA tool reviews stats/flags → authors fix or deprecate variants → promote staged → live.
- Analytics Export: Nightly job extracts facts (sessions, accuracy, time‑to‑answer) → warehouse for reporting.
- Rate Limiting & Anomaly Response: API enforces per‑user limits → anomaly detector throttles/alerts on scraping patterns.
- Teacher/Tutor Playlists: Educator defines sequence/playlist → selection prioritizes playlist order with adaptive tweaks.
- Deploy & Backup: CI/CD builds containers → deploys to Cloud Run → scheduled backups and policy‑based retention.

## Detailed Workflow: Serve a Problem (end‑to‑end)

- Preconditions
  - Valid session (httpOnly cookie), CSRF token ready for writes.
  - User context loaded (skill state, playlists, difficulty band).

- 1) Load session/context
  - Read: session cookie → look up `user_id`, prior serves/attempts, teacher playlist (if any), last difficulty per skill.

- 2) Selection (choose next item)
- MVP: determine `target_type` (query `type` if provided; else last served type for the session; else default type from available items). Dev/testing: if `policy=simple`, rotate to the next available `type` after N serves; if `policy=engine`, ask the dev policy stub (same‑type by default; rotate after N when `ENGINE_STRICT=1`).
  - Read candidates from canonical store filtered by `type == target_type`.
  - Exclude near-duplicates/recents (session recent window).
  - Future: apply playlists/skill/difficulty/policy engine to score and pick.

- 3) Fetch canonical
  - Read canonical JSON by `item.id` (verify `content_version/status`).
  - Confirm media object_keys exist.

- 4) Construct serve snapshot (safe payload)
  - Runtime fields: create `seed`, `watermark`; mint `serve_id` (Later).
  - Steps: include first step (or all steps) without correctness.
  - Choices: set per-step `serve.choice_order` (IDs only, randomized).
  - Media: sign each `object_key` → `signed_url` with `ttl_s`; include `alt` (and optionally expose `long_alt`).
  - UI hints: minimal layout/actions.

- 5) Audit “served” event
  - Write: `problem_served` with {user_id, session_id, serve_id, item.id, template_id, seed, choice_order, timestamp}.

- 6) Respond to client
  - Return serve snapshot: {version, session_id, item{…}, serve{seed, watermark}, ui{…}}.

- 7) Client render
  - FE displays prompt/choices (KaTeX for math).
  - Browser fetches media via `signed_url` (CDN caches; URLs expire).

- 8) Submit (per-step or per-item)
  - Client POSTs {session_id, item_id, step_id, choice_id} with CSRF + credentials.
  - Rate limit check; validate session; basic schema validation.

- 9) Grade on server
  - Read canonical → locate step/choice; determine correctness.
  - Prepare explanation_html; compute `next_step` if multi-step.

- 10) Record attempt
  - Write: `answer_submitted` with {attempt_id, serve_id, step_id, choice_id, correct, latency_ms, timestamp}.

- 11) Update progress
  - Update per-skill stats: attempts, accuracy, streaks, last difficulty, mastery band.
  - Persist last-served pointers for “resume”.

- 12) Respond with feedback
  - Return {correct, explanation{html}, next_step?}.
  - If item completed: write `item_completed` and return a brief summary or signal to fetch next.

- 13) Prefetch/next scheduling (optional)
  - Optionally pre-select next candidate (warm cache, pre-sign media); enqueue spiral review.

- 14) Anti-abuse controls (continuous)
  - Per-user rate limits; short `ttl_s` on signed URLs; watermark in serve; anomaly detection (bursts, multi-IP).

- Error/fallbacks
  - No candidates: return actionable “need content” signal; optionally fall back to spiral review.
  - Media signing fails: omit image with `alt`, log error, continue.
  - Validation/CSRF/rate limit failures: return 400/403 with terse messages.

- IDs used (recommended)
  - Always: `session_id`, `item.id`, `template_id`.
  - Soon/Later: `serve_id` (one serve), `attempt_id` (one submit).

## Terms & Acronyms

| Term | Meaning |
|---|---|
| API | Application Programming Interface; our FastAPI endpoints. |
| ADR | Architecture Decision Record; documented design choices. |
| BE | Backend; FastAPI app, selection, grading, pipelines. |
| BI | Business Intelligence; analytics/reporting destination. |
| CDN | Content Delivery Network; caches media near users. |
| CI/CD | Continuous Integration/Continuous Delivery; automated build/test/deploy. |
| CSP | Content Security Policy; blocks inline/unsafe scripts. |
| CSRF | Cross-Site Request Forgery; token required on state‑changing requests. |
| DB | Database; Postgres with JSONB for canonical items. |
| ETL | Extract, Transform, Load; nightly analytics export. |
| FE | Frontend; React+Vite web app rendering serve snapshots. |
| httpOnly cookie | Cookie not readable by JS; sent automatically by the browser. |
| i18n | Internationalization; later localization hooks. |
| JSONB | Postgres JSON column type with indexing support. |
| KaTeX | Client-side math rendering library for LaTeX. |
| PAT | Personal Access Token (GitHub); used as password for HTTPS pushes. |
| PII | Personally Identifiable Information; kept minimal and protected. |
| RPO/RTO | Recovery Point/Time Objective; backup/restore targets. |
| SSO | Single Sign-On; optional future identity method. |
| SVG | Scalable Vector Graphics; diagrams stored in object storage. |
| TTL (`ttl_s`) | Time To Live in seconds for a signed URL before it expires. |
| UI | User Interface; layout and interaction on the client. |
| Watermark | Subtle per-user/time marker in serve payload/media for deterrence. |
| alt | Short, essential text alternative for an image (HTML img alt). |
| long_alt | Optional extended description for complex diagrams (accessibility). |
