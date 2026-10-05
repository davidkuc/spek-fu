---
name: spec-orchestrator
description: "Coordinates end-to-end multi-agent execution of a completed tasks.md by delegating exactly one task per subagent spawn, phase by phase."
---

# Spec Orchestrator

Reads `tasks.md` from a completed Plan phase and coordinates its execution by spawning `spec-implement-executor` once per task, respecting phase order, `[P]` parallelism, and `[!]` blockers. Never implements a task, never mutates `tasks.md` or any spec file directly.

Delegation and report formats: `spek-fu/plugins/spec/knowledge/orchestration-format.md`

## When to use

Implement phase entry point, after `spec-tasks-draft`, to coordinate a completed `tasks.md` end-to-end across phases. Does not draft tasks, implement them itself, or make design decisions.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `scope` (optional; a single phase name/number — defaults to all phases end-to-end)

</inputs>

<outputs>

## Outputs

- Delegated code changes and `tasks.md` marker updates — performed entirely inside spawned agents, never by this skill
- Phase Report per phase; Orchestration Report at the end
- Overall status: `ok` | `partial` | `blocked` | `fail`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

1. Never implement a task directly — always spawn `spec-implement-executor` for it.
2. Never mutate `tasks.md` or any spec file directly — all writes happen inside spawned agents.
3. Never begin delegating until `tasks.md` exists with at least one `[ ]` task; stop `blocked` otherwise.
4. Never delegate a task marked `[MANUAL]` — skip it and record it.
5. Never delegate a task downstream (later in the same phase) of a `[!]` blocked task — skip it and record it.
6. Never commit to Git except through a task's own `[C-{phase}]` delegation, exactly as tasks.md describes it.
7. Never batch more than one `task-id` per `spec-implement-executor` spawn — a `[P]` group is concurrent single-task spawns in one turn, not one multi-task spawn.
8. By default, coordinate every phase in `tasks.md` end-to-end without pausing; the only interactive gate is an upstream `[NEEDS CLARIFICATION]` marker.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every status line and report entry uses the fewest words that preserve meaning, per constitution `## AI Principles`.

**Delegation-Only** — this skill spawns agents and reports; it never edits code or files itself.

**Respect Dependencies** — `[P]` tasks in a phase run concurrently; all other tasks run in file order; nothing runs downstream of an unresolved `[!]`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Resolve paths

Resolve `spec-file`: if provided use it, otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`. `feature-dir` is its parent directory.

> If no match, or `tasks.md` is absent from `feature-dir`: stop, report `blocked (missing artifact)`, instruct the user to run `spec-tasks-draft` first.

### 2. Parse task state and scope

Read `tasks.md`. Extract task markers (`[ ]`, `[X]`, `[!]`), phase boundaries, and any `[NEEDS CLARIFICATION]` marker.

- No `scope`: target every phase, in file order.
- `scope` names a phase: target that phase only.
- Every task already `[X]`/`[!]`: report status and stop.

> If `[NEEDS CLARIFICATION]` markers exist: surface them and ask the user before delegating anything in the affected phase.

### 3. Detect blocked dependencies

Within the targeted phase(s), for each `[!]` task, treat every later task in the same phase as a downstream dependent unless independence is evident (e.g. a different `[USN]` or unrelated file path). Skip those dependents — do not delegate them — and record them.

### 4. Delegate one phase at a time

Walk the phase's tasks in file order:

1. Skip `[MANUAL]` tasks and tasks skipped per Step 3.
2. Group consecutive `[P]` tasks into one batch; spawn `spec-implement-executor` concurrently, one Agent call per `task-id`, in a single turn; wait for the whole batch.
3. Spawn non-`[P]` tasks alone; wait for completion before the next task.
4. Use the delegation message format in `orchestration-format.md` for every spawn.

**On `blocked`/`fail`**: spawn `framework-compounding-agent` (read mode) against the failure text. If a lesson returns, re-spawn `spec-implement-executor` once more with it attached. Still failing: leave the task's `[!]` marker (set by `spec-implement-executor`), skip its dependents, and record it.

### 5. Report the phase

Produce a Phase Report (format in `orchestration-format.md`) from a fresh read of `tasks.md`.

### 6. Loop or complete

- Remaining phases exist and no `scope` override was given: continue to the next phase's Step 3 without pausing.
- All targeted phases coordinated: produce the Orchestration Report, report overall status, and stop.

</workflow>

<done_conditions>

## Done Conditions

- Every runnable task in scope was delegated, or recorded as skipped/blocked with a reason.
- `tasks.md` and all spec files were touched only by spawned agents, never by this skill directly.
- A Phase Report was produced per phase and an Orchestration Report at the end (Step 5, Step 6).
- No `[NEEDS CLARIFICATION]` marker was silently skipped.

</done_conditions>
