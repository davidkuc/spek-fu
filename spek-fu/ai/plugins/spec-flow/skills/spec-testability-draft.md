---
id: "spec-testability-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Analyzes spec.md and a prior devils-advocate report from a test engineering perspective, producing a Testability Assessment Report at {feature-dir}/test-expert/testability-assessment.md. USE FOR: evaluating feature spec testability, grading requirements as testable/non-testable, identifying structural testing risks, and projecting a testing strategy shape. DO NOT USE FOR: generating test code or test plans; consult the **spec-implement** skill for test execution."
anti-scope: "Does not generate test code, test plans, or implementation artifacts. Does not modify spec.md or any upstream artifact. Read-only analysis only."
tags:
  - "quality"
  - "specification"
  - "analysis"
  - "reporting"
inputs:
  - "feature-dir: path to the feature directory containing spec.md (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "{feature-dir}/test-expert/testability-assessment.md — structured Testability Assessment Report"
  - "Execution status: ok, blocked, or fail"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` via Branch Detection when `feature-dir` is absent; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-testability-draft

<!-- SECTION 1: Identity (primacy position) -->
Evaluates feature spec.md from test engineering perspective, incorporating upstream risk findings from Devils Advocate Report. Constructs multi-dimensional testability model across verifiability, controllability, isolation, strategy shape, risk inversion, and anti-pattern detection. Writes structured Testability Assessment Report to {feature-dir}/test-expert/testability-assessment.md.

**Scope boundary**: Read-only analysis only. Does NOT generate test code, modify spec.md, or alter upstream artifacts. For adversarial spec analysis producing the upstream report, consult **spec-devils-advocate**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER modify spec.md, the devils-advocate report, or any upstream artifact — write permission is strictly bounded to `{feature-dir}/test-expert/` ONLY — WHY: this is a read-only analysis skill; modifying inputs destroys the audit trail and corrupts the upstream phase.
2. NEVER proceed without a confirmed devils-advocate report — WHY: this skill is downstream of spec-devils-advocate; analyzing a spec without the upstream risk findings produces incomplete and misleading testability grades.
3. NEVER soften, omit, or dilute findings — WHY: an accurate risk picture, however uncomfortable, is the product; sanitizing it defeats the purpose of the analysis.
4. ALWAYS abort with an explicit error if `feature-dir`, spec.md, or the devils-advocate report cannot be found — WHY: guessing paths or inventing absent content produces a fabricated report with no analytical value.
5. NEVER equate test coverage percentage with correctness or testability — WHY: a metric that measures the wrong thing misleads design decisions.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `skill-meta-rules.md`, `paginated-read.md`, and `needs-clarification-protocol.md` as needed.

## Operational Anchors
- If feature-dir not supplied, apply Branch Detection procedure.
- Read-only: refuse any impulse to modify spec.md or devils-advocate report.
- Apply inversion thinking, Pareto risk targeting, and architectural layering.

## Branch Detection

> See `spek-fu/ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve feature-dir: if not supplied, apply Branch Detection from `branch-detection.md`. If unable to read that file, run `git branch --show-current`, extract numeric prefix and feature name, construct as `spek-fu/features/<branch-name>`. If command fails, stop and report `blocked`.
- Confirm artifacts exist: spec.md and Devils Advocate Report at devils-advocate/.
- **Stub-content guard**: Read first 200 lines of spec.md. If fewer than 3 distinct requirements/stories, abort with `blocked — spec.md too sparse; populate before running`.
- **Recency**: Use list_dir to enumerate devils-advocate/. Select most recent file by lexicographic sort of timestamp. Fall back to devils-advocate-report.md if no timestamped variants.
- **Report uniqueness**: Use file_search to find any testability-assessment*.md in test-expert/. If none exist, use testability-assessment.md. If prior reports exist, generate timestamped: testability-assessment-<YYYY-MM-DDTHH-mm-ss>.md.
- **Fail-fast**: Abort if feature-dir cannot be resolved; abort if spec.md missing; abort if no devils-advocate report located.

## Done conditions

- **Success**: test-expert/<output_filename> written and confirmed with chat summary.
- **Blocked**: feature-dir, spec.md, or Devils Advocate Report cannot be found — report which is missing and stop.
- **Fail**: Unrecoverable error prevents report creation — state error explicitly.

## Step 1 — Resolve paths and verify inputs

Derive absolute paths:
- spec = {feature-dir}/spec.md
- devils-advocate-dir = {feature-dir}/devils-advocate/
- devils-advocate-report: select in order:
  1. {feature-dir}/devils-advocate/devils-advocate-report.md (if exists)
  2. Most recently modified file matching devils-advocate-report-*.md under {feature-dir}/devils-advocate/

> **If feature-dir cannot be resolved**: abort with `status: fail`. State missing path explicitly.
> **If devils-advocate-report cannot be found**: abort with `status: blocked`. State: "spec-testability-draft requires prior devils-advocate report. Run spec-devils-advocate first."

## Step 2 — Load artifacts

From **spec.md**: Functional Requirements, Non-functional Requirements, User Stories, Edge Cases.

From **Devils Advocate Report**: Executive Warning, Risk Register, Spec-Only Limitations, Top 5 Failure Causes.

Do NOT load plan.md or tasks.md.

If either artifact contains `[NEEDS CLARIFICATION]` markers, record and carry into `## Carried Clarifications` section. Continue with best-effort analysis.

> **If spec.md sections missing or unlabeled**: continue on available content; mark missing rows as `UNDEFINED` in Verifiability column.

## Step 3 — Construct Testability Model

Build six analytical models (internal basis for all sections):

