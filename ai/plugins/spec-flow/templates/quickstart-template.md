# Quickstart: [Phase N] — [System Name] ([User Story ID])

**See also: [tasks.md](../tasks.md)** for implementation task breakdown and dependency graph.

## PRE-IMPLEMENTATION SECTION
<!-- PRE-IMPLEMENTATION SECTION: filled in before work begins -->

**Feature**: [ID-feature-slug]
**Phase**: [N] — [User Story ID] · [System Name] (Priority: [P0/P1/P2/P3])
**Date**: [YYYY-MM-DD]
**Prerequisites**: [Phase X] ✅ ([what it delivers]) · [Phase Y] ✅ ([what it delivers]) · ...

**Related Tasks**: [T001](../tasks.md#T001), [T002](../tasks.md#T002), [T003](../tasks.md#T003)  
<!-- Reference specific task IDs from tasks.md that belong to this phase -->

---

### Goal

<!--
One or two paragraphs describing the goal of the phase — what becomes possible after
completing it that was not possible before. Write from the user's perspective.

Example:
  Deliver the **graph traversal engine** — the core module that resolves paths between
  nodes and makes the system usable end-to-end for the first time.
-->

[Description of the phase goal — what it delivers and why it is an important milestone]

> [A sentence describing the main flow from the user's perspective — e.g. "User submits X → system processes Y → Z is returned"]

<!--
Example:
  > User submits a **traversal request** → system resolves the path → **results are
  > returned** with full node metadata → user inspects the output → next query is ready.
-->

**[Key sentence describing the main change relative to the previous phase.]**
<!--
Example:
  **This is the first phase where traversal queries return real results end-to-end.**
  `TraversalService.Resolve()` was a stub in Phase 2; in Phase 3 it executes the
  full graph walk and returns ranked path results.
-->

[Optional: one sentence about an additional validation scenario, e.g. statistical distribution testing]

---

### [Key Algorithm / Phase Mechanic] — *Optional*

<!--
Optional section — appears when the phase contains one key algorithm or a non-obvious
implementation mechanism worth explaining before coding begins.
Describe it as pseudocode steps.

Example:
  ## Path-Ranking Algorithm

  The ranking implementation scores paths without full re-traversal:

  1. Compute edge weights from node metadata
  2. Run Dijkstra from source; record predecessor map
  3. Extract top-K paths by score threshold
  4. Return ranked list with metadata attached

  This means:
  - Single-pass traversal: O(E log V)
  - Ranking is deterministic given the same graph state
-->

[Description of the algorithm or key mechanism]

```
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

[Optional: consequences / properties of the algorithm that affect tests or UX]

---

### [Pipeline / Main Implementation Flow] — *Conditional*

<!--
Conditional section — appears when the phase's main system flow is complex enough to warrant
explanation before coding. For simple features, this may be omitted.

Describe step by step how data flows through the new components. Write as a numbered
pseudocode list, not as code.

Example:
  #### Traversal Request Pipeline (TraversalService.Resolve)

  For each `TraversalRequest` received:
  1. Validate source and target node IDs against the graph index
  2. Load adjacency data from GraphRepository
  3. Execute path algorithm → collect candidate paths
  4. Rank and filter candidates by score threshold
  5. Return `TraversalResult` with top-K paths and metadata

  `TraversalResult` is immutable; callers must not mutate the returned paths.
-->

[Description of the flow / pipeline]

```
For each [element] in [collection]:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
```

[Optional: important pipeline rules, e.g. "FR-039 enforced: Instantiate/Destroy per wave is explicitly forbidden"]

---



## LIVE SECTION
<!-- LIVE SECTION: filled in during implementation -->

### Key Files Created / Changed in Phase [N]

<!--
Tables divided by architectural layer of the project.
Each section is a separate layer (e.g. Domain, Application, Infrastructure, Tests).
Columns: File | Change or File | Role — depending on whether the change is a modification or a new file.

Example (Domain):
  | `TraversalService.cs` | `Resolve()` fully implemented — executes graph walk and returns ranked path results |

Example (Tests):
  | `TraversalServiceTests.cs` | TDD-010, TDD-011 | Unit        |
  | `GraphRepositoryTests.cs`  | TDD-004, TDD-005 | Integration (added to existing file) |
-->

### [Layer 1 — e.g. Domain] (`[path/]`)

| File | Change |
|------|--------|
| `[FileName.cs]` | [Description of change] |

### [Layer 2 — e.g. Application] (`[path/]`)

| File | Role |
|------|------|
| `[FileName.cs]` | [Description of role] |

### [Layer 3 — e.g. Infrastructure] (`[path/]`)

| File | Role |
|------|------|
| `[FileName.cs]` | [Description of role] |

### Tests

| File | Tests | Type |
|------|-------|------|
| `[TestClassName.cs]` | [TDD-XXX, TDD-YYY] | [Unit / Integration / E2E] |

---


### Phase [N] Checkpoint Validation

<!--
List of DONE conditions for this phase.
Each condition has: task ID (optional) + a sentence describing what is being verified.
[ ] checkbox for manual ticking during implementation.

Focus on:
- test results (TDD)
- observable system behaviour (CLI output, API response, UI feedback)
- no regression in previous tests
- no errors in logs

Example:
  - [ ] **T093** — TDD-030 and TDD-031 green (path uniqueness + ranking correctness)
  - [ ] **All Phase 2 tests still green** — TraversalServiceTests (12), GraphModelTests (5)
  - [ ] **Traversal returns results** — run sample query; correct paths appear in output
  - [ ] **No errors in logs** — zero errors during the above steps
-->

- [ ] **[TXXX]** — [test IDs] green ([brief description of what they verify])
- [ ] **All Phase [N-1] tests still green** — [TestClassName] ([N]), [TestClassName] ([N])
- [ ] **[Behaviour 1]** — [How to verify it — e.g. run command / call endpoint / inspect output]
- [ ] **[Behaviour 2]** — [How to verify it]
- [ ] **[No performance regression / no errors]** — [Description]
- [ ] **No errors in logs** — Zero errors during the above steps

---

### Common Pitfalls

<!--
Table of typical problems, to be filled in during implementation and in subsequent phases.
Columns: Symptom | Likely Cause | Fix

Add entries here as problems are encountered — the most valuable section for future developers.

Example:
  | Traversal returns empty results  | Source node ID not present in graph index  | Verify node is indexed before querying      |
  | Ranking returns wrong order      | Edge weights not recomputed after update   | Call `GraphIndex.Rebuild()` after mutations |
  | Integration test flaky on CI     | Test shares mutable graph state            | Reset graph fixture in `BeforeEach`         |
  | Path contains duplicate nodes    | Cycle guard not enabled by default         | Pass `allowCycles: false` in options        |
-->

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| [Symptom] | [Likely cause] | [How to fix] |

---

### What Is NOT in Phase [N]

<!--
Table of explicitly excluded scope — important for preventing scope creep.
Columns: Feature | Phase

Example:
  | Incremental graph updates (live re-indexing)        | Phase 5 (US3)    |
  | Caching layer for repeated traversal queries        | Phase 6 (Perf)   |
  | Throughput benchmark suite                          | Phase 8 (T136)   |
-->

Phase [N] deliberately excludes the following — addressed in later phases:

| Feature | Phase |
|---------|-------|
| [Out-of-scope feature] | Phase [M] ([US/T ref]) |
| [Out-of-scope feature] | Phase [M] ([US/T ref]) |


