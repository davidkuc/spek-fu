---
id: "orch-wave-verification"
recommended-tier: "fast-agent"
version: 1.0
description: "Composes and writes the wave summary document, then independently verifies a completed execution wave by comparing the wave plan (expected tasks and outputs) against the wave summary (actual results). USE FOR: documenting what a wave executed, confirming produced expected artifacts, and catching structural and semantic gaps before moving to the next wave. Produces both wave summary and verification report files."
anti-scope: "It reads produced output files to confirm existence and spot-check for placeholders, but does NOT assess deep content quality, rewrite artifacts, or execute any tasks."
tags:
  - "quality"
  - "wave"
  - "verification"
  - "reporting"
inputs:
  - "Integer wave number identifying which wave to verify (required)"
  - "Wave task list with IDs, descriptions, assigned agent or skill, and expected output files (required)"
  - "Wave execution task records (inline or as file path) — used to compose the wave summary in Step 0 (required)"
  - "Path to the wave summary markdown file or inline summary content (may be omitted if task records are provided for Step 0) (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail (WAVE PASS or WAVE FAIL)"
  - "Path to written wave summary: `.orchestration-temp/wave-{N}-summary.md`"
  - "Path to written verification artifact: `.orchestration-temp/wave-{N}-verification.md`"
  - "One-line summary of wave verification result"
dispatch-variant: "full"
---

# Skill: orch-wave-verification

<!-- SECTION 1: Identity (primacy position) -->
Receives the wave plan (expected tasks and output file specifications), wave execution task records, and (optionally) an existing wave summary for a single execution wave. In Step 0, composes and writes the wave summary document from the task records. Then performs two verification passes — structural and semantic — and returns a Verification Report with a per-task verdict and an overall wave status.

**Scope boundary**: This skill executes one wave verification cycle only. It composes the wave summary using provided task records (Step 0), then reads produced output files to confirm existence and spot-check for placeholders. It does NOT assess deep content quality, rewrite artifacts, or execute any tasks. Full-orchestration quality belongs to the final quality gate.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Read source artifacts to verify them — do not write to, modify, or delete them. WHY: verification is an observation pass; mutations belong to the execution wave and would contaminate the audit trail.
2. Mark a task as structural PASS only when all expected output files are present and readable; mark it as structural FAIL when any expected file is absent or unreadable — do not infer a passing status from the wave summary alone. WHY: a missing artifact is a definitive structural failure regardless of any summary claim to the contrary.
3. Run semantic failure checks only after a task passes structural verification — do not apply semantic checks to a task that failed structurally. WHY: semantic assessment is meaningful only when the artifact physically exists and is parseable.
4. ALWAYS evaluate every task listed in the wave plan — do not skip tasks even if the wave summary omits them. WHY: an omitted task in the summary is itself a failure signal; silently dropping it produces a false-positive wave status.
5. ALWAYS base the overall wave status on the strictest individual task verdict — do not average, weight, or override individual verdicts. WHY: partial success misleads the orchestrator into continuing with incomplete inputs for the next wave.
6. Run structural file checks only on tasks that declare expected output files; for tasks with no expected output files (e.g., research-only tasks), skip the structural file check and evaluate semantics only — do not mark file-less tasks as structurally failing. WHY: not all tasks produce files; forcing a file check on file-less tasks produces spurious failures.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — verify, report, return. Nothing more.
- Be specific in failure descriptions: cite the exact missing file path, the placeholder text found, or the semantic mismatch observed. Vague failures block correction.
- When a task's actual output is present but contains obvious unfilled placeholders (e.g., `TODO`, `[PLACEHOLDER]`, `{value}`), mark it as FAIL with a semantic note — it is not complete.
- Output the Verification Report to chat AND write it to `.orchestration-temp/wave-{N}-verification.md` so the orchestrator can read it programmatically.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Step 0 — Compose Wave Summary

Before running verification checks, compose and write the wave summary document.

1. Using the wave execution task records provided as input (inline or from a file path), compose the wave summary following the template at `ai/plugins/skf/templates/wave-summary-template.md`.
2. Write the summary to `.orchestration-temp/wave-{N}-summary.md` (replace {N} with the actual wave number).
3. If `wave-summary-template.md` is not found, compose the summary with: wave number, wave goal, tasks completed (ID, description, status, output files), and overall wave status.
4. Log: `Step 0 complete — wave-{N}-summary.md written`

If the summary file cannot be written → log a warning but do NOT block verification (proceed to Step 1).

---

## Preflight

- Resolve `wave-number`, `wave-plan`, and `wave-summary` before verification begins.
- Derive `.orchestration-temp/wave-{N}-verification.md` up front so reruns refresh the same report file.
- Classify the run as first-write, refresh, or already-complete by checking whether the verification file already exists for the same wave number.
- If the summary file is missing, stop before structural checks and emit the fail-fast report.

