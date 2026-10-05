---
name: spec-technical-draft
description: "Translates a validated feature spec into research.md, data-model.md, API contracts, quickstart.md, and a synthesized technical-plan.md."
---

# Spec Technical Draft

Executes technical planning for a validated feature spec in two phases: Phase 0 resolves ambiguities via targeted research; Phase 1 generates data-model.md, API contracts, quickstart.md, and consolidates everything into technical-plan.md. Phase 2 removes vestigial planning artifacts.

Template: `spek-fu/plugins/spec/templates/technical-plan-template.md`
Template: `spek-fu/plugins/spec/templates/quickstart-template.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

Plan phase step, after `spec-testability-draft`, when a spec (and optional testability report) is ready to become a phased technical design with typed contracts.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `testability-report` (optional; resolved from `<spec-file-directory>/test-expert/` if absent)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-technical-draft.contractsPath`)
- Project documentation: `spek-fu/project/project.md`, `spek-fu/project/technical.md`, `spek-fu/project/project-docs/`, `spek-fu/project/contracts/` (best-effort)

</inputs>

<outputs>

## Outputs

- `research.md`, `data-model.md`, `quickstart.md`, `technical-plan.md` written to `<spec-file-directory>/`
- Ephemeral API contract files (draft/in-flux, scoped to this feature) written to `<spec-file-directory>/contracts/`
- Durable API contract files (stable, consumed regularly by the application) written to `<contracts-root>/` (inside `spek-fu/project/`, see Step 2)
- Completion report: artifact list, constitution gate result, carried clarifications, quickstart gaps, contract classification (ephemeral vs durable)

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never author or modify `spec-file`, run tests, or execute implementation work.
- Never silently drop unresolved `[NEEDS CLARIFICATION: <question>]` markers — carry them into every downstream artifact and the final report.
- Never invent a technical decision to fill a marker; leave it marked instead.
- Stop with `BLOCKED` on a real constitution gate violation; if constitution files are missing/unreadable, warn and continue with reduced guarantees.
- Never write an abstraction into `quickstart.md` where a name belongs — ground every flag, key, path, endpoint, field, and control label per the quickstart template's R1–R10, or mark `[NEEDS CLARIFICATION]`.
- Every `quickstart.md` Verify step carries an exact command and an explicit pass condition.
- Default every contract to `<spec-file-directory>/contracts/` (ephemeral). Promote a contract to `<contracts-root>/` only when it's a stable interface another feature or the running application will consume regularly — never promote speculative or single-feature-only shapes, to avoid accumulating redundant files in project documentation.
- Never duplicate a contract in both locations; a promoted contract is moved, not copied.
- Read `spek-fu/project/project.md` and `spek-fu/project/technical.md` in full, and `spek-fu/project/project-docs/` and `spek-fu/project/contracts/` for existing conventions and interfaces, as part of Step 3. Best-effort: if any path is missing or unreadable, warn and continue — never block on it.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every decision, entity, and step description uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Grounded Names** — no plausible-looking flag, path, or field is ever invented; it is read from the repo, attributed to the task that creates it, or marked `[NEEDS CLARIFICATION]`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-technical-draft.contractsPath` (default `spek-fu/project/contracts` if the file or key is missing).

### 2. Resolve paths

Resolve `spec-file`: if provided use it, otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.

Resolve `<contracts-root>` as `contractsPath` joined relative to the repository root (the directory containing `spek-fu/`) — default `<repo-root>/spek-fu/project/contracts/`. Create it if absent. This holds only durable, cross-consumed contracts.

Resolve `<ephemeral-contracts-dir>` as `<spec-file-directory>/contracts/`. Create it if absent. This holds feature-scoped, in-flux contracts by default.

### 3. Load context

Read `spec-file` in full. Look for `testability-report` at `<spec-file-directory>/test-expert/testability-assessment.md`; read it if present, otherwise note absence and treat test scope as incomplete.

Read `spek-fu/project/project.md` and `spek-fu/project/technical.md` in full, and `spek-fu/project/project-docs/` and `spek-fu/project/contracts/` for existing conventions and interfaces relevant to the feature's domain. Hold as context for Steps 6–9. Best-effort: if any path is missing or unreadable, warn and continue.

### 4. Constitution gate and advisory context

Read `spek-fu/constitution/constitution.md` if present; extract every MUST/MUST NOT/ALWAYS/NEVER rule and flag conflicts or missing coverage against the spec and testability report. `BLOCKED` on violations, `CLEAR` otherwise.

Spawn in parallel: `framework-compounding-agent` (read mode, feature summary as input) for advisory lessons; `doc-engine-executor` (Traverse) for existing codebase conventions relevant to the feature's domain. Hold both as advisory context for Steps 6–8.

### 5. Phase 0 — Research

**Skip condition**: `research.md` exists with zero `[NEEDS CLARIFICATION]` markers.

One research task per unresolved marker plus dependency/integration best-practice tasks. For each, spawn a research agent: feature context, the unknown, "match schema exactly, do not invent figures", output `{status, decision, rationale, alternatives_considered, confidence, open_questions}`. Consolidate into `research.md` as `## [Decision topic]` / `**Decision**` / `**Rationale**` / `**Alternatives considered**`. Conflicting results: document all options, keep the marker. Remaining markers: add `## Carried Clarifications` and continue.

