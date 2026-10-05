---
name: project-technical-docs
description: "Extract durable technical knowledge from a shipped spec feature and sync it into technical.md and the technical sections of project-docs."
---

# Project Technical Docs

Extract durable technical knowledge and write it into `technical.md` and the technical section(s) of `project-docs/`, grouped under the feature each detail fulfils.

Template (technical.md): none — headings are created directly per Step 6.
Template (project-docs area file): `spek-fu/plugins/project/templates/project-docs-template.md`
Feature format (IDs, subsections, module links): `spek-fu/plugins/project/knowledge/feature-format.md`
Area registry (area → file → ID prefix): `spek-fu/plugins/project/knowledge/area-registry.md`
Glossary (durable vs ephemeral knowledge): `spek-fu/plugins/project/project-workflow.md`

## When to use

Run manually, after `project-functional-docs` has run for the same area.

<inputs>

## Inputs

- **Feature sync** — path to a shipped spec feature directory: `spek-fu/project/spec-features/###-short-name/`

</inputs>

<outputs>

## Outputs

- Updated `spek-fu/project/technical.md`
- Updated or created `## Technical` section(s) in `spek-fu/project/project-docs/<area>.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Only write durable knowledge (per `project-workflow.md` glossary). Skip task breakdowns and in-progress implementation notes.
- `## Functional` is a read-only ID registry. Never add, remove, rename, renumber, or invent an ID, and never edit `## Functional` or `## Related User Flows`.
- Every `### [ID] Name` heading copies an ID and name exactly from `## Functional` of the same file. A foreign-prefix (reference) ID gets no subsection.
- Never restate a feature's functional sentence. Write only how it is built and which `code-docs` modules implement it.
- Technical detail matching no feature: if it is user-observable, write nothing and report it as a missing feature for `project-functional-docs`. Otherwise put it under `### Shared Mechanics`. Never mint an ID to make a fact fit.
- A feature with nothing technical to add goes on the `_No separate technical detail:_` line, not into an empty subsection.
- Inline module links are bare links. The "what it covers" gloss belongs only in `### Related Modules`.
- Never state a fact not grounded in `spec.md`, `technical-plan.md`, `research.md`, or `data-model.md`.
- `technical.md` never carries a feature list — only the pointer line in Step 7.
- If a `project-docs/<area>.md` file doesn't exist yet, create it from the template, leaving `## Functional` as the template's placeholder.
- Re-running must be idempotent: update a file only if its content changed; leave unchanged files untouched.

</constraints>

<behavioral_anchors>

## Pillars

**The functional list rules the technical section** — its IDs decide what subsections exist, in what order, under what names. A technical fact that fits no ID is a question for `project-functional-docs`, never a new ID.

</behavioral_anchors>

<workflow>

## Steps

### 1. Load the ID registry (ordering gate)

Read the area file's `## Functional` and collect every ID with its exact name, plus the `_Retired:_` line.

If the section is missing, still holds the template placeholder, or contains no IDs, stop and report: "run project-functional-docs for `<area>` first." Write nothing.

### 2. Read source artifacts

- `spec.md` — scope and architecture-relevant acceptance criteria.
- `technical-plan.md` (if present) — architecture decisions and technology choices.
- `research.md` (if present) — durable findings, not exploratory dead ends.
- `data-model.md` (if present) — durable entities and relationships.
- `tasks.md` (if present) — check only for scope changes. Do not copy task breakdown content.

### 3. Classify each technical fact

Into exactly one of:

- Project-wide architecture, stack, or cross-cutting concern → `technical.md`.
- Serves one feature → that feature's `### [ID] Name` subsection.
- Serves no single feature and is not user-observable → `### Shared Mechanics`.
- User-observable with no ID → report as a missing feature, write nothing.

Discard anything ephemeral per the glossary.

### 4. Write the area file's `## Technical`

Preamble, then one subsection per own-prefix feature in `## Functional` ID order, then `### Shared Mechanics` with its `_No separate technical detail:_` line, then `### Related Modules`.

Inline-link the implementing `code-docs` modules in each subsection. Leave `## Functional` and `## Related User Flows` untouched.

Create the file from the template if missing, leaving `## Functional` exactly as the template has it.

### 5. Refresh `### Related Modules`

The complete inventory of `code-docs` modules this area owns, each with its one-line gloss. Every module is owned by exactly one area.

### 6. Update `technical.md`

If the file is empty or missing, create it with:

```
# Technical Overview

## Architecture

## Technology Stack

## Cross-Cutting Concerns
```

Add or update bullets under the matching heading for each project-wide fact from Step 4. Add a heading only if no existing heading fits. No feature list.

Ensure the file contains this line:

> Per-feature technical detail lives under the matching feature ID in [project-docs/](project-docs/); this file stays high-level.

### 7. Verify and report

Verify and report files changed; IDs given a subsection; IDs marked as having none; facts sent to `### Shared Mechanics`; and any missing-feature gaps for `project-functional-docs`.

</workflow>

<done_conditions>

## Done Conditions

- Durable technical facts are reflected in `technical.md` and/or the relevant `project-docs/*.md` `## Technical` section.
- Every `### [ID] …` heading matches an ID and name in the same file's `## Functional`.
- Every own-prefix functional ID has a subsection or is on the `_No separate technical detail:_` line.
- No ID was created, renamed, or removed by this skill.
- No `## Functional` or `## Related User Flows` content was modified.
- `doctor` reports no errors for the touched areas.

</done_conditions>
