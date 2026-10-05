---
name: spec-feature-draft
description: "Generate a feature specification file from a natural-language description, creating a matching numbered branch and feature directory."
---

# Spec Feature Draft

Creates a detailed feature spec (`spec.md`), a matching numbered feature directory, and a matching numbered git branch from a natural-language feature description.

Template: `spek-fu/plugins/spec/templates/spec-feature-template.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

First step of the Define phase; expects a project feature already drafted (via the project plugin's `project-feature-draft` skill) under `spek-fu/project/project-features/`.

<inputs>

## Inputs

- Feature description (natural language)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-feature-draft.maxClarificationMarkers`)
- Existing local/remote branches and `spek-fu/project/spec-features/` directories (for numbering)
- Project documentation: `spek-fu/project/project.md`, `spek-fu/project/technical.md`, `spek-fu/project/project-docs/`, `spek-fu/project/contracts/` (best-effort)

</inputs>

<outputs>

## Outputs

- New branch `###-short-name`
- New directory `spek-fu/project/spec-features/###-short-name/`
- New `spec.md` inside that directory, fully populated, no remaining `[NEEDS CLARIFICATION]` markers

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never write `spec.md` before the branch and feature directory both exist.
- Never create the branch or feature directory more than once per invocation.
- Cap `[NEEDS CLARIFICATION]` markers at `maxClarificationMarkers` (config, default 10); beyond the cap, make informed guesses and record them as assumptions instead.
- Never include implementation details (languages, frameworks, APIs, database/table names) in `spec.md` — specs describe user value, not technology choices.
- Never invent template sections; follow `spec-feature-template.md`'s order exactly.
- If the feature description is empty or too vague to draft from, ask the user before proceeding (constitution `## AI Principles` → Ambiguity).
- Read `spek-fu/project/project.md` and `spek-fu/project/technical.md` in full, and skim `spek-fu/project/project-docs/` and `spek-fu/project/contracts/` for feature-relevant terminology, constraints, and existing interfaces, before drafting. Best-effort: if any path is missing or unreadable, warn and continue — never block on it.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every spec section, assumption, and clarification question uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**No Implementation Leakage** — a feature spec describes actors, actions, data, constraints, and success conditions only; technology choices belong to later planning skills.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-feature-draft.maxClarificationMarkers` (default `10` if the file or key is missing).

### 2. Read project documentation

Read `spek-fu/project/project.md` and `spek-fu/project/technical.md` in full. Skim `spek-fu/project/project-docs/` and `spek-fu/project/contracts/` — file names and headers — reading full content only for files relevant to the feature description's domain. Hold findings (terminology, existing constraints/interfaces) as context for Step 8. Best-effort: if any path is missing or unreadable, warn and continue.

### 3. Retrieve advisory lessons

Spawn the `framework-compounding-agent` agent (read mode) with the feature description as input. Hold any returned lessons as advisory context for Step 8; apply judgment, do not treat as mandatory.

### 4. Generate short name

Extract keywords from the feature description. Build a 2–4 word hyphenated short name in action-noun format, preserving technical terms and acronyms (e.g. "Add user auth" → `user-auth`).

### 5. Find highest existing number

Run:

```bash
git fetch --all --prune
git ls-remote --heads origin | grep -E "refs/heads/[0-9]+-<short-name>$"
git branch | grep -E "^[* ]*[0-9]+-<short-name>$"
```

Also list `spek-fu/project/spec-features/` for directories matching `[0-9]+-<short-name>`. Take the highest number found across all three sources, +1 (or `1` if none exist).

### 6. Create branch and feature directory

Create branch `###-short-name` and directory `spek-fu/project/spec-features/###-short-name/`, both exactly once, using the number and short name from Steps 4–5.

> If either already exists unexpectedly, stop and report failure instead of overwriting.

### 7. Load spec template

Read `spek-fu/plugins/spec/templates/spec-feature-template.md` fully. Identify all required sections and their order.

> If the template cannot be read, stop and report failure.

### 8. Draft the spec

Extract actors, actions, data, constraints, and success conditions from the feature description. Document assumptions for every informed guess. Write to `spek-fu/project/spec-features/###-short-name/spec.md` following the template's section order exactly. Exclude implementation details.

### 9. Mark ambiguities

Use `[NEEDS CLARIFICATION]` only for ambiguities that significantly impact scope, capped at `maxClarificationMarkers`. Beyond the cap, make informed guesses and record them as assumptions instead.

### 10. Resolve clarifications

If markers remain, ask the user for all of them in batches of 5 questions per batch until every marker is answered.

### 11. Replace markers

After each batch of responses, replace the corresponding `[NEEDS CLARIFICATION]` markers in `spec.md` with the user's chosen answers.

### 12. Report

Report the branch name, the `spec.md` path, and the clarification count (resolved / remaining).

</workflow>

<done_conditions>

## Done Conditions

- Branch `###-short-name` and directory `spek-fu/project/spec-features/###-short-name/` exist.
- `spec.md` exists inside that directory with every template section populated and no `[NEEDS CLARIFICATION]` markers remaining.
- No implementation detail present in `spec.md`.

</done_conditions>
