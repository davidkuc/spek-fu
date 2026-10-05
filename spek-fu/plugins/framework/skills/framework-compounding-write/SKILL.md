---
name: framework-compounding-write
description: "Append one or more learnings as stable-ID entries to the shared compound-knowledge.md file."
---

# Framework Compounding Write

Appends learnings to `spek-fu/plugins/framework/knowledge/compound-knowledge.md` as `L-{id}` entries, preserving stable ID ordering.

Entry template: `spek-fu/plugins/framework/templates/compound-knowledge-entry.md`

## When to use

When a learning (a trigger, context, and solution from resolved work) should be recorded for future reuse across the project.

<inputs>

## Inputs

- One or more learnings, each with: a title, tags, trigger, context, solution

</inputs>

<outputs>

## Outputs

- `spek-fu/plugins/framework/knowledge/compound-knowledge.md`, updated with one new `## L-{id}` entry per learning, appended at the end

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Always append new entries at the end of the file, in the order the learnings were given.
- Each new ID is the highest existing `L-{id}` in the file, plus one, incrementing per new entry within the same run.
- If `compound-knowledge.md` does not exist, create it with a `# Compound Knowledge` title before adding entries.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every field of an entry (title, trigger, context, solution) uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Gather learnings

Collect learnings and context from the input.

### 2. Read the current file

Read `spek-fu/plugins/framework/knowledge/compound-knowledge.md`. If it does not exist, treat it as empty (no existing entries, no existing ID).

### 3. Determine the next ID

Scan all `## L-{id}` headings in the file and find the highest numeric `{id}`. The next new entry uses that number plus one; each subsequent learning in the same run increments from there.

### 4. Format each entry

Fill `spek-fu/plugins/framework/templates/compound-knowledge-entry.md` per learning, substituting the assigned ID and the gathered fields.

### 5. Append to the file

Write the file: if it did not exist, start with a `# Compound Knowledge` title; add each formatted entry after the last existing entry, separated by a blank line. Never touch existing entries.

### 6. Self-validate

Confirm every `L-{id}` in the file is unique, IDs increase monotonically top to bottom, and no existing entry's text changed.

</workflow>

<done_conditions>

## Done Conditions

- `compound-knowledge.md` contains one new `## L-{id}` entry per input learning, appended after existing entries.
- All IDs in the file remain unique and in stable, ascending order.
- No pre-existing entry was modified, reordered, or renumbered.

</done_conditions>
