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
