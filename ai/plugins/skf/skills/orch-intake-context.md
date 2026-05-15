---
id: "orch-intake-context"
recommended-tier: "fast-agent"
version: 1.0
description: "Accepts orchestrator-provided intake context and writes it to .orchestration-temp/intake-context.md as a structured markdown document. USE FOR: capturing user-request, complexity tier, framework traversal results, knowledge lessons, pattern selection status, clarifications, and pre-planning validation status before planning begins; overwriting a stale intake snapshot with an overwrite notice."
anti-scope: "It does NOT perform framework traversal, run knowledge consultation, execute pattern selection, modify plan or spec files, or prompt the user with questions."
tags:
  - "utility"
  - "context"
  - "intake"
  - "workflow-state"
inputs:
  - "Verbatim user request text (required)"
  - "Complexity tier, one of Simple, Standard, or Complex, with rationale (required)"
  - "Relevant files and context from framework traversal (optional)"
  - "Applicable lessons from knowledge consultation (optional)"
  - "Pattern selection status, one of ok, blocked, or skipped, with result file path (optional)"
  - "Resolved clarifications from the user (optional)"
  - "Override path for the working-state directory (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Path to written artifact"
  - "One-line summary of what was written"
dispatch-variant: "compact"
---

# Skill: orch-intake-context

<!-- SECTION 1: Identity (primacy position) -->
Accepts orchestrator-provided intake context and synthesizes it into a structured markdown document at `.orchestration-temp/intake-context.md`. Called after all intake sub-steps (traversal, knowledge, pattern selection, clarification) have completed and before pre-planning validation — the orchestrator passes intake-context to validation as its primary input.

**Scope boundary**: This skill writes exactly one file — `.orchestration-temp/intake-context.md`. It does NOT perform framework traversal, run knowledge consultation, execute pattern selection, modify plan or spec files, or prompt the user with questions. All inputs must be supplied by the caller.

**Triggers**: `intake context`, `capture intake`, `write intake context`, `intake snapshot`

**Tier**: fast-agent

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Always write to `{orchestration-temp-path}intake-context.md` and only to that path — never elsewhere. WHY: the pre-planning validation skill (PP-02 check) expects the file at the exact canonical location.
2. Never infer or fabricate values for absent optional inputs — use the literal string `not provided`. WHY: fabricated context silently corrupts downstream planning decisions.
3. When `intake-context.md` already exists at the target path, prepend an overwrite notice at the top of the markdown document containing the ISO timestamp — do not silently replace the prior snapshot. WHY: the prior snapshot may still be needed for audit or resume decisions.
4. `user-request` and `complexity-tier` are required — FAIL immediately with a structured error if either is absent or empty. WHY: these two fields are the minimum context required for any downstream planning step.
5. Write the file using `create_file` only when it does not exist; use `replace_string_in_file` to replace content when the file already exists. WHY: distinguishing create vs. overwrite enforces Constraint 3.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your actions comply with all rules in `<constraints>` above — especially the single-target-file and no-fabrication rules.
- Implement EXACTLY and ONLY what this skill defines — compose the markdown, write it, return confirmation.
- Substitute the literal string `not provided` for any absent optional input; never leave a field blank or omit it.
- Record the exact target path in your confirmation output, not an approximation.
- Do not emit the markdown content in the chat response beyond the first 15 lines required by the output format.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Idempotency Check

Before validating inputs, check whether a prior intake context file exists:

- **if-exists** (prior intake context detected): `.orchestration-temp/intake-context.md` exists and is non-empty → set the overwrite flag and proceed; Constraint 3 applies (prepend overwrite notice with ISO timestamp).
- **if-empty** (no prior state): the file does not exist → proceed normally from Step 1.
- **if-complete** (caller signals no update needed): if the caller explicitly confirms the existing intake context is current and no changes are required → return the existing file path and line count; exit without rewriting.

## Preflight
- Resolve `orchestration-temp-path` (default: `.orchestration-temp/`).
- Confirm `user-request` and `complexity-tier` are present before composing the markdown.

## Step 1 — Validate required inputs

1. Check that `user-request` is present and non-empty. If absent or empty: return `{ "status": "FAIL", "reason": "user-request is required but was not provided" }` and halt.
2. Check that `complexity-tier` is present and non-empty. If absent or empty: return `{ "status": "FAIL", "reason": "complexity-tier is required but was not provided" }` and halt.
3. Resolve all optional inputs; substitute `"not provided"` for any that are absent.
4. Resolve `orchestration-temp-path`; set to `.orchestration-temp/` if not supplied.

