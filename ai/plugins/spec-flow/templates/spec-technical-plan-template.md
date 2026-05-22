# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This file is produced by the `spec-technical-draft` skill (Step 8). It synthesizes all Phase 0 and Phase 1 artifacts into a single reference plan. Downstream skills (`spec-tasks-draft`, `spec-implement`) use this file as their primary technical reference.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Input Artifacts

> These artifacts were used as source inputs when generating this plan. Load them for full detail; this plan is a synthesis, not a replacement.

| Artifact | Path | Notes |
|----------|------|-------|
| Feature Spec | `[feature-dir]/spec.md` | Required |
| Research | `[feature-dir]/research.md` | Phase 0 — resolved technical unknowns |
| Data Model | `[feature-dir]/data-model.md` | Phase 1 — entities and relationships |
| API Contracts | `[feature-dir]/contracts/` | Phase 1 — OpenAPI / GraphQL schemas |
| Quickstart | `[feature-dir]/quickstart.md` | Phase 1 — developer onboarding |
| Testability Assessment | `[feature-dir]/test-expert/testability-assessment.md` | Optional |

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates are determined from `constitution/constitution.md`.
At minimum, include applicable checks from:
- AI Work Principles (always)
- Software Development Principles (when defined)
- Project Specific Principles (when defined)

If a gate is violated, document the violation and justification in this section.]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── research.md          # Phase 0 output (technical-draft skill)
├── data-model.md        # Phase 1 output (technical-draft skill)
├── quickstart.md        # Phase 1 output (technical-draft skill)
├── contracts/           # Phase 1 output (technical-draft skill)
├── technical-plan.md    # Phase 1 output (technical-draft skill) ← this file
└── tasks.md             # Phase 2 output (tasks skill - NOT created by technical-draft skill)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
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

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
