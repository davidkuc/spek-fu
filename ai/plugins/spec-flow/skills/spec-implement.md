---
id: "spec-implement"
recommended-tier: "standard-agent"
version: 1.1
description: "Executes a targeted phase (or explicit set of phases) from tasks.md within a spec-flow feature directory, using lazy context loading, progress tracking, and bounded task-failure escalation. Requires spec-flow artifacts: tasks.md, spec.md, and a resolved feature-dir. This is the implementation skill for the spec-flow pipeline. Defaults to the next single incomplete phase unless the user explicitly requests more. USE FOR: executing one implementation phase at a time from a tasks.md plan after spec-tasks-draft has completed; feature work with an active spec-flow branch and spec.md present. DO NOT USE FOR: generating tasks, drafting specs, evaluating spec quality, making architectural changes outside the task plan, or implementation without spec-flow artifacts — for non-spec-flow implementation, use impl-implement."
anti-scope: "Does not generate tasks, draft specs, modify design artifacts, or make architectural decisions beyond what tasks.md specifies. For task plan generation, use spec-tasks-draft. For implementation of a single task without orchestration, use impl-implement."
tags:
  - "implementation"
  - "specification"
  - "tasks"
  - "build"
inputs:
  - "Feature context or arguments from the user or orchestrator (optional)"
  - "scope: phase name, phase number, task ID range, or 'all' / 'all remaining' to override the default single-phase execution (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Implemented codebase changes for the targeted phase(s), with each completed task marked [X] in tasks.md and failed tasks optionally marked [!] when the user chooses to continue"
  - "Execution status: ok, ok (all complete), ok (partial, blocked tasks), blocked, or fail"
  - "Implementation summary: scope executed, task outcomes, build and test results, upstream clarifications, discovered subtasks, and remaining phases"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` as a fallback when `feature-dir` cannot be resolved and when the execution scope is ambiguous; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-implement

<!-- SECTION 1: Identity (primacy position) -->
Executes a **targeted phase** from `tasks.md` in `feature-dir`. Defaults to the next single incomplete phase unless otherwise specified. Loads the plan, scans for upstream markers, manages project setup, lazy-loads design artifacts, marks tasks as `[X]` or `[!]`, and produces an **Implementation Summary** with remaining phases.

**Scope boundary**: Executes task plans from `tasks.md` only. Does NOT generate tasks, draft specs, or make design decisions beyond what `tasks.md` specifies.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER begin implementing tasks before resolving `feature-dir` and confirming `tasks.md` exists — WHY: all paths are environment-specific and hard-coded paths silently break in other workspaces.
2. NEVER execute more than the targeted phase(s) unless the user explicitly uses the word "all" or specifies multiple phases — default to the next single incomplete phase — WHY: phase-at-a-time execution keeps changes reviewable and prevents runaway implementation beyond what the user intended.
3. NEVER invent task details absent from `tasks.md` or the lazily loaded design artifacts — place `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty — WHY: invented scope silently corrupts the implementation and breaks plan traceability.
4. NEVER skip test tasks that appear before their corresponding implementation tasks within a phase — WHY: the TDD sequence in tasks.md is authoritative; violating it breaks the testing contract.
5. ALWAYS mark each completed task as `[X]` in `tasks.md` immediately after it finishes, and preserve any `[!]` tasks as blocked rather than silently resetting them — WHY: progress tracking and resume correctness depend on the task-state markers staying accurate across runs.
6. NEVER proceed to dependent work after a task has been marked `[!]` during the current run — skip downstream tasks in the same phase that depend on it, and do not retry `[!]` tasks automatically on later runs — WHY: blocked tasks represent known unresolved failures and dependent work would build on a broken prerequisite.
7. NEVER make refactoring changes, add unrequested features, or fix adjacent issues outside the task description — append discovered work as a subtask instead — WHY: unreviewed changes corrupt plan traceability and introduce regressions.
8. ALWAYS surface upstream `[NEEDS CLARIFICATION]` markers before implementation begins — ask whether to proceed when interactive, and stop with `blocked (upstream clarifications)` when non-interactive — WHY: implementation must not silently normalize unresolved design uncertainty into code.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `skill-meta-rules.md`, `paginated-read.md`, `needs-clarification-protocol.md`, and `tech-stack-patterns.md` before acting.

