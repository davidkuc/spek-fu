---
name: spec-tasks-draft
description: "Generates a dependency-ordered tasks.md from a feature's design artifacts, organized by user story and phased for independent, incremental delivery."
---

# Spec Tasks Draft

Reads `spec-file`, `technical-plan.md`, and `tdd-report.md` to produce a checklist-format `tasks.md`: phased by user story, marked for parallel work, with a commit task at each phase end and knowledge-capture and documentation tasks once at the end of the file.

Template: `spek-fu/plugins/spec/templates/tasks-template.md`

## When to use

Final Plan phase step, after `spec-tdd-draft`, when a technical plan and TDD design are ready to become an executable, dependency-ordered task list.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `technical-plan` (optional; resolved from `<spec-file-directory>/technical-plan.md` if absent)
- `tdd-report` (optional; resolved from `<spec-file-directory>/tdd-designer/` if absent)

</inputs>

<outputs>

## Outputs

- `tasks.md` written to `<spec-file-directory>/`
- Completion report: task counts per user story, parallel opportunities, MVP scope, carried clarifications

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never invent task details absent from design artifacts; place `[NEEDS CLARIFICATION: <question>]` at the exact point of uncertainty instead.
- Never generate tasks without `spec-file` and at least one of `technical-plan.md` or `tdd-report.md` present; stop `blocked` otherwise.
- Never omit test tasks unless `spec-file` explicitly waives TDD with rationale (constitution SD8, SD9).
- Every task follows the strict checklist format: `- [ ] TNNN [P?] [USN?] Description (file-path)` — globally sequential `TNNN` across all phases, optional markers, a file path or `n/a`, optional `@ref:` hint.
- Never implement tasks, modify design artifacts, or evaluate spec quality — this skill produces the task plan only.
- Re-running on an existing `tasks.md`: preserve `[X]`/`[!]` markers, `## Discovered Subtasks`, and any `## Phase R<n>: Remediation` sections unchanged.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every task description uses the fewest words that preserve meaning, per constitution `## AI Principles`.

**Grounded Tasks** — no file path, entity, or endpoint is invented; each traces to `spec-file`, `technical-plan.md`, or `tdd-report.md`, or is marked `[NEEDS CLARIFICATION]`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Resolve paths

Resolve `spec-file`: if provided use it, otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.

Resolve `technical-plan.md` and `tdd-report.md` (latest file under `<spec-file-directory>/tdd-designer/`) relative to `<spec-file-directory>`.

> If both are absent: stop, report `blocked` — "spec-tasks-draft requires technical-plan.md or a tdd-report. Run spec-technical-draft or spec-tdd-draft first."

### 2. Load context

Read `spec-file` in full: user stories with priorities, functional requirements, edge cases. Read `technical-plan.md` (tech stack, structure, entities, Input Artifacts table) and `tdd-report.md` (BDD test units, implementation waves) when present. Read `data-model.md` and contracts under `<contracts-root>` (from `technical-plan.md`'s Input Artifacts table) if listed. Carry forward any `[NEEDS CLARIFICATION]` marker found in these artifacts.

### 3. Build the task plan

1. From `technical-plan.md`: identify tech stack, structure, entities, architectural decisions; derive Setup and Foundational tasks.
2. From `spec-file`: extract user stories in priority order; each becomes a phase.
3. Map multi-story entities to the Foundational phase; single-story entities to their story's phase.
4. Map contract endpoints to their story; add `[P]` contract test tasks before implementation tasks.
5. From `tdd-report.md`: one test task per BDD unit, placed in its matching story phase, ordered by wave; reference the unit ID. If `tdd-report.md` is absent, generate generic test-scaffolding tasks per story.
6. Order phases: Setup → Foundational → US1, US2, … (priority order) → Polish → Final.
7. Mark `[P]` for tasks touching different files with no dependency on each other.
8. Assign `[USN]` to every user-story-phase task (`[US1]`, `[US2]`, …).
9. Define one independent test criterion per user story.
10. Assign globally sequential `TNNN` across all phases; never restart numbering per phase.
11. Append `@ref:` hints where a task depends on a specific artifact fragment (e.g. `@ref: data-model.md#User-entity`).

> If a user story is ambiguous and unresolvable from artifacts: place `[NEEDS CLARIFICATION: <question>]` in the task plan at the affected phase; carry any upstream marker into the Generation Report rather than treating it as a blocker.

### 4. Add phase-end tasks

At the end of every phase (Setup, Foundational, each `USN`, Polish), append one task:

```
- [ ] T{N} [C-{phase}] Commit {phase-name} phase work to Git: review and commit all implementation and documentation changes.
```

After the Polish phase's commit task, add a single `## Phase Final: Knowledge Capture & Documentation` phase with two tasks, run once per file:

```
- [ ] T{N} [K-Final] [P] Spawn framework-compounding-agent (write mode): capture lessons from the whole feature — errors, resolutions, cross-task patterns.
- [ ] T{N+1} [D-Final] [P] Spawn doc-engine-executor agent (Update): sync documentation for all feature changes.
- [ ] T{N+2} [C-{phase}] Commit {phase-name} phase work to Git: review and commit all implementation and documentation changes.
```

Keep task IDs sequential across the whole file; use `[P]` on the `[K-Final]` and `[D-Final]` tasks only.

### 5. Generate tasks.md

Load `spek-fu/plugins/spec/templates/tasks-template.md` as scaffold. Populate feature name, all phases with goal and test criterion, tasks in checklist format, dependencies, parallel-execution examples, and implementation strategy. Preserve `## Discovered Subtasks` and any `## Phase R<n>: Remediation` sections if re-running.

**If re-running** (`tasks.md` already exists):
1. Extract `[X]`/`[!]` tasks into a completion map keyed by normalized description; extract `## Discovered Subtasks` and every `## Phase R<n>: Remediation` section unchanged.
2. Regenerate all other phases from current artifacts; re-apply `[X]`/`[!]` markers to matching regenerated tasks.
3. Re-insert each remediation section at its prior position (before `## Phase 1` if it was there, else after the last generated phase); renumber its `T###` IDs only on collision.
4. Re-append `## Discovered Subtasks` unchanged. Note unmatched prior tasks in the Generation Report.

Write to `<spec-file-directory>/tasks.md`, replacing any existing file.

### 6. Report completion

Report: `spec-file` path, `tasks.md` path, total task count, task count per user story, parallel-opportunity count, one-line independent test criterion per story, suggested MVP scope (typically US1), format-validation result, preserved-marker counts (if re-running), and `carried-clarifications: N`.

</workflow>

<done_conditions>

## Done Conditions

- `tasks.md` exists at `<spec-file-directory>/tasks.md`; every task follows the checklist format.
- `spec-file`, `technical-plan.md`, and `tdd-report.md` unchanged.
- No `[NEEDS CLARIFICATION]` marker silently dropped — all carried into the Generation Report.
- Completion report given per Step 6.

</done_conditions>
