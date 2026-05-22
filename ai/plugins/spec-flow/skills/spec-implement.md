---
id: "spec-implement"
recommended-tier: "standard-agent"
version: 1.1
description: "Executes a targeted phase (or explicit set of phases) from tasks.md, using lazy context loading, progress tracking, and bounded task-failure escalation. Defaults to the next single incomplete phase unless the user explicitly requests more. USE FOR: executing one implementation phase at a time from a tasks.md plan after spec-tasks-draft has completed. DO NOT USE FOR: generating tasks, drafting specs, evaluating spec quality, or making architectural changes outside the task plan."
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
Executes a **targeted phase** from `tasks.md` in `feature-dir` — defaulting to the next single incomplete phase unless the user explicitly requests a different scope. The skill loads the plan first, scans for upstream `[NEEDS CLARIFICATION]` markers before implementation, manages project setup from shared **tech-stack patterns** when the first phase is in scope, lazy-loads only the design artifacts needed for each task, marks completed tasks as `[X]`, marks unrecoverable continued failures as `[!]`, and produces a structured **Implementation Summary** including remaining phases.

**Scope boundary**: This skill executes the task plan in `tasks.md` only. It does NOT generate tasks, draft or modify spec files, or make design decisions beyond what `tasks.md` specifies. For task plan generation, use **spec-tasks-draft**. For single-task execution without orchestration, use **impl-implement**.

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
- Apply `ai/plugins/spec-flow/knowledge/skill-meta-rules.md` before acting.
- Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` whenever reading tasks, design artifacts, or checklists.
- Apply `ai/plugins/spec-flow/knowledge/needs-clarification-protocol.md` whenever creating or carrying `[NEEDS CLARIFICATION]` markers.
- Apply `ai/plugins/spec-flow/knowledge/tech-stack-patterns.md` whenever verifying ignore files or selecting build/test commands.

## Operational Anchors
- If a task detail is ambiguous and cannot be resolved from the lazily loaded artifacts, place `[NEEDS CLARIFICATION: <specific question>]` in the task description or implementation summary — do not guess.
- Detect run state before acting: scan `tasks.md` for `[X]`, `[ ]`, and `[!]` tasks; identify the first phase containing runnable `[ ]` tasks as the default execution scope — do not re-execute completed tasks and do not automatically retry blocked tasks.
- Before implementation begins, scan `tasks.md` and every loaded design artifact for carried `[NEEDS CLARIFICATION]` markers. If any exist and `vscode_askQuestions` is available, warn and confirm before continuing. If interactive confirmation is unavailable, stop with `blocked (upstream clarifications)`.
- Anti-drift: if executing a task reveals adjacent work not covered by any existing task, append it under `## Discovered Subtasks` in `tasks.md` as `- [ ] D### <description>` — do not fix it inline.

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

Determine which phase(s) to execute in this run:

1. Parse all phases from `tasks.md` and build a phase inventory:
  - For each phase: name, task count, completed `[X]` count, blocked `[!]` count, runnable `[ ]` count, and status (`complete`, `in-progress`, `blocked`, or `not-started`)
2. Identify the **default scope**: the first phase that contains runnable `[ ]` tasks after excluding already-complete `[X]` tasks and already-blocked `[!]` tasks.
3. Apply the `scope` input (if provided):
   - `"all"` or `"all remaining"` → scope = all phases that are not fully complete, executed sequentially
   - Phase name or number (e.g., `"Phase 1"`, `"Setup"`, `"2"`) → scope = that specific phase only
   - Task ID range (e.g., `"T005-T012"`) → scope = only those tasks, regardless of phase boundaries
  - If the specified scope is already fully complete or only contains `[!]` tasks → report `ok` (already done) or `ok (partial, blocked tasks)` as appropriate and stop
4. If no `scope` input and user arguments do not mention quantity or phase → use the default scope (next single incomplete phase). Do NOT ask the user — just apply the default and state it clearly in the output.
5. If user arguments mention multiple phases or an ambiguous quantity, and no explicit `scope` input is set → ask via `vscode_askQuestions` using the `execution_scope` payload before proceeding.
6. Once the scope is known, load from `spec.md` only the acceptance scenarios for the user story phases in scope (via `grep_search` or equivalent targeted reads). Do not load unrelated story sections.

**Display a scope confirmation** before executing:
```
Execution scope: <phase name(s) or task range>
Reason: <user-specified | default — next incomplete phase>
Remaining after this run: <list of phase names not in scope>
```

## Step 4 — Project setup verification

Project setup runs only when the resolved scope from Step 3 is the first phase or includes Phase 1 (Setup). For mid-plan runs, skip this step.

When setup is in scope:
1. Read `ai/plugins/spec-flow/knowledge/tech-stack-patterns.md` via `read_file` (multi-pass if needed).
2. Detect the stack from `research.md` when it exists, using the existing stack-detection logic.
3. If `research.md` is absent, apply **Universal** patterns only.
4. Verify or create ignore files using the patterns from `tech-stack-patterns.md`:
  - `.gitignore`
  - `.dockerignore` when Docker is detected
  - `.eslintignore` or `eslint.config.*` ignore entries when ESLint is present
  - `.prettierignore` when Prettier is present
