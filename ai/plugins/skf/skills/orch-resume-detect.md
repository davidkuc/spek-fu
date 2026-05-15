---
id: "orch-resume-detect"
recommended-tier: "fast-agent"
version: 1.0
description: "Enumerates prior wave summary files in .orchestration-temp/ to determine whether a prior orchestration run can be resumed. USE FOR: resume detect, resume check, resume state, prior state detection, workflow resume. Returns a structured resume-state report."
anti-scope: "It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions."
tags:
  - "utility"
  - "orchestration"
  - "resume"
  - "workflow-state"
inputs:
  - "Override path for the working-state directory (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "One-line summary of resume detection result"
dispatch-variant: "compact"
---

# Skill: orch-resume-detect

<!-- SECTION 1: Identity (primacy position) -->
Enumerates prior wave summary files in `.orchestration-temp/` and returns a structured resume-state report. Always returns a structured markdown report — even when no prior state exists.

**Scope boundary**: This skill reads files only. It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions. Corrective action is the caller's responsibility.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Keep this skill strictly read-and-report. Never modify any file. WHY: resume detection must not mutate state; corrective action belongs to the caller.
2. Always return a structured report — never block the caller with an error or exception. WHY: the caller depends on a machine-readable result regardless of whether prior state exists.
3. Do NOT probe `.orchestration-temp/` with direct `read_file` glob patterns. Use `file_search` for enumeration. WHY: direct glob reads are unreliable for directory enumeration; `file_search` is the designated tool.
4. If `file_search` returns no results, treat that as a valid "no prior state" result and return the no-prior-state report. WHY: an empty result is a legitimate state, not an error.
5. If a wave summary cannot be read or has no non-blank lines, record it as malformed and set `recommendation` to `"restart"`. WHY: corrupt state is unsafe to resume from.
6. If a wave summary is classified as stale (timestamp older than `staleness-threshold-days` or plan path mismatch), record it in `staleSummaries` and set `recommendation` to `"review-stale-state"` — never auto-accept a stale summary as valid. WHY: stale state is ambiguous; auto-resuming from it risks corrupting orchestration with outdated context.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your report complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — enumerate, read, report, nothing more.
- Parse wave numbers from filenames arithmetically; do not infer from content.
- Record every found summary in the report regardless of validity.
- Never omit `malformedSummaries` from the report — use an empty array when all summaries are valid.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Inputs

| Field | Type | Required | Enum | Description |
|---|---|---|---|---|
| orchestration-temp-path | string | no | — | Override path for the working-state directory |
| staleness-threshold-days | number | no | — | Days after which a wave summary is flagged as potentially stale (default: 7) |

## Preflight

- Resolve `orchestration-temp-path` (default: `.orchestration-temp/`). Ensure path ends with `/` for consistent glob construction.

---

## Step 1 — Enumerate wave summary files
1. Use `file_search` with the glob pattern `{orchestration-temp-path}wave-*-summary.md` to find all existing wave summary markdown files.
2. If `file_search` returns no results: proceed directly to **Step 4 — No-prior-state path**.
3. Extract the wave number from each filename using the pattern `wave-{N}-summary.md`. Sort files by `N` ascending.

## Step 2 — Validate each wave summary

For each file found (in ascending wave-number order):

1. Call `read_file` on the first 20 lines of the file.
2. Classify the file:
   - **Valid**: at least one non-blank line was returned and passes both staleness and plan-path checks.
   - **Malformed**: file is unreadable, returns an error, or has no non-blank lines.
   - **Stale**: file is non-empty but fails the staleness check or plan-path check — treat as suspect rather than auto-accepted.
3. **Staleness check**: scan the summary content for a timestamp line (e.g., a field matching `Date:`, `Completed:`, or an ISO-8601 date pattern `YYYY-MM-DD`). If a timestamp is found and it is older than `staleness-threshold-days` (default: 7) days from the current date, classify the summary as **Stale** and record the reason as `"timestamp-exceeded-threshold"`.
4. **Plan-path check**: scan the summary content for a referenced plan path (e.g., a line containing `orchestration-plan.md` or a `Plan:` field). If a plan path is found and it does NOT match the current `orchestration-plan.md` path, classify the summary as **Stale** and record the reason as `"plan-path-mismatch: {found-path} vs orchestration-plan.md"`.
5. Accumulate results into three lists: `validSummaries`, `malformedSummaries`, and `staleSummaries`.

## Step 3 — Determine recommendation

Evaluate the accumulated lists:

| Condition | `lastCompletedWave` | `recommendation` |
|-----------|-------------------|-----------------|
| Any malformed summaries exist | `null` | `"restart"` || Any stale summaries exist (no malformed) | Highest valid wave `N` or `null` | `"review-stale-state"` || All summaries valid, at least one found | Highest valid wave `N` | `"continue-from-wave-{N+1}"` |
| No summaries found (fallthrough) | `null` | `"no-prior-state"` |

