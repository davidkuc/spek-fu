---
name: spec-devils-advocate
description: "Adversarially reviews a feature spec to surface hidden assumptions, architectural fragility, and failure modes into a Devils Advocate Report."
---

# Spec Devils Advocate

Adversarially critiques a feature spec — hidden assumptions, architectural fragility, requirement gaps, worst-case scenarios — and writes an unsparing **Devils Advocate Report** to disk. No diplomatic softening; the value is institutionalized dissent before planning or implementation.

Template: `spek-fu/plugins/spec/templates/devils-advocate-report-template.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

Optional step in the Define phase, after `spec-feature-draft` (and optionally `spec-research`), when a spec needs adversarial risk review before deeper planning or implementation begins.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `output-dir` (optional; defaults to `<spec-file-directory>/devils-advocate/` folder)
- `user-focus` (optional; biases detection passes toward a named risk area)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-devils-advocate.maxFindings`)

</inputs>

<outputs>

## Outputs

- `devils-advocate-report.md` (or a timestamped variant if one already exists) written to `output-dir`
- Completion report: finding count, status, report path

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read `spec-file` only; never read implementation plans, task lists, or other workspace artifacts, except advisory knowledge retrieval (`framework-compounding-agent`).
- Never modify `spec-file`; write only within `output-dir`.
- Never soften findings, add praise, or balance criticism with positives — unsparing critique is the point.
- Treat every implicit assumption in the spec as credible risk; flag it.
- Cap findings at `maxFindings` (config, default `100`).
- If `spec-file` is missing or unreadable, stop and report `blocked`/`fail` — never invent spec content.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, warning, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Unsparing Critique** — the report exposes credible risk without diplomatic softening; do not propose fixes unless the user explicitly asks after reviewing the report.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-devils-advocate.maxFindings` (default `100` if the file or key is missing).

### 2. Retrieve advisory lessons

Spawn the `framework-compounding-agent` agent (read mode) with the spec's topic as input. Hold any returned lessons as advisory context for Step 6; apply judgment, do not treat as mandatory.

### 3. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.
> If the file exists but can't be read: stop, report `fail`.

### 4. Load spec file

Read `spec-file` in full. Note `user-focus` (if provided) — apply it throughout detection passes to emphasize that risk area.

### 5. Build internal risk models

Construct, from spec content only (used internally, not output verbatim): Assumption Inventory, Fragility Map, Complexity Map, Bias Indicators.

### 6. Run detection passes

Apply each pass independently. Cap total findings at `maxFindings` across all passes.

- **Hidden Assumptions**: unstated dependencies, infrastructure/performance/user-behavior/third-party-reliability assumptions.
- **Optimism & Planning Fallacy**: underestimated complexity, missing contingency, no rollback/monitoring/failure handling.
- **Architectural Fragility**: single points of failure, tight coupling, vendor lock-in, unproven tech, bottlenecks, security gaps, data risks.
- **Requirement Weakness**: vague terms, unmeasurable criteria, conflicting requirements, undefined edge cases.
- **Worst-Case Scenarios**: launch-day failure, 10x growth, malicious input, data corruption, outages, breach, team departure.
- **Adversarial Perspective**: malicious user, competitor, auditor, regulator, maintainer, burned-out engineer.

### 7. Resolve output path

Derive `output-dir` as `<spec-file-directory>/devils-advocate/` directory if not provided. Check for a prior `devils-advocate-report.md` there. If none, use that filename. If one exists, use a timestamped filename: `devils-advocate-report-<YYYY-MM-DDTHH-mm-ss>.md`.

### 8. Compose the report

Load `spek-fu/plugins/spec/templates/devils-advocate-report-template.md`. Feed unique findings into the Risk Register, one row each, classified `ASSUMPTION` | `ARCHITECTURE` | `REQUIREMENT` | `OPERATIONAL` | `SECURITY`. If `spec-file` has `[NEEDS CLARIFICATION]` markers, carry them into `## Carried Clarifications`. Reference Risk Register IDs only in Top 5 Failure Causes; never restate findings there.

### 9. Write the report

Write the composed report to the resolved path from Step 7. If a prior report existed, note in the completion message that it was preserved and the new report was written under a timestamped name.

### 10. Report completion

Report finding count, status (`ok`/`blocked`/`fail`), and the report path.

</workflow>

<done_conditions>

## Done Conditions

- Devils Advocate Report exists at the resolved path, following the template's section order, findings capped at `maxFindings`.
- `spec-file` unchanged.
- No softened, praising, or diplomatically balanced language present in the report.
- Completion report given: finding count, status, report path.

</done_conditions>
