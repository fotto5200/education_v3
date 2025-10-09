## Security Policy

### Sessions & auth
- httpOnly, Secure, SameSite=Lax cookies for session.
- CSRF token required on state-changing requests.
- No tokens in localStorage; no secrets in FE.

### CSP & sanitization
- Strict CSP: disallow inline scripts; allow self origins only; pin to known CDNs if used.
- Sanitize any HTML if ever injected; prefer rendering from plain text.

### Anti-scraping posture
- One-item endpoints; no bulk fetch.
- Per-serve randomization (numbers/order/labels).
- Short-lived signed media URLs; subtle per-user watermark in UI/SVG.
- Per-user rate limits; anomaly throttling; comprehensive logs for audit.

### Data handling
- Canonical truth lives server-side in Postgres JSONB; client receives safe snapshots.
- Logs keyed by `user_id`, `session_id`, `item_id`.
