---
name: project-research
description: "Verify the project docs against the codebase and online sources by delegating parallel fact-finding per dimension, and synthesize findings into a project-research-report.md."
---

# Project Research

Fact-checks the project documentation (`project.md`, `technical.md`, `project-docs/`, `roadmap.md`, `user-flows/`) against reality, delegating parallel investigations per dimension and synthesizing a structured `project-research-report.md`. Reality is `code-docs/` first, real source only where `code-docs/` is silent; online sources add grounding.

Template: `spek-fu/plugins/project/templates/project-research-report-template.md`
Config: `spek-fu/plugins/project/knowledge/config.json`
Area list: `spek-fu/plugins/project/knowledge/area-registry.md`

## When to use

Run manually, independent of any shipped feature, when the project docs need to be checked for drift against the code or grounded against external facts before they are challenged or clarified. Part of the audit track in `project-workflow.md`.

<inputs>

## Inputs

- `target` (optional; a doc path or area name to narrow scope; defaults to the whole `spek-fu/project/` doc set)
- `spek-fu/plugins/project/knowledge/config.json` (`project-research.maxDimensions`, `project-research.defaultDimensions`, `paths.*`)

</inputs>

<outputs>

## Outputs

- `spek-fu/project/reports/project-research/project-research-report.md`, overwriting any prior report
- Completion report: dimension count, findings count, online findings count, status

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never modify any project doc; write only the report file.
- Findings are factual and tied to a doc path and section; never speculate or recommend — flag design implications as considerations instead.
- Check `code-docs/` first; read real source only where `code-docs/` is silent, and say so in the finding's evidence.
- Every online finding needs a source URL and goes only in `## Online Findings`; no URL means no finding.
- Web research is optional: if fetching is unavailable or fails, record that in Methodology and continue docs-vs-code only.
- Cap dimensions at `maxDimensions`.
- If `spek-fu/project/project.md` is missing or the `target` does not exist, stop and report `blocked` — never invent doc content.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, question, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Factual Only** — research produces evidence, not decisions; fixes belong to `project-clarification` or the docs-sync skills.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/project/knowledge/config.json`. Extract `project-research.maxDimensions` (default `8`), `project-research.defaultDimensions` (default: Architecture, Security, Operations & Deployment, Data & Domain Model, UX & User Flows, Quality & Testing, Reliability, Compliance & Legal), and `paths.reportsRoot`.

### 2. Resolve scope

Use `target` if given, otherwise the whole doc set. Confirm the files exist.

> If `project.md` or the `target` is missing: stop, report `blocked`.

### 3. Load doc context

Read the in-scope docs in full. Capture claims that can be verified: stated behavior, architecture and technology choices, environments, quality gates, user-flow steps, `[NEEDS CLARIFICATION]` markers.

### 4. Optional clarification

If the scope or an ambiguous claim materially affects what to verify, ask the user to confirm before proceeding (constitution `## AI Principles` → Ambiguity). Otherwise skip.

### 5. Gather codebase reality

Spawn the `doc-engine-executor` agent (Traverse workflow) over `code-docs/` for the in-scope subject matter. Where `code-docs/` is silent on a claim, record the gap so the dimension agent reads real source for it.

### 6. Retrieve advisory lessons

Spawn the `framework-compounding-agent` agent (read mode) with a summary of the in-scope docs. Hold returned lessons as advisory context for Steps 7 and 8.

### 7. Decompose into dimensions

Start from `defaultDimensions`, adjust to what the docs actually claim, cap at `maxDimensions`. For each dimension extract: relevant doc sections, claims to verify, and open questions into a Research Plan.

### 8. Delegate research in parallel

For each dimension spawn one research agent in parallel with: the doc paths, the dimension's claims and open questions, the `code-docs/` evidence from Step 5, and the instruction "verify each claim against code-docs, then source where code-docs is silent; where an external fact is relevant, ground it online and return the URL; produce factual findings tied to doc sections; no recommendations." Track each dimension's status (pending/in-progress/complete/failed).

> If delegation fails for all dimensions: stop, report `blocked`.
> If some fail: proceed with the rest, note failures in the report.

### 9. Synthesize findings

Collect findings. Load `spek-fu/plugins/project/templates/project-research-report-template.md`; otherwise use its section order: Executive Summary, Methodology, Findings by Dimension, Online Findings, Cross-Dimension Insights, Unknowns & Deferred Questions. Give every drift finding a verdict of `Confirmed`, `Drift`, or `Unverifiable`; move URL-backed external facts into `## Online Findings`.

### 10. Write the report

Write to `spek-fu/project/reports/project-research/project-research-report.md`, creating the folder if needed and overwriting any prior report, with the metadata block filled in.

### 11. Report completion

Report dimension count, findings count, online findings count, status (`ok`/`partial`/`blocked`), and the report path.

</workflow>

<done_conditions>

## Done Conditions

- Report exists at the path above, following the template's section order, every finding tied to a doc section, every online finding carrying a URL.
- No project doc modified.
- Completion report given: dimension count, findings count, online findings count, status, report path.

</done_conditions>