## Operational Anchors
- Place `[NEEDS CLARIFICATION]` when task details are ambiguous; do not guess.
- Detect run state: scan `tasks.md` for `[X]` and `[!]` tasks; identify first phase with runnable `[ ]` tasks as default scope.
- Surface upstream markers before implementation begins; warn and confirm before continuing if interactive.
- Anti-drift: append undocumented work as subtasks; do not fix inline.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve user context or arguments from the invocation before acting.
- Environment Preflight must complete before Step 1 when `env` is `devcontainer`.
- Read `ai/plugins/spec-flow/skills/config.json`; extract `config["spec-implement"].maxFixCycles` and default to `3` if absent.

## Done conditions

- **ok**: All tasks in the targeted phase(s) are marked `[X]`, build and tests pass or are explicitly skipped, and the **Implementation Summary** has been shown with remaining phases listed.
- **ok (all complete)**: Every runnable task in `tasks.md` is `[X]` and no `[!]` tasks remain — no remaining phases.
- **ok (partial, blocked tasks)**: The targeted scope completed as far as possible, one or more tasks were marked `[!]` after escalation, and the **Implementation Summary** lists the blocked tasks and skipped dependents.
- **blocked (missing artifact)**: `tasks.md` is absent — report the missing file and suggest running `spec-tasks-draft` first.
- **blocked (upstream clarifications)**: `tasks.md` or a loaded design artifact contains one or more `[NEEDS CLARIFICATION]` markers and the user declined to proceed, or the run is non-interactive.
- **blocked (task failure)**: A task failed after max fix cycles and the user chose to stop, or the run is non-interactive.
- **fail**: An unrecoverable error occurred — report context and stop.

## Step 1 — Resolve paths

Resolve `feature-dir` and `available-docs`:
- Resolve `feature-dir` via **Branch Detection** first: apply the core procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md`. If the user provides a path, use it as `feature-dir`.
- Use `list_dir` on `feature-dir` to obtain `available-docs` (list all files and subdirectories).

> **If `feature-dir` cannot be resolved**: stop with status `blocked` and report the blocker.
> **If `tasks.md` is absent from `available-docs`**: stop with status `blocked` and suggest running `spec-tasks-draft` first.

## Step 2 — Load implementation context

Using `feature-dir` and `available-docs` from Step 1, load only the baseline context needed to choose work safely:

**Required**:
- `tasks.md` — load the full file. Extract all phases, task IDs, dependencies, `[P]` markers, completed `[X]` tasks, blocked `[!]` tasks, and any existing `## Discovered Subtasks` section.

**Tier 1 optional context** (load only if listed in `available-docs`):
- `spec.md` — extract the feature intent, description, and implementation constraints needed for the run. Defer story-specific acceptance scenarios until the targeted scope is known.
- `technical-plan.md` — extract project structure, build/test cues, and artifact references when present.
- `research.md` — extract stack and tooling cues when present; this is the source for tech-stack detection in Step 3.

