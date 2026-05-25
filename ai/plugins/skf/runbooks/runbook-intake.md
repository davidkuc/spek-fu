---
id: skf-runbook-intake
title: "Intake Phase Runbook"
phase: intake
version: 1.0
steps: 9
---

# Runbook: Intake Phase

**Phase 1** | Steps 1–9 | Orchestrator: skf-general-orchestrator

Captures request, classifies complexity, gathers framework context, consults knowledge, selects patterns, resolves clarifications, writes intake snapshot. Phase 2 begins after Step 9.

> **Shared protocols**: See `runbook-shared.md` for Dispatch Contract, Escalation Policy, and Bounded Retry Policy. Re-read at phase entry.

> **DELEGATE-OR-STOP**: Before every tool call, verify against the DELEGATE-OR-STOP protocol. Only `runSubagent`, `vscode/askQuestions`, `todo`, `web`, and allowlisted `read_file` are permitted.

---

## Step 1 — Initialize via orch-initialize

Dispatch `ai/plugins/skf/skills/orch-initialize.md` (compact) with `workspace-root` = workspace root path.

- After dispatch: cache the inline init result to obtain all config values and environment.
- If returned `status: hard-fail` → **STOP** orchestration immediately with the `hard-fail-reason`.
- On success: extract and cache inline for subsequent steps:
  - `maxClarificationLoops`
  - `environment` (devcontainer | host)
  - `maxPlanRevisions`, `maxWaveRetries`, `maxSubagentRetries`
  - `complexityThresholds` (`simpleMaxFiles`, `standardMaxFiles`, `complexMinFiles`)
  - `approvalTimeoutBehavior`
  - `spec-context` (true | false | unknown) and `spec-feature-dir` (path or none)
- Pass `env` = returned `environment` value in all subsequent skill dispatches.

> `complexityThresholds` drives Step 4, `maxClarificationLoops` caps Step 8 loops, `maxWaveRetries`/`maxSubagentRetries` cap execution retries, `approvalTimeoutBehavior` governs plan approval.

---

## Step 2 — Receive Request

Read user intent from conversation. If vague or incomplete, ask direct scoping questions: end state, files/components in scope, constraints/dependencies, reversibility.

Do NOT infer scope from filesystem — that happens at Step 4.

**If clarification needed**, use this question template:

```json
{
  "header": "intake_clarification",
  "question": "I need clarification before proceeding. Please provide:",
  "options": [
    { "label": "Describe intended end state — what should change" },
    { "label": "List files or components in scope" },
    { "label": "Describe any constraints or dependencies" },
    { "label": "Is this reversible or requires validation?" }
  ],
  "multiSelect": true,
  "allowFreeformInput": true
}
```

**Proceed when**: intent supports complexity classification.

---

## Step 3 — Analyze Request

Analyze the problem from request text, conversation and research. No `grep_search`, `file_search`, `semantic_search`. No `read_file` except allowlisted paths. Delegate research to research subagents (fast-agent) that research specific parts of the problem.

1. Analyze request and context
2. Divide problem into smaller parts
3. Delegate research subagents (fast-agent) for each part
4. Wait for all research to finish and consolidate all findings

Key points to define:
- **Work type**: implementation / QA / documentation / config / mixed
- **Estimated file count** from context and research
- **Skill mapping** clarity or ambiguity
- **Whether Step 4 complexity gate affects scope**
- **Spec-context routing**: When `spec-context: true` (from Step 1), treat the request as a spec-flow execution — set skill hint to `spec-implement` and include `spec-feature-dir` in the intake context. When `spec-context: false`, use `impl-implement` as the implementation skill default. When `spec-context: unknown`, flag ambiguity for clarification at Step 8.

If scope undeterminable from context → skip to Step 8 (clarification) before continuing. If deeper research needed after Step 4, delegate targeted research via compact dispatch.

---

## Step 4 — Complexity Gate

| Tier | Criteria | Routing |
|---|---|---|
| **Simple** | ≤`simpleMaxFiles` files; formatting/mechanical only; no logic changes; fully reversible | Fast-path: confirm → dispatch `fast-agent` → skip Phases 2–4 |
| **Standard** | `simpleMaxFiles+1`–`standardMaxFiles`; bounded scope; clear skill mapping | Full orchestration |
| **Complex** | >`standardMaxFiles`; cross-cutting; architectural | Full orchestration |

### Simple Fast-Path

Name the skill + target file(s) + one-sentence rationale. Present: "Fast-path recommendation: dispatch `{skill}` targeting `{files}`. Confirm?" Confirmed → dispatch and stop. Declined → reclassify Standard.

### Hidden-Complexity Guard

