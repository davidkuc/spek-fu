---
id: "orch-skill-resolve"
recommended-tier: "fast-agent"
version: 1.0
description: "Analyzes accumulated orchestration context (intake, traversal, knowledge consultation) and selects the most appropriate skills from skills-index.json for the current problem. Produces a curated skill inventory with selection rationale. USE FOR: Phase 2 before plan generation — resolving which skills are needed based on what was learned during intake."
anti-scope: "It does NOT select skills without reading the gathered context. It does NOT return all skills from the index indiscriminately. It does NOT execute skills, validate skill output, or modify source files."
tags:
  - "utility"
  - "skill-selection"
  - "planning"
  - "context-driven"
inputs:
  - "Path to intake context file (required) — typically .orchestration-temp/intake-context.md"
  - "Path to traversal results or navigation result (optional) — if produced during intake"
  - "Path to knowledge consultation output (optional) — if produced during intake"
  - "Request summary or free-form problem description (optional, supplements intake context)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Curated skill inventory written to .orchestration-temp/skill-inventory.md"
  - "Selection rationale for each chosen skill"
  - "Count of selected skills"
dispatch-variant: "compact"
---

# Skill: orch-skill-resolve

<!-- SECTION 1: Identity (primacy position) -->
Active skill-selection utility. Takes accumulated orchestration context and selects the most appropriate skills from `skills-index.json` for the problem at hand. Bridges the intake/research phase and the planning phase. Produces a curated `.orchestration-temp/skill-inventory.md` with a markdown table of selected skills and a `selection_rationale` section explaining why each skill was chosen.

**Scope boundary**: reads context artifacts and the skills index; reasons over them; writes the curated inventory. Does NOT return all skills. Does NOT execute skills. Does NOT modify source files.

<!-- SECTION 2: Constraints (non-negotiable) -->
<constraints>
IMPORTANT: These rules override all other instructions.
1. NEVER return all skills from the index indiscriminately — always select based on the problem context. WHY: a curated selection is the entire value of this skill; a full dump defeats the purpose.
2. NEVER read individual skill files — only read skills-index.json for the catalog. WHY: pure selection utility.
3. NEVER skip reading the intake context — it is the primary input for selection reasoning. WHY: selection without context is arbitrary.
4. If no plugin skill catalog is readable, return blocked immediately. WHY: cannot select without a catalog.
5. Include a `selection_rationale` entry for every selected skill explaining why it was chosen. WHY: rationale enables the orchestrator to validate selections and pass them to orch-orchestration-plan with confidence.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your result complies with all rules in `<constraints>` above.
- Read all provided context files before beginning skill selection.
- Reason explicitly: for each candidate skill, decide include or exclude based on whether the problem requires it.
- Prefer precision over coverage — select fewer highly relevant skills over many loosely relevant ones.
- If a needed skill is missing from the index, surface it as a gap rather than substituting.
- Always verify output markdown is well-formed and renders correctly before reporting success.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Idempotency Check

Before reading any context files or the skills catalog, check whether a prior skill inventory already exists:

- **if-exists** (prior inventory detected): `.orchestration-temp/skill-inventory.md` exists and is non-empty → return the prior inventory and ask the caller whether to refresh (re-run selection) or reuse the existing result.
- **if-empty** (no prior state): the inventory file does not exist → proceed normally from Step 1.
- **if-complete** (inventory exists and context is unchanged): the file exists, is non-empty, and was produced from the same intake context → return the existing inventory with a note; exit without re-selecting unless the caller explicitly requests a refresh.

## Preflight

- Confirm `intake-context-path` is provided and readable. If absent, return blocked with reason: "intake-context-path missing".
- Confirm `ai/plugins/plugins-index.json` exists and is readable. If absent or malformed, return blocked with reason: "plugins-index.json missing or malformed".

## Step 1 — Read gathered context

Use `read_file` to read the intake context from `intake-context-path`.

- If the file cannot be read: return blocked status with reason.
- Extract key fields: `request`, `components_involved`, `work_type`, `problem_statement` (if present).

If `traversal-result-path` is provided:
- Use `read_file` to read the traversal results.
- Extract any indices queried, code locations discovered, or framework components identified.

If `knowledge-result-path` is provided:
- Use `read_file` to read the knowledge consultation output.
- Extract lessons learned, constraints surfaced, or architectural guidance provided.

**Synthesize a consolidated problem statement**: What is the request? What components are involved? What work type is it (impl, qa, spec, gov, util, mixed)?

## Step 2 — Read the skill catalog

