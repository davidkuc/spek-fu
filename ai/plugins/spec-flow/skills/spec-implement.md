---
id: "spec-implement"
recommended-tier: "standard-agent"
version: 1.0
description: "Executes a targeted phase (or explicit set of phases) from tasks.md, with checklist gate verification and progress tracking. Defaults to the next single incomplete phase unless the user explicitly requests more. USE FOR: executing one implementation phase at a time from a tasks.md plan after spec-tasks-draft has completed. DO NOT USE FOR: generating tasks, drafting specs, evaluating spec quality, or making architectural changes outside the task plan."
anti-scope: "Does not generate tasks, draft specs, modify design artifacts, or make architectural decisions beyond what tasks.md specifies. For task generation, use spec-tasks-draft. For implementation of a single task without orchestration, use impl-implement."
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
  - "Implemented codebase changes for the targeted phase(s), with each completed task marked [X] in tasks.md"
  - "Execution status: ok, ok (partial), blocked, or fail"
  - "Implementation summary: scope executed, tasks completed, build and test results, remaining phases"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` as a fallback when FEATURE_DIR cannot be resolved and when the execution scope is ambiguous; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-implement

<!-- SECTION 1: Identity (primacy position) -->
Executes a **targeted phase** from `tasks.md` in `FEATURE_DIR` — defaulting to the next single incomplete phase unless the user explicitly requests a different scope. The skill verifies checklist gates before starting, loads the full implementation context (plan, data model, contracts, research), manages project setup (ignore files on the first phase), executes only the in-scope tasks in dependency order, marks each completed task as `[X]` in `tasks.md`, and produces a structured **Implementation Summary** including remaining phases.

**Scope boundary**: This skill executes the task plan in `tasks.md` only. It does NOT generate tasks, draft or modify spec files, or make design decisions beyond what `tasks.md` specifies. For task plan generation, use **spec-tasks-draft**. For single-task execution without orchestration, use **impl-implement**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER begin implementing tasks before resolving FEATURE_DIR and confirming `tasks.md` exists — WHY: all paths are environment-specific and hard-coded paths silently break in other workspaces.
2. NEVER execute more than the targeted phase(s) unless the user explicitly uses the word "all" or specifies multiple phases — default to the next single incomplete phase — WHY: phase-at-a-time execution keeps changes reviewable and prevents runaway implementation beyond what the user intended.
3. NEVER proceed past the checklist gate if any checklist file has incomplete items, unless the user explicitly confirms — WHY: incomplete checklists indicate pre-implementation gates have not been satisfied, risking untested or unreviewed implementation.
4. NEVER invent task details absent from `tasks.md` or the loaded design artifacts — place `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty — WHY: invented scope silently corrupts the implementation and breaks plan traceability.
5. NEVER skip test tasks that appear before their corresponding implementation tasks within a phase — WHY: the TDD sequence in tasks.md is authoritative; violating it breaks the testing contract.
6. ALWAYS mark each completed task as `[X]` in `tasks.md` immediately after it finishes — WHY: progress tracking and resume correctness depend on the checklist state being up to date.
7. NEVER proceed to the next phase if a blocking (non-parallel) task in the current phase fails — WHY: dependent tasks in subsequent phases will produce incorrect results if their prerequisites are incomplete.
8. NEVER make refactoring changes, add unrequested features, or fix adjacent issues outside the task description — report discovered problems as subtasks instead — WHY: unreviewed changes corrupt plan traceability and introduce regressions.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what each task in `tasks.md` specifies — no extra features, no unrequested changes.
- If a task detail is ambiguous and cannot be resolved from loaded artifacts, place `[NEEDS CLARIFICATION: <specific question>]` in the task description — do not guess.
- Detect run state before acting: scan `tasks.md` for already-checked `[X]` tasks; identify the first incomplete phase as the default execution scope — do not re-execute completed tasks.
- Anti-drift: if executing a task reveals an adjacent problem not covered by any task, report it as a discovered subtask — do not fix it inline.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `FEATURE_DIR` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve user context or arguments from the invocation before acting.
- Environment Preflight must complete before Step 1 when `env` is `devcontainer`.

## Done conditions

- **ok**: All tasks in the targeted phase(s) are marked `[X]`, build and tests pass, and the **Implementation Summary** has been shown with remaining phases listed.
- **ok (all complete)**: Every task in `tasks.md` is `[X]` — no remaining phases.
- **blocked (checklist)**: One or more checklists are incomplete and the user has not confirmed proceeding — report which checklists are failing and stop.
- **blocked (missing artifact)**: `tasks.md` is absent — report the missing file and suggest running `spec-tasks-draft` first.
- **blocked (task failure)**: A blocking (non-parallel) task failed after max fix cycles — report the failure and stop.
- **fail**: An unrecoverable error occurred — report context and stop.

