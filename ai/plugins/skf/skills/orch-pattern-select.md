---
id: "orch-pattern-select"
recommended-tier: "fast-agent"
version: 1.0
description: "Selects applicable behavioral patterns for a given task from patterns-index.json. USE FOR: pattern selection during orchestrator intake; determining required vs advisory patterns before dispatch; resolving pattern conflicts."
anti-scope: "It does NOT load pattern file bodies, execute any task, or write any files."
tags:
  - "utility"
  - "patterns"
  - "selection"
  - "signals"
inputs:
  - "Task complexity tier — Simple, Standard, or Complex (required)"
  - "Array of signal names from the pattern-tags.md vocabulary (required)"
  - "Free-form description of the task (optional)"
  - "Override path for patterns-index.json (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok or blocked"
  - "Pattern IDs that must be included"
  - "Pattern IDs that should be included"
  - "Conflict resolutions and auto-pairs applied"
dispatch-variant: "compact"
---


# Skill: orch-pattern-select

<!-- SECTION 1: Identity (primacy position) -->
Selects the appropriate set of behavioral patterns for a given task by matching task signals against `ai/plugins/skf/patterns/patterns-index.json`. Returns a structured selection result with required patterns, advisory patterns, auto-paired dependencies, and resolved conflicts.

**Scope boundary**: This skill reads `patterns-index.json` and returns a pattern selection result. It does NOT load pattern file bodies, execute any task, or write any files. Pattern body loading (for wave bundles) is the orchestrator's responsibility.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Read `ai/plugins/skf/patterns/patterns-index.json` before performing any matching — never infer pattern availability from memory. WHY: pattern catalog evolves; stale assumptions produce wrong selections.
2. Return only pattern IDs that exist in the index. WHY: phantom pattern IDs break dispatch manifests and wave bundles.
3. Apply all conflict resolution rules before returning — never return two patterns from the same exclusion-group. WHY: conflicting patterns in the same dispatch create contradictory instructions.
4. Auto-pair: if PT025 (Self-Correction) is selected, PT009 (Test Before Trust) MUST also be selected as required. WHY: PT025 without PT009 degrades into rationalization rather than verified correction.
5. Verify all referenced pattern IDs exist in patterns-index.json in the preflight step. WHY: broken references in the manifest template cause subagent failures.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — return a pattern selection, nothing more.
- If patterns-index.json is unreadable: return `{"status": "blocked", "reason": "patterns-index.json unreadable", "skill": "orch-pattern-select"}`.
- Record conflict resolutions explicitly in `resolved-conflicts` so the orchestrator can audit the selection.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

1. Read `patterns-index.json` (at the provided path, or the default).
2. Confirm `complexity-tier` and `task-signals` are present.
3. Validate that all signals in `task-signals` appear in the pattern-tags signal vocabulary.

> **If any preflight check fails**: Return **BLOCKED** — reason: {specific failure}

## Done conditions

Output is done when:
- `required` array contains all patterns where signal overlap ≥ 2 and complexity-tier is compatible.
- `advisory` array contains all patterns where signal overlap ≥ 1 and complexity-tier is compatible, excluding those already in `required`.
- `resolved-conflicts` documents every case where two patterns from the same `exclusion-group` matched and one was dropped.
- All `requires` dependencies are satisfied (PT025 → PT009 auto-pair applied).
- All pattern IDs in `required` and `advisory` exist in patterns-index.json.

## Step 1 — Match Patterns to Task Signals

For each pattern entry in `patterns-index.json`:

1. **Tier filter**: Check `tier` field.
   - If `tier: "all"` → eligible for all complexity tiers. Continue.
   - If `tier` names specific agent types (e.g., `"standard-agent, large-context-agent"`) → eligible for `Standard` and `Complex` tiers only. Skip for `Simple`.
2. **Signal overlap**: Count how many of the pattern's `signals` appear in the caller's `task-signals`.
   - Overlap ≥ 2 → candidate for **required**.
   - Overlap = 1 → candidate for **advisory**.
   - Overlap = 0 → exclude.
3. **Classification threshold adjustment by complexity-tier**:
   - `Simple`: lower threshold — overlap ≥ 1 can be considered required if the pattern category is `output-format` or `context-management`.
   - `Complex`: raise advisory bar — overlap ≥ 2 required to enter advisory list (reduce noise on complex tasks).

Build two intermediate lists: `required-candidates` and `advisory-candidates`.