## Done conditions

- **blocked run** is done when the missing-summary fail-fast report is returned and `.orchestration-temp/wave-{N}-verification.md` is refreshed with the blocked status.
- **verification run** is done when every task from the wave plan has a structural verdict, every structurally passing task has a semantic verdict, and the inline report matches `.orchestration-temp/wave-{N}-verification.md`.

## Verification checks

### Structural checks (deterministic)

For each task in the wave plan:

| Check | Pass condition | Fail condition |
|-------|---------------|----------------|
| Task returned | Task ID appears in wave summary | Task ID absent from wave summary |
| Output files present | Every expected output file path exists and is readable | One or more expected paths missing or unreadable |
| Schema match | File extension matches expected type (e.g., `.json` is valid JSON, `.md` is non-empty text) | File is empty, binary where text expected, or fails format parse |

### Semantic checks (lightweight)

For each task that passed all structural checks:

| Check | Pass condition | Fail condition |
|-------|---------------|----------------|
| Output addresses task | Output content is substantively related to the task description (not a blank stub or entirely off-topic) | Output is a stub, entirely off-topic, or consists only of boilerplate with no task-specific content |
| No open placeholders | Output contains no unfilled template placeholders (`TODO`, `[PLACEHOLDER]`, `{value}`, `<!-- fill -->`) | One or more unfilled placeholders found |
| Summary consistent | Wave summary claim for this task is consistent with what the output file actually contains (no contradictions) | Summary claims task completed but output is absent/incomplete, or vice versa |

## Step 1 — Load inputs

Read the wave plan (inline or from file path if provided as a path). Read the wave summary file from `.orchestration-temp/wave-{N}-summary.md`. Parse the markdown content to extract the task list from the Tasks table and the result list from the structured sections of the wave summary.

If the wave summary file is absent, immediately return a FAIL report: "Wave summary file not found — wave may not have completed execution."

### Step 1.5 — Plan-consistency check

After loading the wave summary, perform a plan-consistency check before any structural or semantic verification:

1. Scan the wave summary content for a referenced plan path — look for a line matching `Plan:`, `orchestration-plan:`, or any occurrence of a `.md` file path ending in `orchestration-plan.md`.
2. Compare the found plan path against the current plan (`orchestration-plan.md` by default, or the path passed as `wave-plan` if it is a file path).
3. **If the plan path in the summary differs from the current plan path**: record a `plan-consistency` warning: `"STALE-STATE: wave summary references '{found-path}' but current plan is 'orchestration-plan.md'"`.
4. **If no plan path is found in the summary**: record a `plan-consistency` note: `"UNKNOWN: no plan path reference found in wave summary"`. Do not block verification.
5. **If paths match or no conflict is found**: record `plan-consistency` as `OK`.

Surface the plan-consistency result in the Verification Report (see `<output_format>`).

## Step 2 — Structural pass

For each task in the wave plan:

1. Check if the task ID appears in the wave summary. If absent → structural FAIL on "Task returned".
2. For each expected output file path: attempt to read the file. If missing or unreadable → structural FAIL on "Output files present".
3. For each file that exists: validate format (non-empty, correct type). If invalid → structural FAIL on "Schema match".

Record per-task structural verdict: PASS or FAIL with specific failure notes.

## Step 3 — Semantic pass

For each task that received a structural PASS:

1. Read the output file(s) content.
2. Check that content is substantively related to the task description. Flag if content is a stub or entirely generic.
3. Scan for unfilled placeholders using patterns: `TODO`, `FIXME`, `\[PLACEHOLDER\]`, `\{[A-Za-z_]+\}` (template-style), `<!-- fill -->`.
4. Compare wave summary claim for this task against actual file content. Flag contradictions.

Record per-task semantic verdict: PASS or FAIL with specific failure notes.

## Step 4 — Compute overall wave status

If all tasks have both structural PASS and semantic PASS → overall status: **WAVE PASS**.

If any task has any FAIL → overall status: **WAVE FAIL**.

Write `.orchestration-temp/wave-{N}-verification.md` using the Verification Report template defined in the `<output_format>` section.

Return the Verification Report block using the same template.

The skill is complete when `.orchestration-temp/wave-{N}-verification.md` has been written or refreshed and the Verification Report block has been returned.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Read the wave plan (if file path), wave summary, and expected output files for semantic verification. Use as fallback when scripts are unavailable.
- **create_file**: Write the Verification Report to `.orchestration-temp/wave-{N}-verification.md`.
- **grep_search**: Use for placeholder scanning and targeted plan-summary comparisons.
- Do not use terminal helper scripts in this skill; extract the plan, summary, coverage, and verdict directly from the wave files.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-wave-verification` |
| wave | `N` |
| step | `3.3` |
| output_path_summary | `.orchestration-temp/wave-{N}-summary.md` |
| output_path_verification | `.orchestration-temp/wave-{N}-verification.md` |
| summary | wave composition and verification complete |

Return the Verification Report block below to the caller. Do not add explanatory prose beyond what the template specifies.

```
## Wave {N} Verification Report