## Step 1 — Resolve paths

Resolve FEATURE_DIR and AVAILABLE_DOCS:
- Resolve **FEATURE_DIR** via **Branch Detection** first: apply the core procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md`. If the user provides a path, use it as `FEATURE_DIR`.
- Use `list_dir` on FEATURE_DIR to obtain AVAILABLE_DOCS (list all files and subdirectories).

> **If FEATURE_DIR cannot be resolved**: stop with status `blocked` and report the blocker.
> **If `tasks.md` is absent from AVAILABLE_DOCS**: stop with status `blocked` and suggest running `spec-tasks-draft` first.

## Step 2 — Checklist gate

If `FEATURE_DIR/checklists/` exists in AVAILABLE_DOCS:
1. Use `list_dir` to enumerate all checklist files in `checklists/`.
2. For each checklist file, read it and count:
   - **Total items**: all lines matching `- [ ]` or `- [X]` or `- [x]`
   - **Completed items**: lines matching `- [X]` or `- [x]`
   - **Incomplete items**: lines matching `- [ ]`
3. Display a status table:

   ```
   | Checklist    | Total | Completed | Incomplete | Status |
   |--------------|-------|-----------|------------|--------|
   | ux.md        | 12    | 12        | 0          | ✓ PASS |
   | test.md      | 8     | 5         | 3          | ✗ FAIL |
   | security.md  | 6     | 6         | 0          | ✓ PASS |
   ```

4. Calculate overall status:
   - **PASS**: All checklists have 0 incomplete items → automatically proceed to Step 3.
   - **FAIL**: One or more checklists have incomplete items → ask via `vscode_askQuestions` using the `checklist_gate` payload. If user declines, stop with status `blocked (checklist)`. If user confirms, proceed to Step 3.

If `checklists/` does not exist: skip to Step 3.

## Step 3 — Load implementation context

Using FEATURE_DIR and AVAILABLE_DOCS from Step 1, load documents:

**Required** (stop with `blocked` if absent):
- `tasks.md` — extract: all tasks, phases, dependencies, parallel `[P]` markers, completed `[X]` tasks

**Optional** (load only if listed in AVAILABLE_DOCS):
- `plan.md` — extract: tech stack, libraries, architecture, project structure, ignore file requirements
- `data-model.md` — extract: entities and relationships
- `contracts/` — enumerate with `list_dir`, then load each contract file — extract: API specifications and test requirements
- `research.md` — extract: technical decisions and constraints
- `quickstart.md` — extract: integration scenarios and developer onboarding

Use multi-pass `read_file` on each document: read from line 1 with a generous range; if the response fills the page, advance `startLine` and read again; repeat until the response is shorter than the page size.

Identify the first incomplete phase (the phase containing the first task not marked `[X]`) — this is the default execution scope for Step 5. If all tasks are already `[X]`, report `ok (all complete)` and stop.

## Step 4 — Project setup verification

Verify and create ignore files based on the tech stack detected from `plan.md` (if available):

**Detection logic** (run from workspace root):
- Check if `git rev-parse --git-dir 2>/dev/null` succeeds → verify or create `.gitignore`
- Check if `Dockerfile*` exists or Docker is referenced in `plan.md` → verify or create `.dockerignore`
- Check if `.eslintrc*` exists → verify or create `.eslintignore`
- Check if `eslint.config.*` exists → ensure the config's `ignores` entries cover required patterns
- Check if `.prettierrc*` exists → verify or create `.prettierignore`

**If an ignore file already exists**: read it, verify it contains essential patterns for the detected tech stack, append only missing critical patterns.
**If an ignore file is missing**: create it with the full standard pattern set for the detected technology (see technology patterns in the tech-stack reference below).

**Technology ignore patterns** (applied per tech stack detected in `plan.md`):
- **Node.js/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
- **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
- **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
- **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
- **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
- **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`
- **Universal** (always included): `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

> **If `plan.md` is absent**: skip technology-specific ignore file creation; only apply universal patterns to `.gitignore` if a git repo is detected.

> **Project setup (Step 4) runs only when the targeted scope is the first phase or includes phase 1 (Setup).** Skip for mid-plan phases.

## Step 5 — Resolve execution scope

Determine which phase(s) to execute in this run:

1. Parse all phases from `tasks.md` and build a phase inventory:
   - For each phase: name, task count, completed task count, status (complete / in-progress / not-started)
2. Identify the **default scope**: the first phase that is not fully complete (i.e., contains at least one task without `[X]`).
3. Apply the `scope` input (if provided):
   - `"all"` or `"all remaining"` → scope = all phases that are not fully complete, executed sequentially
   - Phase name or number (e.g., `"Phase 1"`, `"Setup"`, `"2"`) → scope = that specific phase only
   - Task ID range (e.g., `"T005-T012"`) → scope = only those tasks, regardless of phase boundaries
   - If the specified scope is already fully complete → report `ok` (already done) and stop
4. If no `scope` input and user arguments do not mention quantity or phase → use the default scope (next single incomplete phase). Do NOT ask the user — just apply the default and state it clearly in the output.
5. If user arguments mention multiple phases or an ambiguous quantity, and no explicit `scope` input is set → ask via `vscode_askQuestions` using the `execution_scope` payload before proceeding.

**Display a scope confirmation** before executing:
```
Execution scope: <phase name(s) or task range>
Reason: <user-specified | default — next incomplete phase>
Remaining after this run: <list of phase names not in scope>
```

## Step 6 — Execute implementation

Execute only the tasks within the resolved scope from Step 5:

**Phase execution rules**:
1. Execute only phases within the resolved scope — stop after the last in-scope phase even if more phases remain in `tasks.md`.
2. Within a phase, execute tasks without `[P]` sequentially in listed order.
3. Tasks marked `[P]` that operate on different files with no incomplete dependencies may proceed concurrently or in close sequence.
4. Follow TDD: execute test tasks before their corresponding implementation tasks within the same phase.
5. After completing each task:
   - Apply the change (create or modify the target file per the task description).
   - Update `tasks.md`: replace `- [ ]` with `- [X]` for the completed task ID.
   - Report the task ID and one-line completion note.
6. If a non-parallel task fails:
   - Attempt up to `config["spec-implement"].maxFixCycles` fix cycles (fix the error, re-run, verify). *(default: 3 — see `ai/plugins/spec-flow/skills/config.json`)*
   - If still failing after `maxFixCycles` cycles: report status `blocked (task failure)` with the failing task ID, error details, and stop.
7. For parallel `[P]` tasks that fail: report the failure but continue with other tasks in the phase; include the failure in the phase summary.

**Build and test after each phase** (when a build manifest is present):
- Discover build manifests: `*.sln`, `package.json`, `Cargo.toml`, `*.csproj`, `pyproject.toml`, `setup.py`
- Run the appropriate build command for the detected stack
- Run the appropriate test command
- Report build and test results in the phase completion note

> **If no build manifest is found**: skip build/test steps and note "No build manifest detected" in the phase summary.

## Step 7 — Report

Produce the **Implementation Summary** after all phases complete (or after stopping due to a block):
- List all phases with task counts and completion status
- Total tasks completed vs. total tasks in plan
- Build result for each phase where a build was run
- Test result for each phase where tests were run
- Any `[NEEDS CLARIFICATION]` markers placed during execution
- Discovered subtasks (if any)
- Overall status: `ok`, `ok (partial)`, or `blocked`

The skill is complete when all tasks in the **resolved scope** are marked `[X]` and the **Implementation Summary** has been shown (including remaining phases), OR when a `blocked` condition has been reported with full context.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Steps 2, 3, 4, and 5 — read checklist files, design artifacts, and `tasks.md`. Use multi-pass reads for large files.
- **list_dir**: Steps 1, 2, and 3 — enumerate FEATURE_DIR, `checklists/`, and `contracts/` directories.
- **run_in_terminal**: Steps 4 and 6 — run git detection, build commands, and test commands from workspace root.
- **file_search / grep_search**: Step 4 — locate ignore files and build manifests.
- **create_file**: Step 4 and Step 6 — create ignore files and new implementation files required by tasks.
- **replace_string_in_file**: Steps 4 and 6 — patch existing ignore files with missing patterns; mark tasks `[X]` in `tasks.md`; apply implementation changes to existing files.
- **vscode_askQuestions**: Step 2 (checklist gate), Step 5 (scope ambiguity), and Step 1 fallback (FEATURE_DIR resolution when Branch Detection cannot resolve automatically).
- Do NOT use tools not listed here unless this skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Standard Field Table**:

| Field | Value |
|-------|-------|
| status | `ok` \| `ok (partial)` \| `blocked` \| `fail` |
| skill_id | `spec-implement` |
| wave | `N` |
| step | `N.M` |
| output_path | `<FEATURE_DIR>/tasks.md` or `null` |
| summary | one-line summary of what was done |

**Checklist Gate Table** (Step 2, shown always):

```
| Checklist    | Total | Completed | Incomplete | Status |
|--------------|-------|-----------|------------|--------|
| <name>.md    | N     | N         | N          | ✓ PASS / ✗ FAIL |

