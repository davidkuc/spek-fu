---
name: spec-implement
description: "Executes a single delegated task from a feature's tasks.md and reports its result."
---

# Spec Implement

Executes exactly **one task** from `tasks.md`, identified by `task-id`. Loads only the design context that task needs, marks it `[X]` or `[!]` when finished, and reports the result. Built to be called per-task by an orchestrator that sequences, parallelizes, and phases the full task list itself.

## When to use

Implement phase step, invoked by an orchestrator (after `spec-tasks-draft`) once per task to execute a single task from an existing `tasks.md`. Does not choose which task runs next, generate tasks, draft specs, or make design decisions beyond what the task specifies.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `task-id` (required; the single task to execute, e.g. `T012`)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-implement.maxFixCycles`)

</inputs>

<outputs>

## Outputs

- Code changes for `task-id` only
- `tasks.md` updated in place for `task-id` only: `[ ]` → `[X]` or `[!]`; `## Discovered Subtasks` appended if new work surfaces
- Completion report: task result

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`, in particular SD8/SD9 (TDD/BDD) and the Ambiguity principle.

## Rules

- Never begin executing before `feature-dir` is resolved and `tasks.md` is confirmed present.
- Never execute any task other than `task-id`; never choose, sequence, or reorder tasks — that is the orchestrator's responsibility.
- Never read `tasks.md` in full — grep for `task-id`'s line and its enclosing phase header only.
- Never invent task details absent from `tasks.md` or its loaded design artifacts; place `[NEEDS CLARIFICATION: <question>]` at the exact point of uncertainty instead.
- Mark `task-id` `[X]` in `tasks.md` immediately on success, as an independent write touching no other task's marker; mark it `[!]` on unresolved failure instead of silently leaving it `[ ]`.
- Never retry a `task-id` that is already `[!]` on entry — stop and report it blocked instead.
- Never fix issues outside `task-id`'s own description — append discovered work under `## Discovered Subtasks` with the next `D###` ID instead.
- Surface a `[NEEDS CLARIFICATION]` marker found on `task-id` or its loaded design context before implementing: ask whether to proceed if interactive, stop `blocked (upstream clarifications)` if not.
- Comments this skill writes never reference external spec/task/file IDs or names — describe only the file's own functionality; exception: the doc-pointer header defined in `spek-fu/plugins/doc-engine/knowledge/format.md`.
- Never commit changes to Git unless explicitly instructed.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every status line and report entry uses the fewest words that preserve meaning, per constitution `## AI Principles`.

**Grounded Implementation** — no file, entity, or behavior is invented; each traces to `task-id` or a lazily loaded design artifact, or is marked `[NEEDS CLARIFICATION]`.

**Single-Task Scope** — this skill executes exactly the task it is given; sequencing, parallelization, and phase ordering belong to the calling orchestrator, never here.

</behavioral_anchors>

<workflow>

## Steps

### 1. Resolve paths

Resolve `spec-file`: if provided use it, otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`. `feature-dir` is its parent directory.

> If no match, or `tasks.md` is absent from `feature-dir`: stop, report `blocked (missing artifact)`, instruct the caller to run `spec-tasks-draft` first.

### 2. Locate the task

Grep `tasks.md` for `task-id`'s line plus its enclosing phase header. Do not read the rest of the file.

> If `task-id` is not found: stop, report `blocked (task not found)`.
> If `task-id` is already `[X]`: stop, report `ok (already complete)`.
> If `task-id` is already `[!]`: stop, report `blocked (already blocked)` — do not retry automatically.

### 3. Load context

Load `spec.md`, `technical-plan.md`, `research.md` from `feature-dir` if present, for feature intent, structure, and stack cues; note which are absent for the final report. Lazy-load only the design fragment `task-id` needs: an acceptance scenario from `spec.md`, a `contracts/` file, a `data-model.md` section, a `tdd-designer/report.md` block, or the fragment named in an `@ref:` hint.

If working on tests, read `spek-fu\constitution\test-design-guide.md`.

Scan `task-id`'s line and every loaded artifact for `[NEEDS CLARIFICATION]` markers.

> If markers exist: ask whether to proceed if interactive; stop `blocked (upstream clarifications)` and list them if the run is non-interactive or the caller declines.

### 4. Execute the task

1. Apply the change described by `task-id`.
2. Run scoped tests for the touched files only (full suite only if `task-id` explicitly requires it).
3. If the task fails: retry up to `maxFixCycles` (config, default `3`). Still failing: mark `task-id` `[!]` in `tasks.md`, stop `blocked (task failure)`.
4. On success: flip `[ ]` → `[X]` for `task-id` in `tasks.md`.
5. If execution reveals undocumented work: append it under `## Discovered Subtasks` with the next `D###` ID.

### 5. Report

Report: `feature-dir` and `tasks.md` path; `task-id`; one-line result note; test result; `[NEEDS CLARIFICATION]` markers carried or placed; discovered subtasks appended; optional artifacts missing; overall status (`ok` / `ok (already complete)` / `blocked (...)`).

</workflow>

<done_conditions>

## Done Conditions

- `task-id` is `[X]` in `tasks.md`, or a `blocked` condition is reported with full context.
- The `tasks.md` write touched only `task-id`'s marker.
- No task detail was invented; unresolved ambiguity carries a `[NEEDS CLARIFICATION]` marker.
- Completion report given per Step 5.

</done_conditions>
