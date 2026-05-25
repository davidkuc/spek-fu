---
id: "orch-orchestration-summary"
recommended-tier: "fast-agent"
version: 1.0
description: "Compiles and writes the orchestration summary document from inline wave summaries and the orchestration plan. USE FOR: generating the final timestamped orchestration summary report under reports/ at the close of a workflow run; filling the summary template from accumulated orchestration state; returning the completed summary inline for chat display."
anti-scope: "It does NOT modify any wave summary file, the orchestration plan, or any other artifact."
tags:
  - "utility"
  - "orchestration"
  - "summary"
  - "closure"
inputs:
  - "One-line description of what was orchestrated (required)"
  - "Task complexity tier, one of Simple, Standard, or Complex (required)"
  - "Integer count of waves that ran (required)"
  - "Inline wave summaries and verification state (required)"
  - "Inline orchestration plan or approved plan summary (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Path to written timestamped orchestration summary report"
  - "Full summary text returned inline in chat"
dispatch-variant: "compact"
---

# Skill: orch-orchestration-summary

<!-- SECTION 1: Identity (primacy position) -->
Loads the orchestration summary template, fills all `{placeholder}` fields from inline wave summaries and the orchestration plan, writes the completed document to `reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md`, and returns the full summary text for inline chat display.

**Scope boundary**: This skill reads the template and caller-provided orchestration state; writes exactly one timestamped summary report under `reports/`. It does NOT modify any wave summary state, the orchestration plan, or any other artifact. Placeholder values that cannot be resolved are replaced with `N/A` or `(not recorded)` — the output file is always written.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Never modify any wave summary file or the orchestration plan. WHY: those files are the authoritative record of the run; corruption is unrecoverable.
2. Never skip a placeholder — if data is unavailable, substitute `N/A` or `(not recorded)`. WHY: a partially filled template is still a valid summary and is more useful than an aborted one.
3. If the template file is missing, produce a minimal summary using the hardcoded fallback structure defined in Step 1. WHY: the summary must be written regardless of template availability so the close workflow can always proceed.
4. Always write the output file even if some placeholders cannot be resolved. WHY: an incomplete summary is better than no summary; the caller needs the file path to exist for downstream steps.
5. Return the full content of the written file as plain text after writing — do not truncate. WHY: the caller must display the summary inline in chat without reading the file independently.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your next step complies with all rules in `<constraints>` above — especially the no-modify and never-skip-placeholder rules.
- Implement EXACTLY and ONLY the steps defined in this skill — do not add extra wave analysis, quality checks, or content beyond the template's structure.
- Prefer verbatim content from wave summary files over paraphrasing; condense only when a wave summary is longer than 40 lines.
- Use caller-supplied inputs to fill the top-level header fields; use wave summary files for per-wave detail blocks.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Confirm all three required inputs are non-empty. If any are missing, Return **BLOCKED** with reason: `Missing required input: {field}` and halt.
- **State detection**: Scan `reports/` for any existing `reports/orchestration-summary-*.md` using `file_search`. If prior summaries exist, note that a previous run has already been recorded — proceed to generate a fresh timestamped summary (each invocation produces a uniquely named file; no overwrite risk). If no prior summaries exist → proceed with normal execution.

---

## Step 1 — Load template

Attempt to read `ai/plugins/skf/templates/orchestration-summary-template.md` using `read_file`.

- **Success**: Use the file content as the working template string. Proceed to Step 2.
- **File not found / unreadable**: Apply the hardcoded fallback template below. Proceed to Step 2 using the fallback.

### Hardcoded fallback template (used only when template file is missing)

```
## Orchestration Summary

Request: {one-line summary of original request}
Complexity: {complexity-tier}
Waves executed: {waves-executed}

### Per-Wave Summaries

{per-wave-blocks}

### Knowledge Capture

Blockers: (not recorded)
Notes: (not recorded)
```

## Step 2 — Collect inline wave summaries

1. Use the caller-provided wave summaries and verification state.
2. Sort results by wave number ascending.
3. If a wave summary is missing, record `(not recorded)` for that wave.
4. If no wave summaries are provided, record an empty list and note `(no wave summaries found)` for use in Step 4.

## Step 3 — Read orchestration plan (optional)

Use the caller-provided orchestration plan or approved plan summary when present.

- **Success**: Hold the content for placeholder resolution in Step 4.
- **Absent or malformed**: Proceed without plan data; any plan-derived placeholders will be filled with `N/A`.

## Step 4 — Fill placeholders

Resolve every `{placeholder}` token in the working template string using the following priority order:

