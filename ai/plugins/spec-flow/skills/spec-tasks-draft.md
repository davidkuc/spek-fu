---
id: "spec-tasks-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Generates a dependency-ordered tasks.md from feature design artifacts (plan.md, spec.md, data-model.md, contracts/), producing a phased, checklist-format task plan organised by user story. USE FOR: creating an executable task plan before implementation begins. DO NOT USE FOR: implementing tasks, reviewing spec quality, or drafting spec files."
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
  - "tasks.md written to `feature-dir` with all tasks in strict checklist format"
  - "Generation report: task count, parallel opportunities, MVP scope, format validation"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` as a fallback when the prerequisites script fails; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-tasks-draft

<!-- SECTION 1: Identity (primacy position) -->
Generates an actionable, dependency-ordered `tasks.md` for a feature by reading available design artifacts — `plan.md`, `spec.md`, `data-model.md`, contracts, and research — and applying the task-generation rules from the project constitution. The skill organises tasks into phases by user story, marks parallelisable items with `[P]`, assigns `[USN]` story labels, and produces a **Generation Report** covering task counts, parallel opportunities, and the suggested MVP scope.

**Scope boundary**: This skill reads design artifacts and writes `tasks.md` only. It does NOT implement tasks, evaluate spec correctness, or modify any design artifact. For spec review, use **spec-devils-advocate**; for spec drafting, use **spec-feature-draft**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER invent task details absent from design artifacts — place `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty instead — WHY: invented scope silently corrupts the task plan and misleads implementors.
2. NEVER read design files before resolving `feature-dir` — ALWAYS run the prerequisites script first — WHY: paths are environment-specific and hard-coded paths silently break in other workspaces.
3. NEVER generate tasks without both `plan.md` and `spec.md` present — stop with `blocked` status if either is absent — WHY: these are the authoritative sources of tech stack and user story scope; tasks generated without them are unreliable.
4. NEVER omit test tasks without an explicit TDD waiver stated in the spec and documented in the plan — WHY: TDD is a constitution principle and silent omission breaks the testing contract.
5. NEVER write a task outside the strict checklist format (`- [ ] TNNN [P?] [USN?] Description with file path`) — every task MUST carry a checkbox, sequential ID, optional markers, and a file path — WHY: non-compliant tasks cannot be executed or tracked by downstream agents.
6. NEVER implement tasks, modify design artifacts, or evaluate spec quality — this skill generates the task plan only — WHY: scope overreach corrupts the separation between planning and implementation roles.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- If a user story or task detail is ambiguous, place `[NEEDS CLARIFICATION: <specific question>]` at the point of uncertainty in tasks.md; do not guess.
- This skill may be re-run: if `tasks.md` already exists in `feature-dir`, regenerate it from scratch using the current artifact state — do not merge or patch the prior file.

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
- **blocked**: `plan.md` or `spec.md` is absent — report the missing file and stop.
- **blocked (clarification)**: ambiguous user stories cannot be resolved — `[NEEDS CLARIFICATION]` markers placed and the report lists the unresolved points.

## Step 1 — Resolve paths

