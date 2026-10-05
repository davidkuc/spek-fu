---
name: spec-testability-draft
description: "Analyzes a feature spec and its Devils Advocate Report from a test engineering perspective, producing a Testability Assessment Report."
---

# Spec Testability Draft

Grades a feature spec's testability — verifiability, controllability, isolation, strategy shape, risk inversion, anti-patterns — incorporating upstream risk findings from the Devils Advocate Report, and writes a **Testability Assessment Report** to disk. Read-only: never modifies `spec-file` or the source report.

Taxonomy: `spek-fu/plugins/spec/knowledge/testability-taxonomy.md`
Template: `spek-fu/plugins/spec/templates/testability-assessment-report-template.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

Optional step in the Define phase, after `spec-devils-advocate` has produced a report, when a spec needs a test-engineering readiness grade before deeper planning or implementation begins.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `devils-advocate-report` (optional; resolved from `spec-file`'s `devils-advocate/` folder if absent)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-testability-draft.maxFindings`)

</inputs>

<outputs>

## Outputs

- `testability-assessment.md` (or a timestamped variant if one already exists) written to `<spec-file-directory>/test-expert/`
- Completion report: findings count, status, report path

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read `spec-file` and `devils-advocate-report` only; never read plan.md, tasks.md, or other workspace artifacts.
- Never modify `spec-file` or the devils-advocate report; write only within `<spec-file-directory>/test-expert/`.
- Never proceed without a resolved devils-advocate report — this skill is downstream of `spec-devils-advocate`.
- Never soften, omit, or dilute findings.
- Never equate test coverage percentage with correctness or testability.
- Cap findings at `maxFindings` (config, default `40`).
- If `spec-file` or `devils-advocate-report` is missing or unreadable, stop and report `blocked`/`fail` — never invent content.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, label, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Unsparing Critique** — the report exposes credible testability risk without diplomatic softening, mirroring `spec-devils-advocate`'s Pillar of the same name.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-testability-draft.maxFindings` (default `40` if the file or key is missing).

### 2. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.

### 3. Resolve devils-advocate report

If `devils-advocate-report` is provided, use it. Otherwise look under `<spec-file-directory>/devils-advocate/`: prefer `devils-advocate-report.md`; else the most recently modified `devils-advocate-report-*.md`.

> If none found: stop, report `blocked`. State: "spec-testability-draft requires a prior devils-advocate report. Run spec-devils-advocate first."

### 4. Load artifacts

Read `spec-file` in full: Functional Requirements, Non-functional Requirements, User Stories, Edge Cases. Read the devils-advocate report: Executive Warning, Risk Register, Spec-Only Limitations, Top 5 Failure Causes. If either contains `[NEEDS CLARIFICATION]` markers, carry them into `## Carried Clarifications`.

### 5. Build the testability model

Apply the six models in `spek-fu/plugins/spec/knowledge/testability-taxonomy.md` (Verifiability, Controllability, Isolation, Testing Strategy Geometry, Risk Inversion, Anti-Pattern Detection) against the loaded content. Used internally as the basis for every report section; do not output the models verbatim.

### 6. Resolve output path

Derive `<spec-file-directory>/test-expert/` (create if absent). If no `testability-assessment.md` exists there, use that filename. Otherwise use a timestamped filename: `testability-assessment-<YYYY-MM-DDTHH-mm-ss>.md`.

### 7. Compose the report

Load `spek-fu/plugins/spec/templates/testability-assessment-report-template.md`. Populate every Risk Findings row with exact Step 5 labels (Verifiability, Controllability, Isolation). Do not duplicate problem statements across sections. Cap Risk Findings at `maxFindings`; summarize overflow.

### 8. Write the report

Write the composed report to the resolved path from Step 6. If a prior report existed, note in the completion message that it was preserved and the new report was written under a timestamped name.

### 9. Report completion

Report findings count, status (`ok`/`blocked`/`fail`), and the report path. Do not write the full report body to chat.

</workflow>

<done_conditions>

## Done Conditions

- Testability Assessment Report exists at the resolved path, following the template's section order, Risk Findings capped at `maxFindings`.
- `spec-file` and the devils-advocate report unchanged.
- No softened, praising, or diplomatically balanced language present in the report.
- Completion report given: findings count, status, report path.

</done_conditions>
