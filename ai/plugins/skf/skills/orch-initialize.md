---
id: "orch-initialize"
recommended-tier: "fast-agent"
version: 1.0
description: "Reads skf-config.json, resolves the runtime environment, detects spec context, and returns a compact initialization result inline. USE FOR: framework initialization at the start of every orchestration run; centralizing config loading and environment resolution away from inline orchestrator logic. DO NOT USE FOR: per-wave state tracking, skill index navigation, or orchestration planning."
anti-scope: "Does NOT execute orchestration waves, dispatch sub-agents, or manage any workspace file outside skf-config.json and spec-context detection inputs."
tags:
  - "utility"
  - "initialization"
  - "environment"
  - "orchestration"
inputs:
  - "workspace-root: absolute path to the workspace root (required)"
  - "env: runtime environment override — if provided, skips config-based env resolution and uses this value directly; must be devcontainer or host (optional)"
outputs:
  - "Status: ok | hard-fail"
  - "hard-fail-reason: descriptive string when status is hard-fail, else none"
  - "spec-context: true | false | unknown — whether an active spec-flow branch and spec.md were detected"
  - "spec-feature-dir: resolved feature dir path or none"
dispatch-variant: "compact"
---

# Skill: orch-initialize

<!-- SECTION 1: Identity (primacy position) -->
Centralizes framework initialization into a single delegatable skill: reads `skf-config.json` to extract all configuration values, resolves the runtime environment (including devcontainer presence check), detects spec context, and returns a compact structured result inline. Designed to be dispatched as the first step in every orchestration run so that orchestrators no longer carry inline initialization logic. Applies PT001 (Divide and Conquer) by treating each initialization concern as a discrete step, and PT019 (Specialist Dispatch) by serving as a focused specialist whose sole responsibility is environment and context readiness.

**Scope boundary**: This skill reads `skf-config.json`, checks for `.devcontainer/devcontainer.json`, and runs spec-context detection. It does NOT execute orchestration waves, dispatch sub-agents, or manage temp-state folders. For wave planning and decomposition, use **orch-wave-decompose**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER proceed past Step 2 (environment resolution) when the devcontainer check fails — set `status: hard-fail` and jump directly to Step 5 to write init-result.md. WHY: continuing initialization on an unresolved environment causes cascading downstream failures that are harder to diagnose and reverse.
2. ALWAYS return a structured inline result regardless of status — even a `hard-fail` must produce a machine-readable response. WHY: callers depend on a deterministic result to route error handling; a missing output leaves them in an undefined state.
4. NEVER accept an unrecognized value for the `env` input — reject anything other than `devcontainer` or `host` with `status: hard-fail` and reason "Unrecognized env value: {value}". WHY: unrecognized environment values produce undefined resolution behavior in all downstream steps.
5. NEVER modify `skf-config.json` or write any workspace file. Use `run_in_terminal` ONLY for running `detect-spec-context.py` (Step 3) — NEVER for any other path or purpose. WHY: this skill is read-and-report only; writing state exceeds its designated scope.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra config extraction, no unrequested folder cleanup beyond what is specified.
- If `skf-config.json` cannot be read, report `hard-fail` immediately with reason "skf-config.json not found or unreadable" — do not guess config values.
- Apply PT001 (Divide and Conquer) by executing each initialization concern — config extraction, environment resolution, spec detection, output assembly — as a discrete step in strict sequence.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Inputs

| Field | Type | Required | Enum | Description |
|---|---|---|---|---|
| workspace-root | string | yes | — | Absolute path to the workspace root |
| env | string | no | devcontainer \| host | Runtime environment override; if provided, skips config-based env resolution |

**Source**: Provided by the dispatching orchestrator at invocation.

## Preflight

- Confirm `workspace-root` is provided. If absent, set `status: hard-fail`, `hard-fail-reason: "workspace-root input is required"`, skip to Step 4.
- If `env` is provided, validate it is one of `devcontainer` or `host`. If invalid, set `status: hard-fail`, `hard-fail-reason: "Unrecognized env value: {value}"`, skip to Step 4.

## Done conditions

- **ok** is done when the inline result contains `status: ok` and all config values are populated.
- **hard-fail** is done when the inline result contains `status: hard-fail` and `hard-fail-reason` is populated.
- The skill is complete when the structured result has been returned inline.

---

## Step 1 — Read skf-config.json

1. Call `read_file` on `{workspace-root}/skf-config.json` starting at line 1 with a range of at least 100 lines. If the response fills the page, advance `startLine` and read again until the full file is confirmed (response shorter than the page size).
2. Extract the following values into the **config snapshot**:
   - `environment` (top-level field)
   - `maxClarificationLoops` (top-level field)
   - `skf-general-orchestrator.maxPlanRevisions`
   - `skf-general-orchestrator.maxWaveRetries`
   - `skf-general-orchestrator.maxSubagentRetries`
   - `skf-general-orchestrator.complexityThresholds.simpleMaxFiles`
   - `skf-general-orchestrator.complexityThresholds.standardMaxFiles`
   - `skf-general-orchestrator.complexityThresholds.complexMinFiles`
   - `skf-general-orchestrator.approvalTimeoutBehavior`

> **If `skf-config.json` is not found or returns an error**: set `status: hard-fail`, `hard-fail-reason: "skf-config.json not found or unreadable"`, and skip to Step 4.

---

## Step 2 — Resolve environment

1. Determine the effective environment:
   - If the `env` input was provided and validated in Preflight: use that value directly. Set `devcontainer-check: skipped`.
   - Otherwise: use the `environment` value from the **config snapshot**.
