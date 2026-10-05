---
name: spec-quick-planner
description: "Generates a documented remediation plan for an active feature, optionally syncing spec artifacts and injecting concrete tasks into tasks.md."
---

# Spec Quick Planner

Plans an ad-hoc fix or enhancement to an active feature: writes a reference-only remediation plan with design rationale, then optionally syncs that scope into `spec.md`/other artifacts and injects executable tasks into `tasks.md`. Does not implement tasks or evaluate spec quality.

Spec Sync Contract (D2 rules, sync table, record format): `spek-fu/plugins/spec/knowledge/spec-sync-contract.md`
Template: `spek-fu/plugins/spec/templates/remediation-plan-template.md`

## When to use

Any time work on an active feature diverges from its existing tasks.md — a bug found mid-implementation, a scope adjustment, a follow-up enhancement — and needs documented rationale before it becomes tasks. Not for drafting a feature from scratch (`spec-feature-draft`) or generating the initial task list (`spec-tasks-draft`).

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `remediation-intent` (user's description of the fix/enhancement to plan)

</inputs>

<outputs>

## Outputs

- `remediation/<slug>/plan.md` written under `<spec-file-directory>/`
- `spec.md` and other artifact edits (only if spec sync accepted)
- `## Phase R<n>: Remediation — <slug>` section appended to `tasks.md` (only if task injection accepted)
- Planning Report: plan path, spec-sync status, task-injection status, Spec Sync Record

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never invent plan content absent from context and research; place `[NEEDS CLARIFICATION: <question>]` at the point of uncertainty instead.
- Never delete an FR/SC; amend in-place on contradiction only, per `spec-sync-contract.md` Rule 1.
- Never allocate an FR/SC the plan doesn't justify (`spec-sync-contract.md` Rule 7); never author a missing artifact (Rule 4).
- Never touch `research.md`.
- The plan itself never contains `- [ ]` task items — it is reference documentation, not a checklist.
- Injected tasks live only in a dedicated `## Phase R<n>: Remediation — <slug>` section (after the last existing phase by default, before `## Phase 1` if the remediation must run first) and follow the checklist format `- [ ] [ID] [P?] Description (file-path) @ref: remediation/<slug>/plan.md#<section> — FR-###`.
- Plan acceptance, spec-sync acceptance, and task-injection acceptance are three separate approvals (`spec-sync-contract.md` Rule 5); never bundle them into one question.
- Never implement the injected tasks — delegate to `spec-orchestrator`/`spec-implement-executor` for that.
- If `spec-file` is missing or unreadable, stop and report `blocked` — never invent spec content.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every plan section and report line uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Grounded Planning** — no root cause, decision, or task traces to nothing; everything is either sourced from context/research or marked `[NEEDS CLARIFICATION]`.

**Provenance** — every spec change traces back to the remediation plan that justified it, both ways (Rule 2).

</behavioral_anchors>

<workflow>

## Steps

### 1. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`. `feature-dir` is its parent directory.

> If no match or the file doesn't exist: stop, report `blocked` — spec-quick-planner requires an active feature; instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.

### 2. Ask plan intent

Ask whether to author a documented remediation plan for `remediation-intent` on this feature. If declined: stop, report `user-declined`, write nothing.

### 3. Load context

Read what's present under `feature-dir`: `spec.md`, `technical-plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`, any existing `remediation/*/plan.md`. Synthesize a context summary (problem domain, existing design, prior remediation, constraints).

### 4. Retrieve advisory context

Spawn in parallel: `framework-compounding-agent` (read mode) with `remediation-intent` + the context summary, and `doc-engine-executor` (Traverse) for relevant codebase context. Hold returned lessons/context as advisory for Step 6; apply judgment, proceed without them if none return.

### 5. Research

Spawn agents in parallel to answer, tied to this feature's context only: (1) root-cause — why is the current state problematic; (2) design decisions — trade-offs and alternatives; (3) implementation scope — smallest focused unit of work; (4) risks and acceptance criteria — what could go wrong, how success is verified. Collect all four into a synthesis.

### 6. Author the plan

Choose a URL-safe descriptive `<slug>`. Load `spek-fu/plugins/spec/templates/remediation-plan-template.md` and populate Intent, Rationale, Root-Cause Findings, Design Decisions, Acceptance Criteria, Risks & Mitigations, Dependencies & Impedance Notes from Steps 3–5. Leave `[NEEDS CLARIFICATION: ...]` at unresolved points. Do not write yet.

### 7. Ask about spec sync

Ask whether to sync this remediation's scope into the feature's spec artifacts (required if it overrides a standing requirement). If declined: skip Step 8, record `declined` in the Spec Sync Record.

### 8. Plan spec sync (conditional)

Follow `spek-fu/plugins/spec/knowledge/spec-sync-contract.md`: identify FR/SC introduced or contradicted by the plan, allocate new IDs sequentially from `spec.md`'s last ID, plan each edit, and build the Spec Sync Record table. Present the planned edits to the user before writing anything.

### 9. Ask about task injection

Ask whether to inject concrete implementation tasks into `tasks.md`. If declined: skip Step 10.

### 10. Plan task injection (conditional)

From the plan, identify separable units of work — one task per unit, not one plan-pointer task. Assign sequential IDs continuing from the last `T###` in `tasks.md`; mark `[P]` for independent-file tasks; cite `@ref: remediation/<slug>/plan.md#<section> — FR-###` on each. Append the phase-end triplet (`[K-R<n>]` framework-compounding-agent write, `[D-R<n>]` doc-engine-executor Update, `[C-R<n>]` commit). Present the planned tasks for review before writing.

### 11. Write artifacts

1. Write `remediation/<slug>/plan.md` always, including the Spec Sync Record (accepted rows, or the single `declined` row).
2. If spec sync accepted: write `spec.md` first, then any other artifacts flagged in Step 8's table. Never touch `research.md`.
3. If task injection accepted: append `## Phase R<n>: Remediation — <slug>` to `tasks.md` (scaffold the file if absent) at the position chosen in Step 10.

### 12. Report

Produce the Planning Report: plan path, feature branch/dir, spec-sync status (with modified artifacts and IDs, or the decline note), task-injection status (task count, ID range, phase section, or the decline note), and the full Spec Sync Record table.

</workflow>

<done_conditions>

## Done Conditions

- `remediation/<slug>/plan.md` exists, contains no `- [ ]` items, and its Spec Sync Record accounts for every FR/SC touched (or records `declined`).
- `spec.md`/other artifacts synced only if accepted in Step 7; `research.md` never touched.
- `tasks.md` carries the `## Phase R<n>: Remediation — <slug>` section only if accepted in Step 9, every task in strict checklist format with an FR citation.
- Planning Report shown per Step 12.

</done_conditions>
