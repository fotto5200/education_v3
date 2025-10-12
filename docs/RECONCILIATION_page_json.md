## Reconciliation: partner `page.json` → Canonical & Serve

This document maps canonical fields (what we persist) to their sources in `page.json` or to responsibilities (Authoring vs. Ingestion). It also lists `page.json` fields that are unused as-is. Paths use dot-notation. Phase tags: [MVP] or [Later].

### Canonical → Source mapping

- id [MVP]
  - Source: none in page.json → Ingestion generates unique variant ID.

- template_id [MVP]
  - Source: none in page.json → Authoring provides (template grouping).

- content_version [MVP]
  - Source: `version` (page.json) → map directly.

- type [MVP]
  - Source: `type` (page.json).

- title [MVP]
  - Source: `title` (page.json).

- content.html [MVP]
  - Source: `question` (page.json) → use as HTML text (with LaTeX if needed); do not embed text in images.

- media[] [MVP]
  - object_key: Source: `svg` (inline) → Ingestion stores file in object storage and writes `object_key` (prefer Authoring to provide directly in future).
  - alt: Source: none → Authoring provides short description (1–2 sentences).
  - long_alt (optional): Source: none → Authoring provides extended description when needed [Later].

- steps[] [MVP]
  - step_id: Source: none → Ingestion assigns stable IDs.
  - prompt.html: Source: `stepQuestions[].question` (page.json).
  - choices[].text: Source: `stepQuestions[].answers[]` (strings) → map to `{text}`.
  - choices[].id: Source: none → Ingestion assigns stable IDs.
  - hint: Source: `stepQuestions[].hint` (page.json).
  - explanation.html (optional): Source: none → Authoring may provide [Later].

- final.answer_text [MVP]
  - Source: `answerText` (page.json).

- final.explanation.html (optional) [Later]
  - Source: none → Authoring may provide.

- tags.skill [MVP]
  - Source: none → Authoring provides.

- tags.difficulty [MVP]
  - Source: none → Authoring provides (E/M/H).

- generated_at [MVP]
  - Source: none → Ingestion timestamps on save.

- generator_version [MVP]
  - Source: optional from Authoring; otherwise Ingestion sets its own tool version.

- variant_index (optional) [Later]
  - Source: none → Ingestion sets if desired (human-friendly order).

- status / cluster (optional) [Later]
  - Source: none → Ingestion/operations as needed.

### Serve-only runtime (reference)
- session_id, serve.seed, serve.watermark, media[].signed_url, ttl_s, per-step serve.choice_order → Created by backend at serve time; not from `page.json`.

### Unused or transformed fields from page.json
- hasPicture: replaced by presence of `media[]` (not stored).
- svg (inline): not stored inline; transformed into `media[].object_key` (file path).
- answers (top-level): not used when `stepQuestions[]` is present; choices live per-step.
- All other fields are mapped above (type, title, version, question, answerText, stepQuestions[].question/answers/hint).
