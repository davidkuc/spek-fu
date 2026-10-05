---
name: spec-project-feature
description: "Draft a minimal, high-level project feature sketch and register it in the project roadmap."
---

# Spec Project Feature

Creates a minimal, high-level feature sketch (a **project feature**) and registers it in the project roadmap.

Template (PF file): `spek-fu/plugins/spec/templates/project-feature-template.md`
Template (roadmap.md): `spek-fu/plugins/project/templates/roadmap-template.md`

## When to use

First step of the Define phase, before `spec-feature-draft`, when a new feature idea needs a lightweight sketch before deeper spec work begins.

<inputs>

## Inputs

- User's feature idea (title, purpose)
- Answers to clarification prompts for Intent & Rationale, Scope & Anti-scope, Risks & Unknowns
- Existing files under `spek-fu/project/project-features/` (for numbering)
- `spek-fu/project/roadmap.md` (for roadmap registration)

</inputs>

<outputs>

## Outputs

- A new `PF<NUMBER>[-<LETTER>]-<SLUG>.md` file at `spek-fu/project/project-features/`
- One additive (or revised) sentence in the matching roadmap phase of `spek-fu/project/roadmap.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never write the PF file without first reading `spek-fu/plugins/spec/templates/project-feature-template.md`.
- Never invent template sections; follow template order exactly.
- File name format: `PF<NUMBER>[-<LETTER>]-<SLUG>.md`. NUMBER is the next unused sequential integer across `project-features/` (unpadded, e.g. `PF1`, `PF12`). LETTER is added only when revising or splitting an existing PF (e.g. `PF3-A`), never for a brand-new feature.
- SLUG is the feature title in kebab-case.
- Never skip clarification: ask the user for Intent & Rationale, Scope & Anti-scope, and Risks & Unknowns before drafting (constitution `## AI Principles` → Ambiguity).
- The roadmap registration sentence must be additive (new PF) or a revision of the existing sentence (updated PF) — never a duplicate of prior sentences for the same PF.
- `spek-fu/project/roadmap.md` is the single source of truth for roadmap status; never register phases/entries elsewhere.
- If `spek-fu/project/roadmap.md` has no phases yet, create one before registering.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every clarification question, sketch sentence, and roadmap entry uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Minimal Sketch** — a project feature is a sketch, not a spec: no implementation detail, no task breakdown, no acceptance criteria (those belong to `spec-feature-draft` and later phases).

</behavioral_anchors>

<workflow>

## Steps

### 1. Gather requirements

Ask the user, looping until unambiguous:
- Feature title
- Intent & Rationale (why this feature, what problem it solves)
- Scope (what's included)
- Anti-scope (what's explicitly excluded)
- Risks & Unknowns
- References (optional; links, related PFs, prior art)

### 2. Determine roadmap phase

Read `spek-fu/project/roadmap.md`. If it's empty or missing, create it from `spek-fu/plugins/project/templates/roadmap-template.md`. If phases exist, ask the user which phase this PF belongs to (or infer from title/intent and confirm); otherwise rename the template's placeholder phase after the feature area.

### 3. Assign PF number and slug

List `spek-fu/project/project-features/`. NUMBER = next unused integer (unpadded) across existing `PF<N>...md` files. SLUG = kebab-case of the feature title. If this call revises or splits an existing PF instead of creating a new one, reuse that NUMBER and append the next unused LETTER (A, B, ...).

### 4. Draft the PF file

Fill `spek-fu/plugins/spec/templates/project-feature-template.md` using the gathered answers. Write to `spek-fu/project/project-features/PF<NUMBER>[-<LETTER>]-<SLUG>.md`.

### 5. Register in the roadmap

In the matching roadmap phase from Step 2, add or revise one sentence referencing the PF (title + one-line purpose). Keep it additive for a new PF; replace only the sentence for the same PF when revising.

### 6. Report

Confirm the PF file path and the roadmap sentence to the user.

</workflow>

<done_conditions>

## Done Conditions

- PF file exists at `spek-fu/project/project-features/PF<NUMBER>[-<LETTER>]-<SLUG>.md`, following the template exactly.
- `spek-fu/project/roadmap.md` contains exactly one sentence for this PF, in the correct phase.
- No implementation detail, tasks, or acceptance criteria present in the PF file.

</done_conditions>
