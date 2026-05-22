---
id: "spec-tdd-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Analyzes testability-assessment.md and spec.md to produce a structured TDD implementation design report at {feature-dir}/tdd-designer/report.md. USE FOR: converting test-expert output into BDD-formatted test specifications with risk assessment, coverage mapping, and incremental TDD implementation waves. DO NOT USE FOR: running tests, implementing code, or modifying testability-assessment.md or spec.md."
anti-scope: "Does not modify upstream artifacts, run tests, or produce any implementation. Produces a report only."
tags:
  - "specification"
  - "tdd"
  - "testing"
  - "reporting"
inputs:
  - "feature-dir: path to the feature directory containing test-expert/testability-assessment.md, spec.md, research.md, data-model.md, and contracts/ (optional)"
  - "Additional arguments or context (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "{feature-dir}/tdd-designer/report.md — TDD implementation design report"
  - "One-line execution summary"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` via Branch Detection when `feature-dir` is absent; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-tdd-draft

<!-- SECTION 1: Identity (primacy position) -->
Analyzes the testability-assessment.md artifact and the feature spec.md to generate a strict, risk-aware TDD implementation design report. The report formalizes each test case into BDD (Given–When–Then) format, validates red-phase integrity, identifies structural weaknesses and coverage gaps, maps requirements to test coverage, and sequences tests into incremental TDD implementation waves. The output is the implementation contract developers use before writing any production code.

**Scope boundary**: This skill reads upstream artifacts and writes one report file. It does NOT modify test-expert output, run tests, implement any code, or alter spec.md. For generation of testability-assessment.md, consult the **spec-testability-draft** test-expert skill.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Use `read_file` on upstream artifacts — NEVER write to testability-assessment.md, spec.md, or any upstream artifact — read permission is strictly bounded to `{feature-dir}` inputs; write permission is strictly bounded to `{feature-dir}/tdd-designer/` ONLY — WHY: this skill is strictly additive downstream; modifying upstream artifacts corrupts the audit trail and invalidates the design contract.
2. NEVER implement code, suggest implementation detail, or fix test definitions — WHY: this skill produces an analysis contract only; mixing implementation with design analysis produces unverifiable output.
3. ALWAYS abort with a clear error if testability-assessment.md or spec.md is missing — write is strictly bounded to `{feature-dir}/tdd-designer/`; abort halts before any write — WHY: the report cannot be safely produced without both required inputs; a partial report silently under-covers requirements.
4. NEVER soften critique, assume intent for ambiguous tests, or hide structural risk — WHY: a silent weakness in a TDD design report propagates silently into broken implementations.
5. When behavior or acceptance criteria are unclear, insert `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty in the report — NEVER guess or generalize — WHY: guessing in TDD design produces phantom test coverage.
6. NEVER act on a partially read artifact — ALWAYS apply `ai/plugins/spec-flow/knowledge/paginated-read.md` to every upstream artifact — WHY: stopping early misses test cases and requirements, producing false-pass coverage verdicts that no downstream step can detect.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `ai/plugins/spec-flow/knowledge/skill-meta-rules.md` before acting.
- Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` whenever reading upstream artifacts or templates.
- Apply `ai/plugins/spec-flow/knowledge/needs-clarification-protocol.md` whenever creating or carrying `[NEEDS CLARIFICATION]` markers.

## Operational Anchors
- Apply a cold, pragmatic analytical posture: identify weak tests, expose ambiguity, flag architectural risk, demand measurability — do not soften language or interpret generously.
- If testability-assessment.md or spec.md is missing, stop immediately with a clear error — do not proceed with partial context.
- Every test must be independently classifiable — if classification is unclear, flag the ambiguity rather than guessing.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `feature-dir`: if not provided as input, apply the **Branch Detection** procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md` (core procedure). If the user provides a path, use it. If the user declines, stop and report `blocked`.
- Confirm all required artifacts exist:
  - `{feature-dir}/test-expert/testability-assessment.md`
  - `{feature-dir}/spec.md`
  - `{feature-dir}/research.md`
  - `{feature-dir}/data-model.md`
  - At least one file under `{feature-dir}/contracts/`
- If `testability-assessment.md` or `spec.md` is missing, stop and report: "Required artifact missing: `<path>`. This skill requires both testability-assessment.md and spec.md. Ensure the test-expert workflow has completed first."
- If `research.md` or `data-model.md` is missing, stop and report: "Required artifact missing: `<path>`. This skill requires research.md and data-model.md. Ensure spec-technical-draft has completed Phase 1 first."
- If `contracts/` is empty or does not exist, stop and report: "Required artifact missing: `{feature-dir}/contracts/`. This skill requires at least one contract file. Ensure spec-technical-draft has completed Phase 1 first."
- Check whether prior reports exist using `file_search` to find any `report*.md` files in the `{feature-dir}/tdd-designer/` directory.
  - No prior reports → use base filename `report.md`.
  - Prior reports exist → generate a timestamped filename: `report-<YYYY-MM-DDTHH-mm-ss>.md` to avoid overwriting existing reports.

