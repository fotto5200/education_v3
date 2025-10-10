## Ingestion Pipeline (Author → Canonical)

### Inputs
- Author output JSON (schema: `schemas/item_author_input_v1.json`).

### Outputs
- Canonical item JSON persisted to DB (schema: `schemas/item_canonical_v1.json`).

### Responsibilities
- Generate/assign fields the author cannot or should not provide:
  - `id` (unique variant ID)
  - `variant_index?`
  - `generated_at` (timestamp)
  - `generator_version` (fallback if missing)
  - `content_version` (fallback/increment if missing)
  - Optional: `status`, `cluster`, `checksum`
- Validate/normalize author fields:
  - IDs present and stable (`step_id`, `choices[].id`)
  - 4 choices per step (unless yes/no)
  - `media[].object_key` exists; `alt` present; `long_alt` optional
  - LaTeX properly JSON-escaped
- Persist canonical as-is after augmentation; index key columns (e.g., `template_id`, `skill`, `difficulty`).

### Example transform
- Input (author): `template_id`, `type`, `title`, `content`, `media`, `steps`, `final`, `tags` (+ optional versions)  
- Output (canonical): same fields plus system-added `id`, `generated_at`, `content_version` (if missing), etc.

### Notes
- Authors can emit multiple variants per template; the pipeline assigns unique `id` for each.
- Bad variants can be deprecated via `status` without deleting the template.
