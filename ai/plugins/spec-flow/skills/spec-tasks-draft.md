---
id: "spec-tasks-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Generates a dependency-ordered tasks.md from feature design artifacts (spec.md, research.md, data-model.md, contracts/, quickstart.md), producing a phased, checklist-format task plan organised by user story. USE FOR: creating an executable task plan before implementation begins. DO NOT USE FOR: implementing tasks, reviewing spec quality, or drafting spec files."
anti-scope: "Does not implement tasks, evaluate spec correctness, or modify any design artifact. For spec review, use spec-devils-advocate. For spec drafting, use spec-feature-draft."
tags:
  - "specification"
  - "tasks"
  - "planning"
  - "decomposition"
inputs:
  - "Feature context or arguments from the user or orchestrator (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "tasks.md written to `feature-dir` with all tasks in strict checklist format, optional `@ref:` hints, preserved `[X]` / `[!]` markers when a prior tasks.md exists, and a preserved `## Discovered Subtasks` section when present"
  - "Generation report: task count, parallel opportunities, MVP scope, format validation, and task-state preservation results"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` as a fallback when Branch Detection returns no match; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-tasks-draft

<!-- SECTION 1: Identity (primacy position) -->
Generates a dependency-ordered `tasks.md` by reading design artifacts (`spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`) and applying project constitution rules. Organises tasks by user story, marks parallel work with `[P]`, assigns `[USN]` labels, and produces a **Generation Report** covering task counts, parallel opportunities, and MVP scope.

**Scope boundary**: Reads design artifacts and writes `tasks.md` only. Does NOT implement tasks, evaluate specs, or modify design artifacts.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER invent task details absent from design artifacts — place `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty instead — WHY: invented scope silently corrupts the task plan and misleads implementors.
2. NEVER read design files before resolving `feature-dir` — ALWAYS run Branch Detection first — WHY: paths are environment-specific and hard-coded paths silently break in other workspaces.
3. NEVER generate tasks without `spec.md` and at least one of `technical-plan.md`, `research.md`, or `data-model.md` present — stop with `blocked` status if that minimum artifact set is absent — WHY: user story scope comes from the spec, and the downstream design context must come from actual technical outputs rather than invented planning details.
4. NEVER omit test tasks without an explicit TDD waiver stated in the spec and reflected in the technical artifacts — WHY: TDD is a constitution principle and silent omission breaks the testing contract.
5. NEVER write a task outside the strict checklist format (`- [ ] TNNN [P?] [USN?] Description with file path`) — every task MUST carry a checkbox, globally sequential numeric ID (T001, T002, … across ALL phases), optional markers, a file path (or `n/a` for setup/cross-cutting tasks without a single target file), and may append an `@ref:` hint when the implementing agent must load a design-artifact fragment lazily — WHY: non-compliant tasks cannot be executed or tracked by downstream agents.
6. NEVER implement tasks, modify design artifacts, or evaluate spec quality — this skill generates the task plan only — WHY: scope overreach corrupts the separation between planning and implementation roles.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `skill-meta-rules.md`, `paginated-read.md`, and `needs-clarification-protocol.md` before acting.

## Operational Anchors
- Place `[NEEDS CLARIFICATION]` when ambiguous; do not guess.
- Re-run compatibility: if `tasks.md` exists, regenerate from artifacts while preserving `[X]` and `[!]` markers and re-appending existing `## Discovered Subtasks` unchanged.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve user context or arguments from the invocation before acting.
- Environment Preflight must complete before Step 1 when `env` is `devcontainer`.

## Done conditions

- **ok**: `tasks.md` exists in `feature-dir`, all tasks comply with the checklist format, and the **Generation Report** has been shown.
- **blocked**: `spec.md` is absent, or both `research.md` and `data-model.md` are absent — report the missing artifact(s) and stop.
- **ok (carried clarifications)**: `tasks.md` exists with explicit `[NEEDS CLARIFICATION]` markers and the **Generation Report** lists the carried-clarification count.