**Tier 2 on-demand context** (do NOT bulk-load here):
- `contracts/`
- `data-model.md`
- `tdd-designer/report.md`
- `test-expert/testability-assessment.md`
- `quickstart.md`

Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` to each loaded document.

After loading the baseline context:
1. Record which optional artifacts are absent for the final report.
2. Scan `tasks.md` and every loaded design artifact for `[NEEDS CLARIFICATION]` markers.
3. If any markers exist and `vscode_askQuestions` is available, present the `upstream_clarifications` payload listing the markers and ask whether to proceed.
4. If the user declines, stop with `blocked (upstream clarifications)`.
5. If markers exist and the run is non-interactive, stop with `blocked (upstream clarifications)` and list the markers in the response.

Identify the first phase containing runnable `[ ]` tasks (ignoring `[X]` and already-blocked `[!]` tasks). This is the default execution scope for Step 3. If every task is `[X]`, report `ok (all complete)` and stop. If no runnable `[ ]` tasks remain but one or more `[!]` tasks are present, report `ok (partial, blocked tasks)` and stop.

## Step 3 — Resolve execution scope

1. Parse phases from `tasks.md` and build inventory (name, task count, `[X]` count, `[!]` count, runnable `[ ]` count, status).
2. Identify **default scope**: first phase with runnable `[ ]` tasks.
3. Apply `scope` input (if provided): `all`/`all remaining` for all incomplete phases, phase name/number for one phase, task ID range for specific tasks.
4. Use default scope (next incomplete phase) without asking if no explicit input provided. Do NOT ask the user—state it clearly in output.
5. If ambiguous quantity without explicit scope, ask via `vscode_askQuestions` using `execution_scope` payload before proceeding.
6. Once scope is known, load from `spec.md` only acceptance scenarios for in-scope user story phases (via targeted reads).

**Display a scope confirmation** before executing:
```
Execution scope: <phase name(s) or task range>
Reason: <user-specified | default — next incomplete phase>
Remaining after this run: <list of phase names not in scope>
```

## Step 4 — Project setup verification

Project setup runs only when resolved scope includes Phase 1 (Setup). When in scope:
1. Read `tech-stack-patterns.md` via `read_file` (multi-pass if needed).
2. Detect stack from `research.md` when available; otherwise apply Universal patterns.
3. Verify/create ignore files (`.gitignore`, `.dockerignore` for Docker, `.eslintignore` for ESLint, `.prettierignore` for Prettier).
4. For existing files, append missing patterns; for missing files, create from pattern set.

## Step 5 — Execute implementation

**Phase execution rules**:
1. Execute phases within resolved scope only; stop after last in-scope phase.
2. Execute non-`[P]` tasks sequentially in listed order.
3. `[P]` tasks on different files with no dependencies may proceed concurrently.
4. Follow TDD: test tasks before implementation tasks within a phase.
5. Before each task, lazy-load only needed design context:
   - Acceptance scenarios from `spec.md` for user story phases
   - Relevant contract file from `contracts/`
   - Relevant section of `data-model.md`
   - Matching `TDD-XXX` block from `tdd-designer/report.md`
   - Fragment named in `@ref:` hint
   - `test-expert/testability-assessment.md` or `quickstart.md` only when task explicitly requires it
6. After each completed task: apply change, update `tasks.md` (`[ ]` → `[X]`), report task ID and one-line note.
7. If task fails: attempt up to `maxFixCycles` fix attempts (default: 3). If still failing and interactive: present `task_failure_escalation` payload. If non-interactive: stop with `blocked (task failure)`.
8. If task execution reveals undocumented work: append under `## Discovered Subtasks` with next `D###` ID.

## Step 6 — Report

Produce the **Implementation Summary** after all phases complete (or after stopping due to a block):
- List all phases with task counts and completion status
- Total tasks completed vs. total tasks in plan
- Build result for each phase where a build was run
- Test result for each phase where tests were run
- Any upstream or newly placed `[NEEDS CLARIFICATION]` markers
- Blocked `[!]` tasks and skipped dependents (if any)
- Discovered subtasks appended to `tasks.md` (if any)
- Overall status: `ok`, `ok (all complete)`, `ok (partial, blocked tasks)`, or `blocked`

The skill is complete when all tasks in the **resolved scope** are marked `[X]` and the **Implementation Summary** has been shown (including remaining phases), OR when a `blocked` condition has been reported with full context.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Steps 2, 3, 4, 5, and 6 — read `tasks.md`, baseline context, lazy-loaded design artifacts, and `ai/plugins/spec-flow/knowledge/tech-stack-patterns.md`. Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` whenever a file may span multiple reads.
- **list_dir**: Steps 1 and 5 — enumerate `feature-dir` and `contracts/` when a task requires contract context.
- **run_in_terminal**: Steps 4 and 5 — run git detection, build commands, and test commands from workspace root.
- **file_search / grep_search**: Steps 3, 4, and 5 — locate targeted acceptance scenarios, ignore files, build manifests, and targeted artifact fragments such as `TDD-XXX` blocks.
- **create_file**: Steps 4 and 5 — create ignore files, new implementation files, and the `## Discovered Subtasks` section when it does not exist.
- **replace_string_in_file**: Steps 4 and 5 — patch existing ignore files, update task markers (`[X]` or `[!]`) in `tasks.md`, append discovered subtasks, and apply implementation changes to existing files.
- **vscode_askQuestions**: Step 1 fallback (`feature-dir` resolution when Branch Detection cannot resolve automatically), Step 2 (`upstream_clarifications`), Step 3 (`execution_scope` when ambiguity remains), and Step 5 (`task_failure_escalation`).
- Do NOT use tools not listed here unless this skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Implementation Summary** (Step 6):

