---
name: project-documentation-analysis
description: "Inspects the project docs and produces a read-only Documentation Analysis Report with a readiness verdict, inventory and area coverage, staleness signals, clarification-marker counts, ID and cross-reference integrity, shipped-feature coverage, and consistency findings."
---

# Project Documentation Analysis

Read-only inspector of `spek-fu/project/`. Checks presence, staleness, `[NEEDS CLARIFICATION]` markers, ID and cross-reference integrity, shipped spec-feature coverage, and cross-doc consistency, then writes a **Documentation Analysis Report** with a three-tier Readiness Verdict (`READY` / `READY WITH WARNINGS` / `BLOCKED`). Never modifies anything but its own report.

Artifact map: `spek-fu/plugins/project/knowledge/project-artifacts.md`
Area list: `spek-fu/plugins/project/knowledge/area-registry.md`
Feature format: `spek-fu/plugins/project/knowledge/feature-format.md`
Template: `spek-fu/plugins/project/templates/documentation-analysis-report-template.md`
Config: `spek-fu/plugins/project/knowledge/config.json`

## When to use

Anytime, to check what is missing, stale, or inconsistent in the project docs, before or after the other audit-track skills or the docs-sync skills. Part of the audit track in `project-workflow.md`.

<inputs>

## Inputs

- `spek-fu/plugins/project/knowledge/config.json` (`project-documentation-analysis.maxFindings`, `paths.*`)

</inputs>

<outputs>

## Outputs

- `spek-fu/project/reports/project-documentation-analysis/documentation-analysis-report.md`, overwriting any prior report
- Completion report: readiness verdict, marker total, status, report path

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read-only: never write to any file except the report path above.
- Never invoke or dispatch any other skill, agent, or step.
- Never phrase Next Actions as automated actions — prose suggestions addressed to the user only.
- Render the Readiness Verdict as the first substantive line of the written report.
- Overwrite the prior report on re-invocation; never write a timestamped variant.
- Cap Consistency Findings at `maxFindings` (default `50`); summarize overflow in one line.
- If `spek-fu/project/project.md` is missing, stop and report `blocked` — never fabricate findings.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, label, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Read-Only** — this skill informs, it never acts; any mutation belongs to `project-clarification` or the skill that owns the affected doc.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/project/knowledge/config.json`. Extract `project-documentation-analysis.maxFindings` (default `50`) and `paths.*` (defaults: `spek-fu/project/reports`, `.../code-docs`, `.../spec-features`, `.../contracts`).

### 2. Confirm entry point

Confirm `spek-fu/project/project.md` exists.

> If missing: stop, report `blocked`.

### 3. Build inventory and area coverage

Check existence and last-modified (`git log -1 --format=%cI -- <path>`, else `unknown`) for every artifact in `project-artifacts.md`'s path table. Compare `project-docs/` against every row of `area-registry.md`; record each area as present or missing.

### 4. Detect staleness

Compare timestamps along the Staleness Chain in `project-artifacts.md` for every upstream/downstream pair both present. Record `stale` / `current` / `indeterminate`, or `none detected`.

### 5. Count clarification markers

Grep `NEEDS CLARIFICATION` in `project.md`, `technical.md`, `roadmap.md`, `project-docs/`, and `user-flows/`, verifying each hit is a marker. Record per-artifact and grand total.

### 6. Check ID and cross-reference integrity

Per `feature-format.md`:

- Every feature ID uses its area's prefix; IDs are unique and never reused; gaps are only explained by a `_Retired:_` line.
- Cross-area references point at an existing ID in the owner area.
- Every `roadmap.md` link resolves to an existing `project-features/` file; every `project-docs` link to a user flow resolves.
- Every `### Related Modules` entry resolves to an existing `code-docs/` file.

### 7. Check shipped spec-feature coverage

For each directory in `spec-features/` with a `spec.md`, determine whether an area's `## Functional` list, `roadmap.md`, or `user-flows/` reflects it (by its name or linked PF). Record `covered` / `uncovered` / `indeterminate`.

### 8. Cross-doc consistency

Cap total findings at `maxFindings`; summarize overflow in one line.

- **Uncovered shipped feature**: `HIGH`.
- **Marker context**: each marker from Step 5 → doc, line context, question; `HIGH` in `project.md`/`technical.md`, `MEDIUM` elsewhere.
- **Broken reference or ID violation** from Step 6: `HIGH`; a missing area file: `HIGH`.
- **Terminology drift** (including PL/EN) across docs: `MEDIUM`.
- **Contradiction** between `project.md`, `technical.md`, area docs, or roadmap status: `CRITICAL`.

### 9. Compute readiness verdict

First match wins:

1. **`BLOCKED`** — `project.md` or `technical.md` missing, or any `CRITICAL` finding.
2. **`READY WITH WARNINGS`** — not BLOCKED and any of: markers > 0, staleness detected, a `HIGH` finding.
3. **`READY`** — otherwise.

### 10. Write the report

Load `spek-fu/plugins/project/templates/documentation-analysis-report-template.md`. Populate every section from Steps 3–9; Next Actions as prose suggestions only (e.g. "run `project-functional-docs` for `008-project-attachments`"). Delete any prior report at the report path, create the folder if needed, then write the new one.

### 11. Report completion

Report readiness verdict, marker grand total, status (`ok`/`blocked`/`fail`), and the report path.

</workflow>

<done_conditions>

## Done Conditions

- Report exists at the path above, Readiness Verdict as its first substantive line.
- Every other file under `spek-fu/project/` unchanged.
- Findings capped at `maxFindings`; overflow summarized in one line.
- Completion report given: readiness verdict, marker total, status, report path.

</done_conditions>