### A. Verifiability
For each requirement: Can behavior be observed? Outcome asserted? Success/failure measurable? Deterministic trigger?
Classify: `DIRECTLY TESTABLE` | `CONDITIONALLY TESTABLE` | `NON-TESTABLE` | `UNDEFINED`

### B. Controllability
For each dependency: Can dependencies be replaced? Side effects injectable? State resettable? Time controlled? Failures simulated?
Classify: `HIGH CONTROL` | `MEDIUM CONTROL` | `LOW CONTROL` | `ZERO CONTROL`

### C. Isolation
For each risk: Unit isolation supported? Mock boundaries present? Ports/adapters used? Pure domain core? Deterministic execution?
Classify: `HIGH ISOLATION` | `MEDIUM ISOLATION` | `LOW ISOLATION` | `ZERO ISOLATION`

### D. Testing Strategy Geometry
Determine: test shape (Pyramid/Trophy/Honeycomb/Ice Cream Cone), expected unit/integration/E2E ratio, cost-of-failure detection timing.

### E. Risk Inversion Pass
For each module/component: How does it fail? Where will flakiness originate? Over-mocking risk? 80% defect concentration? Impossible to stress/load test?

### F. Anti-Pattern Detection
Technical: flaky test risk, hard-coded test data, over-mocking, happy-path bias, Inspector, Secret Catcher, Loudmouth.
Architectural: God object, spaghetti coupling, local hero environment.
Cultural: automation overload, one-and-done, security theatre.

## Step 4 — Write Testability Assessment Report

Create {feature-dir}/test-expert/ if not present. Write report to resolved output_filename (base or timestamped).

Read spek-fu/ai/plugins/spec-flow/skills/config.json and use config["spec-testability-draft"].maxFindings to cap Section 5 findings; default to 40 if key absent.

> **If config.json unreadable**: default maxFindings to 40 and proceed — log warning in header.

Load testability-template.md using paginated-read.

> **If template unreadable**: compose report manually using sections in order: Executive Summary, Requirement-Level Testability, Non-Functional Verifiability, Architectural Testability, Risk Findings, Testing Strategy Projection, Cost of Doing Nothing, Final Verdict. Record template read failure in header.

Populate every Risk Findings row with exact Step 3 labels (Verifiability, Controllability, Isolation). Do NOT duplicate problem statements in separate sections. Do NOT write full report body to chat — state completion only.

If markers were carried, add `## Carried Clarifications` section and include count in completion message.

**After writing**: 
> "**Testability Assessment Report** written to `{feature-dir}/test-expert/<output_filename>`."
> 
> If timestamped filename generated: "(Existing report(s) preserved alongside new version.)"

Skill complete when test-expert/<output_filename> exists and completion message shown.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load spec.md, the devils-advocate report, config.json, `branch-detection.md`, and the template. Apply `spek-fu/ai/plugins/spec-flow/knowledge/paginated-read.md` whenever a file may span multiple reads.
- **file_search**: Locate `feature-dir` and verify path existence before loading in Step 1.
- **create_file**: Write the final Testability Assessment Report in Step 4 only. Create the `test-expert/` directory as needed.
- **vscode_askQuestions**: Collect `feature-dir` via Branch Detection when it is not supplied.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
- Do NOT use any write tool on spec.md, the devils-advocate report, or any artifact outside `{feature-dir}/test-expert/`.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Rules**:
- `status` is one of: `ok`, `blocked`, `fail`
- `output_path` is the absolute path to the written report (base or timestamped), or `null` if aborted before writing
- `summary` is a single line suitable for inline reporting

**Completion message** (shown in chat after Step 4):

```
Testability Assessment Report written to `{feature-dir}/test-expert/<output_filename>`.
```
> If a timestamped filename was generated, also note that existing reports are preserved.

**Abort message** (shown when blocked):

```
BLOCKED: spec-testability-draft requires <missing artifact>. <Corrective action>.
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: `feature-dir` = `project/features/auth-service`, `spec.md` and `devils-advocate/devils-advocate-report.md` both present. No prior testability-assessment file exists.
Expected behavior: Skill loads both artifacts, constructs the 6-model testability analysis, writes the Testability Assessment Report to `project/features/auth-service/test-expert/testability-assessment.md`, and reports completion in chat. Does not modify spec.md or the devils-advocate report.
</example>

<example>
Input: `feature-dir` = `project/features/auth-service`, and a prior `testability-assessment.md` already exists in the `test-expert/` directory.
Expected behavior: Skill detects the prior report, generates a timestamped filename (`testability-assessment-2026-05-20T14-32-55.md`), writes the new analysis to the timestamped file, and notes in completion message that existing reports are preserved.
</example>

<example>
Input: `feature-dir` = `project/features/payment-flow`, spec.md present, multiple devils-advocate report versions present.
Expected behavior: Skill selects the most recently modified devils-advocate file, loads it, runs full analysis. If prior testability-assessment files exist, creates a timestamped version. No prompt for disambiguation — most-recent file rule applies automatically.
</example>

<example type="counter">
Input: `feature-dir` = `project/features/search`, `spec.md` present, no file matching `devils-advocate-report*.md` found under `project/features/search/devils-advocate/`.
Expected behavior: Skill aborts with `status: blocked`. Responds: "BLOCKED: spec-testability-draft requires a prior devils-advocate report. Run spec-devils-advocate first to produce the upstream findings."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
- Constraint 1 — write only within `{feature-dir}/test-expert/`; never modify upstream artifacts.
- Constraint 2 — require a confirmed devils-advocate report before analysis.
- Constraint 3 — do not soften or omit findings.
- Constraint 4 — fail explicitly if required inputs cannot be found.
- Constraint 5 — do not confuse coverage metrics with testability.
</reminders>