If request contains **"all"/"each"/"every" + plural noun** → do NOT classify Simple. Defer to Step 5 file count. Reclassify if count exceeds `simpleMaxFiles`.

### Not Simple

Identify through these signals: Logic/schema/cross-ref changes · >`simpleMaxFiles` files · plan generation needed · ambiguous skill · "all/each/every" + plural (pending count).

---

## Step 5 — Knowledge Consultation (Parallel)

Dispatch `ai/plugins/skf/skills/meta-knowledge-manage.md` (compact, read mode). Search `knowledge-database.md` for relevant lessons. Runs in parallel with Steps 6 and 7.

- No lessons → proceed silently (do not surface "none found").
- Lessons found → incorporate as advisory (inform, never override reasoning).

---

## Step 6 — Framework Research (Parallel)

Gather framework guidance and tools relevant to the problem (not problem analysis — that was Step 2).

- **Simple tasks**: Dispatch a single `ai/plugins/skf/skills/orch-index-traversal.md` (compact) from `skf-root-index.json`.
- **Standard or Complex tasks**: Dispatch `ai/plugins/skf/skills/orch-index-traversal.md` (compact) **in parallel**, one per predefined framework branch:
  - Branch 1: `ai/` (skills, scripts, patterns, knowledge) with a compact inline traversal summary for the branch
  - Branch 2: `constitution/` (rules, constraints) with a compact inline traversal summary for the branch
  - Branch 3: `project/` (context, readme, configs) with a compact inline traversal summary for the branch

  > **Spec-context priority**: When `spec-context: true`, the `spec-flow` plugin branch (`ai/plugins/spec-flow/`) should be a priority traversal target within Branch 1 to ensure spec-flow skills and artifacts are surfaced for routing.

Each branch dispatch targets the sub-section of `skf-root-index.json` relevant to that branch and produces its own structured traversal result inline. If a branch summary cannot be kept compact without losing required fidelity, spill is allowed only under `reports/orchestration-spill/`.

Guardrails: `skf-config.json` also permitted at Step 1. No speculative reads. No search-tool substitution for delegated discovery.

**Error**: Partial results → hold available, dispatch supplemental research. Do NOT proceed to Step 7 without sufficient context.

---

## Step 7 — Pattern Selection (Parallel)

Dispatch `ai/plugins/skf/skills/orch-pattern-select.md` in parallel with Step 6 (after Step 4 stabilizes).

**Inputs**: `complexity-tier`, `task-signals` (from `pattern-tags.md` canonical vocabulary), `task-description`, `patterns-index-path` (`ai/plugins/skf/patterns/patterns-index.json`).

**Signal sources**: user request (Steps 2–3), complexity tier (Step 4), framework context (Step 6), lessons (Step 5, advisory).

**Persistence**:
- `status: ok` → carry the structured result directly to Step 9
- `blocked` → continue without, note gap in intake context

---

## Step 8 — Clarification Questions

> **Early firing**: May fire earlier if Step 3 analysis produces undeterminable work-type before parallel Steps 6/7 start. Do not wait for parallel research to conclude if a scope clarification would change the research direction.

Bounded loop: max iterations = `maxClarificationLoops`. Each iteration: one `vscode/askQuestions` call batching ALL remaining unknowns. Skip entirely if unambiguous after Steps 3–7.

**Ask about**: ambiguous targets · missing constraints · conflicting signals · unclear acceptance criteria.

**Never ask**: questions answerable from framework indexes · single-question follow-ups when batching is possible.

**Question template**:

```json
{
  "header": "scope_clarification",
  "question": "Please clarify the following to proceed:",
  "options": [
    { "label": "Confirm targets and affected components" },
    { "label": "Confirm constraints and dependencies" },
    { "label": "Confirm acceptance criteria" },
    { "label": "Confirm reversibility requirements" }
  ],
  "multiSelect": true,
  "allowFreeformInput": true
}
```

**If answers significantly change scope**: re-run Steps 3–4 and re-evaluate complexity tier.

---

## Step 9 — Capture Intake Context

Dispatch `ai/plugins/skf/skills/orch-intake-context.md` (compact). Return a structured intake context object containing:

- User request (verbatim)
- Complexity tier + rationale
- Framework context summary (file list from Step 6)
- Knowledge lessons (Step 5, or "none")
- Pattern selection status + structured result (Step 7)
- Clarifications (Step 8, or "none")

If `orch-intake-context` returns `status != ok` → escalate: surface the error and do not advance to Phase 2.

---

## Phase Transition

→ **Phase 2 — Planning** (`runbook-plan.md`). Gate items satisfied: framework context scanned ✓, user request captured ✓.
