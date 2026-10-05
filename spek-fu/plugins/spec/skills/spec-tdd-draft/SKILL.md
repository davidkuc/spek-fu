---
name: spec-tdd-draft
description: "Translates a feature spec and technical plan into a risk-aware TDD design report of BDD test specifications and implementation waves."
---

# Spec TDD Draft

Formalizes a feature's testable behaviors into BDD-formatted TDD units, validates red-phase integrity, maps coverage, flags structural risk, and sequences incremental implementation waves into a **TDD Implementation Design Report**. Read-only: never modifies `spec-file`, `technical-plan.md`, or any other upstream artifact.

Taxonomy: `spek-fu/plugins/spec/knowledge/tdd-design-taxonomy.md`
Template: `spek-fu/plugins/spec/templates/tdd-report-template.md`

## When to use

Plan phase step, after `spec-technical-draft`, when a technical plan is ready to be formalized into sequenced, BDD-specified TDD units before `spec-tasks-draft` runs.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `technical-plan` (optional; resolved from `<spec-file-directory>/technical-plan.md` if absent)

</inputs>

<outputs>

## Outputs

- `tdd-report.md` (or a timestamped variant if one already exists) written to `<spec-file-directory>/tdd-designer/`
- Completion report: test count, risk count, verdict, status, report path

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Read `spec-file`, `technical-plan.md`, and the artifacts listed in its `## Input Artifacts` table only; never write to any of them — write only within `<spec-file-directory>/tdd-designer/`.
- Never implement code, suggest implementation detail, or fix test definitions — this skill produces a design report only.
- Never proceed without a resolved `technical-plan.md` — this skill is downstream of `spec-technical-draft`.
- Never soften risk findings, assume intent for ambiguous behavior, or hide structural risk.
- Mark unclear behavior `[NEEDS CLARIFICATION: <question>]` at the point of uncertainty; never guess.
- If zero testable behaviors are found, stop — do not write a partial report.
- If `spec-file` or `technical-plan.md` is missing or unreadable, stop and report `blocked`/`fail`.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every finding, label, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Unsparing Critique** — the report exposes credible structural risk without diplomatic softening, mirroring `spec-devils-advocate`'s Pillar of the same name.

</behavioral_anchors>

<workflow>

## Steps

### 1. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.

### 2. Resolve technical plan

If `technical-plan` is provided, use it. Otherwise resolve `<spec-file-directory>/technical-plan.md`.

> If missing: stop, report `blocked`. State: "spec-tdd-draft requires a technical plan. Run spec-technical-draft first."

### 3. Load context

Read `spec-file` in full: Functional Requirements, User Stories/Acceptance Scenarios, Edge Cases. Read `technical-plan.md` in full, then read every path in its `## Input Artifacts` table (data-model.md, contracts under `<contracts-root>/`, quickstart.md; testability-assessment.md if listed as present). If any artifact is missing, note the gap and continue on a best-effort basis. Carry any `[NEEDS CLARIFICATION]` marker found in these artifacts forward for `## 4. Carried Clarifications`.

### 4. Extract raw test inventory

From `spec-file`'s Functional Requirements, User Stories, and Edge Cases, plus `technical-plan.md`'s entities and contract endpoints, build one entry per testable behavior: `id` (T-001, T-002, …), `title`, `type` (acceptance/edge-case/negative/integration/non-functional), `described_behavior`, `dependencies`, `referenced_components`. Where testability-assessment.md is present, carry its Requirement-Level Testability label per matching requirement key forward as a flag.

> If zero testable behaviors are found: stop. Report "Zero testable behaviors detected across spec.md and technical-plan.md. Cannot produce a TDD design report." Do not write a partial report.

### 5. Normalize to TDD units

For each raw entry, apply `spek-fu/plugins/spec/knowledge/tdd-design-taxonomy.md` sections A–C: classify the behavior target, rewrite as explicit BDD (`Given`/`When`/`Then`), and validate red-phase integrity (`Strong`/`Weak (<reason>)`).

### 6. Identify risks and ambiguities

Apply taxonomy section D's five passes against the full TDD unit set. Each unique issue appears exactly once in Section 5 of the report with one primary `Type`. Order dependency findings are always `CRITICAL`. Coverage gaps go in Section 3, not Section 5.

### 7. Build implementation waves

Group TDD units into the four waves defined in taxonomy section F. Each wave must be independently greenable.

### 8. Assign risk severity

Apply taxonomy section E's severity scale to every Section 5 finding.

### 9. Resolve output path

Create `<spec-file-directory>/tdd-designer/` if absent. If no `tdd-report.md` exists there, use that filename. Otherwise use a timestamped filename: `tdd-report-<YYYY-MM-DDTHH-mm-ss>.md`.

### 10. Compose and write the report

Load `spek-fu/plugins/spec/templates/tdd-report-template.md`. Populate every section; collapse overlapping ambiguity/fragility findings into one Section 5 row rather than restating across sections. Write to the resolved path from Step 9. If a prior report existed, note in the completion message that it was preserved.

### 11. Report completion

Report test count, risk count, Final Verdict, status (`ok`/`blocked`/`fail`), the report path, and `carried-clarifications: N` when any marker was carried.

</workflow>

<done_conditions>

## Done Conditions

- TDD Implementation Design Report exists at the resolved path, following the template's section order, with every section populated and a Final Verdict selected.
- `spec-file`, `technical-plan.md`, and all other upstream artifacts unchanged.
- No softened, praising, or diplomatically balanced language present in the report.
- Completion report given: test count, risk count, verdict, status, report path.

</done_conditions>
