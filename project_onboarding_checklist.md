## Generic Project Onboarding Checklist (Windows-first, quiet startup)

### Decisions to date (read first)
- See `docs/DOCS_INDEX.md` for the full map of specs, pipelines, and schemas.
- System overview: `docs/SYSTEM_OVERVIEW.md`; decisions: `ARCHITECTURE_DECISIONS.md`.
- Contracts: `docs/API_CONTRACT.md` and `schemas/` (`item_author_input_v1.json`, `item_canonical_v1.json`, `item_serve_v1.json`, `submit_*_v1.json`).
- Security: `docs/SECURITY_POLICY.md` (policy) and `docs/SECURITY_OVERVIEW.md` (plain-language).
- Served flow: `docs/SERVED_ITEM_SPEC.md` and `docs/SERVE_PIPELINE.md`.
- Authoring: `docs/CONTENT_AUTHORING_SPEC.md` and `schemas/item_author_input_v1.json`.
- Ingestion: `docs/INGESTION_PIPELINE.md`.
- Reconciliation: `docs/RECONCILIATION_page_json.md`.
- Workflows/components: `docs/WORKFLOWS.md`, `docs/SYSTEM_COMPONENTS.md`.

### Purpose
- **Capture reusable development know-how** for new repos: quiet startup, external terminal usage, one-command flows, env/key management, CLI UX, docs policy, troubleshooting.
- Designed for Windows 11 + VSCode/Cursor, with optional Mac/Linux notes.

---

### Critical startup policy (quiet by default)
- **Startup should be quiet**: no banners or verbose logs; print a single actionable line on completion.
- Provide `--verbose` to expand logs, and `--quiet` to suppress progress lines; default to minimal output.
- Prefer non-interactive commands to avoid hangs in integrated terminals.

---

### External terminal guidance
- Use an **external CMD/PowerShell** for environment variables and running scripts; IDE terminals can drop env vars.
- Keep secrets out of IDE logs; avoid echoing full keys.

---

### Plan audit hook (restart gate)
- On startup, before any work:
  - Load `\\state.plan.md` and `docs/CURRENT_STATUS.md`.
  - Print: last-updated timestamp, active next target, and 1–3 next actions from `\\state.plan.md`.
  - If `\\state.plan.md` is missing/incomplete, STOP and output ready-to-paste fixes before proceeding.

### Save Protocol reminder (session close)
- Update `\\state.plan.md` (decisions, todos, next actions, timestamp).
- Update `docs/CURRENT_STATUS.md` and `CHANGES_BACKLOG.md` (and `docs/SESSION_LOG.md` if major).
- Commit via external terminal using `git_update.bat`.

---

### Dev persistence (optional)
- Toggle: set `DEV_PERSIST_SELECTION=1` in your external terminal session.
- Files (auto-created, gitignored):
  - `dev_state/selection_state.json` — per-session selection state (last_type, active_type, recent_ids, counters)
  - `dev_state/events.ndjson` — append-only dev events: served/answered
- Notes:
  - Anonymous sessions are not persisted.
  - For testing only; production will use DB-backed persistence and a policy engine.

---

### Quick venv setup (PowerShell, non-interactive)
```powershell
if (!(Test-Path venv)) { python -m venv venv }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& "venv\Scripts\Activate.ps1" | Out-Null
python -m pip install --upgrade pip
if (Test-Path requirements.txt) { pip install -r requirements.txt }
python -V
pip -V
python -c "import sys; print(sys.executable)"
```

Notes:
- Use `| Out-Null` to prevent activation noise.
- Prefer relative paths so scripts are portable across machines.

---

### Environment variables (multi-project)
- Set user-scope env vars (persist between sessions):
```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
[Environment]::SetEnvironmentVariable("PROJECT_OPENAI_KEY", "sk-...", "User")
```
- Verify:
```powershell
[Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
```
- Load into current session without restart:
```powershell
$env:OPENAI_API_KEY = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
```
- VSCode/Cursor: point Python to `.env` via `.vscode/settings.json` → `python.envFile`.

Security:
- Never commit keys. Mask when printing. Rotate and monitor usage.

---

### Standard git update workflow (one command)
- Preferred procedure:
```cmd
git_update.bat
```
- What it does: `git status` → `git add .` → `git commit -m "Update: <timestamp>"` → `git push origin <branch>` with clear success/error messages.
- Provide a PowerShell fallback (`git_update.ps1`) if desired.
- Keep branch configurable; document how to change it.

Template (`git_update.bat`):
```bat
@echo off
echo === Git Update ===
git status --porcelain || exit /b 1
git add . || exit /b 1
for /f "tokens=2 delims==" %%a in ('wmic OS get localdatetime /value') do set dt=%%a
set ts=%dt:~0,4%-%dt:~4,2%-%dt:~6,2% %dt:~8,2%:%dt:~10,2%
git commit -m "Update: %ts%" || exit /b 1
git push origin main || exit /b 1
echo Done.
```