5. If an ignore file already exists, append only missing required patterns for the detected stack.
6. If an ignore file is missing, create it from the shared pattern set.

## Step 5 — Execute implementation

Execute only the tasks within the resolved scope from Step 3:

**Phase execution rules**:
1. Execute only phases within the resolved scope — stop after the last in-scope phase even if more phases remain in `tasks.md`.
2. Within a phase, execute tasks without `[P]` sequentially in listed order.
3. Tasks marked `[P]` that operate on different files with no incomplete dependencies may proceed concurrently or in close sequence.
4. Follow TDD: execute test tasks before their corresponding implementation tasks within the same phase.
5. Before starting each task, lazy-load only the design context that task needs:
  - Always load the relevant acceptance scenarios for the task's user story from `spec.md` when the task belongs to a user story phase.
  - For contract test or endpoint tasks, load only the referenced contract file from `contracts/`.
  - For model or entity tasks, load only the relevant section of `data-model.md`.
  - For BDD test tasks, load only the matching `TDD-XXX` block from `tdd-designer/report.md`.
  - When a task description includes an `@ref:` hint, treat that hint as the authoritative artifact fragment to load.
  - Load `test-expert/testability-assessment.md` or `quickstart.md` only when the task explicitly depends on those expectations.
6. After completing each task:
   - Apply the change (create or modify the target file per the task description).
   - Update `tasks.md`: replace `- [ ]` with `- [X]` for the completed task ID.
   - Report the task ID and one-line completion note.
7. If a task fails:
  - Attempt up to `config["spec-implement"].maxFixCycles` fix cycles (fix the error, re-run, verify). *(default: 3 — loaded during Preflight from `ai/plugins/spec-flow/skills/config.json`)*
  - If the task still fails after `maxFixCycles` cycles and `vscode_askQuestions` is available, present the `task_failure_escalation` payload.
  - If the user chooses **Mark blocked and continue phase (skip dependents)**: mark the task as `[!]`, skip downstream tasks in the same phase that depend on it, continue runnable parallel or independent tasks, and record the block for Step 6.
  - If the user chooses **Mark blocked and stop this run**: stop with `blocked (task failure)`.
  - If the user chooses **Manually edit and retry the task**: re-read the task context, reset the fix-cycle counter, and retry.
  - If the task still fails and the run is non-interactive: stop with `blocked (task failure)` and report the task ID plus the one-line error summary.
8. If executing a task reveals new required work outside the current task list, append a new discovered subtask under `## Discovered Subtasks` at the end of `tasks.md` using the next `D###` ID.

**Build and test after each phase** (when a build manifest is present):
- Use `ai/plugins/spec-flow/knowledge/tech-stack-patterns.md` to discover build manifests and the matching build/test command family for the detected stack.
- Prefer repository-defined commands over generic defaults when the manifest exposes them.
- If no stack-specific manifest is found, skip build/test and note the reason.
- Report build and test results in the phase completion note

> **If no build manifest is found**: skip build/test steps and note "No build manifest detected" in the phase summary.

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
Input: No arguments; current git branch is `003-payment-flow`; `feature-dir` resolves to `features/003-payment-flow/`; tasks.md has 3 phases (Setup 3 tasks, User Story 1 5 tasks, Polish 4 tasks), 0 already completed.
Expected behavior: Step 1 resolves `feature-dir` via branch detection. Step 2 loads `tasks.md`, `spec.md`, and `research.md`, scans for upstream markers, and records any optional artifacts not present. Step 3 resolves scope: no explicit scope input → default = Phase 1 (Setup, 3 tasks); displays scope confirmation. Step 4 reads `tech-stack-patterns.md` and verifies ignore files because Setup is in scope. Step 5 executes Setup only, lazy-loads only the task-specific context needed, marks T001–T003 as [X], and runs build/test using the stack-specific manifest rules. Step 6 returns an **Implementation Summary** showing 3/12 tasks completed this run and the remaining phases. Status: ok.
</example>

<example>
Input: `feature-dir=features/007-notifications/`; scope="all remaining"; some tasks in tasks.md already marked `[X]`; `research.md` contains `[NEEDS CLARIFICATION: confirm notification provider]`.
Expected behavior: Step 1 uses the provided `feature-dir` path directly. Step 2 loads baseline context, detects the upstream clarification marker, and calls `vscode_askQuestions` using `upstream_clarifications`. If the user confirms yes, Step 3 resolves scope: `all remaining` → all phases with runnable `[ ]` tasks. Step 4 skips project setup when Phase 1 is already complete. Step 5 executes the remaining phases sequentially while carrying the clarification count into the final report.
</example>

<example type="counter">
Input: User says "implement everything" without specifying a scope or phase.
Expected behavior: The word "everything" is treated as equivalent to `all`. Step 3 resolves scope = all remaining incomplete phases and displays the scope confirmation listing every pending phase before executing. Skill does NOT silently execute all phases without first showing the scope confirmation.
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
