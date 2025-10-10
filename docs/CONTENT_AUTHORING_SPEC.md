## Content Authoring Specification

### Audience
Content authors/generators. Defines the canonical (server-only) fields you must produce.

### Author output contract
- Schema: `schemas/item_author_input_v1.json` (this is exactly what your Python should emit).
- Examples: see `docs/examples/author_input_example.json` (to be used as a template).
- Our ingestion pipeline augments this into the canonical DB shape (`schemas/item_canonical_v1.json`).

### Required fields (MVP)
- Identity: `item.id` (unique per variant), `template_id` (group of variants), `content_version` (integer).
- Basics (always present): `type`, `title`, `content.html` (the main prompt as HTML + LaTeX, see LaTeX guide).
- Media: `media[] { id, object_key, alt }` (no inline SVG; store files in object storage). See "Media handling" below.
- Steps: `steps[]` (for multi-step) with:
  - `step_id`
  - `prompt.html`
  - `choices[] { id, text }` (exact 4 for SAT-style; yes/no allowed)
  - `hint?` (optional)
- Final: `final { answer_text, explanation.html }` (server-only; not sent pre-submit).
- Provenance: `generated_at`, `generator_version`.
- Tags/meta: `skill`, `difficulty`.

### Optional fields (Later)
- `choices[].tag` (distractor type), `rationale?` (authoring note)
- `variant_index` (human-friendly order), `cluster`, `status`
- `media[].long_alt` (extended description for complex diagrams)

### Media handling (authoring)
- Store diagrams as files (prefer SVG; PNG fallback) in object storage.
- Provide for each media item:
  - `object_key`: path/key in the storage bucket (e.g., `items/i_456/fig1.svg`).
  - `alt`: concise text alternative (1–2 short sentences) describing the essential information.
  - `long_alt` (optional): extended description if the diagram conveys complex relationships that are not otherwise described in `content.html` or step prompts.
- Do not embed instructional text inside the image when it belongs in the prompt; write it in `content.html` / `prompt.html` so it’s readable by assistive tech.

### Authoring rules
- LaTeX must be JSON-escaped in content fields.
- Use plain HTML text for prompts; reserve images for diagrams via `media.object_key`.
- Provide meaningful `alt` for every media item; add `long_alt` when needed for accessibility.
- Keep hints concise; explanations can be richer but remain server-only pre-submit.

### Validation checklist
- 4 choices per step (unless yes/no).
- No correctness flags in any authoring field sent to clients.
- All IDs (`item.id`, `step_id`, `choices[].id`) are stable strings.
- Every `media` object includes `alt`; include `long_alt` for complex figures.

### Reconciliation appendix
See `docs/RECONCILIATION_page_json.md` for mapping from the partner’s `page.json` fields to these canonical fields and serve payload.
