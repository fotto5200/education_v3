## ADR 0001 — Canonical store: Postgres JSONB
**Date**: 2025-10-09
**Context**: Big-picture considered MongoDB; MVP requires transactional integrity and JSON query at scale.
**Decision**: Use Postgres with JSONB for canonical problems and serve snapshots.
**Consequences**: GIN/path indexes for hot attributes; easy warehousing; strong consistency.

## ADR 0002 — Session model: httpOnly cookie sessions
**Date**: 2025-10-09
**Decision**: Authenticate with server-managed sessions via httpOnly, Secure, SameSite=Lax cookies; CSRF on writes.
**Consequences**: Safer than SPA-local JWT; simpler rotation; FE uses `credentials: 'include'`.

## ADR 0003 — UI pattern: lightweight server-driven UI
**Date**: 2025-10-09
**Decision**: Backend returns a small JSON “serve snapshot”; FE maps JSON → components.
**Consequences**: Rapid restyle/A-B without FE redeploy; stable contracts via schemas.

## ADR 0004 — Hosting: Cloud Run + Cloud SQL + Storage + CDN
**Date**: 2025-10-09
**Decision**: Start with GCP Cloud Run (auto-scale); Cloud SQL Postgres; Cloud Storage for media; CDN fronting.
**Consequences**: Low ops, scale-ready; later optional Cloud Armor; alternative clouds remain possible.
