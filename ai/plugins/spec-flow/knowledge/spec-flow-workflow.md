# Spec-Flow Workflow Chain

The spec-flow plugin implements a seven-step feature specification pipeline. Each step produces an artifact consumed by the next. Steps marked **optional** may be skipped when the team determines the risk level is acceptable.

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
spec-tdd-draft
      ↓
spec-technical-draft
      ↓
spec-tasks-draft
      ↓
spec-implement
```

---

## Step-by-Step Reference

### 1. spec-feature-draft
- **Purpose**: Generate the initial feature specification from a raw idea or brief.
- **Input**: Feature name, description, and any seed context supplied by the user.
- **Output**: `FEATURE_DIR/spec.md` — structured feature specification.
- **Status**: Required — all downstream steps depend on this file.

---

### 2. spec-clarification
- **Purpose**: Interactively resolve ambiguities in the spec through a structured multi-pass Q&A loop.
- **Input**: `spec_path` — path to the spec.md to clarify (prompted via `vscode_askQuestions` if absent).
- **Output**: Amended `spec.md` with a populated `## Clarifications` section.
- **Status**: Required — unresolved ambiguities propagate into every downstream artifact.

---

### 3. spec-devils-advocate
- **Purpose**: Adversarially red-team the spec to surface failure modes, hidden assumptions, and architectural fragility before any planning begins.
- **Input**: `spec_path`, optional `output_dir`, optional `user_focus`.
- **Output**: `FEATURE_DIR/devils-advocate/devils-advocate-report.md`.
- **Template**: `ai/plugins/spec-flow/templates/devils-advocate-template.md`
- **Status**: Strongly recommended — skipping means testability analysis proceeds without upstream risk context.

---

### 4. spec-testability-draft
- **Purpose**: Evaluate the spec from a test-engineering perspective and produce a Testability Assessment Report.
- **Input**: `FEATURE_DIR` — must contain `spec.md` and the devils-advocate report from step 3.
- **Output**: `FEATURE_DIR/test-expert/testability-assessment.md`.
- **Template**: `ai/plugins/spec-flow/templates/testability-template.md`
- **Status**: Required — spec-tdd-draft depends on this artifact.

---

### 5. spec-tdd-draft
- **Purpose**: Convert testability findings into a formal TDD implementation design report with BDD-formatted test specifications, coverage mapping, and incremental implementation waves.
- **Input**: `FEATURE_DIR` — must contain `test-expert/testability-assessment.md` and `spec.md`.
- **Output**: `FEATURE_DIR/tdd-designer/report.md`.
- **Template**: `ai/plugins/spec-flow/templates/tdd-report-template.md`
- **Status**: Required — the TDD report is the implementation contract developers use before writing production code.

---

### 6. spec-technical-draft
- **Purpose**: Produce the technical design document — architecture decisions, component breakdown, integration contracts, and data models.
- **Input**: `FEATURE_DIR` containing the upstream spec, devils-advocate, and TDD artifacts.
- **Output**: `FEATURE_DIR/technical-design.md` (or equivalent per skill configuration).
- **Status**: Required — tasks cannot be accurately decomposed without a technical design.

---

### 7. spec-tasks-draft
- **Purpose**: Decompose the technical design into a phased, dependency-ordered task list ready for implementation.
- **Input**: `FEATURE_DIR` containing upstream artifacts including the technical design.
- **Output**: `FEATURE_DIR/tasks.md` — implementation task list.
- **Template**: `ai/plugins/spec-flow/templates/tasks-template.md`
- **Status**: Required — final artifact that developers execute against.

---

### 8. spec-implement
- **Purpose**: Execute the implementation plan by processing all tasks in `tasks.md` phase by phase, with checklist gate verification, TDD sequencing, and progress tracking.
- **Input**: `FEATURE_DIR` containing `tasks.md` and optional design artifacts (`plan.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md`).
- **Output**: Implemented codebase changes; each completed task marked `[X]` in `FEATURE_DIR/tasks.md`.
- **Status**: Required — final execution step; produces the working implementation.

---

## Artifact Map

| Step | Skill | Output Artifact |
|------|-------|-----------------|
| 1 | spec-feature-draft | `FEATURE_DIR/spec.md` |
| 2 | spec-clarification | `FEATURE_DIR/spec.md` (amended) |
| 3 | spec-devils-advocate | `FEATURE_DIR/devils-advocate/devils-advocate-report.md` |
| 4 | spec-testability-draft | `FEATURE_DIR/test-expert/testability-assessment.md` |
| 5 | spec-tdd-draft | `FEATURE_DIR/tdd-designer/report.md` |
| 6 | spec-technical-draft | `FEATURE_DIR/technical-design.md` |
| 7 | spec-tasks-draft | `FEATURE_DIR/tasks.md` |
| 8 | spec-implement | Implemented codebase; `FEATURE_DIR/tasks.md` (all tasks `[X]`) |
