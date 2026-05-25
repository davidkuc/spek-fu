---
id: skf-runbook-planning
title: "Planning Phase Runbook"
phase: planning
version: 1.0
steps: 5
---

# Runbook: Planning Phase

**Phase 2** | Steps 1–5 | Orchestrator: skf-general-orchestrator

Breaks work into waves, applies complexity gate per task, generates formal plan via `ai/plugins/skf/skills/orch-orchestration-plan.md`, gets user approval, validates before execution. Phase 3 begins after Step 5 succeeds.

> **Shared protocols**: See `runbook-shared.md` for Dispatch Contract, Escalation Policy, and Bounded Retry Policy.

> **DELEGATE-OR-STOP**: Before every tool call, verify against the DELEGATE-OR-STOP protocol. Only `runSubagent`, `vscode/askQuestions`, `todo`, `web`, and allowlisted `read_file` are permitted.

---

## Step 1 — Resolve Skill Inventory & Decompose Waves (Parallel)

Dispatch `ai/plugins/skf/skills/orch-skill-resolve.md` (compact manifest).
- Input: `intake-context: structured object from Intake Step 9`
- Output: structured `skill-inventory`
- If blocked → surface error.

---

## Step 2 — Decompose into Waves (Parallel)

Dispatch `ai/plugins/skf/skills/orch-wave-decompose.md` (compact manifest).
- Input: `intake-context: structured object from Intake Step 9`
- Output: structured `wave-decompose`
- If blocked → surface error.

---

## Step 3 — Generate Plan

**Wait for both** Step 1 and Step 2.

Dispatch `ai/plugins/skf/skills/orch-orchestration-plan.md`.

**Key inputs**:
- Intake context: structured object from Intake Step 9
- Skill inventory: structured result from Step 1
- Wave decomposition: structured result from Step 2
- Pattern selection result: structured result from intake Step 7 (optional)
- Governance wave: include | skip

**Constraints**: validate all skill-ids against the skill inventory; no invented skill names; return the orchestration plan inline as the canonical planning output.

**Expected output**: formal plan document using the pre-decomposed waves from `wave-decompose`, skill-id + agent tier per task, expected outputs, dependency markers.

---

## Step 4 — Present Plan & Get Approval

**6 gate items** before Phase 3:

1. Framework context scanned ✓ (intake)
2. User request captured ✓ (intake)
3. Scope and complexity analyzed
4. Clarifications resolved
5. Plan generated and presented inline
6. Explicit user approval via `vscode/askQuestions`

**Presentation**: show actual plan inline — do not paraphrase away wave structure or task decomposition.

**Approval question template**:

```json
{
  "header": "plan_approval",
  "question": "Review the plan above. How would you like to proceed?",
  "options": [
    { "label": "Approve — execute plan", "recommended": true },
    { "label": "Edit — request changes" },
    { "label": "Cancel — stop orchestration" }
  ],
  "allowFreeformInput": true
}
```

**Approval outcomes**:
- **Approve** → proceed to Phase 3 (Execution)
- **Edit** → incorporate feedback, re-dispatch planning skill, re-present plan, repeat approval (consumes `maxPlanRevisions`)
- **Cancel** → discard plan, advance to Phase 4 (Closure) without execution

Pattern bundle dispatch happens per-wave in Phase 3 — see `runbook-execute.md`.

**Revision cycle**: incorporate feedback → re-dispatch `ai/plugins/skf/skills/orch-orchestration-plan.md` → re-present → re-prompt. Each revision consumes one `maxPlanRevisions` unit. Budget exhausted → escalate with unresolved conflict.

**Timeout**: honor `approvalTimeoutBehavior` from config (`wait-for-explicit-response`).

**Cancel**: discard plan, stop orchestration, do not enter Phase 3.

---

## Step 5 — Pre-Execution Validation

Dispatch `ai/plugins/skf/skills/orch-pre-execution-validation.md` (compact) with the approved inline plan. Validate skill IDs, detect wave conflicts, check dependency issues.

| Failure | Action |
|---|---|
| Unknown skill ID | Surface + correct plan |
| Wave conflicts | Surface + offer serialization |
| Dependency cycle | Surface + require resolution |
| Script failure | Surface + stop |

Failures return to Step 4 for correction and re-approval. Do not consume revision budget unless user requests changes. On success → Phase 3.

---

## Phase Transition

→ **Phase 3 — Execution** (`runbook-execute.md`). All 6 gate items satisfied.

## Error Paths

- **Unstable waves (Step 2)**: circular deps or missing prereqs → surface with options, don't present plan until resolved.
- **Revision limit (Step 4)**: escalate with unresolved conflict stated explicitly.
- **User cancels (Step 4)**: discard plan → Phase 4 (Closure) for lesson capture.
