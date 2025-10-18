## API Contract

This document shows canonical examples and links to JSON Schemas in `schemas/`.

See also: `LaTeX_Escaping_Guide.md` for escaping rules.

### Serve snapshot (GET /api/item/next)
```json
{
  "version": "1.0",
  "session_id": "s_123",
  "item": {
    "id": "i_456",
    "type": "mcq",
    "content": { "html": "Evaluate \\( y = 2x^2 + 3x - 5 \\) at \\( x = 2 \\)." },
    "media": [
      { "id": "fig1", "signed_url": "https://cdn.example/abc", "ttl_s": 120, "alt": "Quadratic diagram" }
    ]
  },
  "choices": [
    { "id": "A", "text": "9" },
    { "id": "B", "text": "11" },
    { "id": "C", "text": "13" }
  ],
  "serve": { "seed": "r8xz", "choice_order": ["B","C","A"], "watermark": "u_abc_2025-10-09" },
  "ui": { "layout": "question-above-choices", "actions": ["submit"] }
}
```

Schema: `schemas/item_serve_v1.json`

#### Query parameters (MVP)
- `type` (optional): when provided, the server scopes selection to items whose `item.type` matches the given value (case-insensitive). Without this parameter, selection defaults to the same type as the last item served in the session.
- `policy` (optional, dev/testing): when set to `simple`, the server rotates to the next available `item.type` after N serves (default N=3, configurable via env `POLICY_N`). Ignored if `type` is provided.

Examples:
- `GET /api/item/next` → next item of the same type as last served (session-scoped)
- `GET /api/item/next?type=PARALLEL_LINE_FIND_X` → next item of that type

Notes:
- `skill` is NOT used for next-item selection in the MVP; it is reserved for future remedial focus flows.
- `policy=simple` is for development/testing only; production policy selection will be governed by a server-side policy engine.

### Submit step (POST /api/answer)
Request:
```json
{ "session_id": "s_123", "item_id": "i_456", "step_id": "step_1", "choice_id": "B" }
```

Response:
```json
{ "correct": true, "explanation": { "html": "Correct: 8 + 6 - 5 = 9." }, "next_step": { "id": "step_2" } }
```

Schemas: `schemas/submit_step_v1.json`, `schemas/submit_result_v1.json`

### Notes
- Never include correctness flags in the serve snapshot.
- All LaTeX in JSON must use escaped delimiters (e.g., `\\( ... \\)`).
- The client must pass credentials (cookies) and CSRF token on writes.
