---
name: spec-manual-implement
description: "Executes one, several, or all selected tasks from a feature's tasks.md inline and reports the results."
---

# Spec Manual Implement

Executes a user-selected set of tasks from `tasks.md` (a list, a range, a phase, or `all`) inline in the current session, in file order. Loads shared design context once and per-task fragments lazily, marks each task `[X]` or `[!]`, and reports one consolidated result. Multi-task counterpart of `spec-implement`.

## When to use

Implement phase step, run by the user directly instead of `spec-orchestrator`, to implement one or many tasks under their supervision. Does not draft tasks or make design decisions beyond what a task specifies; spawns subagents only for `[K-*]`/`[D-*]` tasks, per their own description.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `tasks` (optional; task IDs `T003,T005`, a range `T003-T010`, a phase name/number, or `all`; asked for if absent)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-manual-implement.maxFixCycles`)

</inputs>

<outputs>

## Outputs

- Code changes for the selected tasks only
- `tasks.md` updated in place, one marker per task: `[ ]` → `[X]` or `[!]`; `## Discovered Subtasks` appended if new work surfaces
- Consolidated completion report: per-task result plus summary

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`, in particular SD8/SD9 (TDD/BDD) and the Ambiguity principle.

## Rules

- Never begin executing before `feature-dir` is resolved and `tasks.md` is confirmed present.
- Never execute a task outside the resolved selection; never reorder it — run in `tasks.md` file order, sequentially, treating `[P]` as ordinary.
- Never spawn subagents except as a task's own action: a `[K-*]` task spawns `framework-compounding-agent` (write mode), a `[D-*]` task spawns `doc-engine-executor` (Update workflow) — per `spec-orchestrator`'s pattern. Every other task is implemented inline.
- Never invent task details absent from `tasks.md` or its loaded design artifacts; place `[NEEDS CLARIFICATION: <question>]` at the exact point of uncertainty instead.
- Write each marker `[X]` / `[!]` immediately after its task, as an independent write touching no other task's marker.
- `all` and phase selections cover `[ ]` tasks only; a `[X]` or `[!]` task is reported and skipped. An explicit `[!]` task is never retried — report `blocked (already blocked)`.
- Skip and record every `[MANUAL]` task.
- Skip and record every later task in the same phase as a `[!]` task, unless independence is evident (different `[USN]` or unrelated file paths); continue with independent tasks.
- Execute a `[C-*]` commit task only if it is in the resolved selection; never commit to Git otherwise.
- Never fix issues outside a task's own description — append discovered work under `## Discovered Subtasks` with the next `D###` ID; never execute it in the same run unless its ID is in the selection.
- Comments this skill writes never reference external spec/task/file IDs or names — describe only the file's own functionality; exception: the doc-pointer header defined in `spek-fu/plugins/doc-engine/knowledge/format.md`.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every status line and report entry uses the fewest words that preserve meaning, per constitution `## AI Principles`.

**Grounded Implementation** — no file, entity, or behavior is invented; each traces to the task or a lazily loaded design artifact, or is marked `[NEEDS CLARIFICATION]`.

**Selection Fidelity** — this skill executes exactly the tasks selected, in file order; nothing beyond the selection runs.

</behavioral_anchors>

<workflow>

## Steps

### 1. Resolve paths

Resolve `spec-file`: if provided use it, otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`. `feature-dir` is its parent directory.

> If no match, or `tasks.md` is absent from `feature-dir`: stop, report `blocked (missing artifact)`, instruct the user to run `spec-tasks-draft` first.

### 2. Resolve the selection

Read `tasks.md` in full for markers (`[ ]`, `[X]`, `[!]`, `[MANUAL]`, `[P]`, `[C-*]`), phase boundaries, and IDs. If `tasks` is absent, show a phase-level state summary and ask what to run.

Expand `tasks` to an ordered list in file order. Then classify each task:

- `[ ]` → runnable.
- `[X]` → skip, `ok (already complete)`.
- `[!]` → skip, `blocked (already blocked)`.
- `[MANUAL]` → skip, record.

> If an ID is not found: stop, report `blocked (task not found)`, list the unknown IDs.
> If no runnable task remains: report status and stop.

### 3. Load shared context

Load `spec.md`, `technical-plan.md`, `research.md` from `feature-dir` if present, once, for feature intent, structure, and stack cues; note which are absent for the final report.

If any selected task touches tests, read `spek-fu\constitution\test-design-guide.md`.

### 4. Surface clarifications upfront

For each runnable task, scan its line and the design fragments it needs (an acceptance scenario from `spec.md`, a `contracts/` file, a `data-model.md` section, a `tdd-designer/report.md` block, or an `@ref:` fragment) for `[NEEDS CLARIFICATION]` markers.

> If markers exist: list them all in one pass and ask whether to proceed. A task whose marker is declined or unresolved is skipped, `blocked (upstream clarifications)`, and treated as blocked for its downstream dependents.

### 5. Execute tasks sequentially

For each runnable task in file order:

1. Skip it if it is a downstream dependent of a `[!]` task per the Rules; record it.
2. Lazy-load only the design fragment this task needs.
3. Apply the change the task describes: a `[K-*]` task spawns `framework-compounding-agent` (write mode) with the phase's errors/resolutions/patterns as input; a `[D-*]` task spawns `doc-engine-executor` (Update workflow) to sync documentation for the phase's changes; every other task is implemented inline. Wait for the spawned agent to finish before continuing.
4. Run scoped tests for the touched files only (full suite only if the task requires it).
5. On failure: retry up to `maxFixCycles` (config, default `3`). Still failing: mark the task `[!]`, record `blocked (task failure)`, continue with the next independent task.
6. On success: flip `[ ]` → `[X]` immediately.
7. If execution reveals undocumented work: append it under `## Discovered Subtasks` with the next `D###` ID.

### 6. Report

Report: `feature-dir` and `tasks.md` path; the resolved selection; per task — ID, one-line result note, test result, status (`ok` / `ok (already complete)` / `skipped (MANUAL)` / `skipped (downstream of T###)` / `blocked (...)`); `[NEEDS CLARIFICATION]` markers carried or placed; discovered subtasks appended; optional artifacts missing; overall status (`ok` / `partial` / `blocked`).

</workflow>

<done_conditions>

## Done Conditions

- Every task in the selection is `[X]`, or recorded as skipped/blocked with a reason.
- `tasks.md` writes touched only selected tasks' markers and `## Discovered Subtasks`.
- No task detail was invented; unresolved ambiguity carries a `[NEEDS CLARIFICATION]` marker.
- No commit was made except through a selected `[C-*]` task.
- Consolidated report given per Step 6.

</done_conditions>