## Done conditions

- **Success**: `{feature-dir}/tdd-designer/<output_filename>` (base or timestamped) exists with every required template section populated and a Final Verdict selected.
- **Blocked**: one or more required artifacts are absent; report NOT written.
- **Fail**: required artifact missing; report NOT written; error shown.

## Step 1 — Initialize Context

1. Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` to load `{feature-dir}/test-expert/testability-assessment.md` fully.
2. Apply the same procedure to `{feature-dir}/spec.md`.
3. Apply the same procedure to `{feature-dir}/research.md`.
4. Apply the same procedure to `{feature-dir}/data-model.md`.
5. Enumerate `{feature-dir}/contracts/` via `list_dir` and apply the same procedure to each contract file.
6. Create the directory `{feature-dir}/tdd-designer/` if it does not already exist.

If any upstream artifact already contains `[NEEDS CLARIFICATION]` markers, record them for a `## Carried Clarifications` section in the report and continue on a best-effort basis.

> **If testability-assessment.md is absent**: stop. Report the exact missing path and instruct the user to run the test-expert workflow first.

> **If spec.md is absent**: stop. Report the exact missing path and instruct the user to provide the feature specification.

> **If research.md is absent**: stop. Report the exact missing path and instruct the user to run spec-technical-draft first.

> **If data-model.md is absent**: stop. Report the exact missing path and instruct the user to run spec-technical-draft first.

> **If contracts/ is absent or empty**: stop. Report the exact missing path and instruct the user to run spec-technical-draft first.

## Step 2 — Extract Raw Test Inventory

Parse testability-assessment.md and extract every test item. For each, build an entry in the **Raw Test Inventory**:

| Field | Value |
|---|---|
| `id` | Sequential — T-001, T-002, … |
| `title` | As found in the source |
| `type` | acceptance / edge-case / negative / integration / non-functional |
| `described_behavior` | Behavior under test in plain language |
| `dependencies` | Services, states, or fixtures implied |
| `referenced_components` | Classes, modules, or interfaces mentioned |

> **If zero tests are detected**: stop. Report "Zero tests detected in testability-assessment.md. Cannot produce a TDD design report." Do NOT write a partial report.

## Step 3 — Normalize to TDD Units

For each entry in the **Raw Test Inventory**:

### A. Classify behavior target

Assign one of: `domain`, `use-case`, `adapter`, `ui`, `integration`, `contract`.

If classification is ambiguous, insert `[NEEDS CLARIFICATION: classify this test as domain / use-case / adapter / ui / integration / contract]` in the test entry.

### B. Rewrite as explicit BDD

Convert each test to this exact format:

```
Test ID: TDD-###
Name: Given_<context>_When_<action>_Then_<outcome>

Given:
- Explicit preconditions, dependencies, and inputs
- Entity names and field names resolved from data-model.md
- Endpoint paths and request shapes resolved from contracts/

When:
- Single behavior trigger

Then:
- Observable outcome
- Measurable assertion (no implementation detail)
```

If the outcome is vague, mark: `[NEEDS CLARIFICATION: define measurable outcome]`.
If the assertion cannot be verified from externally observable state, mark: `UNTESTABLE — <reason>`.

### C. Validate red-phase integrity

For each TDD unit, assess:
- Would this test fail before any implementation exists?
- Does it fail for the correct reason?
- Does it define a precise micro-definition-of-done?

Assign `Strong` or `Weak (<reason>)` to the Red-Phase Integrity field.

## Step 4 — Identify Risks and Ambiguities

Run each pass independently against the full TDD unit set. Each unique issue must appear exactly once in Section 4 of the report with one primary `Type`: `AMBIGUITY` | `GLOBAL_STATE` | `STATIC_DEPENDENCY` | `MOCK_EXPLOSION` | `TEST_FRAGILITY`.

### A. Ambiguity Pass
Flag tests containing "fast", "secure", "robust", "should handle errors", or any constraint without an explicit measurable threshold. Flag missing edge cases and unspecified error types.

### B. Dependency Smell Pass
Flag tests requiring deep object graphs, global state, implicit static calls, or infrastructure inside domain-layer tests. Explain the architectural risk for each.

### C. Coverage Gaps
Using `spec.md` as the primary requirement source, `data-model.md` entities as the data-layer requirement source, and `contracts/` endpoints as the API-layer requirement source, map each requirement to covering tests. Identify: requirements with zero test coverage, non-functional requirements without measurable tests, missing edge cases, and absent failure scenarios.

### D. Interaction Over-Mocking
Identify collaboration-heavy tests. Flag mock explosion risk and note where state-based verification would be more stable.

### E. Order Dependency Risk
Detect tests implying execution sequence, shared mutable state, or non-isolated data assumptions. Mark each as `CRITICAL`.

