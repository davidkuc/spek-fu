# Orchestration Format

Delegation message and report formats for `spec-orchestrator`.

## Delegation message (per `spec-implement-executor` spawn)

```
Task ID: T###
Description: [task description from tasks.md]
Feature directory: [feature-dir]
Tasks file: [tasks.md path in feature-dir]
References: [@ref: hint, if present]
Recovered lesson: [lesson from framework-compounding-agent read, if this is an informed retry; otherwise omit]
Test scope: run scoped/targeted tests for this task by default; wide suite only if the task requires it.
Do not proceed beyond this task until acknowledged.
Do not commit changes to Git unless this task's own description instructs it.
```

One task-id per spawn, never a batch. A `[P]` batch is N concurrent spawns in one turn, each carrying one task-id.

## Phase Report (after each phase)

```
## Phase Report — [phase name/number]

Scope: [task count]
Delegations: [n] succeeded, [n] failed, [n] skipped
Blocked: [!] count and skipped dependents
Remaining phases: [phases with runnable [ ] tasks, from a fresh read of tasks.md]
```

## Orchestration Report (once, at the end)

```
## Orchestration Report

Phases coordinated: [name/number, scope, task count] per phase
Total delegations: [n] succeeded, [n] failed, [n] skipped
Blocked tasks: [!] count and skipped dependents, as reported by spec-implement-executor
Manual tasks skipped: [count, with task IDs]
Remaining phases: [phases with runnable [ ] tasks, from a fresh read of tasks.md]
```
