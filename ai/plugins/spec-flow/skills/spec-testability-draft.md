---
id: "spec-testability-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Analyzes spec.md and a prior devils-advocate report from a test engineering perspective, producing a Testability Assessment Report at FEATURE_DIR/test-expert/testability-assessment.md. USE FOR: evaluating feature spec testability, grading requirements as testable/non-testable, identifying structural testing risks, and projecting a testing strategy shape. DO NOT USE FOR: generating test code or test plans; use implementation skills for test execution."
anti-scope: "Does not generate test code, test plans, or implementation artifacts. Does not modify spec.md or any upstream artifact. Read-only analysis only."
tags:
  - "quality"
  - "specification"
  - "analysis"
  - "reporting"
inputs:
  - "FEATURE_DIR: path to the feature directory containing spec.md (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "FEATURE_DIR/test-expert/testability-assessment.md — structured Testability Assessment Report"
  - "Execution status: ok, blocked, or fail"
dispatch-variant: "full"
---

# Skill: spec-testability-draft

<!-- SECTION 1: Identity (primacy position) -->
Evaluates a feature spec.md from a test engineering perspective, incorporating upstream risk findings from the **Devils Advocate Report**. The skill constructs a multi-dimensional testability model across verifiability, controllability, isolation, strategy shape, risk inversion, and anti-pattern detection, then writes a structured **Testability Assessment Report** to `FEATURE_DIR/test-expert/testability-assessment.md`.

