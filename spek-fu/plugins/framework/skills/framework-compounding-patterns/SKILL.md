---
name: framework-compounding-patterns
description: "Extract recurring patterns from the compound-knowledge.md learnings and merge the duplicate learnings that fed them."
---

# Framework Compounding Patterns

Finds groups of `L-{id}` learnings in `spek-fu/plugins/framework/knowledge/compound-knowledge.md` that describe the same recurring problem, writes one `P-{id}` pattern entry per group to `spek-fu/plugins/framework/knowledge/compound-patterns.md`, then merges the duplicate learnings and renumbers the remaining `L-{id}` entries.

Pattern template: `spek-fu/plugins/framework/templates/compound-pattern-template.md`
Learning entry template: `spek-fu/plugins/framework/templates/compound-knowledge-entry-template.md`

## When to run

On-demand, once `compound-knowledge.md` has accumulated enough learnings that recurring problems are worth naming as a pattern.

<inputs>

## Inputs

- `spek-fu/plugins/framework/knowledge/compound-knowledge.md` (source learnings)
- `spek-fu/plugins/framework/knowledge/compound-patterns.md` (existing patterns, if any)

</inputs>

<outputs>

## Outputs

- `spek-fu/plugins/framework/knowledge/compound-patterns.md`, updated with one new `P-{id}` entry per identified pattern
- `spek-fu/plugins/framework/knowledge/compound-knowledge.md`, with duplicate learnings merged and `L-{id}` values renumbered sequentially

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- A pattern requires at least 2 learnings that share the same root cause; never create a pattern from a single learning.
- Never delete a learning's information when merging; combine trigger/context/solution text instead of dropping any.
- Each new pattern ID is the highest existing `P-{id}` in the file, plus one, incrementing per new pattern within the same run.
- After renumbering, `L-{id}` values MUST be unique and strictly ascending top to bottom, with no gaps.
- If `compound-patterns.md` does not exist, create it with a `# Compound Patterns` title before adding entries.
- If `compound-knowledge.md` has fewer than 2 entries, stop: there is nothing to cluster.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every field of a pattern (why/what/prevents/examples) uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Load both files

Read `compound-knowledge.md` (all `L-{id}` entries) and `compound-patterns.md` (existing `P-{id}` entries, or treat as empty if missing).

### 2. Cluster recurring findings

Group learnings whose **Trigger** and **Context** describe the same underlying root cause, even if worded differently. Discard groups with fewer than 2 learnings — those are not yet recurring.

### 3. Determine the next pattern ID

Scan all `## [Pattern Name]\n**ID**: P-{id}` blocks and find the highest numeric `{id}`. Each new pattern in this run increments from there.

### 4. Draft each pattern

For each qualifying cluster, fill `spek-fu/plugins/framework/templates/compound-pattern-template.md`: name the pattern, explain why the problem repeats, what the pattern achieves, what it prevents, and list each source learning as a concrete example (reference its original title/trigger).

### 5. Append patterns

Append the drafted pattern entries to `compound-patterns.md`, after existing entries, in ascending ID order.

### 6. Merge duplicate learnings

For each clustered group, combine the learnings into a single `L-{id}` entry: keep the clearest title, union the tags, and merge trigger/context/solution text without losing information from any source entry. Remove the now-redundant entries.

### 7. Renumber learning IDs

Reassign `L-{id}` values sequentially from 1, preserving the original relative order of the remaining (merged and untouched) entries. Update every heading.

### 8. Self-validate

Confirm: every `P-{id}` and `L-{id}` is unique; `L-{id}` values are strictly ascending with no gaps; no learning's content was lost, only merged; `compound-patterns.md` entries follow the template section order exactly.

</workflow>

<done_conditions>

## Done Conditions

- One `P-{id}` entry exists per qualifying cluster of 2+ similar learnings, appended to `compound-patterns.md`.
- `compound-knowledge.md` has no remaining duplicate learnings; merged entries preserve all source information.
- `L-{id}` values in `compound-knowledge.md` are unique and strictly ascending with no gaps.
- `P-{id}` values in `compound-patterns.md` are unique and strictly ascending with no gaps.

</done_conditions>
