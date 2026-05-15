---
id: "orch-artifact-coherence-check"
recommended-tier: "fast-agent"
version: 1.0
description: "Verifies that all outputs produced by Wave N are present and compatible with the inputs expected by Wave N+1 according to the orchestration plan. USE FOR: inter-wave coherence checks after a wave completes; detecting missing outputs or path mismatches before the next wave starts."
anti-scope: "It writes only to `.orchestration-temp/wave-{N}-coherence-report.md`. It does NOT create missing artifacts, execute other skills, halt execution, or ask the user questions. Corrective action and halt decisions are the caller's responsibility."
tags:
  - "utility"
  - "artifacts"
  - "coherence"
  - "validation"
inputs:
  - "Index of the wave just completed (required)"
  - "Index of the wave about to start (required)"
  - "Relative path to the orchestration plan markdown file (required)"
  - "Override path for the working-state directory (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Path to .orchestration-temp/wave-{N}-coherence-report.md (coherence report)"
  - "Summary of coherence check result"
dispatch-variant: "compact"
---

# Skill: orch-artifact-coherence-check

<!-- SECTION 1: Identity (primacy position) -->
After completing Wave N, verifies that all declared outputs of Wave N exist on disk and match the inputs expected by Wave N+1 as declared in the orchestration plan. Returns a structured OK or BLOCKED report inline and writes it to `.orchestration-temp/wave-{completed-wave}-coherence-report.md`.

**Scope boundary**: It writes only to `.orchestration-temp/wave-{N}-coherence-report.md`. It does NOT create missing artifacts, execute other skills, halt execution, or ask the user questions. Corrective action and halt decisions are the caller's responsibility.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Write ONLY to `.orchestration-temp/wave-{N}-coherence-report.md` — never modify plan files, wave summaries, or any artifact file. WHY: the coherence report is the skill's persisted deliverable; all other files are inputs and must be kept intact.
2. If the plan file is unreadable or not found, return `BLOCKED` immediately with that as the reason. WHY: no plan means no declared output/input contracts to verify.
3. Never issue a halt — return only the structured report. The caller decides whether to block the next wave. WHY: this skill reports facts; execution control is an orchestrator responsibility.
4. Evaluate every declared output and every declared input found in the plan — do not short-circuit on the first failure. WHY: partial validation produces incomplete reports that mis-direct resolution effort.
5. If no inter-wave dependencies are declared in the plan for Wave N+1, return `OK` with note `"no inter-wave dependencies declared"` rather than failing. WHY: absence of declared dependencies is a valid plan state.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your report complies with all rules in `<constraints>` above — especially the write-scope and no-halt rules.
- Implement EXACTLY and ONLY what this skill defines — check files, produce the report, nothing more.
- Record every check result (exists or missing) regardless of outcome; never suppress a failing check.
- Treat a path mismatch as a distinct incoherence type from a missing output — report both independently.
- Carry the exact file paths from the plan verbatim; do not normalize or infer paths.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Idempotency Check

Before executing any steps, check whether a prior coherence report already exists for this wave:

- **if-exists** (prior report detected): `.orchestration-temp/wave-{completed-wave}-coherence-report.md` exists and is non-empty → return the prior report and ask the caller whether to refresh (re-run checks) or reuse the existing report.
- **if-empty** (no prior state): the report file does not exist → proceed normally from Step 1.
- **if-complete** (report exists with `Status: OK`): the file exists, is non-empty, and declares `Status: OK` → return the existing report with a note that coherence was already confirmed; exit without re-running unless the caller explicitly requests a refresh.

## Preflight

- Confirm `completed-wave`, `next-wave`, and `plan-file` are all present and non-empty before loading any files.
- If any required input is absent, Return **BLOCKED** — reason: Missing required input: {field} and halt.
- Keep all steps read-only.

---