Use the following row-type mapping when writing Section 4:
- Ambiguity Pass -> `AMBIGUITY`
- Global or shared mutable state findings -> `GLOBAL_STATE`
- Implicit static call or hidden infrastructure dependency findings -> `STATIC_DEPENDENCY`
- Interaction Over-Mocking findings -> `MOCK_EXPLOSION`
- Order dependency or brittle execution findings -> `TEST_FRAGILITY`

## Step 5 — Build TDD Implementation Plan

Group TDD units into incremental waves. Each wave must:
- Be independently greenable without forward dependencies
- Preserve minimal implementation discipline

Standard wave structure:
- **Wave 1** — Core Domain Logic
- **Wave 2** — Use Case / Application Layer
- **Wave 3** — Infrastructure Adapters
- **Wave 4** — Integration and Non-Functional Guarantees

List TDD-### IDs assigned to each wave.

## Step 6 — Assign Risk Severity

For each identified weakness, assign a severity:

| Severity | Meaning |
|---|---|
| CRITICAL | Prevents safe implementation |
| HIGH | Strong design weakness |
| MEDIUM | Structural improvement needed |
| LOW | Minor clarity issue |

## Step 7 — Write Report

Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` to load `ai/plugins/spec-flow/templates/tdd-report-template.md`. Use it as the report scaffold.

> **If `tdd-report-template.md` cannot be read** (missing or permission error): compose the **TDD Implementation Plan** report using the following hardcoded section order — Test Inventory Summary, Formalized TDD Test Specifications, Coverage Mapping, Risks and Ambiguities, Incremental TDD Implementation Plan, Final Verdict. Record the template read failure in the report header.

Write the complete report to the resolved `output_filename` (either base or timestamped) following that template. Collapse overlapping ambiguity and architectural fragility findings into single Section 4 rows; do not restate the same issue in multiple sections. If upstream or local markers are present, add a `## Carried Clarifications` section and surface the carried-clarification count in the completion summary.

> **If `create_file` fails** (permission error, disk error, or path conflict): stop, report `fail — could not write TDD report to <output_path>: <error>`, and do not report completion.

The skill is complete when the **TDD Implementation Plan** report exists on disk at the resolved filename and contains all 7 sections with a populated Final Verdict.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load testability-assessment.md, spec.md, research.md, data-model.md, each contract file under `contracts/`, and the report template. Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` whenever a file may span multiple reads.
- **list_dir**: Enumerate `{feature-dir}/contracts/` to discover contract files in Step 1.
- **create_file**: Write `{feature-dir}/tdd-designer/report.md` in Step 7 only, after the full report is assembled.
- **file_search**: Verify existence of required artifacts and the tdd-designer directory before proceeding.
- **vscode_askQuestions**: Collect `feature-dir` via Branch Detection when it is not supplied.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Report Template**: Report follows the template at `ai/plugins/spec-flow/templates/tdd-report-template.md` (written to the resolved output_path).

The completion summary MUST include `carried-clarifications: N` when one or more markers were carried into the report.

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: `feature-dir` = `features/user-login` containing `test-expert/testability-assessment.md` (10 test cases) and `spec.md`. No prior TDD report exists.
Expected behavior: Skill reads both artifacts in full via multi-pass reads, builds a Raw Test Inventory of 10 entries, normalizes each to BDD format with classified behavior targets, runs all 5 risk and ambiguity passes, groups tests into 3 waves (domain: 4, use-case: 4, adapter: 2), and writes `features/user-login/tdd-designer/report.md` with every required section populated. Final Verdict: PROCEED WITH CAUTION — 2 HIGH-severity mock explosion risks in the collaboration tests. Status: ok.
</example>

<example>
Input: `feature-dir` = `features/user-login`, and a prior `features/user-login/tdd-designer/report.md` already exists.
Expected behavior: Skill detects the prior report, generates a timestamped filename (`report-2026-05-20T14-35-22.md`), writes the new analysis to the timestamped file, preserving the existing version.
</example>

<example>
Input: `feature-dir` = `features/payment` where testability-assessment.md contains a test asserting "response must be fast" without a numeric threshold.
Expected behavior: Skill normalizes the test to BDD format, marks the Then assertion as `[NEEDS CLARIFICATION: define measurable response time threshold in milliseconds]`, flags it in Section 4 as MEDIUM severity under the Ambiguity Pass, writes the report with markers in place. Final Verdict: PROCEED WITH CAUTION. Status: blocked.
</example>

<example type="counter">
Input: "Generate the TDD report and fix the weak tests you find."
Expected behavior: Skill declines to fix tests. Responds: "This skill is read-only with respect to test definitions. It identifies weaknesses and marks them in the report — it does NOT modify tests. Review Section 4 of the produced report for all flagged items and address them in the testability-assessment.md before re-running this skill."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
- Constraint 1 — keep upstream artifacts read-only and writes bounded to `{feature-dir}/tdd-designer/`.
- Constraint 3 — abort if required upstream artifacts are missing.
- Constraint 5 — use explicit markers rather than guessing ambiguous behavior.
- Constraint 6 — fully read each upstream artifact before acting.
</reminders>