## Step 1 — Resolve paths

Resolve `feature-dir` and `available-docs`:
- Apply Branch Detection from `branch-detection.md` first. Use provided path if supplied; otherwise detect and stop if not resolved.
- Use `list_dir` on `feature-dir` to list files/subdirectories.

> **If `feature-dir` cannot be resolved**: stop with status `blocked` and report the blocker.

## Step 2 — Load design documents

Load in this order:

**Required**:
- `spec.md` (user stories with priorities) — stop blocked if absent
- At least ONE of `technical-plan.md`, `research.md`, or `data-model.md` — stop blocked if all absent

**Primary** (prefer over `research.md` when present): `technical-plan.md`

**Optional**: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, `tdd-designer/report.md`

Apply `paginated-read.md` to each file.

> **If `spec.md` is absent, or all of `technical-plan.md`, `research.md`, and `data-model.md` are absent**: set status to `blocked`, report which artifact(s) are missing, and stop.

## Step 3 — Build the Task Plan

1. From `technical-plan.md`/`research.md`/`data-model.md`: identify tech stack, structure, constraints, entities, relationships; generate setup/foundational tasks.
2. From `spec.md`: extract user stories and priority. Each becomes a phase.
3. Map entities to stories; place multi-story entities in foundational phase.
4. Map endpoints to stories; add `[P]` contract test tasks before implementation.
5. Map architectural decisions to setup tasks.
6. For BDD tests: generate one test task per BDD test in matching story phase; reference test ID; use Wave assignments (Wave 1, 2, 3, 4) to order within phase. If absent, generate generic scaffolding.
7. Organise: Setup → Foundational → US1, US2... (priority order) → Polish.
8. Mark `[P]` for tasks on different files with no dependencies.
9. Assign `[USN]` to user story phase tasks (e.g., `[US1]`, `[US2]`).
10. Define one independent test criterion per user story.
11. Assign globally sequential `TNNN` across ALL phases (T001, T002...). Do NOT restart per phase.
12. Append `@ref:` hint when task requires lazy-loading a design-artifact fragment (e.g., `@ref: data-model.md#User-entity`).

> **If a user story is ambiguous and cannot be resolved from artifacts**: place `[NEEDS CLARIFICATION: <specific question>]` in the **Task Plan** at the affected phase.

If any upstream artifact already contains `[NEEDS CLARIFICATION]` markers, carry them into the **Generation Report** rather than treating them as a blocker.

## Step 4 — Generate tasks.md

Load `tasks-template.md` as scaffold. Populate with:
- Feature name from `spec.md`
- All phases with story goal and test criterion
- Tasks in checklist format: `- [ ] TNNN [P?] [USN?] Description @ref:hint` (use `n/a` for no single file)
- Dependencies, parallel execution examples, implementation strategy
- Preserve `## Discovered Subtasks` if re-running

If re-running:
1. Extract `[X]` and `[!]` tasks into Completion Map keyed by normalized description.
2. Extract existing `## Discovered Subtasks` unchanged.
3. Regenerate from current artifacts.
4. Re-apply `[X]` and `[!]` markers to matching regenerated tasks.
5. Re-append `## Discovered Subtasks` unchanged.
6. Note unmatched prior tasks in **Generation Report**.

Write to `{feature-dir}/tasks.md` (replace if exists).

## Step 5 — Report

Produce the **Generation Report**:
- Path to `tasks.md`
- Total task count
- Task count per user story
- Parallel opportunities identified
- Independent test criteria per story
- Suggested MVP scope (typically User Story 1 only)
- Format validation: confirm all tasks comply with the checklist format
- Preserved task states: counts of `[X]` and `[!]` markers re-applied, plus any unmatched prior task descriptions
- Carried Clarifications: `N` plus the list of carried or newly inserted markers when present

