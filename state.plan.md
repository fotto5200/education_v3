# Plan Persistence and Handoff Protocol

### Goals

- Ensure no planning info is lost between chats/sessions.
- Maintain a single source of truth with lightweight redundancy.
- Keep updates quiet, structured, and versioned in-repo.

### Onboarding Hook (hard gate)

- Trigger: When the restart prompt “Please read the PROJECT_ONBOARDING_CHECKLIST.md file and follow the steps to get oriented on this project.” is detected.
- Actions (before any work):
  1) Load `\state.plan.md` and `docs/CURRENT_STATUS.md`.
  2) Print a Start Gate line: last‑updated timestamp, active next target, and 1–3 next actions from this plan.
  3) If `\state.plan.md` is missing/incomplete, stop and output ready‑to‑paste edits to reconstruct it from `docs/CURRENT_STATUS.md` and `CHANGES_BACKLOG.md`.

### External Terminal Enforcement

- Never run PowerShell/CMD inside Cursor.
- Ask mode: provide diffs; remind to run commands externally.
- Agent mode: propose commands, explicitly noting they must be run outside Cursor.

### Single Source of Truth

- Canonical plan file: `\state.plan.md` (authoritative, always current).
- Ephemeral notes: `@local.plan.md` (browser) are scratch; reconcile into `\state.plan.md` before session end if deltas exist.

### Supporting Docs (when applicable)

- Current status and next targets: `docs/CURRENT_STATUS.md` (brief, dated).
- Backlog/ideas not yet planned: `CHANGES_BACKLOG.md`.
- Architecture decisions: `ARCHITECTURE_DECISIONS.md` (true ADRs only).
- Session log (optional for major shifts): `docs/SESSION_LOG.md` (dated entries, link to plan commit).
- Milestone snapshots: `docs/PLAN_HISTORY/` (dated files).

### Architecture Overview

- Client Experience (Frontend)
  - React + Vite + Tailwind + KaTeX; renders server‑driven serve snapshots.
  - Key: `frontend/`, `docs/SERVED_ITEM_SPEC.md`, `docs/SERVE_PIPELINE.md`.

- Delivery Engine (Backend)
  - FastAPI endpoints: `POST /api/session`, `GET /api/item/next`, `POST /api/answer`; selection; grading; rate limits.
  - Selection: session‑scoped rotation with no immediate repeats; type‑aware by last served type (optional `?type` override); dev/testing `policy=simple` rotates to the next available type after N serves (`POLICY_N`, default 3).
  - Dev persistence & logs: when `DEV_PERSIST_SELECTION=1`, selection state is saved to `dev_state/selection_state.json` and events are appended to `dev_state/events.ndjson` (gitignored).
  - Key: `backend/app/main.py`, `backend/app/routes/*.py`, `backend/app/util.py`, `backend/app/store.py`, `docs/WORKFLOWS.md`.

- Content Pipeline
  - Authoring → Ingestion → Canonical store; strict JSON Schemas.
  - Key: `docs/CONTENT_AUTHORING_SPEC.md`, `docs/INGESTION_PIPELINE.md`, `schemas/`.

- Media & Data Stores
  - Canonical problems in Postgres JSONB; media in object storage with short‑lived signed URLs (CDN fronted).
  - Key: `ARCHITECTURE_DECISIONS.md`, `docs/SYSTEM_OVERVIEW.md`.

- Identity & Accounts
  - httpOnly cookie sessions; CSRF on writes; roles/orgs later.
  - Key: `docs/SECURITY_POLICY.md`, `docs/SYSTEM_COMPONENTS.md`.

- Security & Policy
  - Strict CSP, sanitization; anti‑scraping (randomization, watermarking); per‑user rate limits.
  - Key: `docs/SECURITY_POLICY.md`, `docs/SECURITY_OVERVIEW.md`.

- Analytics & Ops
  - Logs/metrics keyed by user/session/item; nightly exports/reporting later; feature flags later.
  - Key: `docs/WORKFLOWS.md`, `docs/SYSTEM_COMPONENTS.md`.

- Platform & Deployment
  - Cloud Run + Cloud SQL + Storage + CDN per ADR; CI/CD later.
  - Key: `ARCHITECTURE_DECISIONS.md`.

- Current Local MVP Note
  - Dev uses `data/canonical/*.json` and `media/` with in‑memory selection and stub `ttl_s` for media.

### Program Roadmap (big-picture phases)