### 6. Phase 1 — Data model

**Prerequisite**: `research.md` has zero unresolved markers.

Extract entities from `spec-file` and `research.md`. Write `data-model.md`: entity name, fields, types, relationships, validation rules, state transitions. Undeterminable fields: `[NEEDS CLARIFICATION: <question>]`, continue with grounded entities only.

### 7. Phase 1 — API contracts

**Prerequisite**: `data-model.md` has zero unresolved markers.

One endpoint per user action in `spec-file` (REST or GraphQL). Write schema files (OpenAPI YAML or GraphQL SDL) to `<ephemeral-contracts-dir>/` by default.

Promote a contract to `<contracts-root>/` only if it meets all: (a) the interface is stable, not expected to change with this feature's own iteration; (b) it's consumed regularly by the running application or by another feature, not just internally during this feature's build. When in doubt, leave it ephemeral — durable placement is the exception, not the default.

> Zero user actions found: stop, report `blocked — no user actions in spec`.

### 8. Phase 1 — Quickstart

Load `spek-fu/plugins/spec/templates/quickstart-template.md` in full; its AUTHORING RULES comment block is binding. Ground every name per R2 by reading `<ephemeral-contracts-dir>/`, `<contracts-root>/`, source, and sibling `spek-fu/project/spec-features/*/quickstart.md` files. Cite requirements/decisions inline (FR-0xx, D-0xx, SC-0xx). Flag any path the feature's own artifacts don't yet cover, at the point of use, and record it for Step 11. Run the template's self-check before writing; re-evaluate the constitution gate after.

### 9. Phase 1 — Technical plan

**Skip condition**: `technical-plan.md` exists and no upstream artifact changed this run.

Load `spek-fu/plugins/spec/templates/technical-plan-template.md`. Populate from `spec-file`, `research.md`, `data-model.md`, `<ephemeral-contracts-dir>/`, `<contracts-root>/`, `quickstart.md`, and the Step 4 gate result. Insert `[NEEDS CLARIFICATION]` for any undetermined Technical Context field rather than inventing it. Fill Complexity Tracking only if the gate required justification. Write, replacing any existing file.

### 10. Phase 2 — Cleanup

Scan `<spec-file-directory>` for spike/throwaway files, superseded research notes, and `[DRAFT]`/`[SPIKE]`/`[EXPERIMENTAL]`/`[DEAD-END]` markers not referenced by any final artifact. Remove only what's confirmed unreferenced; log each removal. Also scan `<ephemeral-contracts-dir>/` for contracts superseded by a later revision or by a promoted copy in `<contracts-root>/`; remove superseded ephemeral copies once the durable one exists. Update `technical-plan.md`'s `## Cleanup Summary` with what was removed and why, or "No cleanup required — all artifacts finalized."

### 11. Report completion

Report: branch, `spec-file` path, `<ephemeral-contracts-dir>` path, `<contracts-root>` path, artifact list (created/updated/skipped) split by ephemeral vs durable contracts, constitution gate result and violations, `carried-clarifications: N`, `constitution-warnings`, `quickstart-gaps` (section — what's missing — where it must land, or `none`).

</workflow>

<done_conditions>

## Done Conditions

- `research.md`, `data-model.md`, `quickstart.md`, `technical-plan.md` (with `## Cleanup Summary`) exist in `<spec-file-directory>`; at least one contract file exists in `<ephemeral-contracts-dir>` or `<contracts-root>`.
- Constitution gate passes, or the run stopped `BLOCKED` with violations reported.
- Zero unresolved `[NEEDS CLARIFICATION]` markers are silently dropped — all carried into the report.
- `spec-file` unchanged.

</done_conditions>