## Step 1 — Validate inputs
1. Confirm `completed-wave` is a positive integer. If not, Return **BLOCKED** — reason: "completed-wave must be a positive integer" and halt.
2. Confirm `next-wave` is a positive integer. If not, Return **BLOCKED** — reason: "next-wave must be a positive integer" and halt.
3. Confirm `plan-file` is present and non-empty. If not, Return **BLOCKED** — reason: "plan-file is required" and halt.
4. Resolve `orchestration-temp-path` (default: `.orchestration-temp/`).

## Step 2 — Read plan and extract wave contracts

1. Call `read_file` on `plan-file` to load the full plan content. If unreadable, Return **BLOCKED** — reason: "plan-file is unreadable or not found: {plan-file}" and halt.
2. Parse the plan as markdown. Search for headings such as `## Wave {N}`, `### Wave {N}`, or equivalent markers. Extract declared **outputs** — fields, lists, or inline artifact paths labelled `outputs`, `produces`, `output-files`, or equivalent. For Wave N+1 extract declared **inputs** — fields labelled `inputs`, `requires`, `input-files`, `depends-on`, or equivalent.
3. If Wave N has no declared outputs and Wave N+1 has no declared inputs, record `no_declared_outputs = true` and `no_declared_inputs = true`. Proceed to Step 6 (early OK).
4. Normalize all extracted paths to forward-slash format.

## Step 3 — Check Wave N outputs exist
For each path in the Wave N output list:
1. Attempt `read_file` on that path (first 3 lines). Record `exists: true` if successful; `exists: false` if the read fails or returns empty.
2. Mark `producedByWaveN: true` for every path in this list.
3. Record each check result before continuing.

## Step 4 — Check Wave N+1 inputs exist
For each path in the Wave N+1 input list:
1. Attempt `read_file` on that path (first 3 lines). Record `exists: true` if successful; `exists: false` if the read fails or returns empty.
2. Mark `requiredByWaveN1: true` for every path in this list.
3. Record each check result before continuing.

> If a path appears in both the Wave N output list and the Wave N+1 input list, consolidate it into a single check entry with both `producedByWaveN: true` and `requiredByWaveN1: true`.

## Step 5 — Detect path mismatches
1. Build the set of paths Wave N declares as outputs: `produced_set`.
2. Build the set of paths Wave N+1 declares as inputs: `expected_set`.
3. Paths in `expected_set` that are NOT in `produced_set` are **path mismatches** — Wave N+1 expects a file that Wave N never declared as output (even if the file exists on disk, a contract mismatch must be flagged).
4. Record each mismatch as `{ "type": "path-mismatch", "detail": "Wave N+1 expects '{path}' but Wave N did not declare it as an output." }`.
5. Paths in `produced_set` that are NOT in `expected_set` are **orphan outputs** — Wave N produced a file Wave N+1 does not use. These are informational; record as a note, not an incoherence.

## Step 6 — Compile and return report

Assemble the structured report:

**No inter-wave dependencies declared** (both lists empty):

**Status:** OK
**completedWave:** N | **nextWave:** N+1
**checks:** _(none)_
**incoherences:** _(none)_
**message:** no inter-wave dependencies declared

**All checks pass** (all outputs exist, no path mismatches):

**Status:** OK
**completedWave:** N | **nextWave:** N+1

**checks:**
| file | producedByWaveN | requiredByWaveN1 | exists |
|------|----------------|-----------------|--------|
| path | yes | yes | yes |

**incoherences:** _(none)_
**message:** All coherence checks pass.

**Incoherences found** (missing outputs or path mismatches):

**Status:** BLOCKED
**completedWave:** N | **nextWave:** N+1

**checks:**
| file | producedByWaveN | requiredByWaveN1 | exists |
|------|----------------|-----------------|--------|
| path | yes | yes | no |

**incoherences:**
- `missing-output`: Wave N declared output '{path}' but file does not exist.
- `path-mismatch`: Wave N+1 expects '{expected}' but Wave N declared '{produced}'.

**message:** Wave N produced {produced-paths} but Wave N+1 expects {expected-paths}. Resolution needed.

**Plan unreadable** (Step 2 halt):
Return **BLOCKED** — reason: "plan-file is unreadable or not found: {plan-file}"

