---
name: framework-compounding-read
description: "Match input against the shared compound-knowledge.md file and return the relevant learnings."
---

# Framework Compounding Read

Reads `spek-fu/plugins/framework/knowledge/compound-knowledge.md`, scores each entry's relevance against the given input, and returns only the entries that meet the confidence threshold.

## When to use

Before or during work that could reuse a prior learning (e.g. drafting a plan, starting a task, hitting a recurring problem), to surface applicable `L-{id}` entries.

<inputs>

## Inputs

- Input to match against (e.g. a task description, error, or topic)

</inputs>

<outputs>

## Outputs

- List of matched `L-{id}` entries (title, tags, trigger, context, solution), each with its confidence score
- Empty result if no entry meets the threshold

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never modify `compound-knowledge.md`; this skill is read-only.
- Strong match: confidence `x >= 0.6` — include in the result.
- Weak match: confidence `x < 0.6` — ignore, do not include or mention.
- If `compound-knowledge.md` does not exist or has no entries, return an empty result; do not fabricate matches.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every returned entry and confidence note uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Load the knowledge database

Read `spek-fu/plugins/framework/knowledge/compound-knowledge.md`. If missing or empty, skip to step 4 with no entries.

### 2. Score each entry

For each `## L-{id}` entry, judge how relevant its **Trigger**, **Context**, and **Tags** are to the input. Assign a confidence score from 0 to 1.

### 3. Filter by threshold

Keep entries scoring `>= 0.6` (strong match). Discard entries scoring `< 0.6` (weak match).

### 4. Return matches

Return the kept entries in descending confidence order, each with its `L-{id}`, title, and confidence score. Return an empty result if none qualify.

</workflow>

<done_conditions>

## Done Conditions

- All entries in `compound-knowledge.md` were evaluated against the input.
- Only entries with confidence `>= 0.6` are returned.
- `compound-knowledge.md` is unchanged.

</done_conditions>
