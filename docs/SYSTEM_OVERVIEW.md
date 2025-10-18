## System Overview

### Goals and principles
- **Low cost**: free OSS UI stack; frugal hosting that scales.
- **Security**: httpOnly cookie sessions, CSRF, strict CSP, no secrets in FE.
- **Anti-scraping**: no bulk endpoints, per-serve randomization, signed media, watermarking, rate limits.
- **Fast redesign**: headless components + Tailwind tokens; lightweight server-driven UI.

### Architecture (high level)
- **Frontend**: React + Vite + Tailwind + Radix (headless) + KaTeX.
  - Renders items from a small server-provided JSON “serve snapshot”.
  - Design tokens via CSS variables; theme switch at runtime.
- **Backend**: FastAPI (Python), httpOnly cookie sessions, CSRF for writes.
  - Endpoints: `POST /api/session`, `GET /api/item/next`, `POST /api/answer`.
  - Selection: session-scoped rotation with no immediate repeats (recent window ~5 for MVP).
  - Randomizes `choice_order`; evaluates submissions; logs attempts.
- **Data**: Postgres JSONB (canonical problems & serve snapshots); object storage for media (SVG/PNG) via signed URLs.
- **Hosting**: GCP Cloud Run (containers), Cloud SQL Postgres, Cloud Storage, Cloud CDN. Alternatives optional.

### Data model
- **Canonical problem (server-only)**: full truth (keys, explanations, authoring metadata).
- **Serve snapshot (client payload)**: safe subset for rendering.
  - Includes: `version`, `session_id`, `item {id,type,content.html,choices[] {id,text}, media[]}`, `serve {seed, choice_order, watermark}`.
  - Excludes: any correctness flags or final keys.
- All LaTeX stored as JSON-escaped text (see `LaTeX_Escaping_Guide.md`).

### API surface (summary)
- `POST /api/session` → start or resume session; sets httpOnly cookie.
- `GET /api/item/next` → returns serve snapshot for next item.
- `POST /api/answer` → `{session_id,item_id,step_id?,choice_id?}` → `{correct, explanation_html?, next_step?}`.
  - Per-step “Check” (recommended). Optionally phase or end-of-item submit.

### Security and CSP
- Cookies: `httpOnly`, `Secure`, `SameSite=Lax`.
- CSRF token required on state-changing requests.
- Strict **CSP**: no inline scripts; whitelist own origins; sanitize any HTML.
- No secrets in FE. Avoid third-party scripts.

### Anti-scraping posture
- One-item endpoints only; no bulk lists.
- Per-serve randomization (numbers/labels/order).
- Short-lived signed media URLs; light per-user watermark in UI/SVG.
- Per-user rate limits + anomaly throttling; comprehensive logs.

### Hosting and environments
- Local: in-memory/SQLite; file-based media; same JSON contracts.
- Staging/Prod: Cloud Run + Cloud SQL + Storage + CDN; same images.

### Logging and metrics
- Correlate by `user_id`, `session_id`, `item_id`.
- Track `problem_served`, `answer_submitted`, accuracy by skill, time-to-answer.

### Troubleshooting quick notes
- If venv issues: re-activate with Out-Null (see checklist).
- If math renders wrong: verify JSON escape rules; see `LaTeX_Escaping_Guide.md`.

### Glossary
- **Serve snapshot**: client payload for rendering a single item instance.
- **Canonical problem**: full authoring truth stored server-side.
