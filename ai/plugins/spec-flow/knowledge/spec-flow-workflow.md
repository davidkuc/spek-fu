# Spec-Flow Workflow Chain

The spec-flow plugin implements a nine-step feature specification pipeline. Each step produces an artifact consumed by the next.

---

## Workflow Chain

```
spec-feature-draft
      ↓
spec-clarification
      ↓
spec-devils-advocate
      ↓
spec-testability-draft
      ↓
spec-technical-draft
      ↓
spec-tdd-draft
      ↓
spec-tasks-draft
      ↓
spec-feature-analysis
      ↓
spec-implement
```

---

## Step-by-Step Reference

### 1. spec-feature-draft
- **Purpose**: Generate the initial feature specification from a raw idea or brief.
- **Input**: Feature name, description, and any seed context supplied by the user.
- **Output**: `feature-dir/spec.md` — structured feature specification.
- **Status**: Required — all downstream steps depend on this file.

---

### 2. spec-clarification
- **Purpose**: Interactively resolve ambiguities in the spec through a structured multi-pass Q&A loop.
- **Input**: `spec-file` — path to the spec.md to clarify (prompted via `vscode_askQuestions` if absent).
- **Output**: Amended `spec.md` with a populated `## Clarifications` section.
- **Status**: Required — unresolved ambiguities propagate into every downstream artifact.

---

### 3. spec-devils-advocate
- **Purpose**: Adversarially red-team the spec to surface failure modes, hidden assumptions, and architectural fragility before any planning begins.
- **Input**: `spec-file`, optional `output-dir`, optional `user_focus`.
- **Output**: `feature-dir/devils-advocate/devils-advocate-report.md`.
- **Template**: `ai/plugins/spec-flow/templates/devils-advocate-template.md`
- **Status**: Required — spec-testability-draft Constraint 2 hard-requires this report; skipping means testability analysis proceeds without upstream risk context.

---

### 4. spec-testability-draft
- **Purpose**: Evaluate the spec from a test-engineering perspective and produce a Testability Assessment Report.
- **Input**: `feature-dir` — must contain `spec.md` and the devils-advocate report from step 3.
- **Output**: `feature-dir/test-expert/testability-assessment.md`.
- **Template**: `ai/plugins/spec-flow/templates/testability-template.md`
- **Status**: Required — spec-tdd-draft depends on this artifact.

---

### 5. spec-technical-draft
- **Purpose**: Produce the technical design document — architecture decisions, component breakdown, integration contracts, and data models.
- **Input**: `feature-dir` containing the upstream spec, testability-assessment, and devils-advocate artifacts.
- **Output**: `feature-dir/research.md`, `feature-dir/data-model.md`, `feature-dir/contracts/`, `feature-dir/quickstart.md`.
- **Status**: Required — tasks cannot be accurately decomposed without a technical design.

---

### 6. spec-tdd-draft
- **Purpose**: Convert testability findings into a formal TDD implementation design report with BDD-formatted test specifications, coverage mapping, and incremental implementation waves.
- **Input**: `feature-dir` — must contain `test-expert/testability-assessment.md`, `spec.md`, `research.md`, `data-model.md`, and `contracts/`.
- **Output**: `feature-dir/tdd-designer/report.md`.
- **Template**: `ai/plugins/spec-flow/templates/tdd-report-template.md`
- **Status**: Required — the TDD report is the implementation contract developers use before writing production code.

---

### 7. spec-tasks-draft
- **Purpose**: Decompose the technical design into a phased, dependency-ordered task list ready for implementation.
- **Input**: `feature-dir` containing upstream artifacts including the technical design.
- **Output**: `feature-dir/tasks.md` — implementation task list.
- **Template**: `ai/plugins/spec-flow/templates/tasks-template.md`
- **Status**: Required — final artifact that developers execute against.

---

### 8. spec-feature-analysis
- **Purpose**: Inspect all pipeline artifacts for existence, staleness, and `[NEEDS CLARIFICATION]` markers; perform cross-artifact consistency analysis; and produce a **Readiness Verdict** (`READY` / `READY WITH WARNINGS` / `BLOCKED`) before implementation begins.
- **Input**: `feature-dir` — resolved via Branch Detection if not supplied.
- **Output**: `feature-dir/feature-analysis-report.md` — overwritten on each invocation.
- **Template**: `ai/plugins/spec-flow/templates/feature-analysis-template.md`
- **Status**: Recommended — surfaces staleness, unresolved clarifications, and coverage gaps before the implementation phase commits to them.

---

### 9. spec-implement
- **Purpose**: Execute the implementation plan by processing all tasks in `tasks.md` phase by phase, with checklist gate verification, TDD sequencing, and progress tracking.
- **Input**: `feature-dir` containing `tasks.md` and optional design artifacts (`research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `test-expert/testability-assessment.md`, `tdd-designer/report.md`).
- **Output**: Implemented codebase changes; each completed task marked `[X]` in `feature-dir/tasks.md`.
- **Status**: Required — final execution step; produces the working implementation.

---

## Artifact Map

| Step | Skill | Output Artifact |
|------|-------|-----------------|
| 1 | spec-feature-draft | `feature-dir/spec.md` |
| 2 | spec-clarification | `feature-dir/spec.md` (amended) |
| 3 | spec-devils-advocate | `feature-dir/devils-advocate/devils-advocate-report.md` |
| 4 | spec-testability-draft | `feature-dir/test-expert/testability-assessment.md` |
| 5 | spec-technical-draft | `feature-dir/research.md`, `feature-dir/data-model.md`, `feature-dir/contracts/`, `feature-dir/quickstart.md` |
| 6 | spec-tdd-draft | `feature-dir/tdd-designer/report.md` |
| 7 | spec-tasks-draft | `feature-dir/tasks.md` |
| 8 | spec-feature-analysis | `feature-dir/feature-analysis-report.md` |
| 9 | spec-implement | Implemented codebase; `feature-dir/tasks.md` (all tasks `[X]`) |