```
## Implementation Summary

Feature: <feature name from spec.md or tasks.md>
feature-dir: <resolved path>
Scope executed: <phase name(s) or task range>

Phases in scope:
  Phase N — <name>: N tasks ✅ | N blocked [!] | N skipped dependents

Tasks completed (this run): N
Total tasks completed overall: N / N in plan
Tasks marked [X] in tasks.md: N
Tasks marked [!] in tasks.md: N

Build results:
  <Phase N>: ✅ SUCCESS (N errors, N warnings) | ❌ FAILED | ⏭ SKIPPED

Test results:
  <Phase N>: ✅ PASSED (N passed) | ❌ FAILED (N failed) | ⏭ SKIPPED

[NEEDS CLARIFICATION] markers carried or placed: N
  - <task ID>: <question>

Blocked tasks:
  - <task ID>: <one-line failure summary>

Skipped dependents:
  - <task ID>: skipped because dependency <task ID> is [!]

Optional artifacts missing: <list or "None">

Discovered subtasks appended:
  - D### <description>

Remaining phases (not executed this run):
  - Phase N — <name>: N tasks pending
  ...
  Run again to continue, or pass scope="all remaining" to execute all at once.

Status: ok | ok (all complete) | ok (partial, blocked tasks) | blocked
Blocker (if any): <task ID, error summary, or "None">
```
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: No arguments; git branch: `003-payment-flow`; tasks.md has 3 phases (Setup 3, US1 5, Polish 4), 0 completed.
Expected: Step 1 resolves `feature-dir`. Step 2 loads baseline context, records optional artifacts missing. Step 3 → default scope = Phase 1 (Setup). Step 4 reads patterns, verifies ignore files. Step 5 executes Setup, marks T001–T003 as `[X]`, runs build/test. Step 6 reports 3/12 tasks completed, remaining phases. Status: ok.
</example>

<example>
Input: `feature-dir=features/007-notifications/`; scope="all remaining"; some tasks marked `[X]`; `research.md` contains `[NEEDS CLARIFICATION]`.
Expected: Step 1 uses provided path. Step 2 detects upstream marker, calls `vscode_askQuestions`. If confirmed, Step 3 → scope = all remaining. Step 4 skips setup. Step 5 executes sequentially, carrying clarification count to final report. Status: ok.
</example>

<example type="counter">
Input: "implement everything" without scope or phase.
Expected: "everything" treated as `all`. Step 3 → scope = all remaining phases; displays confirmation listing every pending phase before executing. Does NOT silently execute all phases.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- Constraint 2 — do not execute beyond the resolved scope without explicit instruction.
- Constraint 5 — mark completed tasks `[X]` immediately and preserve `[!]` markers.
- Constraint 7 — do not fix adjacent issues outside the task description.
- Constraint 1 — resolve `feature-dir` and confirm `tasks.md` before implementation begins.
- Constraint 8 — surface upstream clarification markers before implementing.

## Question Payloads

### `upstream_clarifications`

```json
{
  "header": "upstream_clarifications",
  "question": "Upstream artifacts still contain [NEEDS CLARIFICATION] markers. Do you want to proceed with implementation anyway?",
  "options": [
    { "label": "Yes — proceed with implementation" },
    { "label": "No — stop until the upstream clarifications are resolved" }
  ],
  "allowFreeformInput": true
}
```

### `execution_scope`

```json
{
  "header": "execution_scope",
  "question": "Which phase(s) should be executed in this run?",
  "options": [
    { "label": "Next incomplete phase only (default)", "recommended": true },
    { "label": "All remaining incomplete phases" },
    { "label": "Specify a phase name or number" }
  ],
  "allowFreeformInput": true
}
```

### `task_failure_escalation`

```json
{
  "header": "task_failure_escalation",
  "question": "Task <T-ID> failed after <maxFixCycles> fix attempts. Error: <one-line summary>. How would you like to proceed?",
  "options": [
    { "label": "Mark blocked and continue phase (skip dependents)" },
    { "label": "Mark blocked and stop this run" },
    { "label": "Manually edit and retry the task" }
  ],
  "allowFreeformInput": true
}
```

</reminders>
