---
name: project-user-flows
description: "Extract durable user scenarios from a shipped spec feature and write them as step-by-step user-flow files."
---

# Project User Flows

Extract durable user scenarios from a shipped spec feature and write them as step-by-step user-flow files.

Template: `spek-fu/plugins/project/templates/user-flow-template.md`
Glossary (durable vs ephemeral knowledge): `spek-fu/plugins/project/project-workflow.md`

## When to use

Run manually, given a reference to a shipped (merged) spec feature directory.

<inputs>

## Inputs

- Path to the shipped spec feature directory: `spek-fu/project/spec-features/###-short-name/`

</inputs>

<outputs>

## Outputs

- One user-flow file per user story/scenario at `spek-fu/project/user-flows/<feature-short-name>-<scenario-slug>.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Only write durable knowledge (per `project-workflow.md` glossary). Skip implementation detail, task breakdowns, and in-progress notes.
- Never invent a step not grounded in `spec.md` or `quickstart.md`.
- Stay scoped to `user-flows/`. Never edit `project.md`, `technical.md`, `roadmap.md`, or `project-docs/`.
- If `spec.md` is missing or the feature directory does not exist, stop and report failure.
- Re-running for the same feature must be idempotent: update a scenario's file only if its content changed; leave unchanged files untouched.

</constraints>

<workflow>

## Steps

### 1. Resolve the feature directory

Confirm `spek-fu/project/spec-features/###-short-name/spec.md` exists. Stop and report failure if not.

### 2. Read source artifacts

- `spec.md` — read `### Core Flows` for the flow inventory, and `## User Scenarios & Testing` for each `### User Story N - [Title] (Priority: ...)` block (description, acceptance scenarios).
- `quickstart.md` (if present) — read `## Run` for the concrete user-facing actions (UI labels, commands) that ground each step.
- `tasks.md` (if present) — check only for scope changes that diverge from `spec.md` (e.g. a story dropped or altered during implementation). Do not copy task breakdown content.

### 3. Build one user-flow draft per user story

For each `### User Story N` in `spec.md`:

- Title: the story's brief title.
- Goal: the story's plain-language description, one sentence.
- Steps: convert its `Given/When/Then` acceptance scenarios into numbered steps, grounding each in concrete actions from `quickstart.md` where available.
- Outcome: the end state after the last `Then`.

Skip a story if `tasks.md` shows it was not actually shipped.

### 4. Write files

Fill `spek-fu/plugins/project/templates/user-flow-template.md` per draft. Slugify the story title (kebab-case) for the filename.

Write to `spek-fu/project/user-flows/<feature-short-name>-<scenario-slug>.md`.

- If the target file doesn't exist, create it.
- If it exists and content differs, overwrite it.
- If it exists and content is unchanged, skip it.

### 5. Report

List the files written, updated, and skipped (unchanged).

</workflow>

<done_conditions>

## Done Conditions

- Every shipped user story in the feature's `spec.md` has a corresponding file under `spek-fu/project/user-flows/`.
- No file contains ephemeral implementation detail.
- No file outside `spek-fu/project/user-flows/` was modified.

</done_conditions>
