---
name: project-functional-docs
description: "Extract durable functional knowledge from a shipped spec feature and sync it into project.md, roadmap.md, and the functional sections of project-docs."
---

# Project Functional Docs

Extract durable functional knowledge and write it into `project.md`, `roadmap.md`, and the functional section(s) of `project-docs/`.

Template (project-docs area file): `spek-fu/plugins/project/templates/project-docs-template.md`
Template (roadmap.md): `spek-fu/plugins/project/templates/roadmap-template.md`
Feature format (IDs, reference lines, retirement): `spek-fu/plugins/project/knowledge/feature-format.md`
Area registry (area → file → ID prefix): `spek-fu/plugins/project/knowledge/area-registry.md`
Glossary (durable vs ephemeral knowledge): `spek-fu/plugins/project/project-workflow.md`

## When to use

Run manually.

<inputs>

## Inputs

- **Feature sync** — path to a shipped spec feature directory: `spek-fu/project/spec-features/###-short-name/`

</inputs>

<outputs>

## Outputs

- Updated `spek-fu/project/project.md`
- Updated `spek-fu/project/roadmap.md`
- Updated or created `## Functional` section(s) in `spek-fu/project/project-docs/<area>.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Only write durable knowledge (per `project-workflow.md` glossary). Skip task breakdowns and in-progress implementation notes.
- Never state a fact not grounded in `spec.md` or the matching `project-features/PF*.md`.
- A feature is user-observable (`feature-format.md`). Internal mechanics are not features — hand them to `project-technical-docs` instead of listing them.
- Follow `feature-format.md` for ID allocation, definition lines, reference lines, and retirement. Never renumber, reorder, or reuse an ID.
- Own `## Functional` (including its `_Retired:_` line) and `## Related User Flows`. Never edit `## Technical` or anything under it, including a `### [ID]` heading — report renames instead, so `project-technical-docs` can follow.
- `project.md` and `technical.md` never carry feature lists. `project.md` gets only the pointer line in Step 9.
- `roadmap.md` is the single source of truth for roadmap status; mark the shipped feature's entry done instead of duplicating it elsewhere.
- If a `project-docs/<area>.md` file doesn't exist yet, create it from the template, leaving `## Technical` as the template's placeholder.
- Re-running must be idempotent: update a file only if its content changed; leave unchanged files untouched.

</constraints>

<behavioral_anchors>

## Pillars

**The functional list is the ID registry** — every feature ID in the project is minted here and nowhere else. `project-technical-docs` only reads it.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read source artifacts

- `spec.md` — feature purpose, scope, user-facing behavior.
- The matching `spek-fu/project/project-features/PF*.md` (if any) — the roadmap phase this belongs to.
- `tasks.md` (if present) — check only for scope changes that diverge from `spec.md`. Do not copy task breakdown content.

### 2. Read the existing ID registry

Parse the area file's `## Functional`: every `[PREFIX-NN]` with its name, plus the `_Retired:_` line. This is the state to preserve — existing IDs, their numbers, and their order.

### 3. Classify facts

Split each candidate fact into:

- High-level, project-wide (what the product does, major capability additions) → `project.md`.
- A user-observable behavior of one area → that area's `## Functional` list.
- Delivery status (feature shipped) → `roadmap.md`.

Discard anything ephemeral per the glossary. Hand any internal mechanic to `project-technical-docs` instead of listing it as a feature.

### 4. Match features to existing IDs

Match by meaning, not by position. The same feature, even renamed, keeps its ID. Handle splits, merges, and removals per `feature-format.md`. Anything left over is new.

### 5. Allocate IDs for new features

Next ID = the highest number ever used in this area, live or retired, plus one — ascending in write order. Never reuse, never renumber.

### 6. Decide the owner area

Pick each feature's owner per `feature-format.md`. Write the definition line only in the owner area; add a reference line in each other area that depends on it.

### 7. Write the area file's `## Functional`

Owned features in ID order, then reference lines, then optional prose, then the `_Retired:_` line. Update `## Related User Flows`.

Create the file from the template if missing, leaving `## Technical` exactly as the template has it.

### 8. Update `project.md` and `roadmap.md`

`project.md` — no feature list. Ensure its Reference Map contains this line:

> Granular, numbered feature lists live per area in [project-docs/](project-docs/); this file stays high-level.

`roadmap.md` — create from `spek-fu/plugins/project/templates/roadmap-template.md` if missing. Mark the entry matching this feature's PF as shipped. If no entry exists, add one under the correct phase, additive only — never duplicate an existing entry for the same PF.

### 9. Verify and report

Verify and report files created, updated, and skipped (unchanged); new IDs; retired IDs; features handed to `project-technical-docs`; and any `[NEEDS CLARIFICATION]`.

</workflow>

<done_conditions>

## Done Conditions

- Durable functional facts are reflected in `project.md`, `roadmap.md`, and/or the relevant `project-docs/*.md` `## Functional` section.
- Every new feature has a fresh ID; no existing ID was renumbered, reordered, or reused.
- Every removed feature's ID is on the `_Retired:_` line.
- No `## Technical` content was modified.
- `doctor` reports no errors for the touched areas.

</done_conditions>