The skill is complete when `tasks.md` exists at `{feature-dir}/tasks.md`, all tasks comply with the checklist format, and the **Generation Report** has been shown.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load spec.md, data-model.md, research.md, quickstart.md, tdd-designer/report.md, the tasks template, `ai/plugins/spec-flow/knowledge/branch-detection.md`, and `ai/plugins/skf/knowledge/devcontainer-guidelines.md` (in devcontainer environments). Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` whenever a file may span multiple reads.
- **vscode_askQuestions**: Collect `feature-dir` from the user in Step 1 only when Branch Detection returns no match.
- **list_dir**: Enumerate files in `feature-dir` to determine `available-docs`; enumerate the `contracts/` directory in Step 2 when present.
- **create_file**: Write the generated `tasks.md` to `feature-dir` at the end of Step 4 when the file does not yet exist.
- **replace_string_in_file**: Replace the full content of `tasks.md` in Step 4 if the file already exists, including re-applied `[X]` / `[!]` markers and any preserved `## Discovered Subtasks` section.
- Do NOT use tools not listed here unless this skill explicitly escalates.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Generation Report**:

```
## Task Generation Report

Feature: <feature name from spec.md>
Output: <absolute path to tasks.md>

Tasks generated: <total count>
  Per user story:
    US1 (<story title>): <count> tasks
    US2 (<story title>): <count> tasks

Parallel opportunities: <count>
MVP scope: US1 — <story title>

Independent test criteria:
  US1: <one-line criterion>
  US2: <one-line criterion>

Format validation: All tasks comply with checklist format ✅  |  <N> violations found ❌

Preserved task states:
  [X]: <count reapplied>
  [!]: <count reapplied>
  Unmatched prior tasks: <count>
```

**Clarification Markers** (when present in tasks.md):

```
[NEEDS CLARIFICATION: <specific question about a user story or task>]
```

Placed inline at the exact point of uncertainty in tasks.md. Each marker contains a single, specific question.

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: Feature directory contains spec.md (3 user stories: P1 Login, P2 Registration, P3 Password Reset), research.md (React + FastAPI, project structure), data-model.md (User, Session entities), contracts/auth.yaml.
Expected behavior: Skill runs Branch Detection, resolves `feature-dir`, loads all four documents. Generates tasks.md with: Phase 1 Setup (T001–T005), Phase 2 Foundational (T006–T009, User + Session models), Phase 3 [US1] Login (T010–T018, contract test + endpoint + integration test tasks), Phase 4 [US2] Registration (T019–T026), Phase 5 [US3] Password Reset (T027–T032), Final Phase Polish (T033–T035). Tasks that depend on specific artifact fragments include `@ref:` hints. Literal Generation Report:

```
## Task Generation Report

Feature: User Authentication
Output: features/001-user-auth/tasks.md

Tasks generated: 35
  Per user story:
    US1 (Login): 9 tasks
    US2 (Registration): 8 tasks
    US3 (Password Reset): 6 tasks

Parallel opportunities: 12
MVP scope: US1 — Login

Independent test criteria:
  US1: Login endpoint returns 200 with valid JWT on correct credentials
  US2: Registration endpoint returns 201 with user ID on valid input
  US3: Password-reset email dispatched within 5 seconds of request

Format validation: All tasks comply with checklist format ✅
Preserved task states:
  [X]: 0
  [!]: 0
  Unmatched prior tasks: 0
```
</example>

<example>
Input: spec.md + research.md only (2 stories). No data-model.md, no contracts.
Expected: Generates Setup, Foundational, US1, US2, Polish. Optional sections omitted; no contract test tasks. Report notes missing artifacts.

<example type="counter">
Input: User asks the skill to implement the tasks after generation.
Expected: Generates tasks.md as requested, stops. Responds: "tasks.md generated at `{feature-dir}/tasks.md`. This skill produces the task plan only — it does not implement.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
- Constraint 1 — insert explicit markers instead of inventing task details.
- Constraint 2 — resolve `feature-dir` before reading design artifacts.
- Constraint 3 — stop when the minimum required artifact set is absent.
- Constraint 5 — keep task IDs sequential and `[USN]` numeric.
- Constraint 6 — generate the task plan only; do not implement it.
</reminders>
