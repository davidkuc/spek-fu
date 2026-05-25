---
id: "orch-intake-context"
recommended-tier: "fast-agent"
version: 1.0
description: "Accepts orchestrator-provided intake context and returns it inline as a structured orchestration-state object. USE FOR: capturing user-request, complexity tier, framework traversal results, knowledge lessons, pattern selection status, clarifications, and pre-planning validation status before planning begins."
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
  - "Pattern selection status, one of ok, blocked, or skipped, with structured result payload (optional)"
  - "Resolved clarifications from the user (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Structured intake context object"
  - "One-line summary of what was assembled"
dispatch-variant: "compact"
---

# Skill: orch-intake-context

<!-- SECTION 1: Identity (primacy position) -->
Accepts orchestrator-provided intake context and synthesizes it into a structured intake-context object returned inline. Called after all intake sub-steps (traversal, knowledge, pattern selection, clarification) have completed and before planning begins — the orchestrator passes this intake context as the primary planning input.

**Scope boundary**: This skill returns exactly one structured intake-context payload. It does NOT perform framework traversal, run knowledge consultation, execute pattern selection, modify plan or spec files, or prompt the user with questions. All inputs must be supplied by the caller.

**Triggers**: `intake context`, `capture intake`, `write intake context`, `intake snapshot`

**Tier**: fast-agent

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Always return a single structured intake-context payload and never write orchestration state to disk. WHY: planning now consumes inline state as the canonical handoff contract.
2. Never infer or fabricate values for absent optional inputs — use the literal string `not provided`. WHY: fabricated context silently corrupts downstream planning decisions.
3. `user-request` and `complexity-tier` are required — FAIL immediately with a structured error if either is absent or empty. WHY: these two fields are the minimum context required for any downstream planning step.
4. Preserve the caller's supplied structure for traversal summaries, lessons, pattern selection, and clarifications. WHY: later phases depend on those payloads, not on flattened prose.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your actions comply with all rules in `<constraints>` above — especially the single-target-file and no-fabrication rules.
- Implement EXACTLY and ONLY what this skill defines — compose the markdown, write it, return confirmation.
- Substitute the literal string `not provided` for any absent optional input; never leave a field blank or omit it.
- Do not emit flattened prose when the caller supplied structured fields; preserve compact structure in the output.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight
- Confirm `user-request` and `complexity-tier` are present before composing the markdown.

## Step 1 — Validate required inputs

1. Check that `user-request` is present and non-empty. If absent or empty: return `{ "status": "FAIL", "reason": "user-request is required but was not provided" }` and halt.
2. Check that `complexity-tier` is present and non-empty. If absent or empty: return `{ "status": "FAIL", "reason": "complexity-tier is required but was not provided" }` and halt.
3. Resolve all optional inputs; substitute `"not provided"` for any that are absent.
4. Resolve all structured optional payloads exactly as supplied; use `not provided` only when absent.

## Step 2 — Compose the intake context payload

Construct the structured intake context using the template below. Substitute all `{placeholder}` values from resolved inputs.

```yaml
intake-context:
  user-request: {user-request verbatim}
  complexity-tier:
    value: {Simple | Standard | Complex}
    rationale: {complexity-tier rationale or not provided}
  framework-context: {framework-context-summary or not provided}
  knowledge-lessons: {knowledge-lessons or not provided}
  pattern-selection:
    status: {ok | blocked | skipped | not provided}
    result: {structured pattern result or not provided}
  clarifications: {clarifications or not provided}
```

Substitution rules:
- `{user-request verbatim}`: copy the input exactly — do not summarize, truncate, or reformat.
- Any absent optional field must render as the literal string `not provided`.
- Preserve structured payloads for `framework-context`, `knowledge-lessons`, `pattern-selection.result`, and `clarifications` when the caller supplied them as objects or arrays.

## Step 3 — Return confirmation

Return the assembled payload using the output format defined in Section 6.


</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- No state-writing tools are permitted for this skill.
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
| output_path | `none` |
| summary | one-line summary of what was written |

```
## Intake Context Ready

Status: SUCCESS | FAIL | BLOCKED
Summary: {one-line summary}
State: {structured intake-context payload}
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
Input: user-request="Add OAuth login to the API", complexity-tier="Standard — single feature with known pattern".
Expected output: Status SUCCESS. Inline `intake-context` payload returned with all fields populated; optional fields rendered as `not provided`.
</example>

<example>
Input: user-request="Refactor payment module", complexity-tier="Complex — cross-module impact".
Expected output: Status SUCCESS. Inline `intake-context` payload returned with the supplied structured context preserved.
</example>

<example type="counter">
Input: complexity-tier provided but user-request is absent.
Expected behavior: Returns FAIL immediately — `{ "status": "FAIL", "reason": "user-request is required but was not provided" }`. No state is written. Does NOT infer or fabricate the missing user request.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
