---
id: skf-runbook-closure
title: "Closure Phase Runbook"
phase: closure
version: 1.0
steps: 7
---

# Runbook: Closure Phase

**Phase 4** | Steps 1–7 | Orchestrator: skf-general-orchestrator

Runs **unconditionally** — even after partial completion, cancellation, or failure. Verifies completion state, runs final QA, updates docs, captures lessons, produces summary.

> **Shared protocols**: See `runbook-shared.md` for Dispatch Contract, Escalation Policy, and Bounded Retry Policy.

> **DELEGATE-OR-STOP**: Before every tool call, verify against the DELEGATE-OR-STOP protocol. Only `runSubagent`, `vscode/askQuestions`, `todo`, `web`, and allowlisted `read_file` are permitted.

---

## Step 1 — Confirm Completion

**Fully complete**: all waves `ok`, all planned artifacts exist, no open escalations.

**Partially complete** (cancel, error, wave failure):
- Inventory which waves completed vs. not
- List outstanding unexecuted tasks
- Note files in intermediate state
- Proceed through closure with partial-state inventory

**Do NOT** re-run failed tasks during closure. Closure documents state and hands off cleanly.

---

> **Parallel execution**: Steps 2 and 3 are independent and SHOULD be dispatched concurrently.

## Step 2 [parallel] — Final Quality Check

Dispatch `ai/plugins/skf/skills/orch-final-orchestration-validation.md` (full 9-section manifest).

**Scope**: all artifacts produced during execution (from inline wave summaries and verification state). For partial runs: scope to completed artifacts only. Read-only — do not modify files.

**Checks**: schema conformance, cross-reference integrity, completeness.

**Output**: per-artifact status (ok/warn/fail), quality issues summary, verdict (PASS / PASS WITH WARNINGS / FAIL).

**If FAIL**: surface findings to user. Do NOT block Steps 3–6. Note in orchestration summary.

---

## Step 3 [parallel] — Documentation Update

Dispatch `ai/plugins/skf/skills/gov-update.md` (full 9-section manifest).

Update framework indexes, READMEs, and governance docs to reflect execution changes. Only update docs corresponding to actual changes — do not touch unchanged components.

**Input context**: inline wave summaries, changed file list, iteration path.

**If fails**: note in orchestration summary. Do NOT block Steps 4–5.

---

## Step 4 — Report

> Sequences after Steps 2, 3, and 3b all complete.

**[parallel with Step 5]** Steps 4 and 5 write to different output paths and have no shared file targets — dispatch both concurrently. Step 4 is independent of Step 3 documentation result.

Dispatch `ai/plugins/skf/skills/orch-orchestration-summary.md` (compact) using the accumulated inline execution state to write `reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md` using template at `ai/plugins/skf/templates/orchestration-summary-template.md`.

Then present summary **inline in chat** — user must see outcome without reading a file. (Orchestration summary is available in `reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md` for reference.)

**Summary MUST include**:
- Overall status: COMPLETE / PARTIAL / FAILED
- Request and complexity tier
- Waves executed and outcomes
- Artifacts produced (paths)
- Outstanding tasks (if partial)
- QA verdict
- Next actions for user (if any)

---

## Step 5 — Knowledge Capture (parallel with Step 4)

**[parallel with Step 4]** Independent of Step 4 — dispatch concurrently. Step 5 is independent of Step 3 documentation result.

Dispatch `ai/plugins/skf/skills/meta-knowledge-manage.md` (compact, write mode).

**Topics to record**:
- Blockers and resolutions (grouped by category)
- Manual commands that could be automated
- Slow or multi-retry steps
- Framework gaps (missing skills, policies, protocols)
- Improvements for future runs

**Rules**: each lesson concrete and actionable (not "things went well"). Append to `knowledge-database.md` — do not overwrite existing entries.

**Database unavailable**: skip with note.

---

## Step 6 — Knowledge Distillation (sequences after Step 5)

**[conditional]** Sequences after Step 5 completes.

Check the Step 5 meta-knowledge-manage subagent output for the `distillation-recommended: true` signal:

**If signal present**: Dispatch `ai/plugins/skf/skills/meta-knowledge-distillation.md` (compact, distill operation) with `knowledge-database.md` as input. The skill will classify lessons as project-specific or general-recurring, cluster general-recurring lessons, propose new patterns, and promote viable patterns to `ai/plugins/skf/patterns/`. Promoted lessons are removed from knowledge-database.md; project-specific lessons remain untouched.

**If signal absent or Step 5 was skipped**: Skip this step silently.

**Non-blocking**: If distillation fails or is skipped, note in orchestration summary. Does NOT block closure or any subsequent step. Consistent with Closure Invariants — distillation is a non-blocking enhancement to the self-learning loop.

**Rules**: Distillation only proceeds on explicit signal from Step 5. Pattern creation follows existing schema from `ai/plugins/skf/patterns/pattern-tags.md` and ID auto-increments from `patterns-index.json`.

---

## Closure Invariants

Closure ALWAYS runs:
- User cancelled mid-execution → proceed from last completed action
- QA returned FAIL → continue all steps
- Documentation update failed → continue remaining steps
- Index sync failed → continue remaining steps (will note in summary)
- Execution remained within the current session (resume disabled in the inline-only contract)

Each step is independent — failure at Step N does NOT block Step N+1.

---

## Error Paths

- **Partial completion (Step 1)**: document in orchestration summary, list outstanding tasks explicitly. Closure completes — does not attempt remaining work.
- **Documentation update fails (Step 3)**: note in summary, continue to Step 3b.
- **Index sync fails (Step 3b)**: note in summary, continue to Steps 4–5 (reporting and knowledge capture).
- **Knowledge DB unavailable (Step 5)**: skip with note. Record in summary.
- **Distillation skipped (Step 6)**: no distillation-recommended signal from Step 5, or meta-knowledge-distillation failed — note in summary, does not affect closure.
