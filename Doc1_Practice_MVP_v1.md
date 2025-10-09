# Doc 1 — What to implement **now** (Practice MVP)

## Goal
Independent student signs up → gets **endless MCQ** practice for one SAT Math type (likely Parallel Lines) → difficulty adjusts sensibly → short progress summary. No tests, payments, or integrations.

## Core choices (locked for v1)
- **Audience:** Independent students  
- **Mode:** Practice (endless)  
- **Format:** MCQ  
- **Domain:** SAT Math (start with one problem type)  
- **Rendering policy:**  
  - Prose as **HTML**  
  - **Inline math** rendered client-side with **KaTeX** (`\( … \)` / `\[ … \]`)  
  - Diagrams/charts as **SVG** files from backend (signed URLs)
- **Stack:** React + Vite + Tailwind + Radix (headless) + KaTeX (front end), FastAPI (back end)  
- **Server-driven UI:** Backend returns a small JSON serve snapshot; FE maps JSON → components (rapid restyle, no redeploy).  
- **Data stores:** **Postgres** (system-of-record, JSONB for problems & snapshots), **Object storage** for SVG/media  
- **Containers/Hosting:** Docker images on **Cloud Run** (or Fargate as alternative)  
- **Auth:** httpOnly cookie sessions (optionally backed by Firebase Auth); email+password

## Content (pilot)
- One problem type (e.g., Parallel Lines)  
- **10 vetted instances** (3 easy, 4 medium, 3 hard)  
- Each instance: prompt, choices, correct key, **one-sentence rationale**, skill tag, difficulty

## Selection rules (simple, explainable)
- Miss last item in a skill → step **down** in difficulty  
- Get **two correct in a row** → repeat once at same difficulty, then **consider step up**  
- Insert **spiral review** every 4–6 items  
- **No near-duplicates** in the same session

## Data you capture (Postgres, high level)
- **Users** (minimal PII)  
- **Problems (canonical):** JSONB per instance + columns for skill/difficulty/status  
- **Served items (audit):** **snapshot** JSON of the exact served payload (incl. choice order)  
- **Progress per skill:** attempts, streaks, last difficulty, mastery band (Low/Med/High)  
- **Events (append table):** problem_served, answer_submitted, session_started/ended

## Anti-scraping posture (must-do in v1)
- **Login required**; **rate limits** per user (per minute/hour/day)  
- **Per-serve randomization** (numbers/order/labels) to reduce reuse value  
- **Short-lived signed URLs** for SVG/media  
- **Light watermark** (user+time hash) in footer and/or SVG metadata  
- **No bulk/list endpoints**; one problem per request  
- **Comprehensive serve logs** (user/session/instance/timestamp)

## Provisioning run sheet (high level)
1. Pick cloud (**GCP Cloud Run** recommended), single **US region**  
2. Managed **Postgres** (PITR + daily backups)  
3. Session auth (httpOnly cookies; optional Firebase Auth backing)  
4. **Object storage** bucket for SVG/media (versioning optional)  
5. Deploy **API container** (FastAPI) and **Front-end** (static hosting/CDN)  
6. **Secrets manager** for DB/Auth creds  
7. **Domain + TLS** (managed cert)  
8. **Logging/metrics:** searchable by user_id/session_id; basic alerts (error rate, DB CPU/storage)

## Acceptance (definition of done)
- New user completes 10 items and sees a **clear summary** (attempts, accuracy, suggested focus)  
- Difficulty shifts feel sane; **no in-session duplicates**  
- Closing/reopening resumes appropriately (persisted state)  
- Logs show problem_served / answer_submitted with timestamps
