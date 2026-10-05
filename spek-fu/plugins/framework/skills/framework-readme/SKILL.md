---
name: framework-readme
description: "Owns spek-fu/README.md and keeps it synchronized with the current state of the framework."
---

# Framework Readme

Owns `spek-fu/README.md`: the framework's top-level glossary, high-level flow, plugin index, and structure map.

## When to use

Run after any structural change to the framework — a plugin, skill, or agent is added, renamed, or removed; a new term needs defining; or the top-level `spek-fu/` layout changes. Invoked as the final step of every plugin's `<plugin>-maintenance` skill.

<inputs>

## Inputs

- Current `spek-fu/README.md`
- Every plugin's `<plugin>-workflow.md` (purpose line, glossary terms, skill sequence)
- Actual `spek-fu/plugins/` and top-level `spek-fu/` folder layout, including each plugin's `skills/` folder (for `<plugin>-maintenance` skills)

</inputs>

<outputs>

## Outputs

- Updated `spek-fu/README.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never add a plugin, glossary term, map entry, or flow step that isn't backed by an actual file, folder, or workflow doc entry — verify with a directory listing or the source workflow doc first.
- Keep every entry in the README's existing top-level sections (Glossary, High-Level Flow, Plugins table, Framework Map, Plugin Structure) and one-line format; do not add new top-level sections without an explicit user request.
- High-Level Flow's subsections are the exception: add or remove them to match the ordered skill sequences actually documented across the plugins' workflow docs — no user request needed for that.
- Do not duplicate plugin-internal detail (skill lists, rules) — the README stays a high-level index; that detail lives in each `<plugin>-workflow.md`. High-Level Flow is the one exception: it may name skills in sequence because no other file shows the cross-plugin order.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every glossary and table entry uses the fewest words that preserve meaning, per constitution `## AI Principles`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read current README

Read `spek-fu/README.md` in full.

### 2. Gather current framework state

List `spek-fu/plugins/*` and read each plugin's `<plugin>-workflow.md` in full — its purpose line, glossary terms, and every ordered/numbered skill sequence in its "How to use" / "Choosing the right skill" section. List top-level `spek-fu/*` folders and each plugin's `skills/` folder.

### 3. Diff and update

- **Glossary** — add terms introduced by any plugin's workflow doc that aren't yet defined; remove terms for concepts no longer present.
- **High-Level Flow** — one subsection per distinct ordered skill sequence found across the workflow docs, sourced from those docs, not invented:
  - Known subsections today: **Feature Lifecycle** (spec's ordered sequence, `[P]` on steps marked parallel there, annotated with where `doc-engine` and `project` plugin skills plug in per their own workflow docs), **Bootstrapping a new plugin** (framework-workflow.md's plugin-creation steps), **Maintaining a plugin** (the generic change → `<plugin>-maintenance` → `framework-readme` loop, listing every `<plugin>-maintenance` skill actually present).
  - **Identify new flows**: for each workflow doc, check whether it defines an ordered sequence not yet covered by an existing subsection (e.g. a new plugin's own "how to use" sequence, or a second distinct flow added to an existing plugin). If found, add a new subsection named after that flow, numbered/ordered exactly as the source doc has it, with `[P]` preserved on any steps marked parallel there.
  - Remove a subsection if its source sequence no longer exists in any workflow doc.
- **Plugins table** — one row per plugin actually present under `spek-fu/plugins/`, purpose sourced from its workflow doc.
- **Framework Map** — one line per top-level `spek-fu/*` folder actually present.
- **Plugin Structure** — reflects the folder types actually used by plugins (`agents/`, `knowledge/`, `scripts/`, `skills/`, `templates/`, `*-workflow.md`).

### 4. Write the file

Save `spek-fu/README.md` only if content changed.

</workflow>

<done_conditions>

## Done Conditions

- Plugins table lists every plugin under `spek-fu/plugins/` with an accurate one-line purpose.
- Glossary has no term missing or stale relative to plugin workflow docs.
- High-Level Flow has one subsection per ordered skill sequence actually documented in a plugin's workflow doc, with no stale or missing subsection: Feature Lifecycle matches `spec-workflow.md`, Bootstrapping matches `framework-workflow.md`, Maintaining lists every `<plugin>-maintenance` skill actually present, and any newly introduced flow has its own subsection.
- Framework Map matches the actual top-level `spek-fu/` folders.

</done_conditions>