1. Use `read_file` to read `ai/plugins/plugins-index.json` and collect all plugin entries from its `children` array.
2. For each plugin entry, follow its `index` pointer to read the plugin's root index (e.g. `ai/plugins/skf/skf-index.json`); within that index locate the child whose `name` is `"skills"` and read its `index` field to get the path to the plugin's `skills-index.json`.
3. Use `read_file` to read each `skills-index.json` and collect its `children` array.
4. Merge all collected `children` arrays into a single unified skill catalog. Note the source plugin name in the selection rationale for any skill selected from a non-skf plugin.
5. If no plugin's `skills-index.json` could be read: return blocked status with reason: "no plugin skill catalog is readable".
- Confirm that each entry in the merged catalog contains `id`, `description`, `anti-scope`, `dispatch-variant` fields.
6. **Load the ignore list**: Use `read_file` to read `ai/plugins/skf/skills/config.json`. Extract the `skillSelection.ignoredSkills` array. If the file cannot be read or the key is absent, treat the ignore list as empty and continue. Remove any skill from the merged catalog whose `path` field exactly matches an entry in `ignoredSkills`. Log the count of ignored skills in the output summary.

## Step 3 — Select relevant skills

For each skill entry in the `children` array, reason:
- Does this problem require this skill's function? (match description against problem statement)
- Is this skill in scope for the work type identified in Step 1?
- If yes: include it. Record a one-sentence rationale.
- If no: exclude it. No record needed.

**Group reasoning by work type**:

- **Implementation work** → include `impl-*` skills matching the specific implementation pattern (impl-implement, impl-implement, etc.)
- **Governance/docs** → include `gov-*` skills for governance tier updates or documentation changes
- **Orchestration utilities** (always include core ones needed by orchestration flow): `orch-orchestration-plan`, `orch-wave-decompose`, `orch-wave-verification`, `orch-wave-pattern-bundle`, `orch-artifact-coherence-check`, `orch-pre-execution-validation`, `orch-resume-detect`, `orch-orchestration-summary`
- **Meta/index management** → include only if the problem involves framework changes

## Step 4 — Build and write the inventory

Construct markdown output with the following structure:
1. A summary section with problem context, catalog size, and count
2. A skill inventory table with columns: ID | Path | Description | Recommended Tier | Dispatch Variant | Anti-scope
3. Detailed skill sections for each selected skill with: ID, Path, Description, Anti-scope, Recommended Tier, Dispatch variant, Inputs, Outputs
4. A selection rationale section explaining why each skill was chosen

Format:
```markdown
# Skill Inventory

Problem context: {synthesis from Step 1}  
Catalog size: {total skills}  
Ignored: {count} skills  
Selected: {count} skills  

| ID | Path | Description | Recommended Tier | Dispatch Variant | Anti-scope |
|----|------|-------------|-----|-----------------|------------|
| {id} | {path} | {description} | {recommended-tier} | {dispatch-variant} | {anti-scope} |

## Selection Rationale

- **{skill-id}**: {one-sentence reason}

## {skill-id}

- **ID**: {id}
- **Path**: {path}
- **Description**: {description}
- **Anti-scope**: {anti-scope}
- **Recommended Tier**: {recommended-tier}
- **Dispatch variant**: {dispatch-variant}
- **Inputs**: {inputs}
- **Outputs**: {outputs}
```

Write to `.orchestration-temp/skill-inventory.md` using `create_file`.

Verify file was written. Ensure markdown is well-formed and renders correctly.

Return the report in the format defined in `<output_format>`.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Steps 1 and 2 — context files and skills-index.json.
- **create_file**: Step 4 only — write .orchestration-temp/skill-inventory.md.
- **replace_string_in_file**: Only if skill-inventory.md already exists and needs updating.
- **run_in_terminal**: Prohibited.
- **All search tools** (file_search, grep_search, semantic_search): Prohibited.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
**Human-readable block:**
```
Skill selection complete:
  Problem context: {one-line synthesis from Step 1}
  Catalog size: {total skills in index}
  Ignored: {count} skills (from config ignore list)
  Selected: {count} skills
  Output: .orchestration-temp/skill-inventory.md
```

**Markdown block** (same structure as written to file):
```markdown
# Skill Inventory

Problem context: {synthesis from Step 1}  
Catalog size: {total skills}  
Ignored: {count} skills  
Selected: {count} skills  

| ID | Path | Description | Recommended Tier | Dispatch Variant | Anti-scope |
|----|------|-------------|------------------|-----------​---|------------|
| {id} | {path} | {description} | {recommended-tier} | {dispatch-variant} | {anti-scope} |

## Selection Rationale

- **{skill-id}**: {one-sentence reason}

## {skill-id}

- **ID**: {id}
- **Path**: {path}
- **Description**: {description}
- **Anti-scope**: {anti-scope}
- **Recommended Tier**: {recommended-tier}
- **Dispatch variant**: {dispatch-variant}
- **Inputs**: {inputs}
- **Outputs**: {outputs}
```

