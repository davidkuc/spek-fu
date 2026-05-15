---
id: "orch-initialize"
recommended-tier: "fast-agent"
version: 1.0
description: "Reads skf-config.json, resolves the runtime environment, manages the .orchestration-temp/ working folder lifecycle, and writes a compact initialization report to .orchestration-temp/init-result.md. USE FOR: framework initialization at the start of every orchestration run; centralizing config loading, environment resolution, and temp-folder setup away from inline orchestrator logic. DO NOT USE FOR: per-wave state tracking, skill index navigation, or orchestration planning."
anti-scope: "Does NOT execute orchestration waves, dispatch sub-agents, or manage any file outside .orchestration-temp/ and skf-config.json."
tags:
  - "utility"
  - "initialization"
  - "environment"
  - "orchestration"
inputs:
  - "workspace-root: absolute path to the workspace root (required)"
  - "env: runtime environment override — if provided, skips config-based env resolution and uses this value directly; must be devcontainer or host (optional)"
outputs:
  - "Path to .orchestration-temp/init-result.md (always written)"
  - "Status: ok | hard-fail"
  - "hard-fail-reason: descriptive string when status is hard-fail, else none"
dispatch-variant: "compact"
---

# Skill: orch-initialize

<!-- SECTION 1: Identity (primacy position) -->
Centralizes framework initialization into a single delegatable skill: reads `skf-config.json` to extract all configuration values, resolves the runtime environment (including devcontainer presence check), manages the `.orchestration-temp/` working folder lifecycle (create, clear, or leave as-is), and writes a compact **init-result.md** report to that folder. Designed to be dispatched as the first step in every orchestration run so that orchestrators no longer carry inline initialization logic. Applies PT001 (Divide and Conquer) by treating each initialization concern as a discrete step, and PT019 (Specialist Dispatch) by serving as a focused specialist whose sole responsibility is environment and folder readiness.

**Scope boundary**: This skill reads `skf-config.json`, checks for `.devcontainer/devcontainer.json`, and manages files inside `.orchestration-temp/` only. It does NOT execute orchestration waves, dispatch sub-agents, or read any file outside these three paths. For wave planning and decomposition, use **orch-wave-decompose**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER proceed past Step 2 (environment resolution) when the devcontainer check fails — set `status: hard-fail` and jump directly to Step 4 to write init-result.md. WHY: continuing initialization on an unresolved environment causes cascading downstream failures that are harder to diagnose and reverse.
2. NEVER delete `.orchestration-temp/` itself — delete only the files inside it. WHY: the folder is a workspace convention; deleting the directory breaks callers that hold references to the directory path.
3. ALWAYS write `init-result.md` regardless of status — even a `hard-fail` must produce a machine-readable output file. WHY: callers depend on the file to route error handling; a missing output leaves them in an undefined state.
4. NEVER accept an unrecognized value for the `env` input — reject anything other than `devcontainer` or `host` with `status: hard-fail` and reason "Unrecognized env value: {value}". WHY: unrecognized environment values produce undefined resolution behavior in all downstream steps.
5. NEVER modify `skf-config.json` or write any file outside `.orchestration-temp/`. Use `run_in_terminal` ONLY for `mkdir -p` and `rm -f` on the temp folder — NEVER for any other path. WHY: this skill is read-and-setup only; writes outside the temp folder exceed its designated scope.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra config extraction, no unrequested folder cleanup beyond what is specified.
- On re-run (idempotency): check whether `.orchestration-temp/` exists and whether it has files before acting — do not assume first-run state.
- If `skf-config.json` cannot be read, report `hard-fail` immediately with reason "skf-config.json not found or unreadable" — do not guess config values.
- Apply PT001 (Divide and Conquer) by executing each initialization concern — config extraction, environment resolution, folder management, output write — as a discrete step in strict sequence.
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

- **ok** is done when `init-result.md` exists at `.orchestration-temp/init-result.md` with `status: ok` and all config values populated.
- **hard-fail** is done when `init-result.md` exists with `status: hard-fail` and `hard-fail-reason` is populated.
- The skill is complete when `init-result.md` has been written and its path has been returned inline.

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

## Step 3 — Manage .orchestration-temp/ folder

Apply PT001 (Divide and Conquer) by treating folder state as three discrete branches:

1. Attempt `list_dir` on `{workspace-root}/.orchestration-temp/`.
   - **If the directory does not exist** (`list_dir` errors or returns not found): run `mkdir -p {workspace-root}/.orchestration-temp/` in terminal. Set `orchestration-temp: created`.
   - **If the directory exists and is empty** (`list_dir` returns zero entries): do nothing. Set `orchestration-temp: existed-empty`. Note: "folder existed, was empty, no action taken."
   - **If the directory exists and has files** (`list_dir` returns one or more entries): run `rm -f {workspace-root}/.orchestration-temp/*` in terminal to delete all files inside (NOT the directory itself). Set `orchestration-temp: existed-files-deleted`. Note: "folder existed with files — all files deleted."

> **If `rm -f` fails** (permission error or other terminal error): set `status: hard-fail`, `hard-fail-reason: "Failed to delete files in .orchestration-temp/: {error message}"`, and proceed to Step 4.

---

## Step 4 — Write init-result.md

Apply PT006 (Scratchpad Externalization) by writing the initialization result to a persistent file, and PT014 (Structured Output) by using the canonical template from `<output_format>`.