| Placeholder | Source |
|-------------|--------|
| `{one-line summary of original request}` | `request-summary` input |
| `{complexity-tier}` / `{Simple \| Standard \| Complex}` | `complexity-tier` input |
| `{total waves}` / `{waves-executed}` | `waves-executed` input |
| `{total}` / `{count}` (steps planned, executed, skipped, failed) | Aggregated from wave summary files; `N/A` if not present |
| Execution log rows | Populated from wave summaries in wave-number order; rows without data use `(not recorded)` |
| Per-wave summary blocks | Populated verbatim from each inline wave summary content; each missing wave → `(not recorded)` block |
| Manual intervention, retry, and knowledge-capture tables | Extracted from wave summaries where present; `None.` or `(not recorded)` when absent |

**Rules:**
- Every `{placeholder}` token remaining after resolution must be replaced — never leave a raw `{...}` token in the output.
- If a value is unavailable from any source, use `N/A` for numeric/single-value fields and `(not recorded)` for descriptive fields.

## Step 5 — Write output file

Write the fully resolved template string to `reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md` using `create_file` as appropriate. Create the `reports/` directory if it does not exist.

- If the write fails, Return **FAILED** with reason: `Could not write the timestamped orchestration summary report: {error}` and halt — do not suppress the error.

## Step 6 — Return summary inline

Return the full content of the written summary as plain text in the response, preceded by the header:

```
## Orchestration Summary — reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md
```

Do not truncate or abbreviate. The caller uses this inline text to confirm the summary without reading the file.

## Run Telemetry

The skill should collect the following telemetry fields from inline orchestration state and include them in the generated orchestration summary:

| Field | Type | Source | Description |
|---|---|---|---|
| `run_id` | string | wave summary state / plan metadata | Timestamp-based identifier in format `YYYY-MM-DD-HHmmss` |
| `complexity_tier` | enum | caller inputs | One of: simple \| standard \| complex |
| `total_dispatches` | integer | orchestration plan state | Total count of all dispatches in the run |
| `failed_dispatches` | integer | wave summary state | Count of dispatches that returned fail or blocked status |
| `retried_waves` | list | wave summary state | List of wave numbers that required retry |
| `skills_used` | list | wave summary state | List of skill IDs that were dispatched |
| `completion_state` | enum | aggregated from results | One of: full \| partial \| failed |

**Data collection**:
- `run_id`: Extract from wave summary file metadata or generate from current timestamp
- `complexity_tier`: Read from the caller-provided complexity input or inline intake context
- `total_dispatches`: Count from the inline orchestration plan dispatch list
- `failed_dispatches`: Aggregate dispatch results from all wave summary files
- `retried_waves`: Extract from wave summary file retry records
- `skills_used`: Aggregate all skill IDs from all wave summary files
- `completion_state`: Determine from aggregated dispatch results across all waves

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Use in Step 1 to load the template only.
- **create_file**: Use in Step 5 to write the timestamped orchestration summary report when the file does not yet exist.
- **replace_string_in_file / multi_replace_string_in_file**: Use in Step 5 to overwrite the timestamped orchestration summary report when it already exists — replace the full content in one operation.
- **grep_search**: Prohibited — wave summary data comes from caller-provided state, not search.
- **run_in_terminal**: Prohibited — this skill performs no command execution.
- **vscode_askQuestions**: Prohibited — this skill takes no interactive decisions.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `failed` |
| output_path | `reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md` |
| summary | `one-line summary of the orchestration run` |

```
## Orchestration Summary — reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md

{full text of the written timestamped orchestration summary report, untruncated}
```

Rules:
- The header line must include the exact output path so the caller can reference it.
- The summary body must be returned verbatim — no rewording, no truncation.
- If the skill halts due to a BLOCKED or FAILED condition, return the JSON error object instead of the summary.
- The `reports/` directory must be created if it does not exist before writing the output file.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: request-summary="Implemented user auth system", complexity-tier="Standard", waves-executed=3
Expected output: Template read; wave-1/2/3-summary.md files read; all placeholders filled; reports/orchestration-summary-{timestamp}.md written; full text returned inline. Status: ok.
</example>

<example>
Input: waves-executed=2 but only one inline wave summary is provided
Expected output: Wave 2 summary block filled with "(not recorded)" for all fields. Output file still written with partial data. Status: ok — a partial summary is better than no summary.
</example>

<example type="counter">
Input: complexity-tier not provided.
Expected behavior: Returns BLOCKED — "Missing required input: complexity-tier". No template is read. No output file is written.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