Overall status: WAVE PASS | WAVE FAIL
Plan consistency: OK | STALE-STATE: {details} | UNKNOWN: {details}
Tasks verified: {total}
Structural failures: {count}
Semantic failures: {count}

### Per-task results

| Task ID | Description | Structural | Semantic | Notes |
|---------|-------------|-----------|---------|-------|
| {id} | {description} | PASS/FAIL | PASS/FAIL/SKIP | {specific notes or "—"} |

### Failure details

{For each failed task:}
**{task-id}**: {specific description of failure — missing file path, placeholder text found, semantic mismatch, etc.}

{If no failures:}
No failures detected.

### Recommended actions

{If WAVE FAIL:}
- {Specific correction action per failed task}

{If WAVE PASS:}
Wave is clear to proceed.
```

Field definitions:
- `overall status`: `WAVE PASS` if all task verdicts are PASS; `WAVE FAIL` if any task verdict is FAIL.
- `plan consistency`: `OK` when the plan referenced in the wave summary matches the current plan; `STALE-STATE: {details}` when a mismatch is detected (surface as a warning — does NOT automatically force `WAVE FAIL` but must be visible to the orchestrator); `UNKNOWN: no plan path reference found in wave summary` when no reference exists.
- `Tasks verified`: total count of tasks from the wave plan.
- `Structural failures`: count of tasks with a structural FAIL verdict.
- `Semantic failures`: count of tasks with a semantic FAIL verdict (SKIP is not a failure).
- `Semantic` column: `PASS`, `FAIL`, or `SKIP` (research-only tasks with no expected output files).
- Include `### Failure details` only when at least one failure exists.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>

### Example 1 — Wave pass (structural and semantic checks both pass)

**Input (wave-plan excerpt)**:
```
Task W2-T1: Update skills-index.json
  Agent: fast-agent / index maintenance workflow
  Expected outputs: [ai/plugins/skf/skills/skills-index.json]
```

**Input (wave-summary excerpt)**:
```
W2-T1: Completed. Added 3 new skill entries.
```

**Verification**:
- Structural: `ai/plugins/skf/skills/skills-index.json` → file exists and is valid JSON → PASS
- Semantic: Content references the 3 new skills described in the task → no placeholders → PASS

**Output**:
```
## Wave 2 Verification Report

Overall status: WAVE PASS
Tasks verified: 1
Structural failures: 0
Semantic failures: 0

### Per-task results

| Task ID | Description | Structural | Semantic | Notes |
|---------|-------------|-----------|---------|-------|
| W2-T1 | Update skills-index.json | PASS | PASS | — |

### Recommended actions
Wave is clear to proceed.
```

</example>

---

<example>

### Example 2 — Semantic failure (unfilled placeholder)

**Input (wave-plan excerpt)**:
```
Task W3-T2: Write orch-wave-verification.md skill spec
  Agent: standard-agent / skill maintenance workflow
  Expected outputs: [ai/plugins/skf/skills/orch-wave-verification.md]
```

**Verification**:
- Structural: file exists, non-empty markdown → PASS
- Semantic: file contains `[PLACEHOLDER]` in the constraints section → FAIL

**Output**:
```
## Wave 3 Verification Report

Overall status: WAVE FAIL
Tasks verified: 1
Structural failures: 0
Semantic failures: 1

### Per-task results

| Task ID | Description | Structural | Semantic | Notes |
|---------|-------------|-----------|---------|-------|
| W3-T2 | Write orch-wave-verification.md skill spec | PASS | FAIL | Unfilled placeholder found in constraints section |

### Failure details
**W3-T2**: File `ai/plugins/skf/skills/orch-wave-verification.md` contains unfilled placeholder `[PLACEHOLDER]` at constraints section. Content appears to be an incomplete draft.

### Recommended actions
- W3-T2: Re-open skill spec and replace all `[PLACEHOLDER]` tokens with concrete content before proceeding.
```

</example>

---

<example type="counter">

### Example 3 — Counter-example (do not rewrite failed artifact)

A task fails semantic verification because its output is a stub. This skill reports the failure and recommends a correction action — it does NOT attempt to rewrite the artifact itself. Rewriting belongs to the execution wave triggered by the orchestrator in response to the failure.

</example>
</examples>

<!-- SECTION 8: Reminders (recency anchors) -->
<reminders>
</reminders>
</output_format>