Rules:
- `status` is `OK` only when every check has `exists: true` and `incoherences` is empty.
- Any `exists: false` or `path-mismatch` entry produces `status: BLOCKED`.
- The `message` field summarizes the overall result in one human-readable sentence.
- `incoherences` array is always present; use `[]` when empty.

**After assembling the JSON report, write the report as a markdown file** to `.orchestration-temp/wave-{completed-wave}-coherence-report.md` using `create_file`. The markdown format is:

```markdown
# Wave {N}→{N+1} Coherence Report

Status: OK | BLOCKED
Completed wave: {N}
Next wave: {N+1}

## Checks

| File | Produced by Wave {N} | Required by Wave {N+1} | Exists |
|------|----------------------|------------------------|--------|
| {path} | yes/no | yes/no | yes/no |

## Incoherences

{none — or bullet list}

## Notes

{message}
```

Call `create_file` with the assembled markdown content. If the `.orchestration-temp/` directory does not exist, `create_file` will create it automatically.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Use in Step 2 to load the full plan file. Use in Steps 3 and 4 to check artifact existence (first 3 lines per file). Read one file per call; prefer one call per file over fragmented reads.
- **file_search**: Permitted as a fallback when `read_file` returns ambiguous results for artifact existence checks (Steps 3–4).
- **grep_search**: Permitted as a fallback in Step 2 to locate wave headings or extract output/input declarations when `read_file` content is ambiguous.
- **create_file**: Use in Step 6 to write the coherence report to `.orchestration-temp/wave-{N}-coherence-report.md`.
- **replace_string_in_file / run_in_terminal**: Prohibited — this skill never modifies existing files and never executes commands.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` |
| skill_id | `orch-artifact-coherence-check` |
| wave | `N` |
| step | `5.5` |
| output_path | `.orchestration-temp/wave-{N}-coherence-report.md` |
| summary | one-line summary of coherence check result |

Return the structured JSON report defined in Step 6 as inline output. The full structured report is also written to `.orchestration-temp/wave-{N}-coherence-report.md`. No additional prose wrapping is required.

Rules:
- Always include `status`, `completedWave`, `nextWave`, `checks`, `incoherences`, and `message` in every non-BLOCKED response.
- For BLOCKED responses caused by unreadable plan file (Step 2 halt), return only `{ "status": "BLOCKED", "reason": "..." }`.
- For BLOCKED responses caused by missing required inputs (Step 1 halt), return only `{ "status": "BLOCKED", "reason": "..." }`.
- Do not include additional fields not defined in Step 6.
- `completedWave` and `nextWave` must be integers, not strings.

## Outputs

| Field | Type | Enum | Description |
|---|---|---|---|
| output_path | string | — | Path to `.orchestration-temp/wave-{N}-coherence-report.md` (coherence report) |
| summary | string | — | Summary of coherence check result |

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: completed_wave=2, next_wave=3, plan_file=plan.md. Wave 2 declares output `.orchestration-temp/final-quality-report.md`. Wave 3 declares input `.orchestration-temp/final-quality-report.md`. The file exists on disk. Path contract is satisfied.
Expected output: Status OK, checks table shows the file as present, incoherences empty. Report written to `.orchestration-temp/wave-{N}-coherence-report.md`.
</example>

<example>
Input: completed_wave=1, next_wave=2, plan_file=plan.md. Wave 1 declares output `.orchestration-temp/orchestration-plan.md`. Wave 2 declares input `.orchestration-temp/orchestration-plan.md`. The file does not exist on disk.
Expected output: Status BLOCKED, checks table shows `.orchestration-temp/orchestration-plan.md` as exists=no, incoherences list `missing-output`. Report written to `.orchestration-temp/wave-{N}-coherence-report.md`.
</example>

<example type="counter">
Input: completed_wave=3, next_wave=4, plan_file=plan.md. A missing artifact is detected. Agent attempts to create the missing file to resolve the incoherence.
Expected behavior: Returns BLOCKED status and the coherence report only. Does NOT create or modify any artifact. Corrective action is the caller's responsibility per Constraint 3.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

</reminders>