2. If the effective environment is `devcontainer`:
   - Use `file_search` with pattern `.devcontainer/devcontainer.json` to check for existence.
   - If the file is found: set `devcontainer-check: passed`.
   - If the file is NOT found: set `devcontainer-check: hard-fail`, `status: hard-fail`, `hard-fail-reason: "skf-config.json specifies devcontainer but .devcontainer/devcontainer.json not found."` — skip to Step 4.
3. If the effective environment is `host`: set `devcontainer-check: skipped`. No further resolution needed.

> **If `file_search` returns no result for `.devcontainer/devcontainer.json`**: treat as file not found and apply the `hard-fail` branch above.

---

## Step 3 — Detect spec context

Apply PT019 (Specialist Dispatch) by delegating spec-flow branch detection to an external script.

1. Run `python3 {workspace-root}/ai/scripts/python/detect-spec-context.py --workspace-root {workspace-root}` in terminal.
2. If the script exits non-zero or the stdout cannot be parsed as JSON: set `spec-context: unknown`, `spec-feature-dir: unknown`. Do NOT set `status: hard-fail` — spec detection is advisory only.
3. If the script exits 0: parse the JSON stdout and extract `spec-context` and `feature-dir`.
4. Map to step outputs:
   - JSON `spec-context: true` → set `spec-context: true`, `spec-feature-dir: {feature-dir value from JSON}`
   - JSON `spec-context: false` → set `spec-context: false`, `spec-feature-dir: none`
   - Parse error or non-zero exit → set `spec-context: unknown`, `spec-feature-dir: unknown`

---

## Step 4 — Return result

Return the following inline:

```
## orch-initialize Result
- status: ok | hard-fail
- hard-fail-reason: {reason or none}
- environment: {value}
- spec-context: true | false | unknown
- spec-feature-dir: {path or none | unknown}
```

The skill is complete when the inline result above has been returned.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Use in Step 1 to read `skf-config.json` in full. Read from line 1; if the response fills the page, advance `startLine` and read again until confirmed complete.
- **file_search**: Use in Step 2 only to check for `.devcontainer/devcontainer.json` existence. Do NOT use for directory listing.
- **run_in_terminal**: Use in Step 3 to run `detect-spec-context.py`.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Standard Field Table**:

| Field | Value |
|-------|-------|
| status | `ok` \| `hard-fail` |
| skill_id | `orch-initialize` |
| output_path | `none` |
| summary | one-line description of initialization result |

**Inline result template**:

```markdown
# orch-initialize Result
- environment: {value from config or env input}
- config.maxClarificationLoops: {value}
- config.maxPlanRevisions: {value}
- config.maxWaveRetries: {value}
- config.maxSubagentRetries: {value}
- config.simpleMaxFiles: {value}
- config.standardMaxFiles: {value}
- config.complexMinFiles: {value}
- config.approvalTimeoutBehavior: {value}
- devcontainer-check: passed | skipped | hard-fail
- spec-context: true | false | unknown
- spec-feature-dir: {path or none}
- status: ok | hard-fail
- hard-fail-reason: {reason or none}
```

**Inline return** (returned at Step 4):

```
## orch-initialize Result
- status: ok | hard-fail
- hard-fail-reason: {reason or none}
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: workspace-root = `/workspaces/spek-fu`, no env override. `skf-config.json` has `environment: "devcontainer"`. `.devcontainer/devcontainer.json` exists on disk.

Expected behavior:
1. Reads `skf-config.json` in full; extracts all config values into the **config snapshot**.
2. Effective environment is `devcontainer` (from config). `file_search` finds `.devcontainer/devcontainer.json`. Sets `devcontainer-check: passed`.
3. Runs `detect-spec-context.py`. Parses JSON stdout; sets `spec-context` and `spec-feature-dir` accordingly.
4. Returns inline with all extracted values, `devcontainer-check: passed`, `spec-context`, `spec-feature-dir`, `status: ok`, `hard-fail-reason: none`.
</example>

<example>
Input: workspace-root = `/workspaces/spek-fu`, env = `host`.

Expected behavior:
1. Reads `skf-config.json` in full; extracts all config values into the **config snapshot**.
2. `env` input is `host` (validated in Preflight). Effective environment is `host`. Sets `devcontainer-check: skipped`.
3. Runs `detect-spec-context.py`. Parses JSON stdout; sets `spec-context` and `spec-feature-dir` accordingly.
4. Returns inline with all extracted values, `devcontainer-check: skipped`, `spec-context`, `spec-feature-dir`, `status: ok`, `hard-fail-reason: none`.
</example>

<example type="counter">
Input: workspace-root = `/workspaces/spek-fu`, no env override. `skf-config.json` has `environment: "devcontainer"`. `.devcontainer/devcontainer.json` does NOT exist on disk.

Expected behavior: Step 2 detects that `file_search` returns no result for `.devcontainer/devcontainer.json`. Sets `devcontainer-check: hard-fail`, `status: hard-fail`, `hard-fail-reason: "skf-config.json specifies devcontainer but .devcontainer/devcontainer.json not found."` Skips Step 3. Returns inline: `status: hard-fail`, `hard-fail-reason: "skf-config.json specifies devcontainer but .devcontainer/devcontainer.json not found."` Does NOT proceed to any further initialization.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **NEVER proceed past environment resolution when devcontainer-check fails** — set `status: hard-fail` and skip directly to writing `init-result.md`. Continuing on an unresolved environment causes cascading downstream failures.
- **ALWAYS return the inline initialization result** even when status is `hard-fail` — callers depend on a machine-readable result for error routing; a missing output leaves them in an undefined state.
- **NEVER accept unrecognized `env` values** — reject anything other than `devcontainer` or `host` with a `hard-fail` before executing any steps.

</reminders>
