---
id: "orch-skill-resolve"
recommended-tier: "fast-agent"
version: 1.0
description: "Analyzes accumulated orchestration context (intake, traversal, knowledge consultation) and selects the most appropriate skills from skills-index.json. Produces a curated inline skill inventory with selection rationale. USE FOR: Phase 2 before plan generation — resolving which skills are needed based on what was learned during intake."
anti-scope: "It does NOT select skills without reading the gathered context. It does NOT return all skills from the index indiscriminately. It does NOT execute skills, validate skill output, or modify source files."
tags:
  - "utility"
  - "skill-selection"
  - "planning"
  - "context-driven"
inputs:
  - "Structured intake context object (required)"
  - "Structured traversal summary or navigation result (optional)"
  - "Structured knowledge consultation output (optional)"
  - "Request summary or free-form problem description (optional, supplements intake context)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Curated inline skill inventory"
  - "Selection rationale for each chosen skill"
  - "Count of selected skills"
dispatch-variant: "compact"
---

# Skill: orch-skill-resolve

<!-- SECTION 1: Identity (primacy position) -->
Active skill-selection utility. Takes accumulated orchestration context and selects the most appropriate skills from `skills-index.json` for the problem at hand. Bridges the intake/research phase and the planning phase. Produces a curated inline skill inventory with a markdown table of selected skills and a `selection_rationale` section explaining why each skill was chosen.

**Scope boundary**: reads caller-supplied structured context and the skills catalog; reasons over them; returns the curated inventory inline. Does NOT return all skills. Does NOT execute skills. Does NOT modify source files.

<!-- SECTION 2: Constraints (non-negotiable) -->
<constraints>
IMPORTANT: These rules override all other instructions.
1. NEVER return all skills from the catalog indiscriminately — always select based on the problem context. WHY: a curated selection is the entire value of this skill; a full dump defeats the purpose.
2. NEVER read individual skill files or skills-index.json directly — always obtain the catalog by running `gather-skills.py`. WHY: the script handles merging, deduplication, and ignore-list filtering in one step.
3. NEVER skip reading the intake context — it is the primary input for selection reasoning. WHY: selection without context is arbitrary.
4. If `gather-skills.py` fails or returns zero available skills, return blocked immediately. WHY: cannot select without a catalog.
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

## Preflight

- Confirm `intake-context` is provided. If absent, return blocked with reason: "intake-context missing".

## Step 1 — Read gathered context

Use the caller-provided structured inputs directly.

- Extract key fields from `intake-context`: `request`, `components_involved`, `work_type`, `problem_statement`, `complexity-tier` (if present).

If `traversal-result` is provided:
- Extract any indices queried, code locations discovered, or framework components identified.

If `knowledge-result` is provided:
- Extract lessons learned, constraints surfaced, or architectural guidance provided.

**Synthesize a consolidated problem statement**: What is the request? What components are involved? What work type is it (impl, qa, spec, gov, util, mixed)?

## Step 2 — Read the skill catalog

Run the gather-skills script from the repo root:

```
python3 ai/scripts/python/gather-skills.py --format json
```

Use `run_in_terminal` with the command above.

- If the script exits with a non-zero code or produces no parseable output: return blocked status with reason: "skill catalog unavailable — gather-skills.py failed".
- Parse the JSON output. The result has the shape:
  ```json
  { "total": N, "ignored": N, "available": N, "skills": [...] }
  ```
- Use `result.skills` as the unified skill catalog — it is already merged across all plugins and filtered against the ignore list from `ai/plugins/skf/skills/config.json`.
- If `result.available` is 0: return blocked status with reason: "no plugin skill catalog is readable".
- Log `result.total`, `result.ignored`, and `result.available` in the output summary.
- Confirm that each entry in the catalog contains `id`, `description`, `anti-scope`, `dispatch-variant` fields.

## Step 3 — Select relevant skills

For each skill entry in the `children` array, reason:
- Does this problem require this skill's function? (match description against problem statement)
- Is this skill in scope for the work type identified in Step 1?
- If yes: include it. Record a one-sentence rationale.
- If no: exclude it. No record needed.

**Group reasoning by work type**:

- **Implementation work** → include `impl-*` skills matching the specific implementation pattern
- **Governance/docs** → include `gov-*` skills for governance tier updates or documentation changes
- **Meta/index management** → include only if the problem involves framework changes

Note: orchestration utility skills (`orch-*`) are excluded from the catalog by the ignore list; do not attempt to select them.

## Step 4 — Build and return the inventory

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

Return the report in the format defined in `<output_format>`.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **run_in_terminal**: Step 2 only — run `python3 ai/scripts/python/gather-skills.py --format json` to obtain the pre-filtered skill catalog.
- No state-writing tools are permitted for this skill.
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
  Output: inline skill-inventory state
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
**Output path**: none
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
- intake-context: structured object containing:
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
2. Run `python3 ai/scripts/python/gather-skills.py --format json`; parse JSON output (e.g. total=30, ignored=23, available=7)
3. Select skills from the 7 available:
   - Include `impl-implement` (core implementation executor)
   - Include `gov-update` (update governance tier with changes)
   - Exclude all `meta-*` skills (no framework changes)
   - Note: `orch-*` skills are pre-filtered out by the script; do not attempt to select them
4. Write inventory with selected skills
5. Return:
```
Skill selection complete:
  Problem context: Multi-module implementation work with verification and governance coordination
  Catalog size: 7
  Ignored: 23 skills (pre-filtered by gather-skills.py)
  Selected: 2 skills
  Output: inline skill-inventory state
```

Markdown output file:
```markdown
# Skill Inventory

Problem context: Multi-module implementation work with verification and governance coordination  
Catalog size: 7  
Ignored: 23 (pre-filtered by gather-skills.py)  
Selected: 2 skills  

| ID | Path | Description | Recommended Tier | Dispatch Variant | Anti-scope |
|----|------|-------------|------------------|-----------\u200b---|------------|
| gov-update | ai/plugins/skf/skills/gov-update.md | Applies targeted changes to a governance tier with per-change user approval | fast-agent | full | It does NOT perform analysis, modify source code, or touch iteration in-progress files |
| impl-implement | ai/plugins/skf/skills/impl-implement.md | ... | fast-agent | full | ... |

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
Input: Orchestrator calls orch-skill-resolve without providing intake-context (only request-summary provided).

Expected behavior:
1. Step 1 preflight: intake-context is missing.
2. Return blocked immediately (markdown format):
```markdown
# Skill Inventory

**Status**: Blocked  
**Reason**: intake-context missing  
**Count**: 0  
**Output path**: none
```
3. Report to orchestrator: "Skill selection blocked — intake context required."

**Why**: Selection without gathered context is arbitrary and defeats the skill's purpose.
</example>

<example name="counter2">
Input: intake-context contains valid request data. `gather-skills.py` fails (plugins-index.json is missing or malformed).

Expected behavior:
1. Step 1: reads intake context successfully.
2. Step 2: runs `python3 ai/scripts/python/gather-skills.py --format json`; script exits with code 1.
3. Return blocked (markdown format):
```markdown
# Skill Inventory

**Status**: Blocked  
**Reason**: skill catalog unavailable — gather-skills.py failed  
**Count**: 0  
**Output path**: none
```

**Why**: Cannot select skills without a catalog.
</example>
</examples>

<!-- SECTION 8: Reminders -->
<reminders>
</reminders>