Resolve `feature-dir` and `available-docs`:
- Resolve `feature-dir` via **Branch Detection** first: apply the core procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md`. If the user provides a path, use it as `feature-dir`. If the user declines, stop and report `blocked`.
- Use `list_dir` on `feature-dir` to obtain `available-docs` (list all files and subdirectories).

> **If `feature-dir` cannot be resolved**: stop with status `blocked` and report the blocker.

## Step 2 — Load design documents

Using `feature-dir` and `available-docs` from Step 1, load documents in this order.

**Required** (stop with `blocked` if either is absent):
- `plan.md` — extract: tech stack, libraries, project structure
- `spec.md` — extract: user stories with priorities (P1, P2, P3...)

**Optional** (load only if listed in `available-docs`):
- `data-model.md` — extract: entities and relationships
- `contracts/` — enumerate with `list_dir`, then load each contract file — extract: endpoints and their user story owners
- `research.md` — extract: architectural decisions relevant to setup tasks
- `quickstart.md` — extract: test scenarios for independent test criteria

Use multi-pass `read_file` on each document: read from line 1 with a generous range; if the response fills the page, advance `startLine` and read again; repeat until the response is shorter than the page size.

> **If plan.md or spec.md is absent**: set status to `blocked`, report which file is missing, and stop.

## Step 3 — Build the Task Plan

Using the loaded artifacts, produce the **Task Plan**:

1. From `plan.md`: identify tech stack, libraries, and project structure. Generate setup and foundational tasks.
2. From `spec.md`: extract every user story and its priority (P1, P2, P3...). Each user story becomes a dedicated phase.
3. If `data-model.md` present: map each entity to the user story(ies) requiring it. Place entities serving multiple stories in the foundational phase.
4. If `contracts/` present: map each endpoint to its user story. Add a contract test task marked `[P]` before each implementation task in the relevant story phase.
5. If `research.md` present: map architectural decisions to setup tasks.
6. Organise phases in this order:
   - Phase 1: Setup (project initialisation)
   - Phase 2: Foundational (blocking prerequisites)
   - Phase 3+: One phase per user story in priority order; each phase includes story goal, independent test criterion, and test tasks (default)
   - Final Phase: Polish and cross-cutting concerns
7. Assign `[P]` markers to tasks that operate on different files and have no dependency on incomplete tasks in the same phase.
8. Assign `[USN]` labels to all tasks in user story phases.
9. For each user story phase, define one measurable independent test criterion.

> **If a user story is ambiguous and cannot be resolved from artifacts**: place `[NEEDS CLARIFICATION: <specific question>]` in the **Task Plan** at the affected phase.

## Step 4 — Generate tasks.md

Load `ai/plugins/spec-flow/templates/tasks-template.md` as the document scaffold. Populate with:
- Feature name from `plan.md`
- All phases from the **Task Plan** (Step 3)
- Every task in strict checklist format: `- [ ] TNNN [P?] [USN?] Description with file path`
- Phase headers showing: story goal and independent test criterion
- Dependencies section showing user story completion order
- Parallel execution examples per story
- Implementation strategy section (MVP first, incremental delivery)

> **If the tasks template is unavailable**: generate `tasks.md` using the phase structure from Step 3 without the template scaffold.

Write the completed document to `{feature-dir}/tasks.md`. If `tasks.md` already exists, replace its content rather than appending.

## Step 5 — Report

Produce the **Generation Report**:
- Path to `tasks.md`
- Total task count
- Task count per user story
- Parallel opportunities identified
- Independent test criteria per story
- Suggested MVP scope (typically User Story 1 only)
- Format validation: confirm all tasks comply with the checklist format

The skill is complete when `tasks.md` exists at `{feature-dir}/tasks.md`, all tasks comply with the checklist format, and the **Generation Report** has been shown.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load plan.md, spec.md, data-model.md, research.md, quickstart.md, and the tasks template. Use multi-pass reads for large files (advance `startLine` until the response is shorter than page size).
- **vscode_askQuestions**: Collect `feature-dir` from the user in Step 1.
- **list_dir**: Enumerate files in `feature-dir` to determine `available-docs`.
- **list_dir**: Enumerate the `contracts/` directory in Step 2 when present.
- **create_file**: Write the generated `tasks.md` to `feature-dir` at the end of Step 4 when the file does not yet exist.
- **replace_string_in_file**: Replace the full content of `tasks.md` in Step 4 if the file already exists.
- **vscode_askQuestions**: Collect `feature-dir` from the user in Step 1 only when the prerequisites script fails.
- Do NOT use tools not listed here unless this skill explicitly escalates.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Generation Report**:

```
## Task Generation Report

Feature: <feature name from plan.md>
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
Input: Feature directory contains plan.md (React + FastAPI, feature: User Authentication), spec.md (3 user stories: P1 Login, P2 Registration, P3 Password Reset), data-model.md (User, Session entities), contracts/auth.yaml.
Expected behavior: Skill runs prerequisites script, resolves `feature-dir`, loads all four documents. Generates tasks.md with: Phase 1 Setup, Phase 2 Foundational (User + Session models), Phase 3 [US1] Login (contract test + endpoint + integration test tasks), Phase 4 [US2] Registration, Phase 5 [US3] Password Reset, Final Phase Polish. Reports ~35 tasks total, 12 parallel opportunities, MVP = US1 Login.
</example>

<example>
Input: Feature directory contains only plan.md and spec.md with 2 user stories. No data-model.md or contracts directory present.
Expected behavior: Skill loads only plan.md and spec.md. Generates tasks.md with four phases: Setup, Foundational, US1 phase, US2 phase, and Polish. Optional artifact sections are omitted. No contract test tasks generated. Generation Report notes no contracts or data model were present.
</example>

<example type="counter">
Input: User asks the skill to implement the generated tasks after tasks.md is written.
Expected behavior: Skill generates tasks.md as requested and stops. Responds: "tasks.md has been generated at `{feature-dir}/tasks.md`. This skill produces the task plan only — it does not implement tasks. To begin implementation, consult the **impl-implement** skill."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never invent task details not present in design artifacts** — place `[NEEDS CLARIFICATION: <question>]` at every point of uncertainty instead.
- **Never read design files before resolving `feature-dir`** — always run the prerequisites script first.
- **Never generate tasks without both plan.md and spec.md** — stop with `blocked` status if either is absent.
- **Never implement tasks, modify design artifacts, or evaluate spec quality** — this skill generates the task plan only.

</reminders>