## Step 2 — Resolve Exclusion-Group Conflicts

For each `exclusion-group` that appears in the candidate lists:

1. Identify all patterns in that group present across `required-candidates` + `advisory-candidates`.
2. If more than one pattern from the same group is selected, apply the following resolution order:
   a. If one has higher signal overlap than the others → keep the higher-overlap pattern.
   b. If overlap is equal → prefer the pattern with more specific signal names (exact match over broad match).
   c. If still tied → keep the pattern listed first in `patterns-index.json` (stable ordering).
   d. Demote the losing pattern: if it was in `required-candidates` → move to `advisory-candidates`; if in `advisory-candidates` → drop entirely.
3. Record each resolution in the output `resolved-conflicts` array:
   ```
   { "conflict": "<group>", "kept": "<PT-ID>", "dropped": "<PT-ID>", "reason": "<resolution rule applied>" }
   ```

## Step 3 — Apply Dependency Auto-Pairs

After conflict resolution:

1. Check every pattern in `required-candidates` for a `requires` field.
2. If `requires` is set (e.g., `requires: PT009`):
   - If the required dependency is already in `required-candidates` → no action needed.
   - If the required dependency is only in `advisory-candidates` → promote it to `required-candidates`.
   - If the required dependency is absent from both lists → add it to `required-candidates` and note why in `resolved-conflicts`:
     ```
     { "conflict": "dependency", "kept": "<dependency-PT-ID>", "dropped": null, "reason": "auto-paired: <source-PT-ID> requires <dependency-PT-ID>" }
     ```
3. Apply the same check for `advisory-candidates` — promote dependencies to advisory if missing.

## Step 4 — Final Deduplication

1. Ensure no pattern ID appears in both `required` and `advisory` — if it does, keep it in `required` only.
2. Ensure all pattern IDs in the output exist in `patterns-index.json`. If a resolved ID is missing, log a warning and remove it from the output:
   ```
   { "warning": "pattern <PT-ID> not found in patterns-index.json — removed from output" }
   ```

Produce the output defined in `<output_format>`.

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Use in Preflight to load patterns-index.json. Read in a single call; prefer large reads over fragmented reads.
- **file_search / grep_search / semantic_search**: Permitted for loading skill context only. Do not use to substitute for patterns-index.json reading.
- **create_file / replace_string_in_file / edit**: Prohibited — this skill never writes files.
- **run_in_terminal**: Prohibited — this skill performs no command execution.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` |
| complexity-tier | `Simple` \| `Standard` \| `Complex` |
| task-signals-matched | comma-separated list of matched signals |
| required | comma-separated list of required PT-IDs |
| advisory | comma-separated list of advisory PT-IDs |
| resolved-conflicts | description of any resolved conflicts |
| warnings | comma-separated list of warnings |
</output_format>

<!-- SECTION 7: Examples -->
<examples>

<example>
Input: Complexity tier Simple, task signals: [implementation, code-quality]. patterns-index.json is readable.

Expected output (simplified):
```json
{
  "status": "ok",
  "complexity-tier": "Simple",
  "task-signals-matched": ["implementation", "code-quality"],
  "required": ["PT001", "PT003"],
  "advisory": ["PT010"],
  "resolved-conflicts": [],
  "warnings": []
}
```
</example>

<example type="positive" title="Standard task — conflict resolution applied">
Input: Complexity tier Standard, task signals: [quality-review, compliance, implementation-work], patterns-index.json readable. Two patterns in the same exclusion-group both match: PT005 (overlap 2) and PT012 (overlap 1).

Expected output (simplified):
```json
{
  "status": "ok",
  "complexity-tier": "Standard",
  "task-signals-matched": ["quality-review", "compliance", "implementation-work"],
  "required": ["PT005", "PT003"],
  "advisory": ["PT011"],
  "resolved-conflicts": [
    { "conflict": "format-group", "kept": "PT005", "dropped": "PT012", "reason": "PT005 had higher signal overlap (2 vs 1)" }
  ],
  "warnings": []
}
```
</example>

<example type="counter">
Input: patterns-index.json is missing or unreadable.

Wrong: Attempt to infer pattern catalog from memory or hardcoded defaults.

Correct: Return blocked status immediately:
```json
{ "status": "blocked", "reason": "patterns-index.json unreadable", "skill": "orch-pattern-select" }
```
</example>

</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>

</workflow>