- Phase 1 — Local MVP hardening (dev only)
  - Deliverables: stateful selection (round‑robin + simple skill filters), enforced CSRF on submit, basic rate limits, multi‑step render/advance, item‑level media render, quiet startup.
  - Data: consume provided canonical JSONs from `data/canonical/` (no generation planned).

- Phase 2 — Persistence and selection state
  - Deliverables: Postgres JSONB for canonical and serve snapshots; session‑scoped selection pointers/history persisted; simple migrations and seeds.
  - Security: keep CSRF/session model; no secrets in FE.

- Phase 3 — Media signing and CDN
  - Deliverables: object storage bucket, short‑lived signed URLs, CDN in front; update CSP for media origin; keep local static for dev.

- Phase 4 — Identity & accounts (basic)
  - Deliverables: signup/login, password reset, minimal roles; keep httpOnly sessions; FE uses `credentials: 'include'`.

- Phase 5 — Analytics & observability
  - Deliverables: structured logs keyed by user/session/item; basic metrics; nightly export of facts to warehouse later; minimal dashboards/alerts.

- Phase 6 — Security & anti‑abuse posture
  - Deliverables: tuned rate limits, anomaly throttling hooks, watermarking policy, CSP tighten, HTML sanitization where applicable.

- Phase 7 — Frontend UX and accessibility
  - Deliverables: server‑driven UI refinements, alt/long_alt exposure pattern, theme tokens; cooldown UI for 429 already present.

- Phase 8 — Platform & deployment
  - Deliverables: containerize FE/BE; Cloud Run + Cloud SQL + Storage + CDN; secrets management; CI/CD pipeline.

- Phase 9 — Admin/QA & content lifecycle
  - Deliverables: lightweight content QA surface, flags/promotions (staged → live); teacher/tutor playlist hooks later.

- Phase 10 — v1.5 → v2 expansions (see Doc2)
  - Deliverables: more skills/content (arrive externally), hidden 1–10 difficulty scale mapped from E/M/H, explainability (“why this item”), reporting tables, feature flags, privacy & org/roles groundwork.

- Out of scope
  - Content generation: assume canonical problem JSONs are authored by colleagues and appear in storage/DB; we only ingest/serve them.

### Required Sections in `\state.plan.md`

- Title; Context; Scope; Files to change; Design; Verification; Risks/Limits; Todos (checkboxes); Last updated (timestamp).

### Process

- Start‑of‑session (via Onboarding Hook)
  - Load `\state.plan.md` and `docs/CURRENT_STATUS.md`.
  - Present Start Gate summary (active next target + next actions).
- During‑session (living updates)
  - When decisions change scope/design, immediately update `\state.plan.md` and (if relevant) ADR/backlog.
- End‑of‑session Save Protocol (must complete in order)
  1) Update `\state.plan.md` with all decisions/todos and a “Next actions” block; update timestamp.
  2) Update `docs/CURRENT_STATUS.md` (date + concise “What changed” + “Next targets”).
  3) Append any non‑committed ideas to `CHANGES_BACKLOG.md`.
  4) If major shifts, add an entry to `docs/SESSION_LOG.md` with links to the plan commit.
  5) Commit via external terminal using `git_update.bat` (quiet, timestamped).

### Redundancy

- For major milestones, snapshot `\state.plan.md` to `docs/PLAN_HISTORY/YYYY‑MM‑DD.md`.
- Keep `@local.plan.md` minimal; treat as scratch only after syncing to `\state.plan.md`.

### Verification

- At session close, repo is clean (`git status`) with updated files above.
- `\state.plan.md` top section lists the exact next actionable tasks.

### Communication Commitments

- Start Gate: “Loaded plan (Last updated: …). Active next target: …. Next actions: …”.
- End Gate: “Save Protocol completed” (or “blocked; diffs provided”) + next actions.

### To-dos

- [x] Create selection.py with session queues and recent history
- [x] Use selector in item.next; wire session_id and watermark
- [x] Type-aware selection by last served type with optional `?type` override
- [x] Simple policy-driven type rotation (dev/testing; `policy=simple`, N via `POLICY_N`)
- [x] Dev-only persistence of selection state and append-only dev events (`DEV_PERSIST_SELECTION=1`)
- [x] Manual curl/FE tests; update CURRENT_STATUS usage notes

### Active Next Target

- Define server-side policy engine interface (no-op stub) that accepts a session/performance summary and returns desired next `item.type`; default continues same-type until a real policy is enabled