## Step 2 — Check for existing intake-context.md

1. Use `file_search` for `{orchestration-temp-path}intake-context.md`.
2. If the file is **not found**: proceed to Step 3 (first write).
3. If the file **is found**: set the overwrite flag and read the first 5 lines to confirm it is non-empty before proceeding to Step 3.

## Step 3 — Compose the intake context markdown

Construct the markdown document using the template below. Substitute all `{placeholder}` values from resolved inputs.

**When overwrite flag is set**, prepend an overwrite notice block:

```markdown
> **Overwrite Notice**
> This file replaced a prior intake-context.md snapshot on {ISO timestamp}.
> Prior snapshot was overwritten intentionally at caller request.

# Intake Context

**Generated:** {ISO timestamp or runtime}
**Complexity Tier:** {Simple | Standard | Complex}

## User Request

{user-request verbatim}

## Complexity Rationale

{complexity-tier rationale or not provided}

## Framework Context

{framework-context-summary or not provided}

## Knowledge Lessons

{knowledge-lessons or not provided}

## Pattern Selection Status

**Status:** {ok | blocked | skipped | not provided}
**Result File:** {result file path if status is ok, otherwise N/A}

## Clarifications

{clarifications or not provided}
```

**On first write** (no prior file), omit the overwrite notice block entirely.

Substitution rules:
- `{ISO timestamp or runtime}`: use an ISO 8601 timestamp if available; otherwise write the literal `runtime`.
- `{user-request verbatim}`: copy the input exactly — do not summarize, truncate, or reformat.
- For `patternSelectStatus`: use the status token (`ok` | `blocked` | `skipped`) directly. Put the result file path on the **Result File** line; use `N/A` when status is not `ok`.
- Any absent optional field must render as the literal string `not provided`.
- **Overwrite notice**: include only when overwrite flag is set; omit the block entirely on first write.

## Step 4 — Write the file

- **First write** (no prior file): call `create_file` with the full composed markdown at `{orchestration-temp-path}intake-context.md`.
- **Overwrite** (prior file found): call `replace_string_in_file` to replace the entire prior content with the new markdown (which includes the overwrite notice block at the top), OR call `create_file` after confirming the path to replace — whichever is supported by the active tool set.

## Step 5 — Return confirmation

Count the lines in the written document and return the confirmation block defined in Section 6.


</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **file_search**: Use in Step 2 to check whether `intake-context.md` already exists. Prefer over terminal find.
- **read_file**: Use in Step 2 (overwrite path) to confirm the prior JSON file is non-empty. Read only the first 5 lines.
- **create_file**: Use in Step 4 to write the document when no prior file exists.
- **replace_string_in_file**: Use in Step 4 (overwrite path only) to replace prior content and prepend the overwrite notice.
- **grep_search / semantic_search**: Prohibited — this skill composes and writes a document; search tools are not part of its workflow.
- **run_in_terminal**: Prohibited — no scripts or terminal commands are required.
- **vscode_askQuestions**: Prohibited — all inputs must be supplied by the caller; this skill never prompts the user.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-intake-context` |
| wave | `N` |
| step | `N.M` |
| output_path | `.orchestration-temp/intake-context.md` |
| summary | one-line summary of what was written |

```
## Intake Context Written

Status: SUCCESS | FAIL | BLOCKED
File: {orchestration-temp-path}intake-context.md
Lines: {line count of written file}
Overwrite: yes | no
```

**On FAIL** (missing required input):
```
## Intake Context — FAILED

Status: FAIL
Reason: {exact reason — e.g., "user-request is required but was not provided"}
```

**On BLOCKED** (tool failure or write error):
```
## Intake Context — BLOCKED

Status: BLOCKED
Reason: {description of what failed and which step}
Next action: {what the caller should do to unblock}
```
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: user-request="Add OAuth login to the API", complexity-tier="Standard — single feature with known pattern". No prior intake-context.md exists.
Expected output: Status SUCCESS. File created at `.orchestration-temp/intake-context.md` with all fields populated; optional fields rendered as `not provided`. Overwrite: no.
</example>

<example>
Input: user-request="Refactor payment module", complexity-tier="Complex — cross-module impact". A prior intake-context.md already exists.
Expected output: Status SUCCESS. File overwritten with overwrite notice block prepended containing ISO timestamp. Overwrite: yes.
</example>

<example type="counter">
Input: complexity-tier provided but user-request is absent.
Expected behavior: Returns FAIL immediately — `{ "status": "FAIL", "reason": "user-request is required but was not provided" }`. No file is written. Does NOT infer or fabricate the missing user request.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