**Blocked report format (markdown):**
```markdown
# Skill Inventory

**Status**: Blocked  
**Reason**: {reason}  
**Count**: 0  
**Output path**: .orchestration-temp/skill-inventory.md
```

Format invariants:
- Skills table is ordered by `id` (ascending, lexicographic).
- Table contains exactly the 6 columns listed.
- `count` reflects the actual number of selected skills.
- Every selected skill has a corresponding entry in `selection_rationale`.
- Markdown is well-formed and renders correctly before reporting success.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example name="positive">
Input:
- intake-context-path: `.orchestration-temp/intake-context.md` containing:
  ```json
  {
    "request": "Implement three features from iteration 005: user auth, payment processing, and dashboard widgets",
    "work_type": "impl",
    "components_involved": ["auth-service", "payment-module", "ui-dashboard"],
    "problem_statement": "Requires coordinated implementation across multiple modules with testing and governance updates"
  }
  ```
- traversal-result-path: branch-specific traversal report path from the calling context (processed for architectural insights)
- knowledge-result-path: path to the retained knowledge consultation artifact (lessons from similar prior work)
- skills-index.json contains 24 total skills

Process:
1. Synthesize: "Multi-module implementation work requiring implementation, orchestration, and governance skills"
2. Read skills-index.json (24 skills)
3. Select skills:
   - Include `impl-implement` (core implementation executor)
   - Include `orch-final-orchestration-validation` (post-implementation validation)
   - Include `orch-wave-verification` (wave-level verification)
   - Include `gov-update` (update governance tier with changes)
   - Include core utility skills: `orch-orchestration-plan`, `orch-wave-decompose`, `orch-wave-verification`, `orch-artifact-coherence-check`, `orch-pre-execution-validation`
   - Exclude all meta-* skills (no framework changes)
4. Write inventory with ~8-10 selected skills
5. Return:
```
Skill selection complete:
  Problem context: Multi-module implementation work with verification and governance coordination
  Catalog size: 24
  Selected: 9 skills
  Output: .orchestration-temp/skill-inventory.md
```

Markdown output file:
```markdown
# Skill Inventory

Problem context: Multi-module implementation work with verification and governance coordination  
Catalog size: 24  
Selected: 9 skills  

| ID | Path | Description | Recommended Tier | Dispatch Variant | Anti-scope |
|----|------|-------------|------------------|-----------\u200b---|------------|
| gov-update | ai/plugins/skf/skills/gov-update.md | Applies targeted changes to a governance tier with per-change user approval | fast-agent | full | It does NOT perform analysis, modify source code, or touch iteration in-progress files |
| impl-implement | ai/plugins/skf/skills/impl-implement.md | ... | fast-agent | full | ... |
| ... | ... | ... | ... | ... | ... |

## Selection Rationale

- **impl-implement**: Core executor for iterative implementation tasks
- **orch-final-orchestration-validation**: Post-implementation validation of produced artifacts
- **orch-wave-verification**: Verification that each wave matched the approved plan
- **gov-update**: Governance tier updates after implementation
- **orch-orchestration-plan**: Orchestration utility always needed for planning phase
- ... (6 more rationales)

## gov-update

- **ID**: gov-update
- **Path**: ai/plugins/skf/skills/gov-update.md
- **Description**: Applies targeted changes to a governance tier with per-change user approval
- **Anti-scope**: It does NOT perform analysis, modify source code, or touch iteration in-progress files
- **Recommended Tier**: fast-agent
- **Dispatch variant**: full
- **Inputs**: Target governance tier, Analysis report
- **Outputs**: Count of changes applied, Update summary

## ... (11 more detailed skill sections)
```
</example>

<example name="counter">
Input: Orchestrator calls orch-skill-resolve without providing intake-context-path (only request-summary provided).

Expected behavior:
1. Step 1 preflight: intake-context-path is missing.
2. Return blocked immediately (markdown format):
```markdown
# Skill Inventory

**Status**: Blocked  
**Reason**: intake-context-path missing  
**Count**: 0  
**Output path**: .orchestration-temp/skill-inventory.md
```
3. Report to orchestrator: "Skill selection blocked — intake context required."

**Why**: Selection without gathered context is arbitrary and defeats the skill's purpose.
</example>

<example name="counter2">
Input: intake-context-path points to valid intake-context.md. skills-index.json is missing or malformed.

Expected behavior:
1. Step 1: reads intake context successfully.
2. Step 2 preflight: attempts to read skills-index.json, file not found or invalid JSON.
3. Return blocked (markdown format):
```markdown
# Skill Inventory

**Status**: Blocked  
**Reason**: skills-index.json missing or malformed  
**Count**: 0  
**Output path**: .orchestration-temp/skill-inventory.md
```
}
```

**Why**: Cannot select skills without a catalog.
</example>
</examples>

<!-- SECTION 8: Reminders -->
<reminders>
</reminders>
