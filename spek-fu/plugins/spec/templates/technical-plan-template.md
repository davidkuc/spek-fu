# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `spek-fu/project/spec-features/[###-feature-name]/spec.md`

**Note**: This file is produced by the `spec-technical-draft` skill. It synthesizes all Phase 0 and Phase 1 artifacts into a single reference plan. Downstream skills (`spec-tdd-draft`, `spec-tasks-draft`) use this file as their primary technical reference.

## Summary

[Extract from feature spec: primary requirement + technical approach from research.md]

## Input Artifacts

> These artifacts were used as source inputs when generating this plan. Load them for full detail; this plan is a synthesis, not a replacement.

| Artifact | Path | Notes |
|----------|------|-------|
| Feature Spec | `spek-fu/project/spec-features/[###-feature-name]/spec.md` | Required |
| Research | `spek-fu/project/spec-features/[###-feature-name]/research.md` | Phase 0 — resolved technical unknowns |
| Data Model | `spek-fu/project/spec-features/[###-feature-name]/data-model.md` | Phase 1 — entities and relationships |
| API Contracts | `[contracts-root]/` | Phase 1 — OpenAPI / GraphQL schemas, written inside `spek-fu/project/` (see skill config `contractsPath`) |
| Quickstart | `spek-fu/project/spec-features/[###-feature-name]/quickstart.md` | Phase 1 — operator guide |
| Testability Assessment | `spek-fu/project/spec-features/[###-feature-name]/test-expert/testability-assessment.md` | Optional |

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, TypeScript 5.4 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, React or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, files or N/A]
**Testing**: [e.g., pytest, Vitest or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, web browser or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 60 fps or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, offline-capable or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 50 screens or NEEDS CLARIFICATION]
**Testing Strategy**: Scoped test command (per-task use): `[exact command]`. Full-suite command (baseline capture / completion gate only): `[exact command]`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates are determined from `spek-fu/constitution/constitution.md`.
At minimum, include applicable checks from:
- AI Principles (always)
- Software Development Principles (when defined)
- Project Specific Principles (when defined)

If a gate is violated, document the violation and justification in this section.]

## Project Structure

### Documentation (this feature)

```text
spek-fu/project/spec-features/[###-feature]/
├── research.md          # Phase 0 output (spec-technical-draft skill)
├── data-model.md        # Phase 1 output (spec-technical-draft skill)
├── quickstart.md        # Phase 1 output (spec-technical-draft skill)
├── technical-plan.md    # Phase 1 output (spec-technical-draft skill) ← this file
└── tasks.md             # Later phase output (spec-tasks-draft skill - NOT created here)
```

### API Contracts (inside `spek-fu/project/`)

```text
[contracts-root]/         # e.g. <repo-root>/spek-fu/project/contracts/ — see skill config `contractsPath`
└── [contract files]      # OpenAPI YAML / GraphQL SDL, one per user action
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths. The delivered plan must not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |

## Cleanup Summary

> Filled in Phase 2 by `spec-technical-draft`. Lists vestigial artifacts removed after the plan was finalized, or states none were needed.

[List each removed artifact with a one-line reason, or: "No cleanup required — all artifacts finalized."]
