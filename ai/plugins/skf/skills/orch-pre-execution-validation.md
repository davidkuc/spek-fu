---
id: "orch-pre-execution-validation"
recommended-tier: "fast-agent"
version: 1.0
description: "Validates wave conflicts and dependency graph in the orchestration plan before execution begins. Returns a structured PASS/FAIL report."
anti-scope: "It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions."
tags:
  - "utility"
  - "plan"
  - "validation"
  - "gate"
inputs:
  - "Structured orchestration plan object (required)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "One-line summary of validation result"
dispatch-variant: "compact"
---


# Skill: orch-pre-execution-validation

<!-- SECTION 1: Identity (primacy position) -->
Runs gated pre-execution checks on the orchestration plan before the orchestrator begins executing tasks. Detects wave conflicts and parses the dependency graph. Returns a structured PASS/FAIL report; takes no corrective action.

**Scope boundary**: This skill reads the inline plan object only. It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions. Corrective action is the caller's responsibility.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Keep this skill strictly read-and-report. WHY: validation must not mutate; corrective action belongs to the caller.
2. Run BOTH checks (PE-02, PE-03) even if an earlier check fails. WHY: partial validation produces false confidence and allows silent failures through the gate.
3. Return findings inline instead of asking follow-up questions. WHY: interaction is the orchestrator's responsibility, not this skill's.
4. If `plan` is absent or malformed, record FAIL immediately and do not proceed to any checks. WHY: validating an unknown or missing plan produces undefined output.
5. If a dependency summary cannot be derived confidently from the plan structure, record PE-03 as SKIPPED — do not fail. WHY: graceful degradation is correct when the plan format does not support a reliable dependency summary.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your report complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — run checks, produce a report, nothing more.
- Record every check result (PASS, FAIL, or SKIPPED) regardless of outcome.
- Carry all raw script output into the report verbatim for any FAIL check.
- Do not infer the plan from conversation context — require it explicitly from the caller.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Confirm `plan` is present in the inputs before selecting any checks.
- Keep all validation steps read-only.
- **State detection**: This skill produces an inline report only (no output file is written). Each invocation re-runs all validation checks fresh; there is no prior-output file to detect. Proceed with normal execution.

## Step 1 — Validate inputs

1. Confirm `plan` is present and non-empty. If absent or empty, record FAIL: `plan is required` and halt — skip Steps 2–4.
2. Confirm the plan exposes wave sections and step entries. If the structure is malformed, record FAIL: `plan malformed` and halt.

## Step 2 — Run PE-02: Wave Conflict Detection

Read the plan object and compare steps within each wave.

- **PASS**: no two parallel steps modify the same target file and no step depends on a prerequisite satisfied only by another step in the same wave.
- **FAIL**: one or more parallel steps collide on target files or have mutually incompatible preconditions. Capture the conflicting wave, step IDs, and target files in the finding detail.

Record result before proceeding to Step 3.

## Step 3 — Run PE-03: Dependency Graph Summary

1. Review the plan's wave sections and step numbering.
2. If the plan clearly identifies which steps depend on prior wave outputs versus caller-provided context, summarize the parallel candidates and sequential dependencies directly in the report.
3. **PASS**: the dependency structure is explicit enough to identify which steps can run in parallel and which are sequential.
4. **SKIPPED**: the plan format does not expose dependencies clearly enough to derive a reliable summary.

Record result before proceeding to Step 4.

## Step 4 — Produce and Return Report

Compile all check results and return the structured Pre-Execution Validation Report (see Section 6 Output Format).

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- No file-reading, search, or execution tools are permitted for the core validation logic because the plan is provided inline.
- **edit / create_file / replace_string_in_file**: Prohibited because this skill never modifies or creates files.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-pre-execution-validation` |
| wave | `N` |
| step | `N.M` |
| summary | one-line summary of validation result |

```
## Pre-Execution Validation Report
Plan: inline structured plan

PE-02 Conflict detection: PASS | FAIL
PE-03 Dependency summary: PASS | FAIL | SKIPPED

Overall: PASS | FAIL

{Script output verbatim for any FAIL checks:}

**{script name}** (exit {code}):
```
{full stdout/stderr verbatim}
```

### Dependency Graph Summary (PE-03, PASS only)

Wave {N}:
  Parallel candidates: {step list or "none identified"}
  Blocking steps: {step list or "none identified"}
```

Rules:
- Overall is PASS only when all executed checks are PASS (SKIPPED does not count as FAIL).
- Script output blocks are omitted entirely when both PE-02 and PE-03 pass.
- Dependency Graph Summary block is omitted when PE-03 is FAIL or SKIPPED.
- FAIL at Step 1 (missing plan) produces the minimal report: `Plan: not provided — Overall: FAIL — Reason: {message}`.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: inline plan; no conflicts detected; dependency summary derivable.
Expected output: PE-02 PASS, PE-03 PASS. Overall: PASS. Structured report returned inline. No files modified.
</example>

<example>
Input: inline plan; conflict detection passes but dependency summary reveals issues.
Expected output: PE-02 PASS, PE-03 FAIL. Overall: FAIL. Full findings in report with dependency details listed.
</example>

<example type="counter">
Input: plan not provided.
Expected behavior: Returns minimal FAIL report: "Plan: not provided — Overall: FAIL — Reason: plan is required". No scripts are run. No files are modified.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