Proceed to Step 5 to build the report.

## Step 4 — No-prior-state path

Return immediately:

```markdown
## Resume State Report

- **Prior state**: false
- **Last completed wave**: none
- **Wave summaries found**: none
- **Malformed summaries**: none
- **Recommendation**: no-prior-state
```

## Step 5 — Build and return structured report

Assemble the final report using the schema in **Section 6 — Output format**.

- `priorState`: `true` if at least one valid summary was found; `false` otherwise.
- `lastCompletedWave`: highest valid wave number, or `null`.
- `waveSummaries`: sorted list of all found filenames (valid, stale, and malformed).
- `malformedSummaries`: list of filenames that failed validation (empty array if all valid).
- `staleSummaries`: list of filenames flagged as potentially stale with their reasons (empty array if none).
- `recommendation`: derived in Step 3.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **file_search**: Use in Step 1 to enumerate `wave-*-summary.md` files under `{orchestration-temp-path}`. Prefer over terminal find or grep for directory enumeration.
- **read_file**: Use in Step 2 to read the first 5 lines of each found summary file. Read one call per file.
- **grep_search**: Prohibited — use `file_search` for enumeration and `read_file` for content inspection.
- **edit / create_file / replace_string_in_file / run_in_terminal**: Prohibited because this skill never modifies or creates files and never runs terminal commands.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-resume-detect` |
| wave | `N` |
| step | `N.M` |
| summary | one-line summary of resume detection result |

```markdown
## Resume State Report

- **Prior state**: true | false
- **Last completed wave**: {N} | none
- **Wave summaries found**: {comma-separated filenames or none}
- **Malformed summaries**: {comma-separated filenames or none}
- **Stale summaries**: {comma-separated "filename (reason)" entries or none}
- **Recommendation**: continue-from-wave-{N+1} | restart | review-stale-state | no-prior-state
```

Rules:
- `Recommendation` must be one of the four literal values above. When `continue-from-wave-{N+1}`, substitute the actual next wave number (e.g., `continue-from-wave-3`). `review-stale-state` indicates stale summaries were found — the caller must inspect them before resuming.
- **Malformed summaries** is always present — use `none` when no malformed files exist.
- **Stale summaries** is always present — use `none` when no stale files exist. When stale files are present, list each as `{summary-file} (reason)` where reason is `timestamp-exceeded-threshold` or `plan-path-mismatch: {details}`.
- **Wave summaries found** lists filenames only (not full paths), sorted by wave number ascending, using `.md` extensions.
- When **Prior state** is `false`, **Last completed wave** is always `none`.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Invocation: Fresh run — no `.orchestration-temp/` directory or no `wave-*-summary.md` files found.
Agent: Runs `file_search` with glob `{orchestration-temp-path}wave-*-summary.md`. Receives empty results. Proceeds to Step 4 — No-prior-state path. Returns: Prior state: false, Last completed wave: none, Wave summaries found: none, Malformed summaries: none, Recommendation: no-prior-state. Does not attempt to read any files or modify anything.
</example>

<example>
Invocation: Prior run completed wave 2; `.orchestration-temp/` contains `wave-1-summary.md` and `wave-2-summary.md`, both timestamped within the staleness threshold and referencing the correct plan path.
Agent: Enumerates both files via `file_search`. Reads the first 20 lines of each. Classifies both as Valid (non-empty, timestamp within threshold, plan path matches). Sets lastCompletedWave = 2. Returns: Prior state: true, Last completed wave: 2, Wave summaries found: wave-1-summary.md, wave-2-summary.md, Malformed summaries: none, Stale summaries: none, Recommendation: continue-from-wave-3.
</example>

<example type="counter">
Invocation: `.orchestration-temp/` contains `wave-1-summary.md` with a timestamp 10 days old (exceeding the default 7-day staleness threshold).
Agent does NOT: auto-accept the summary as valid just because it is non-empty. Instead, classifies it as Stale with reason `timestamp-exceeded-threshold`. Returns Recommendation: review-stale-state and records the file in `staleSummaries`. The caller — not this skill — decides whether to resume or restart.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
- ALWAYS validate timestamps against the staleness threshold before classifying a summary as valid.
- ALWAYS check the plan path reference in each summary against the current `orchestration-plan.md` path — a mismatch is a staleness indicator, not an error.
- NEVER auto-accept a stale or ambiguous summary as valid — set `recommendation` to `"review-stale-state"` and let the caller decide.
- Use `file_search` for enumeration — never use `grep_search` or direct glob reads for directory enumeration.
- Include `malformedSummaries` and `staleSummaries` in every report — use empty arrays/`none` when all summaries are valid.
</reminders>