Overall: ✓ PASS — proceeding to implementation  |  ✗ FAIL — awaiting user confirmation
```

**Implementation Summary** (Step 7):

```
## Implementation Summary

Feature: <feature name from plan.md or tasks.md>
FEATURE_DIR: <resolved path>
Scope executed: <phase name(s) or task range>

Phases in scope:
  Phase N — <name>: N tasks ✅ | ✗ N blocked

Tasks completed (this run): N
Total tasks completed overall: N / N in plan
Tasks marked [X] in tasks.md: N

Build results:
  <Phase N>: ✅ SUCCESS (N errors, N warnings) | ❌ FAILED | ⏭ SKIPPED

Test results:
  <Phase N>: ✅ PASSED (N passed) | ❌ FAILED (N failed) | ⏭ SKIPPED

[NEEDS CLARIFICATION] markers placed: N
  - <task ID>: <question>

Discovered subtasks: <list or "None">

Remaining phases (not executed this run):
  - Phase N — <name>: N tasks pending
  ...
  Run again to continue, or pass scope="all remaining" to execute all at once.

Status: ok | ok (all complete) | blocked
Blocker (if any): <task ID, error summary, or "None">
```
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: No arguments; current git branch is `003-payment-flow`; FEATURE_DIR resolves to `features/003-payment-flow/`; all checklists pass; tasks.md has 3 phases (Setup 3 tasks, User Story 1 5 tasks, Polish 4 tasks), 0 already completed.
Expected behavior: Step 1 resolves FEATURE_DIR via branch detection. Step 2 displays checklist table (all ✓ PASS) and proceeds. Step 3 loads tasks.md, plan.md, contracts/. Step 4 runs project setup (first phase). Step 5 resolves scope: no explicit scope input → default = Phase 1 (Setup, 3 tasks); displays scope confirmation. Step 6 executes Setup phase only, marks T001–T003 as [X], runs build/test. Step 7 returns Implementation Summary: 3/12 tasks completed this run; remaining phases: User Story 1 (5 tasks), Polish (4 tasks). Status: ok.
</example>

<example>
Input: `FEATURE_DIR=features/007-notifications/`; scope="all remaining"; some tasks in tasks.md already marked `[X]` (Phase 1 fully done); checklist `security.md` has 3 incomplete items.
Expected behavior: Step 1 uses the provided FEATURE_DIR path directly. Step 2 detects security.md has 3 incomplete items, displays the checklist gate table with ✗ FAIL, and calls `vscode_askQuestions`. If user confirms yes, Step 3 loads context. Step 4 skips project setup (Phase 1 already complete). Step 5 resolves scope: "all remaining" → all phases not fully marked [X]. Step 6 executes all remaining phases sequentially, skipping already-complete tasks within each phase.
</example>

<example type="counter">
Input: User says "implement everything" without specifying a scope or phase.
Expected behavior: The word "everything" is treated as equivalent to "all". Step 5 resolves scope = all remaining incomplete phases and displays the scope confirmation listing every pending phase before executing. Skill does NOT silently execute all phases without first showing the scope confirmation.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never execute beyond the resolved scope without explicit user instruction** — default is the next single incomplete phase; "all" must be stated explicitly.
- **Never bypass the checklist gate without explicit user confirmation** — incomplete checklists signal unmet pre-implementation requirements.
- **Always mark completed tasks [X] in tasks.md immediately** — downstream resume and orchestration depend on accurate checklist state.
- **Never modify design artifacts (spec.md, plan.md, data-model.md, contracts/)** — this skill executes the task plan; design changes require spec-flow upstream skills.
- **Always show the scope confirmation before executing** — the user must see which phase(s) will run and which will be deferred.

## Question Payloads

### `checklist_gate`

```json
{
  "header": "checklist_gate",
  "question": "Some checklists are incomplete. Do you want to proceed with implementation anyway?",
  "options": [
    { "label": "Yes — proceed with implementation" },
    { "label": "No — stop and complete the checklists first" }
  ],
  "allowFreeformInput": false
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

</reminders>
