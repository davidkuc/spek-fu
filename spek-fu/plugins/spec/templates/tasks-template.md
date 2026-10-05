---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `<spec-file-directory>/`
**Prerequisites**: spec.md (required), technical-plan.md or tdd-report.md (at least one required), data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are REQUIRED by the constitution (SD8, SD9) unless
the feature spec explicitly waives them with rationale.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description (file-path)`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions
- Runtime task states:
  - `- [ ]` = not started
  - `- [X]` = completed
  - `- [!]` = blocked after bounded retries; do not retry automatically without explicit user direction
- Optional `@ref:` hints may be appended when a task depends on a specific design-artifact fragment, e.g. `@ref: data-model.md#User-entity`

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  spec-tasks-draft MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Entities from technical-plan.md / data-model.md
  - Endpoints from contracts/
  - BDD test units and waves from tdd-report.md

  Tasks MUST be organized by user story so each story can be implemented,
  tested, and delivered as an MVP increment independently.

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per technical-plan.md (src/)
- [ ] T002 Initialize [language] project with [framework] dependencies (package.json)
- [ ] T003 [P] Configure linting and formatting tools (.eslintrc)
- [ ] T004 [C-Setup] Commit Setup phase work to Git: review and commit all implementation and documentation changes.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Setup database schema and migrations framework (db/migrations/)
- [ ] T006 [P] Create base models/entities that all stories depend on (src/models/) @ref: data-model.md
- [ ] T007 [P] Setup API routing and middleware structure (src/api/)
- [ ] T008 [C-Foundational] Commit Foundational phase work to Git: review and commit all implementation and documentation changes.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (DEFAULT) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py @ref: contracts/[contract-file]
- [ ] T010 [P] [US1] BDD test for [behavior] in tests/integration/test_[name].py @ref: tdd-report.md#T-001

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create [Entity1] model in src/models/[entity1].py @ref: data-model.md#[entity1]
- [ ] T012 [US1] Implement [Service] in src/services/[service].py (depends on T011)
- [ ] T013 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T014 [C-US1] Commit User Story 1 phase work to Git: review and commit all implementation and documentation changes.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (DEFAULT) ⚠️

- [ ] T015 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py @ref: contracts/[contract-file]
- [ ] T016 [P] [US2] BDD test for [behavior] in tests/integration/test_[name].py @ref: tdd-report.md#T-002

### Implementation for User Story 2

- [ ] T017 [P] [US2] Create [Entity] model in src/models/[entity].py @ref: data-model.md#[entity]
- [ ] T018 [US2] Implement [Service] in src/services/[service].py
- [ ] T019 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T020 [C-US2] Commit User Story 2 phase work to Git: review and commit all implementation and documentation changes.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T021 Code cleanup and refactoring (src/)
- [ ] T022 [P] Additional unit tests (if requested) in tests/unit/
- [ ] T023 Run quickstart.md validation (quickstart.md)
- [ ] T024 [C-Polish] Commit Polish phase work to Git: review and commit all implementation and documentation changes.

---

## Phase Final: Knowledge Capture & Documentation

**Purpose**: Run once, after all other phases complete

- [ ] T025 [K-Final] [P] Spawn framework-compounding-agent (write mode): capture lessons from the whole feature — errors, resolutions, cross-task patterns.
- [ ] T026 [D-Final] [P] Spawn doc-engine-executor agent (Update): sync documentation for all feature changes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed), or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services; services before endpoints; core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup/Foundational tasks marked [P] can run in parallel within their phase
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "BDD test for [behavior] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Once Foundational is done: Developer A takes US1, Developer B takes US2, etc.
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- `[!]` means blocked after bounded retries; downstream dependent tasks should be skipped until the blocker is resolved
- `@ref:` points to the authoritative design-artifact fragment to lazy-load when executing the task
- Verify tests fail before implementing
- Commit after each phase (see [C-] tasks); [K-]/[D-] run once in the Final phase
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Phase R<n>: Remediation — <slug>

<!-- Populated by spec-quick-planner when injecting remediation tasks into an existing feature's tasks.md. Structurally identical to any other phase's tasks. Multiple remediation phases may appear (R1, R2, R3... with different slugs). Preserved during spec-tasks-draft regeneration. Leave empty on initial generation. -->

---

## Discovered Subtasks

<!-- Leave empty on initial generation. Implementation appends D### items here when new follow-up work is discovered mid-implementation. -->
