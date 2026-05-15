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
  - "Relative path to the orchestration plan file (required)"
  - "Override path for the working-state directory (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "One-line summary of validation result"
dispatch-variant: "compact"
---


# Skill: orch-pre-execution-validation

<!-- SECTION 1: Identity (primacy position) -->
Runs gated pre-execution checks on the orchestration plan before the orchestrator begins executing tasks. Detects wave conflicts and parses the dependency graph. Returns a structured PASS/FAIL report; takes no corrective action.

**Scope boundary**: This skill reads the plan file and runs Python validation scripts only. It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions. Corrective action is the caller's responsibility.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Keep this skill strictly read-and-report. WHY: validation must not mutate; corrective action belongs to the caller.
2. Run BOTH checks (PE-02, PE-03) even if an earlier check fails. WHY: partial validation produces false confidence and allows silent failures through the gate.
3. Return findings inline instead of asking follow-up questions. WHY: interaction is the orchestrator's responsibility, not this skill's.
4. If `plan-file` is absent or the file is unreadable, record FAIL immediately and do not proceed to any script. WHY: running scripts against an unknown or missing plan produces undefined output.
5. When a Python script exits non-zero, capture its full stdout/stderr and carry it verbatim into the report. WHY: full output is required for the caller to diagnose and fix.
6. If a dependency summary cannot be derived confidently from the plan structure, record PE-03 as SKIPPED — do not fail. WHY: graceful degradation is correct when the plan format does not support a reliable dependency summary.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your report complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — run checks, produce a report, nothing more.
- Record every check result (PASS, FAIL, or SKIPPED) regardless of outcome.
- Carry all raw script output into the report verbatim for any FAIL check.
- Do not infer the plan path from context — require it explicitly from the caller.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Confirm `plan-file` is present in the inputs before selecting any checks.
- Keep all validation steps read-only.
- **State detection**: This skill produces an inline report only (no output file is written). Each invocation re-runs all validation checks fresh; there is no prior-output file to detect. Proceed with normal execution.

## Step 1 — Validate inputs

1. Confirm `plan-file` is present and non-empty. If absent or empty, record FAIL: `plan-file is required` and halt — skip Steps 2–5.
2. Attempt to read the first 5 lines of `plan-file` using `read_file`. If the file is unreadable or not found, record FAIL: `plan-file not found or unreadable: {plan-file}` and halt.
3. Resolve `orchestration-temp-path` (default: `.orchestration-temp/`).

## Step 2 — Run PE-02: Wave Conflict Detection

Read the plan file and compare steps within each wave.

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
- **read_file**: Use in Step 1 to verify `plan-file` is readable. Read in one call per file; prefer large reads over fragmented reads.
- **file_search**: Use in Step 4 only if you need to verify referenced plan targets exist on disk.
- **grep_search**: Permitted as a fallback in Step 1 to locate plan headings when `read_file` output is ambiguous.
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
Plan file: {plan-file}

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
- FAIL at Step 1 (missing plan-file) produces the minimal report: `Plan file: {value or "not provided"} — Overall: FAIL — Reason: {message}`.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: plan-file=".orchestration-temp/orchestration-plan.md"; detect-wave-conflicts exits 0; get-plan-dependency-summary exits 0.
Expected output: PE-02 PASS, PE-03 PASS. Overall: PASS. Structured report returned inline. No files modified.
</example>

<example>
Input: plan-file=".orchestration-temp/orchestration-plan.md"; detect-wave-conflicts exits 0 but dependency summary indicates issues; get-plan-dependency-summary reveals problems.
Expected output: PE-02 PASS, PE-03 FAIL. Overall: FAIL. Full findings in report with dependency details listed.
</example>

<example type="counter">
Input: plan-file not provided.
Expected behavior: Returns minimal FAIL report: "Plan file: not provided — Overall: FAIL — Reason: plan-file is required". No scripts are run. No files are modified.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
