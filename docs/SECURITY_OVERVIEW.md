## Security Overview (plain language)

### Goals
- Protect people’s data and privacy.
- Make it hard to copy content and answers in bulk.
- Keep the service reliable in the face of mistakes or abuse.
- Keep secrets off user devices and leave a clear audit trail.

### What we do and the tech behind it

- Secure session cookie (server-managed login)
  - After you log in, your browser stores a special cookie that the page’s JavaScript cannot read (an “httpOnly” cookie). The browser sends it automatically with each request, and the server checks it. This reduces the chance of someone stealing your login inside the page.
  - Tech: httpOnly, Secure, SameSite cookies managed by our server.

- Write protection with a one‑time token
  - For important actions (like submitting an answer), the page must include a short‑lived token that came from the server. This helps prevent tricks where a hidden button on another site causes you to act without knowing.
  - Tech: CSRF tokens included in requests that change data.

- Strict browser rules to prevent risky behavior
  - We tell the browser not to run inline scripts or load unknown sources by default. This makes it harder for attackers to inject malicious code into pages.
  - Tech: a Content Security Policy (CSP) header that whitelists what the page can load and execute.

- Clean handling of anything users can type or upload
  - We treat all user inputs as untrusted and clean them before using or showing them. We avoid injecting raw HTML into the page.
  - Tech: server-side validation and sanitization; frontend avoids dangerous APIs.

- Limits and anomaly checks
  - If a user or script hits the system too fast or in unusual patterns, we slow them down or block them. We also alert on suspicious bursts.
  - Tech: rate limiting middleware and anomaly detection rules.

- Short‑lived links for images and diagrams
  - We store diagrams (SVG/PNG) in secure storage and hand out links that expire quickly. We can also add a subtle per‑user mark to trace bulk copying.
  - Tech: signed URLs with a short “time to live” and optional watermarking in the image/SVG metadata.

- No secrets in the web app
  - Keys and passwords stay on the server. The browser only gets the minimum data needed to display a page.
  - Tech: secrets in managed server config; the client uses standard API calls with the session cookie.

- Logging and audits
  - We record who saw what and when. This helps investigate issues and improve reliability.
  - Tech: structured logs keyed by user/session/item, with basic dashboards and alerts.

- Backups and data rules
  - We take regular backups and can restore them. We follow clear rules for how long to keep data and how to delete it if asked.
  - Tech: scheduled database backups, storage versioning, documented retention policies.

### Strengths
- Session cookies are harder to steal through page scripts.
- Short‑lived media links and watermarking reduce the value of bulk copying.
- Strict browser rules and cleaned inputs block many common attacks.
- The server never sends correct answers before a submit, so “view source” won’t reveal them.
- Logs and limits help detect and stop abuse early.

### Limitations
- A determined person can still take screenshots or copy by hand.
- Short‑lived links still work until they expire.
- Strict browser rules can limit third‑party widgets unless we explicitly allow them.
- Aggressive limits can annoy power users if tuned too tightly.
- If a user’s device is already compromised, any site is at risk.