---


**FILES TO READ SILENTLY**:
- Big picture stuff about creating a full education system.docx
- Doc1_Practice_MVP_v1.md
- Doc2_Soon_v1_5_to_v2.md

### CLI UX contract (single-command + numbered quick actions)
- Provide a **single end-to-end command** that halts with one actionable one-liner:
  - Exit 0: `Done: {input}`
  - Exit 2: `You have to {ACTION} for {input} in stage {stage}\nPath: {suggested_path}`
  - Exit 1: `You have to fix error for {input} in stage {stage} ({brief})`
- Print minimal progress only when useful; default to quiet.
- Support numbered quick actions (ephemeral):
  - Display a numbered list of suggested commands.
  - Allow invoking by number (e.g., `tool 4`), `?` to reprint, `!!` to repeat.
  - Validate action-map hash to avoid mismatches; reprint if changed.

---

### File processing pattern (prevent reprocessing)
- Separate directories for active vs processed for both inputs and intermediates.
- Move successfully processed items out of active dirs; retain processed for audit/recovery.
- Status command should report active/processed counts.

---

### Examples policy (stage-specific)
- Per leaf/mid policy: `off | auto | required`.
- If examples are missing under `auto`, run base-only, emit a machine-readable TODO and a suggested path, then allow replay once authored.
- Keep examples in predictable hierarchical paths; maintain a "missing examples" index and a concise rollup.

---

### JSON/schema discipline
- Enforce a **strict core schema** with explicit field names for stability.
- Add **pass-through** for unknown fields; provide graceful defaults for non-critical omissions.
- **Fail fast** on critical errors; continue with logging otherwise.

---

### Documentation policy (portable)
- Files: `CURRENT_STATUS.md`, `ARCHITECTURE_DECISIONS.md`, troubleshooting, changelog, step/component guides.
- Formatting: Markdown only; TOC for long docs; language-tagged code blocks; explicit file paths; timestamps for time-sensitive info.
- Update triggers: new/changed features, bugs fixed, workflow or dependency changes, test results.
- Ownership & review cadence: weekly status sweep, monthly troubleshooting pass, quarterly doc audit.
- Commit discipline: include doc edits with code; allow `[docs]`-only commits.

---

### Troubleshooting (quick fixes)
- Hangs in integrated terminal → use non-interactive patterns or external terminal.
- Venv not active → run activation with `| Out-Null`.
- Missing env vars → set user-scope keys; reload into session.
- Missing packages → `pip install -r requirements.txt` (confirm interpreter path).
- UTF-8 issues → read/write JSON with UTF-8; set `Content-Type: application/json; charset=utf-8` in servers.

---

### Health checks / daily ops
- Status script prints minimal one-liners and counts (quiet by default).
- Lightweight AI/provider connectivity sanity check before first run.
- Optional scheduled script to report recent errors and directory sizes.

---

### Portability & safety
- Favor relative paths in scripts; avoid user-specific absolute paths.
- Keep Windows-first commands with optional Mac/Linux notes.
- Don’t echo secrets; mask if displayed.

---

### Templates
- ADR skeleton:
```markdown
**Date**: YYYY-MM-DD
**Context**: ...
**Alternatives**: ...
**Decision**: ...
**Consequences**: Pros/Cons
**Status**: Proposed | Implemented | Deprecated
```

- Example authoring notes:
```markdown
**Rationale**: Why this example helps
**I/O pairs**: 1–2 concise, high-quality examples
**Common mistakes**: Brief bullets
**Alignment**: Fields required by the stage’s JSON contract
```

---

### Quick start (copy/paste)
```powershell
# 1) Create/activate venv quietly
if (!(Test-Path venv)) { python -m venv venv }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& "venv\Scripts\Activate.ps1" | Out-Null

# 2) Install deps
if (Test-Path requirements.txt) { pip install -r requirements.txt }

# 3) Run the one-command flow (example)
run.bat <input>

# Contract: prints exactly one actionable line at the end
# Exit codes: 0=done, 2=need, 1=error
```

---

### Python execution note (Windows)
- Always run Python from an external terminal (PowerShell/CMD), not the IDE-integrated terminal.
- Do not execute Python inside Cursor sessions; scripts like `tools/generate_canonical_seed.py` must be run externally.
- Keep scripts quiet and non-interactive; provide `--help` and env-driven options.

---

### Frontend/backend hygiene (if applicable)
- Ensure servers use UTF-8; test key endpoints locally.
- Keep backend startup quiet; log only a single readiness line.
- Confirm mock/sample data loads end-to-end.

---

### Final reminders
- Prefer external terminal for scripts and env changes.
- Keep startup quiet and outputs actionable.
- Use one-command workflows and numbered quick actions.
- Update docs with each meaningful change.


