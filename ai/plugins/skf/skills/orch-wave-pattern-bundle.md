---
id: "orch-wave-pattern-bundle"
recommended-tier: "fast-agent"
version: 1.0
description: "Builds a wave pattern bundle for a specific execution wave by reading the pattern-select result and resolving each required and advisory pattern to its full file body. USE FOR: assembling per-wave pattern bundles before subagent dispatch; resolving pattern IDs to full bodies via the patterns index; writing .orchestration-temp/wave-{N}-pattern-bundle.md."
anti-scope: "It does NOT select which patterns apply (that is the caller's responsibility), modify any pattern file, modify `patterns-index.json`, or take corrective action on missing patterns beyond logging a warning and continuing."
tags:
  - "utility"
  - "patterns"
  - "wave"
  - "subagent"
inputs:
  - "1-based integer wave index for which to build the bundle (required)"
  - "Complexity tier level for pattern selection — Simple, Standard, or Complex (required)"
  - "Override path for the working-state directory (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Path to written wave pattern bundle at .orchestration-temp/wave-{N}-pattern-bundle.md"
  - "Summary of pattern bundle generation"
dispatch-variant: "compact"
---

# Skill: orch-wave-pattern-bundle

<!-- SECTION 1: Identity (primacy position) -->
Reads `.orchestration-temp/pattern-select-result.md`, resolves each required and advisory pattern ID to its full file body via `ai/plugins/skf/patterns/patterns-index.json`, and writes the assembled bundle to `.orchestration-temp/wave-{N}-pattern-bundle.md` for use by subagents dispatched in that wave.