**Scope boundary**: This skill reads and analyzes only — it does NOT generate test code, modify spec.md, or alter any upstream artifact. For adversarial spec analysis that produces the upstream report this skill depends on, use **spec-devils-advocate**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER modify spec.md, the devils-advocate report, or any upstream artifact — WHY: this is a read-only analysis skill; modifying inputs destroys the audit trail and corrupts the upstream phase.
2. NEVER proceed without a confirmed devils-advocate report — WHY: this skill is downstream of spec-devils-advocate; analyzing a spec without the upstream risk findings produces incomplete and misleading testability grades.
3. NEVER soften, omit, or dilute findings — WHY: an accurate risk picture, however uncomfortable, is the product; sanitizing it defeats the purpose of the analysis.
4. ALWAYS abort with an explicit error if FEATURE_DIR, spec.md, or the devils-advocate report cannot be found — WHY: guessing paths or inventing absent content produces a fabricated report with no analytical value.
5. NEVER equate test coverage percentage with correctness or testability — WHY: a metric that measures the wrong thing misleads design decisions.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes, no test code.
- If FEATURE_DIR is not supplied, apply the **Branch Detection** procedure — do not guess paths.
- This skill is read-only. Any impulse to modify spec.md or the devils-advocate report must be refused.
- Apply inversion thinking, Pareto risk targeting, and architectural layering principles throughout analysis.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `FEATURE_DIR` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve FEATURE_DIR: if not provided as input, apply the **Branch Detection** procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md` (core procedure). If the user provides a path, use it. If the user declines, stop and report `blocked`.
- Confirm run state: if `FEATURE_DIR/test-expert/testability-assessment.md` already exists, overwrite it — this is `output-type: report`.
- Declare fail-fast: abort if FEATURE_DIR cannot be resolved; abort if spec.md is missing; abort if no devils-advocate report can be located.

## Done conditions

- **Success**: `FEATURE_DIR/test-expert/testability-assessment.md` has been written and confirmed with a chat summary line.
- **Blocked**: FEATURE_DIR, spec.md, or the **Devils Advocate Report** cannot be found — report which is missing and stop.
- **Fail**: An unrecoverable error prevents report creation — state the error explicitly.

## Step 1 — Resolve paths and verify inputs

Derive absolute paths:
- `SPEC` = `FEATURE_DIR/spec.md`
- `DEVILS_ADVOCATE_DIR` = `FEATURE_DIR/devils-advocate/`
- `DEVILS_ADVOCATE_REPORT`: select in this order:
  1. `FEATURE_DIR/devils-advocate/devils-advocate-report.md` (if exists)
  2. Most recently modified file matching `devils-advocate-report-*.md` under `FEATURE_DIR/devils-advocate/`

> **If FEATURE_DIR cannot be resolved** (not supplied, not on a feature branch, and no path provided by the user): abort with `status: fail`. State the missing path explicitly.

> **If DEVILS_ADVOCATE_REPORT cannot be found**: abort with `status: blocked`. State: "spec-testability-draft requires a prior devils-advocate report. Run spec-devils-advocate first."

## Step 2 — Load artifacts

From **spec.md**, load:
- Functional Requirements
- Non-functional Requirements
- User Stories
- Edge Cases

From **Devils Advocate Report**, load:
- Executive Warning
- Critical Failure Points
- Requirement Ambiguities
- Worst-Case Scenario Analysis

Do NOT load or analyze plan.md or tasks.md.

> **If spec.md sections are missing or unlabeled**: continue analysis on available content; mark missing sections as UNDEFINED in the Verifiability Map.

## Step 3 — Construct Testability Model

Build the following six analytical models internally. These form the evidentiary basis for all report sections.

### A. Verifiability Map

For each requirement derived from spec.md, assess:
- Can behavior be observed?
- Can outcome be asserted?
- Is success measurable? Is failure measurable?
- Is there a deterministic trigger?

Classify each requirement as: `DIRECTLY TESTABLE` | `CONDITIONALLY TESTABLE` | `NON-TESTABLE` | `UNDEFINED`

### B. Controllability Map

For each component or dependency explicitly mentioned in spec.md:
- Can dependencies be replaced?
- Are side effects injectable?
- Is state resettable?
- Can time be controlled? Can failures be simulated?

Classify each element as: `HIGH CONTROL` | `MEDIUM CONTROL` | `LOW CONTROL` | `ZERO CONTROL`

### C. Isolation Potential

Based only on what spec.md explicitly states or implies:
- Is unit isolation supported?
- Are mock boundaries present?
- Does the design use ports and adapters?
- Is there a pure domain core?
- Is execution deterministic?

Classify architecture as one of: `Hexagonal-compatible` | `Clean-layered` | `Functional-core ready` | `Tightly coupled` | `Spaghetti risk`

### D. Testing Strategy Geometry

Determine:
- Natural test shape: Pyramid / Trophy / Honeycomb / Ice Cream Cone risk
- Expected unit / integration / E2E ratio
- Cost-of-failure detection timing

### E. Risk Inversion Pass

Ask for each module or component:
- How does this fail?
- Where will flakiness originate?
- Where will over-mocking occur?
- What modules will accumulate 80% of defects?
- What is impossible to stress test, load test, or simulate?

### F. Anti-Pattern Detection

Detect technical anti-patterns:
- Flaky test risk, hard-coded test data, over-mocking, happy-path bias, Inspector pattern, Secret Catcher, Loudmouth

Detect architectural anti-patterns:
- God object, spaghetti coupling, local hero environment

Detect cultural signals (if detectable):
- Automation overload, one-and-done mindset, security theatre

## Step 4 — Write Testability Assessment Report

Create directory `FEATURE_DIR/test-expert/` if not present.

Write the report to `FEATURE_DIR/test-expert/testability-assessment.md`.

Read `ai/plugins/spec-flow/templates/testability-template.md` via `read_file` and use it as the report scaffold. The report must follow that template exactly. Do NOT write the full report body to chat — only state completion.

---

After writing the report, state in chat:
> "Testability Assessment Report written to `<FEATURE_DIR>/test-expert/testability-assessment.md`."

The skill is complete when `FEATURE_DIR/test-expert/testability-assessment.md` exists on disk and the completion message has been shown.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load spec.md and the devils-advocate report in Step 2. Use multi-pass reads for large files — advance startLine until the response is shorter than the page size.
- **file_search**: Locate FEATURE_DIR and verify path existence before loading in Step 1.
- **create_file**: Write the final Testability Assessment Report in Step 4 only. Create the `test-expert/` directory as needed.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
- Do NOT use any write tool on spec.md, the devils-advocate report, or any artifact outside `FEATURE_DIR/test-expert/`.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

```json
{
  "status": "ok | blocked | fail",
  "skill_id": "spec-testability-draft",
  "wave": "N",
  "step": "N.M",
  "output_path": "FEATURE_DIR/test-expert/testability-assessment.md",
  "summary": "one-line summary of what was done"
}
```

**Rules**:
- `status` is one of: `ok`, `blocked`, `fail`
- `output_path` is the absolute path to the written report, or `null` if aborted before writing
- `summary` is a single line suitable for inline reporting

**Completion message** (shown in chat after Step 4):

```
Testability Assessment Report written to `<FEATURE_DIR>/test-expert/testability-assessment.md`.
```

**Abort message** (shown when blocked):

```
BLOCKED: spec-testability-draft requires <missing artifact>. <Corrective action>.
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: FEATURE_DIR = `project/features/auth-service`, `spec.md` and `devils-advocate/devils-advocate-report.md` both present.
Expected behavior: Skill loads both artifacts, constructs the 6-model testability analysis, writes the Testability Assessment Report to `project/features/auth-service/test-expert/testability-assessment.md`, and reports completion in chat. Does not modify spec.md or the devils-advocate report.
</example>

<example>
Input: FEATURE_DIR = `project/features/payment-flow`, spec.md present, multiple devils-advocate report versions present (`devils-advocate-report-v1.md`, `devils-advocate-report-v2.md`).
Expected behavior: Skill selects the most recently modified file (`devils-advocate-report-v2.md`), loads it, runs full analysis, and writes the report. No prompt for disambiguation — most-recent file rule applies automatically.
</example>

<example type="counter">
Input: FEATURE_DIR = `project/features/search`, `spec.md` present, no file matching `devils-advocate-report*.md` found under `project/features/search/devils-advocate/`.
Expected behavior: Skill aborts with `status: blocked`. Responds: "BLOCKED: spec-testability-draft requires a prior devils-advocate report. Run spec-devils-advocate first to produce the upstream findings."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never modify spec.md, the devils-advocate report, or any upstream artifact** — this skill is strictly read-only analysis. WHY: modifying inputs destroys the audit trail and corrupts the upstream phase.
- **Never proceed without a confirmed devils-advocate report** — this skill is downstream of spec-devils-advocate; proceeding without it produces incomplete and misleading testability grades.
- **Never soften or omit findings** — an accurate risk picture is the product. WHY: sanitizing it defeats the purpose.
- **Always verify** output against `<constraints>` before reporting completion.

</reminders>
