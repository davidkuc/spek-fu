---
name: project-devils-advocate
description: "Adversarially reviews the project docs to surface hidden assumptions, architectural fragility, scope and vision weaknesses, and documentation gaps into a Devils Advocate Report."
---

# Project Devils Advocate

Adversarially critiques the project docs on three surfaces — vision and scope, documented architecture, and the documentation as an artifact — and writes an unsparing **Devils Advocate Report**. No diplomatic softening; the value is institutionalized dissent.

Template: `spek-fu/plugins/project/templates/project-devils-advocate-report-template.md`
Config: `spek-fu/plugins/project/knowledge/config.json`

## When to use

Run manually when the project docs need adversarial review, optionally after `project-research`, before they are clarified or relied on for new feature work. Part of the audit track in `project-workflow.md`.

<inputs>

## Inputs

- `target` (optional; a doc path or area name to narrow scope; defaults to the whole doc set)
- `user-focus` (optional; biases detection passes toward a named risk area)
- `spek-fu/plugins/project/knowledge/config.json` (`project-devils-advocate.maxFindings`, `paths.reportsRoot`)

</inputs>

<outputs>

## Outputs

- `spek-fu/project/reports/project-devils-advocate/project-devils-advocate-report.md` (or a timestamped variant if one already exists)
- Completion report: finding count, status, report path

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read project docs only (`project.md`, `roadmap.md`, `project-features/`, `technical.md`, `project-docs/`, `user-flows/`); never read source code, `code-docs/`, or spec artifacts, except advisory knowledge retrieval (`framework-compounding-agent`).
- Never modify any project doc; write only within the report folder.
- Never soften findings, add praise, or balance criticism with positives.
- Treat every implicit assumption in the docs as credible risk; flag it.
- Do not propose fixes unless the user explicitly asks after reading the report.
- Cap findings at `maxFindings` (default `100`).
- If `project.md` is missing or the `target` does not exist, stop and report `blocked` — never invent doc content.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, warning, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Unsparing Critique** — the report exposes credible risk without softening.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/project/knowledge/config.json`. Extract `project-devils-advocate.maxFindings` (default `100`) and `paths.reportsRoot` (default `spek-fu/project/reports`).

### 2. Retrieve advisory lessons

Spawn the `framework-compounding-agent` agent (read mode) with the project's topic. Hold returned lessons as advisory context for Step 5; apply judgment, do not treat as mandatory.

### 3. Resolve and load scope

Use `target` if given, otherwise the whole doc set. Read the in-scope docs in full. Note `user-focus` and apply it throughout Step 5.

> If `project.md` or the `target` is missing: stop, report `blocked`.

### 4. Build internal risk models

From the docs only, construct (internal, not output verbatim): Assumption Inventory, Fragility Map, Scope Creep Map, Bias Indicators.

### 5. Run detection passes

Apply each pass independently across the three surfaces; cap total findings at `maxFindings`.

- **Hidden Assumptions**: unstated users, adoption, infrastructure, third-party, and regulatory assumptions in vision, scope, and architecture.
- **Optimism & Planning Fallacy**: roadmap phases without dependency or contingency, claims of "done" with no evidence, no rollback or monitoring.
- **Architectural Fragility**: single points of failure, tight coupling, vendor lock-in, unproven tech, bottlenecks, security and data risks in `technical.md` and area Technical.
- **Documentation Weakness**: vague terms, unverifiable claims, contradictions between docs, orphaned or missing areas, stale-looking sections, feature entries that describe mechanics.
- **Worst-Case Scenarios**: launch failure, 10x growth, malicious input, data loss, outage, breach, maintainer departure.
- **Adversarial Perspective**: malicious user, competitor, auditor, regulator, new maintainer reading only these docs.

### 6. Resolve output path

Default folder `spek-fu/project/reports/project-devils-advocate/`. If no prior `project-devils-advocate-report.md` exists there, use that filename; otherwise `project-devils-advocate-report-<YYYY-MM-DDTHH-mm-ss>.md`.

### 7. Compose the report

Load `spek-fu/plugins/project/templates/project-devils-advocate-report-template.md`. Feed unique findings into the Risk Register, one row each, classified `VISION` | `SCOPE` | `ARCHITECTURE` | `OPERATIONAL` | `SECURITY` | `DOCUMENTATION`. Carry any `[NEEDS CLARIFICATION]` markers from the in-scope docs into `## Carried Clarifications`. Reference Risk Register IDs only in Top 5 Failure Causes.

### 8. Write the report

Write to the path from Step 6, creating the folder if needed. If a prior report existed, say so in the completion message.

### 9. Report completion

Report finding count, status (`ok`/`blocked`/`fail`), and the report path.

</workflow>

<done_conditions>

## Done Conditions

- Report exists at the resolved path, following the template's section order, findings capped at `maxFindings`.
- No project doc modified.
- No softened, praising, or balanced language in the report.
- Completion report given: finding count, status, report path.

</done_conditions>