**Scope boundary**: This skill reads pattern files and writes exactly one bundle file per invocation. It does NOT select which patterns apply (that is the caller's responsibility), modify any pattern file, modify `patterns-index.json`, or take corrective action on missing patterns beyond logging a warning and continuing.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Never modify pattern files or `patterns-index.json`. WHY: patterns are shared framework assets; unintended edits corrupt all consumers.
2. Skip unreadable pattern files with a warning and continue — do not fail the entire bundle for a single missing file. WHY: a partial bundle is more useful to subagents than no bundle; the caller can investigate missing patterns separately.
3. If `pattern-select-result.md` is absent, return `{status: "skipped"}` immediately — this is not an error. WHY: pattern selection is optional for some waves; absence means no bundle is needed.
4. Write ONLY the bundle file at `.orchestration-temp/wave-{N}-pattern-bundle.md` — do not create or modify any other file. WHY: unscoped writes corrupt orchestration state outside the declared output.
5. Emit each pattern body verbatim from the source file — do not summarize, paraphrase, or truncate. WHY: subagents must receive the full authoritative pattern text to apply it correctly.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your next action complies with all rules in `<constraints>` above — especially the no-modify and verbatim-emit rules.
- Implement EXACTLY and ONLY the steps below — do not select additional patterns, reorder the bundle sections, or add commentary beyond the prescribed template.
- When a pattern ID is present in the result but its file cannot be read, log the warning inline and continue; never silently drop a pattern without a logged reason.
- If `pattern-select-result.md` exists but contains neither `required` nor `advisory` arrays, treat both as empty and write a bundle with empty sections rather than failing.
- Prioritize completeness: always attempt all pattern IDs before writing the bundle so the warning count is accurate in the return value.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `orchestration-temp-path` (default: `.orchestration-temp/`).
- Confirm `wave-number` is a positive integer; if not, halt and return `{ "status": "BLOCKED", "reason": "wave-number must be a positive integer" }`.
- Confirm `complexity-tier` is `Simple`, `Standard`, or `Complex`; if not, halt and return `{ "status": "BLOCKED", "reason": "complexity-tier must be Simple | Standard | Complex" }`.
- **State detection**: Check whether `.orchestration-temp/wave-{wave-number}-pattern-bundle.md` already exists using `file_search`. If the file exists and is non-empty → return `status: ok` with the existing path (reuse). The caller may re-invoke to force a fresh bundle. If absent → proceed with normal execution.

---

## Step 1 — Read pattern-select result
1. Attempt `read_file` on `{orchestration-temp-path}pattern-select-result.md`.
2. If the file is not found or unreadable:
   - Log: `⚠ No pattern-select result found — skipping bundle for Wave {wave-number}`
  - Return immediately: Return **skipped** — reason: no pattern-select-result.md
3. Parse the JSON. Extract:
   - `required`: array of pattern ID strings (e.g., `["PT001", "PT009"]`). Default to `[]` if absent.
   - `advisory`: array of pattern ID strings. Default to `[]` if absent.

## Step 2 — Build pattern ID set
1. Deduplicate each array independently (preserve order, remove exact-string duplicates).
2. If a pattern ID appears in both `required` and `advisory`, keep it only in `required` and remove it from `advisory`.
3. Record `required_ids` and `advisory_ids` as the resolved lists for use in subsequent steps.

## Step 3 — Resolve filenames from patterns index
1. Read `ai/plugins/skf/patterns/patterns-index.json` in full using `read_file`.
2. For each ID in `required_ids` and `advisory_ids`, locate the matching entry in the `children` array where the `name` field starts with that ID (e.g., `PT001-divide-and-conquer`).
3. Record the resolved `path` value for each matched entry.
4. For any ID with no matching `children` entry, log: `⚠ Pattern ID {ID} not found in patterns-index.json — skipping` and remove it from the active list.

## Step 4 — Read required pattern bodies

For each entry in `required_ids` (after Step 3 resolution):
1. Attempt `read_file` on the resolved path (e.g., `ai/plugins/skf/patterns/PT001-divide-and-conquer.md`).
2. If readable: store the full file content as `body_{ID}`.
3. If unreadable: log `⚠ Could not read required pattern {ID} at {path} — skipping` and remove that ID from the active required list.

## Step 5 — Read advisory pattern bodies

For each entry in `advisory_ids` (after Step 3 resolution):
1. Attempt `read_file` on the resolved path.
2. If readable: store the full file content as `body_{ID}`.
3. If unreadable: log `⚠ Could not read advisory pattern {ID} at {path} — skipping` and remove that ID from the active advisory list.

## Step 6 — Write bundle file

Write `{orchestration-temp-path}wave-{wave-number}-pattern-bundle.md` using `create_file` (or `replace_string_in_file` if the file already exists) with the following structure:

```markdown
# Wave {N} Pattern Bundle
**Generated**: {ISO 8601 timestamp or "runtime"}
**Wave**: {N}
**Complexity tier**: {complexity-tier}

## Required Patterns (binding)
### {PT-ID}: {Pattern Name}
{Full pattern body verbatim}
---

## Advisory Patterns (informational)
### {PT-ID}: {Pattern Name}
{Full pattern body verbatim}
---

## Precedence Rules
- Required patterns override advisory patterns when instructions conflict.
- Within advisory patterns, first listed takes precedence.
```

Where:
- `{N}` = `wave-number` input value.
- `{Pattern Name}` = the `description` field from the patterns-index entry (shortened to the first sentence if over 80 characters), or the filename slug if description is absent.
- Each pattern section header is `### {PT-ID}: {Pattern Name}` followed immediately by the full verbatim body.
- If the active required list is empty, write `_No required patterns for this wave._` under the `## Required Patterns` heading.
- If the active advisory list is empty, write `_No advisory patterns for this wave._` under the `## Advisory Patterns` heading.
- The `---` separator appears after each pattern body (including the last one in each section).

## Step 7 — Return success

Emit the success line defined in `<output_format>`, substituting `{R}` and `{A}` with the actual counts of included required and advisory patterns.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Use in Steps 1, 3, 4, and 5 to read JSON and pattern markdown files. Prefer a single full read per file over multiple partial reads.
- **file_search**: Permitted as a fallback in Step 3 to locate a pattern file by glob when the index path is ambiguous (e.g., `ai/plugins/skf/patterns/{PT-ID}-*.md`).
- **create_file**: Use in Step 6 to write the bundle file when it does not already exist.
- **replace_string_in_file / multi_replace_string_in_file**: Use in Step 6 only if the bundle file already exists and must be overwritten by replacing its entire content.
- **grep_search**: Permitted in Step 3 as a fallback to locate a pattern ID in `patterns-index.json` when direct JSON parsing is unreliable.
- **run_in_terminal**: Prohibited — this skill performs no command execution.
- **vscode_askQuestions**: Prohibited — this skill is stateless and does not interact with the user.
- Pattern files and `patterns-index.json` must never be passed to any write tool.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|---|---|
| status | ok \| skipped \| blocked |
| skill_id | orch-wave-pattern-bundle |
| wave | N |
| step | 5.5 |
| output_path | .orchestration-temp/wave-{N}-pattern-bundle.md |
| summary | one-line summary of pattern bundle generation |

**Success:**
```
✓ Wave {N} pattern bundle written → {orchestration-temp-path}wave-{N}-pattern-bundle.md ({R} required, {A} advisory patterns)
```

**Skipped (no pattern-select-result.md):**
**status:** skipped — reason: no pattern-select-result.md

**Blocked (invalid inputs):**
**status:** BLOCKED — reason: {reason text}

**Warnings** (emitted inline before the final return, one per skipped pattern):
```
⚠ {reason} — skipping
```

Rules:
- The success line is the final output; all warning lines precede it.
- Do not emit a success line when status is `skipped` or `BLOCKED`.
- The bundle file path in the success line must match the actual written path exactly.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: wave_number=2, complexity_tier="Standard"; pattern-select-result.md contains required=["PT001"] and advisory=["PT009"].
Expected output: PT001 and PT009 resolved from patterns-index.json; both pattern bodies read verbatim; `.orchestration-temp/wave-{N}-pattern-bundle.md` written; returns "✓ Wave 2 pattern bundle written → .orchestration-temp/wave-{N}-pattern-bundle.md (1 required, 1 advisory patterns)".
</example>

<example>
Input: wave_number=1; pattern-select-result.md is absent from .orchestration-temp/.
Expected output: Returns status: skipped — reason: no pattern-select-result.md. No file is read or written beyond the initial check.
</example>

<example type="counter">
Input: wave_number=0 (invalid — must be a positive integer).
Expected behavior: Returns BLOCKED — "wave-number must be a positive integer". No file is read or written.
</example>
</examples>


