# Doc 2 — What you’ll need **shortly** (v1.5 → early v2)

> See `docs/SYSTEM_OVERVIEW.md` for canonical architecture/security; this doc lists near-term expansions.

## Product expansions
- **More content:** add 3–5 new SAT Math types; scale to 30–50 vetted instances each  
- **Difficulty refinement:** keep E/M/H; add hidden **1–10** scale mapped from it  
- **Practice affordances:** “Focus by skill,” “I’m done for now,” “See one easier like this”  
- **Explainability:** always show “why this item” (one-line reason)

## Platform/data expansions
- **JSON filtering at scale:** keep canonical problems in Postgres **JSONB**; add **GIN/path indexes** on hot attributes (skill, difficulty, has_diagram, etc.)  
- **Redis (optional):** add if selection reads get hot or for rate limiting/queues  
- **Analytics:** nightly export **facts** from Postgres → warehouse (BigQuery/Redshift/Snowflake)  
- **Event stream (optional):** add Kinesis/PubSub **only** if you need live dashboards or multiple consumers; otherwise keep Postgres events  
- **Reporting tables:** precompute daily summaries (sessions, accuracy by skill, time-to-answer)

## Anti-scraping posture (nice-to-add)
- **Behavioral bot signals** → progressive throttling/challenges on anomalies  
- **Anomaly alerts:** bursts (e.g., 300 items/10 min), multi-IP on one account  
- **Honey tokens/markers:** unique marker items served only to suspected scrapers  
- **Policy:** visible ToS + notice of watermarking and account termination for abuse

## Ops & quality
- **Content QA cadence:** weekly “staged → live” promotions; auto-flag top failing items  
- **Feature flags / A/B groundwork:** small cohorts for selection tweaks  
- **Security hardening:** CSP (no inline scripts), SVG served via signed URLs, sanitize anything user-generated (if introduced later), token hygiene (httpOnly cookies or short-lived JWTs with refresh)

## Extensibility hooks (don’t build fully yet)
- **Exam tags** on problems (SAT Math now; SAT Verbal/PSAT/ACT later)  
- **Theme packs** (labels now; toggles later)  
- **Teacher controls** (later): mastery threshold, skill playlists—same selection fields underneath

## “Ready for schools” track (later)
- **Privacy posture:** define PII retention, admin boundaries, region policy (FERPA/COPPA)  
- **Org/roles:** teacher ↔ student grouping; CSV roster upload before Classroom/LMS
