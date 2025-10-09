# LaTeX Inline Escaping — Practical Guide (JSON → API → Browser)

This document captures only the **escape sequence issues** we discussed and the **fixes**. It assumes inline LaTeX delimiters `\( … \)` and display `\[ … \]` with **KaTeX** (or MathJax) on the client. See `docs/API_CONTRACT.md` for JSON payload examples.

---

## Core Rule (One Sentence)
**Author and store LaTeX as plain text, and let each layer’s serializer/renderer handle escaping.** Don’t hand‑build or double‑escape strings.

---

## 1) Authoring & Storage (JSON)
- **What to store in JSON:** use JSON‑compliant backslashes.
- **Correct JSON value example:**
```json
{
  "text": "Find \\( m \\) if \\( y = mx + b \\)."
}
```
- When your frontend parses this JSON, it becomes a normal JS string:
  - `Find \( m \) if \( y = mx + b \).`

**Avoid:** hand‑crafted JSON with inconsistent escaping, or mixing path backslashes into content.

---

## 2) Frontend (JavaScript/TypeScript)
- If you **hardcode** a LaTeX string in code, escape backslashes in **string literals**:
```js
const inline = "\\( a^2 + b^2 = c^2 \\)";
const display = "\\[ \\frac{y_2 - y_1}{x_2 - x_1} \\]";
```
- **Template literals** still need escaping:
```js
const inlineT = `\\( m = \\frac{\\Delta y}{\\Delta x} \\)`;
```
- **Best practice:** don’t hardcode; **read from parsed JSON** so you aren’t managing escapes in code.

**Renderer use:** pass the plain string to KaTeX (or your math component). No `eval`, no innerHTML of untrusted content.

---

## 3) Backend (Python) — if you must embed LaTeX in code
- Prefer to keep LaTeX **in data**, not code. If you must embed:
```py
# Normal string with escapes
s = "\\( a^2 + b^2 = c^2 \\)"

# Or raw string (cannot end with a single backslash)
s_raw = r"\( a^2 + b^2 = c^2 \)"
```
- When returning JSON from the API, let your framework’s **JSON serializer** produce the correct escapes automatically.

---

## 4) React Rendering Safety
- Render math from **text strings**; do **not** inject untrusted HTML.
- If you must use `dangerouslySetInnerHTML` (generally avoid), sanitize first.
- Keep a **Content Security Policy (CSP)** that disallows inline scripts.

---

## 5) Windows‑Specific Notes
- The old “Windows escape problems” come from **string literal** handling, not the renderer.
- **CRLF vs LF** line endings don’t affect KaTeX.
- **Backslashes in file paths** are irrelevant as long as you don’t mix them into LaTeX content.
- Always keep LaTeX content **separate from code paths** and let JSON/HTTP transport handle escaping.

---

## 6) End‑to‑End Safe Pattern (Recommended)
1. **Author** prose with delimiters and **store in JSON** using `\\(`…`\\)` and `\\[`…`\\]`.
2. **DB**: Postgres **JSONB** stores the same string (no manual munging).
3. **API**: return JSON via the framework serializer (don’t re‑escape).
4. **Frontend**: parse JSON → receive normal strings containing `\(` and `\[` → pass to KaTeX.
5. **Never** do search/replace hacks on backslashes; never double‑escape.

---

## 7) Quick Sanity Tests

**JSON round‑trip test**
```json
{"text":"Find \\( m \\) if \\( y = mx + b \\)."}
```
- After `JSON.parse(...)` in the browser → log it. You should see:
```
Find \( m \) if \( y = mx + b \).
```

**JS literal test**
```js
console.log("\\( a^2 + b^2 = c^2 \\)"); // should print: \( a^2 + b^2 = c^2 \)
```

**Python literal test**
```py
print("\\( a^2 + b^2 = c^2 \\)")  # prints: \( a^2 + b^2 = c^2 \)
print(r"\( a^2 + b^2 = c^2 \)")   # prints: \( a^2 + b^2 = c^2 \)
```

---

## 8) Common Pitfalls (and fixes)
- **Double‑escaping** (e.g., turning `\\(` into `\\\\(` accidentally) → **Fix:** only escape at the layer you’re in; let serializers handle it.
- **Hand‑built JSON strings in code** → **Fix:** use proper JSON libraries/serializers.
- **Injecting HTML** for math → **Fix:** render from text, or sanitize and constrain via CSP.

---

## TL;DR
- Store `\\( ... \\)` in JSON, **don’t** mutate it in transit, and render the resulting `\(`…`\)` with KaTeX in the browser.
