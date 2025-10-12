## System Components (categorized)

### Content Pipeline
- Content Authoring Pipeline: Produces author output JSON for each problem/variant.
- Ingestion Pipeline: Validates/enriches author output into canonical items stored in DB.

### Delivery Engine
- Selection Engine: Chooses the next item per user using skill/difficulty, playlists, and rules.
- Serve Pipeline: Derives safe serve snapshots (randomized choices, watermark, signed media).
- Grading & Feedback: Evaluates submissions against canonical data and returns explanations.
- Public API (FastAPI): Endpoints for session, next item, submit; secure, quiet defaults.
- Playlists & Sequences: Teacher/tutor-defined delivery order that guides item selection.

### Client Experience
- Frontend Web App (React+Vite): Renders serve snapshots, posts answers, KaTeX for math.
- Onboarding Flow: First-run guidance (verify email → tutorial/assessment → start practice).
- Profiles & Preferences: User settings (goal, accessibility, theme) editable in-app.
- Support & Feedback: In-app feedback and help surfaces for users and tutors.

### Identity & Accounts
- Identity & Auth: Signup/login, email verification, password reset; httpOnly sessions.
- User Directory (DB): Stores users, roles, minimal PII, and consent flags.
- Organizations & Roles: Teacher/tutor/student grouping and class/roster management.
- Payments & Subscription: Plans, billing, invoices; license seats for organizations.

### Media & Data Stores
- Canonical Item Store (Postgres JSONB): Source of truth for problems, steps, and metadata.
- Media Storage & Signing: Stores SVG/PNG and issues short‑lived signed URLs with alt/long_alt.

### Security, Compliance & Anti‑abuse
- Security & CSP: Strict CSP, CSRF on writes, cookie hygiene, minimal attack surface.
- Rate Limiting & Anomaly Detection: Throttle abuse and detect scraping patterns.
- Consent & Compliance: COPPA/FERPA tracking, data export/delete, region policies.
- Data Retention & Backups: Backup/restore and purge jobs aligned to policies.

### Ops, Analytics & Admin
- Observability (Logs/Metrics): Correlates by user/session/item with basic alerts and audits.
- Content QA Tooling: Review stats, flag bad items, promote variants staged → live.
- Feature Flags & Experiments: Toggle features and run A/B tests safely.
- Analytics & Warehouse Export: Nightly facts for BI (sessions, accuracy, time-to-answer).
- Admin Console: Manage content lifecycle and basic user/session lookups.

### Platform & Deployment
- Deployment & Infra (Cloud Run/SQL/Storage/CDN): Scalable hosting, managed DB, cached media.
- Automation: CI/CD, schema validation gates, and environment promotion flows.
