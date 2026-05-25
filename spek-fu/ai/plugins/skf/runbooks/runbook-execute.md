---
id: skf-runbook-execute
title: "Execution Phase Runbook"
phase: execution
version: 1.0
steps: 6
---

# Runbook: Execution Phase

**Phase 3** | Steps 1–6 | Orchestrator: skf-general-orchestrator

Loads dispatch protocol, caches approved inline orchestration state, executes the approved plan wave-by-wave with verification and coherence checks. Phase 4 (Closure) begins after Step 6 or on early closure.

> **Shared protocols**: See `runbook-shared.md` for Dispatch Contract, Escalation Policy, and Bounded Retry Policy. Re-read at phase entry.

> **Skill inventory caching**: Cache the inline `skill-inventory` once at Phase 3 entry. Reference this in-memory copy for all subsequent dispatch manifest construction — do not re-read or reconstruct it per dispatch.

> **DELEGATE-OR-STOP**: Before every tool call, verify against the DELEGATE-OR-STOP protocol. Only `runSubagent`, `vscode/askQuestions`, `todo`, `web`, and allowlisted `read_file` are permitted.

---

## Step 1 — Load Dispatch Protocol

**Inline dispatch checklist** — verify before EVERY `runSubagent` call:

1. **Variant selection**: `impl-*`/`gov-*` → Full manifest by default; `orch-*`/`meta-*` → Compact manifest by default. If `dispatch-variant` in the skill inventory says otherwise, follow the inventory.
2. **Static fields**: read from the cached inline `skill-inventory` (id, path, description, anti-scope, inputs, outputs, dispatch-variant)
3. **Runtime fields**: read from the approved inline orchestration plan (task, context, constraints, wave/step number)
4. **Response format**: subagent must return `status` (ok/blocked/fail) + `summary` (one line) + structured result payload; `output_path` is optional and reserved for durable reports or oversize spill artifacts
5. **SKILL section**: must point to file path, not inline behavior description
6. **CONTEXT section**: must cite file paths only — never paste file contents
7. **CONSTRAINTS**: must include wave number and step number
8. **Escalation**: if subagent fails, retry ONCE with a different approach + explicit failure reason; if still blocked → `vscode/askQuestions`
9. **Tier is advisory**: consult `recommended-tier` in skill-inventory, but decide based on task complexity and context
10. **Dry run required**: for irreversible/bulk actions (mass replace, delete) → preview → confirm → execute

**Verify against checklist** (items below use shorthand from the checklist above):

1. `impl-*`/`gov-*` or skill marked `full` → full manifest? (see Full template in runbook-shared.md)
2. `orch-*`/`meta-*` or skill marked `compact` → compact manifest? (see Compact template in runbook-shared.md)
3. SKILL points to file path (not inline behavior)?
4. CONTEXT cites paths (no pasted file contents)?
5. CONSTRAINTS includes wave/step number?

---

## Step 2 — Cache Approved State

Cache the approved plan, skill inventory, wave decomposition, pattern selection, and intake context from Phase 2. Execution is single-session only in this contract.

**Rule**: Do not dispatch `orch-resume-detect.md`. Resume remains disabled until a non-temp persistence model is approved.

---

## Step 3 — Execute Wave-by-Wave

For each wave, run substeps 3.1–3.3 in order.

### 3.1 Pre-Wave Conflict Detection

Collect all `target-files` across parallel tasks. If any file appears in multiple tasks → serialize the conflicting task:
```
⚠ Conflict: {skill-a} and {skill-b} both target {file} — serializing {skill-b}
```
Clean → `✓ No file conflicts in Wave {N}.`

### 3.2 Wave Pattern Bundle

Reference the current wave's inline pattern bundle. If it has not been built yet, dispatch `spek-fu/ai/plugins/skf/skills/orch-wave-pattern-bundle.md` (compact) to build it now before proceeding.

- **Success**: inject compact required/advisory pattern state into each task's CONSTRAINTS and ADVISORY sections
- **Skipped** (no pattern selection result): log warning, dispatch without bundle
- **No bundle at dispatch time**: proceed without blocking

The bundle aggregates required (binding) + advisory (informational) patterns from the inline pattern selection result, resolved via `patterns-index.json`. Subagents consume one compact wave bundle object rather than many individual pattern files.

**Precedence within bundle**: required > advisory; within advisory, earlier PT-ID > later. PT025 (Self-Correction) requires PT009 (Test Before Trust) when either is selected.

