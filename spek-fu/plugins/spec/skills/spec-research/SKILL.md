---
name: spec-research
description: "Decompose a feature spec into orthogonal research dimensions, delegate parallel fact-finding to specialized agents, and synthesize findings into a spec-research-report.md."
---

# Spec Research

Orchestrates multi-dimensional research into a feature spec, delegating parallel investigations to specialized agents and synthesizing findings into a structured `spec-research-report.md`.

Template: `spek-fu/plugins/spec/templates/spec-research-report-template.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

Optional step in the Define phase, after `spec-feature-draft`, when spec areas carry unresolved fact-finding needs before deeper planning.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-research.maxDimensions`, `spec-research.defaultDimensions`)
- Current spec content (requirements, scope, constraints, ambiguities, references)

</inputs>

<outputs>

## Outputs

- `spec-research-report.md` written next to `spec-file`
- Completion report: dimension count, findings count, status

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read `spec-file` only; do not read other workspace artifacts, except advisory knowledge retrieval (`framework-compounding-agent`) and codebase traversal (`doc-engine-executor`).
- Never modify `spec-file`; write only to `spec-research-report.md`.
- Findings must be factual and tied to spec sections; never speculate or make design recommendations — flag design implications as considerations instead.
- Cap research dimensions at `maxDimensions`.
- If `spec-file` is missing or unreadable, stop and report `blocked`/`fail` — never invent spec content.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, question, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Factual Only** — research produces evidence, not decisions; design choices belong to later planning skills.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-research.maxDimensions` (default `8`) and `spec-research.defaultDimensions` (default: Architecture, Security, Performance, Reliability, Operations, Data, UX, Legal).

### 2. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.
> If the file exists but can't be read: stop, report `fail`.

### 3. Load spec context

Read `spec-file` in full. Capture requirements, scope boundaries (in/out), constraints, `[NEEDS CLARIFICATION]` markers, and references.

### 4. Optional clarification

If marked ambiguities or scope boundaries materially affect research scope, ask the user to confirm before proceeding (constitution `## AI Principles` → Ambiguity). Otherwise skip.

### 5. Gather codebase context

Spawn the `doc-engine-executor` agent (Traverse workflow) to gather relevant project context for the spec's domain.

### 6. Retrieve advisory lessons

Spawn the `framework-compounding-agent` agent (read mode) with a summary of the spec's requirements and scope. Hold returned lessons as advisory context for Steps 7 and 8.

### 7. Decompose into research dimensions

From the spec context, identify independent, orthogonal research dimensions — starting from `defaultDimensions`, adjusted to what the spec actually raises — capped at `maxDimensions`. For each dimension, extract: relevant spec sections, known facts/constraints, and open questions into a Research Plan.

### 8. Delegate research in parallel

For each dimension, spawn one research agent in parallel with: the `spec-file` path, the dimension's open questions and known facts, and the instruction "produce factual, actionable findings tied to spec sections; no design recommendations." Track each dimension's status (pending/in-progress/complete/failed).

> If delegation fails for all dimensions: stop, report `blocked`.
> If some dimensions fail: proceed with the rest, note failures in the report.

### 9. Synthesize findings

Collect findings from all completed dimensions. Load `spek-fu/plugins/spec/templates/spec-research-report-template.md` if available; otherwise use its hardcoded section order: Executive Summary, Methodology, Findings by Dimension, Cross-Dimension Insights, Unknowns & Deferred Questions. Tie every finding to the spec section(s) it relates to.

### 10. Write the report

Write to `spec-research-report.md` in `spec-file`'s directory under `spec-research/` folder, including the metadata block (`spec_file`, `research_date`, `dimensions_investigated`, `findings_count`, `research_status`).

### 11. Report completion

Report dimension count, findings count, status (`ok`/`partial`/`blocked`), and the report path.

</workflow>

<done_conditions>

## Done Conditions

- `spec-research-report.md` exists next to `spec-file`, following the template's section order, every finding tied to a spec section.
- `spec-file` unchanged.
- Completion report given: dimension count, findings count, status, report path.

</done_conditions>