1. Compose the **init-result.md** content by filling in the template from `<output_format>` with all values resolved in Steps 1–3.
2. If status is `hard-fail`, populate `hard-fail-reason` and set all unresolved fields to `n/a`.
3. Write the file using `create_file` at `{workspace-root}/.orchestration-temp/init-result.md`.

> **If `create_file` fails**: report `hard-fail` with reason "Failed to write init-result.md: {error message}" inline — the skill cannot guarantee a persisted output in this case.

---

## Step 5 — Return result

Return the following inline:

```
## orch-initialize Result
- output-path: .orchestration-temp/init-result.md
- status: ok | hard-fail
- hard-fail-reason: {reason or none}
```

The skill is complete when `init-result.md` exists at `{workspace-root}/.orchestration-temp/init-result.md` and the inline result above has been returned.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Use in Step 1 to read `skf-config.json` in full. Read from line 1; if the response fills the page, advance `startLine` and read again until confirmed complete.
- **file_search**: Use in Step 2 only to check for `.devcontainer/devcontainer.json` existence. Do NOT use for directory listing.
- **list_dir**: Use in Step 3 to inspect whether `.orchestration-temp/` exists and whether it contains files.
- **run_in_terminal**: Use in Step 3 only for `mkdir -p` (create folder) and `rm -f` (delete files inside folder). NEVER use `rm -rf`. NEVER run commands against any path other than `.orchestration-temp/`.
- **create_file**: Use in Step 4 to write `init-result.md`. Use only after the **config snapshot** and all step outputs are finalized.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Standard Field Table**:

| Field | Value |
|-------|-------|
| status | `ok` \| `hard-fail` |
| skill_id | `orch-initialize` |
| output_path | `.orchestration-temp/init-result.md` |
| summary | one-line description of initialization result |

**init-result.md template** (written to disk at Step 4):

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
- orchestration-temp: created | existed-empty | existed-files-deleted
- status: ok | hard-fail
- hard-fail-reason: {reason or none}
```

**Inline return** (returned at Step 5):

```
## orch-initialize Result
- output-path: .orchestration-temp/init-result.md
- status: ok | hard-fail
- hard-fail-reason: {reason or none}
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: workspace-root = `/workspaces/spek-fu`, no env override. `skf-config.json` has `environment: "devcontainer"`. `.devcontainer/devcontainer.json` exists on disk. `.orchestration-temp/` does not exist.

Expected behavior:
1. Reads `skf-config.json` in full; extracts all config values into the **config snapshot**.
2. Effective environment is `devcontainer` (from config). `file_search` finds `.devcontainer/devcontainer.json`. Sets `devcontainer-check: passed`.
3. `list_dir` on `.orchestration-temp/` fails (not found). Runs `mkdir -p .orchestration-temp/`. Sets `orchestration-temp: created`.
4. Writes `init-result.md` with all extracted values, `devcontainer-check: passed`, `orchestration-temp: created`, `status: ok`, `hard-fail-reason: none`.
5. Returns inline: `output-path: .orchestration-temp/init-result.md`, `status: ok`, `hard-fail-reason: none`.
</example>

<example>
Input: workspace-root = `/workspaces/spek-fu`, env = `host`. `.orchestration-temp/` exists with three files inside.

Expected behavior:
1. Reads `skf-config.json` in full; extracts all config values into the **config snapshot**.
2. `env` input is `host` (validated in Preflight). Effective environment is `host`. Sets `devcontainer-check: skipped`.
3. `list_dir` finds three entries in `.orchestration-temp/`. Runs `rm -f .orchestration-temp/*`. Sets `orchestration-temp: existed-files-deleted`.
4. Writes `init-result.md` with all extracted values, `devcontainer-check: skipped`, `orchestration-temp: existed-files-deleted`, `status: ok`, `hard-fail-reason: none`.
5. Returns inline: `output-path: .orchestration-temp/init-result.md`, `status: ok`, `hard-fail-reason: none`.
</example>

<example type="counter">
Input: workspace-root = `/workspaces/spek-fu`, no env override. `skf-config.json` has `environment: "devcontainer"`. `.devcontainer/devcontainer.json` does NOT exist on disk.

Expected behavior: Step 2 detects that `file_search` returns no result for `.devcontainer/devcontainer.json`. Sets `devcontainer-check: hard-fail`, `status: hard-fail`, `hard-fail-reason: "skf-config.json specifies devcontainer but .devcontainer/devcontainer.json not found."` Skips Step 3. Writes `init-result.md` with `status: hard-fail` and the reason (all unresolved fields set to `n/a`). Returns inline: `status: hard-fail`, `hard-fail-reason: "skf-config.json specifies devcontainer but .devcontainer/devcontainer.json not found."` Does NOT proceed to folder management or any further initialization.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **NEVER proceed past environment resolution when devcontainer-check fails** — set `status: hard-fail` and skip directly to writing `init-result.md`. Continuing on an unresolved environment causes cascading downstream failures.
- **NEVER delete `.orchestration-temp/` itself** — only delete files inside it using `rm -f`, not `rm -rf`. Deleting the directory breaks callers holding references to the path.
- **ALWAYS write `init-result.md`** even when status is `hard-fail` — callers depend on a machine-readable result for error routing; a missing output leaves them in an undefined state.
- **NEVER accept unrecognized `env` values** — reject anything other than `devcontainer` or `host` with a `hard-fail` before executing any steps.

</reminders>
