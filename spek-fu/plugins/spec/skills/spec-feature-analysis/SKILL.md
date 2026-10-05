---
name: spec-feature-analysis
description: "Inspects a feature's pipeline artifacts and produces a read-only Feature Analysis Report with a readiness verdict, artifact inventory, staleness signals, clarification-marker counts, and cross-artifact consistency findings."
---

# Spec Feature Analysis

Read-only pipeline inspector. Checks every spec artifact for a feature branch — presence, staleness, `[NEEDS CLARIFICATION]` markers, `tasks.md` state, cross-artifact consistency — and writes a **Feature Analysis Report** with a three-tier Readiness Verdict (`READY` / `READY WITH WARNINGS` / `BLOCKED`). Never modifies any artifact but its own report.

Artifact map: `spek-fu/plugins/spec/knowledge/pipeline-artifacts.md`
Template: `spek-fu/plugins/spec/templates/feature-analysis-report-template.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

Anytime before or between pipeline steps, to check what's present, stale, or unresolved in a feature's artifacts before running the next spec skill.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-feature-analysis.maxFindings`, `spec-technical-draft.contractsPath`)

</inputs>

<outputs>

## Outputs

- `feature-analysis-report.md` written to `<spec-file-directory>/`, overwriting any prior report
- Completion report: readiness verdict, marker total, status, report path

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read-only: never write to any file except `<spec-file-directory>/feature-analysis-report.md`.
- Never invoke or dispatch any other skill, agent, or pipeline step.
- Never phrase Next Actions as automated actions — prose suggestions addressed to the user only.
- Render the Readiness Verdict as the first substantive line of the written report.
- Overwrite the prior report on re-invocation; never write a timestamped variant.
- Cap Consistency Findings at `maxFindings` (config, default `50`); summarize overflow in one line.
- If `spec-file` is missing, stop and report `blocked` — never fabricate findings from an unresolved path.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, label, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Read-Only** — this skill informs, it never acts; any mutation belongs to `spec-clarification` or the pipeline skill that owns the stale artifact.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-feature-analysis.maxFindings` (default `50`) and `spec-technical-draft.contractsPath` (default `spek-fu/project/contracts`).

### 2. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.

### 3. Build artifact inventory

Check existence and last-modified timestamp (`git log --format="%ai" -1 -- <path>`, else `unknown`) for every artifact in `spek-fu/plugins/spec/knowledge/pipeline-artifacts.md`'s path table, resolved against `<spec-file-directory>` (and `<contracts-root>` for the contracts entry). For `spec.md`, also record `## Clarifications` / `## Assumptions` section presence.

### 4. Detect staleness

Compare timestamps along the Staleness Chain in `pipeline-artifacts.md` for every upstream/downstream pair both present. Record `stale` (upstream newer than downstream) / `current` / `indeterminate`. Record `none detected` if none apply.

### 5. Count clarification markers

Grep `NEEDS CLARIFICATION` and verify it is a marker - per artifact that can carry it (`spec.md`, devils-advocate report, `research.md`, `data-model.md`, `quickstart.md`, `technical-plan.md`, `tdd-report.md`, `tasks.md`). Record per-artifact and grand total.

### 6. Analyze tasks.md state

If present, parse: phase headings with per-phase task count; global `[ ]`/`[X]`/`[!]` counts; subtask count; tasks carrying an `@ref:` hint to a TDD unit ID. Record `unknown` per metric if unparseable.

### 7. Cross-artifact consistency

Load `spec.md`'s User Stories and Functional Requirements, and `tasks.md`'s task descriptions and `[USN]` tags. Cap total findings at `maxFindings`; summarize overflow in one line.

- **Coverage gaps**: a User Story with no `[USN]`-tagged task referencing it → `UNCOVERED`, `HIGH`.
- **Marker context**: each marker from Step 5 → artifact, line context, question text; `HIGH` in `spec.md`/`tasks.md`, `MEDIUM` elsewhere.
- **Inconsistency**: terminology drift across artifacts (`MEDIUM`); an entity in `data-model.md` missing from `tasks.md` (`HIGH`); contradicting requirements in `spec.md` (`CRITICAL`).

> If `tasks.md` is absent: skip Coverage gaps, record why; continue the rest.

### 8. Compute readiness verdict

First match wins:

1. **`BLOCKED`** — `spec.md` or `tasks.md` missing, or any `CRITICAL` finding.
2. **`READY WITH WARNINGS`** — not BLOCKED and any of: markers > 0, staleness detected, a `HIGH` finding, an intermediate artifact missing.
3. **`READY`** — otherwise.

### 9. Write the report

Load `spek-fu/plugins/spec/templates/feature-analysis-report-template.md`. Populate every section from Steps 3–8; Next Actions as prose suggestions only (e.g. "run `spec-tasks-draft`"), never phrased as instructions the agent itself will execute. Delete any prior `feature-analysis-report.md` at `<spec-file-directory>/`, then write the new one there.

### 10. Report completion

Report readiness verdict, marker grand total, status (`ok`/`blocked`/`fail`), and the report path.

</workflow>

<done_conditions>

## Done Conditions

- `feature-analysis-report.md` exists at `<spec-file-directory>/`, Readiness Verdict as its first substantive line.
- Every other artifact in `<spec-file-directory>` (and `<contracts-root>`) unchanged.
- Findings capped at `maxFindings`; overflow summarized in one line.
- Completion report given: readiness verdict, marker total, status, report path.

</done_conditions>
