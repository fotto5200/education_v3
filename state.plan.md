# Plan Persistence and Handoff Protocol

### Goals

- Ensure no planning info is lost between chats/sessions.
- Maintain a single source of truth with lightweight redundancy.
- Keep updates quiet, structured, and versioned in-repo.

### Onboarding Hook (hard gate)

- Trigger: When the restart prompt “Please read the PROJECT_ONBOARDING_CHECKLIST.md file and follow the steps to get oriented on this project.” is detected.
- Actions (before any work):
  1) Load `\state.plan.md` and `docs/CURRENT_STATUS.md`.
  2) Print a Start Gate line: last‑updated timestamp, active next target, and 1–3 next actions from this plan.
  3) If `\state.plan.md` is missing/incomplete, stop and output ready‑to‑paste edits to reconstruct it from `docs/CURRENT_STATUS.md` and `CHANGES_BACKLOG.md`.

### External Terminal Enforcement

- Never run PowerShell/CMD inside Cursor.
- Ask mode: provide diffs; remind to run commands externally.
- Agent mode: propose commands, explicitly noting they must be run outside Cursor.

### Single Source of Truth

- Canonical plan file: `\state.plan.md` (authoritative, always current).
- Ephemeral notes: `@local.plan.md` (browser) are scratch; reconcile into `\state.plan.md` before session end if deltas exist.

### Supporting Docs (when applicable)

- Current status and next targets: `docs/CURRENT_STATUS.md` (brief, dated).
- Backlog/ideas not yet planned: `CHANGES_BACKLOG.md`.
- Architecture decisions: `ARCHITECTURE_DECISIONS.md` (true ADRs only).
- Session log (optional for major shifts): `docs/SESSION_LOG.md` (dated entries, link to plan commit).
- Milestone snapshots: `docs/PLAN_HISTORY/` (dated files).

### Required Sections in `\\state.plan.md`

- Title; Context; Scope; Files to change; Design; Verification; Risks/Limits; Todos (checkboxes); Last updated (timestamp).

### Process

- Start‑of‑session (via Onboarding Hook)
  - Load `\state.plan.md` and `docs/CURRENT_STATUS.md`.
  - Present Start Gate summary (active next target + next actions).
- During‑session (living updates)
  - When decisions change scope/design, immediately update `\state.plan.md` and (if relevant) ADR/backlog.
- End‑of‑session Save Protocol (must complete in order)
  1) Update `\state.plan.md` with all decisions/todos and a “Next actions” block; update timestamp.
  2) Update `docs/CURRENT_STATUS.md` (date + concise “What changed” + “Next targets”).
  3) Append any non‑committed ideas to `CHANGES_BACKLOG.md`.
  4) If major shifts, add an entry to `docs/SESSION_LOG.md` with links to the plan commit.
  5) Commit via external terminal using `git_update.bat` (quiet, timestamped).

### Redundancy

- For major milestones, snapshot `\state.plan.md` to `docs/PLAN_HISTORY/YYYY‑MM‑DD.md`.
- Keep `@local.plan.md` minimal; treat as scratch only after syncing to `\state.plan.md`.

### Verification

- At session close, repo is clean (`git status`) with updated files above.
- `\state.plan.md` top section lists the exact next actionable tasks.

### Communication Commitments

- Start Gate: “Loaded plan (Last updated: …). Active next target: …. Next actions: …”.
- End Gate: “Save Protocol completed” (or “blocked; diffs provided”) + next actions.

### To-dos

- [ ] Index canonical items by id in store.py; add get_canonical_by_id
- [ ] Create selection.py with session queues and recent history
- [ ] Use selector in item.next; wire session_id and watermark
- [ ] Parse skill query param; rebuild queue when filter changes
- [ ] Manual curl/FE tests; update CURRENT_STATUS usage notes