### 3.3 Dispatch Each Task

Log: `→ Wave {N}, Step {M} → {agent-tier}: {skill-id} — {reason}`

**Manifest**: full for `impl-*`/`gov-*` and any skill whose `dispatch-variant` is `full`; compact for `orch-*`/`meta-*` and any skill whose `dispatch-variant` is `compact`. Look up the skill entry in the cached inline `skill-inventory` (produced by `orch-skill-resolve` in Phase 2) to get all static fields, then use the matching template from `runbook-shared.md § Dispatch Manifest Templates` to build the manifest. Fill all `<RUNTIME: ...>` fields from the orchestration plan.

**Tier selection**: Select the appropriate agent tier for this dispatch. Consult the `recommended-tier` field in the cached inline `skill-inventory` as a starting point, but decide based on task complexity and context. Never default all dispatches to the same agent tier.

**Dry run**: before irreversible/bulk actions (`rm`, `drop`, `truncate`, mass refactors) → preview → confirm → execute.

**Tool whitelisting** (set in CONSTRAINTS; all others implicitly forbidden):

| Role | Permitted |
|---|---|
| Research | `read_file`, `grep_search`, `list_dir`, `file_search` |
| Analyzer | `read_file`, `grep_search`, `file_search`, `create_file`, `run_in_terminal` (scripts) |
| Implementer | `replace_string_in_file`, `create_file`, `read_file` |
| Verifier | `read_file`, `get_errors`, `run_in_terminal` (test-only) |
| Documenter | `read_file`, `create_file` |

> **Role selection**: Use **Analyzer** for any `orch-*` skill that produces a report file (for example `orch-wave-verification`, `orch-artifact-coherence-check`, `orch-branch-analyze`, `orch-final-orchestration-validation`). Analyzer includes `create_file` so the skill can write its report without a separate delegation step.



---

## Step 4 — Verify Each Wave

Dispatch `spek-fu/ai/plugins/skf/skills/orch-wave-verification.md` (full manifest) with task list, expected outputs, plan reference, and wave scope. The skill performs structural + semantic verification and returns both wave summary and verification state inline. If the compact response budget is exceeded after compaction, it may spill to `spek-fu/reports/orchestration-spill/` as an exception.

**Failure handling**:
- First fail → retry with correction context in CONSTRAINTS (consumes `maxWaveRetries`)
- Second fail → escalate via `vscode/askQuestions`

---

## Step 5 — Corrections

If `orch-wave-verification` fails:

**First failure**: re-dispatch with CORRECTION section added to CONSTRAINTS:
```
CORRECTION CONTEXT: Previous attempt failed.
Reason: {specific failure — not "it didn't work"}.
What must be different: {concrete change in approach}.
Attempt {N} of {cap}.
```

**Budget exhausted**: escalate with options → retry · skip to next wave · abort.

**Rules**: every retry states specific failure reason + concrete difference. No same-approach rewording. Delegate wave-summary updates through Dispatch Contract.

---

## Step 6 — Artifact Coherence Check

**Conditional trigger**: Only dispatch `orch-artifact-coherence-check` when the approved plan declares inter-wave dependencies between the completed wave and the next wave. If no inter-wave dependencies are declared, skip this step and proceed to the next wave.

Dispatch `spek-fu/ai/plugins/skf/skills/orch-artifact-coherence-check.md` (compact) after each wave verification.

**Checks**:
- Wave N+1 input files exist and are well-formed
- No schema mismatches between Wave N output and N+1 expected input
- No path assumption mismatches (Wave N wrote `a.md` but N+1 expects `b.md`)

**Incoherence detected** → HALT before Wave N+1. Surface: "Wave N produced `{paths}` but Wave N+1 expects `{expected}`. Resolution needed."

---

## Phase Transition

After all waves complete + final coherence check passes → **Phase 4 — Closure** (`runbook-close.md`).

**Early closure** (user cancels): stop at end of current action, preserve completed work, proceed directly to Phase 4.

## Error Paths

- **Verification failure (3.4/4)**: retry once with concrete correction context. Second fail → blocked, surface with devcontainer context.
- **Coherence failure (6)**: halt and surface for resolution.
- **User cancels (3)**: stop current action, preserve work → Phase 4.
- **Correction budget exhausted (5)**: escalate — never invent third approach without authorization.
