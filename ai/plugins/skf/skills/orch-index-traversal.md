---
id: "orch-index-traversal"
recommended-tier: "fast-agent"
version: 1.0
description: "Traverses the framework index hierarchy based on a free-form query, selects only the most relevant files and folders, and returns a Navigation Result report. USE FOR: discovering which framework resources are relevant to a request; locating skills, agents, flows, commands, constitution files, projects, or iterations."
anti-scope: "It does NOT read resolved resource files, modify source or index files, or ask the user questions."
tags:
  - "utility"
  - "index"
  - "navigation"
  - "discovery"
inputs:
  - "Free-form text describing what the caller is looking for (required)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
  - "Optional spill output path for the traversal report when inline compaction is insufficient"
outputs:
  - "Navigation result status: ok, blocked, or fail"
  - "One-line summary of navigation result"
  - "Optional spill path for the traversal report"
dispatch-variant: "compact"
---


# Skill: orch-index-traversal

<!-- SECTION 1: Identity (primacy position) -->
Traverses the Spek-Fu index hierarchy based on a free-form query. Starts at `skf-root-index.json`, follows index pointers through intermediate indexes using progressive disclosure, evaluates entries for relevance to the query at each level, and returns only the most relevant files and folders as a Navigation Result report.

**Scope boundary**: This skill traverses indexes and reports paths only. It does NOT read resolved resource files, modify source or index files, or ask the user questions. It returns the Navigation Result report inline for downstream orchestration use and may spill under `reports/orchestration-spill/` only when compaction is insufficient.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Start traversal from `skf-root-index.json`; do not hardcode resource paths outside the index chain. WHY: hardcoded paths break when framework structure changes; index traversal is the SSOT.
2. Use progressive disclosure — stop descending a branch once one or more high-relevance entries are confirmed or the full index level has been inspected without a match; do not load every sub-index speculatively. WHY: loading unnecessary branches wastes tokens.
3. When no relevant resource is found, report the lookup path taken and the failure — do not guess paths. WHY: guessed paths silently reference non-existent files, causing downstream failures.
4. Keep traversal read-only with respect to index files — do not write to, modify, or create any index file. WHY: index mutations belong to the index management skill, not a lookup utility.
5. Return only results that are relevant to the query — do not return unfiltered index listings unless the query is explicitly a broad listing request. WHY: returning every file defeats the purpose of relevance selection.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — traverse indexes, pick relevant entries, return a report. Nothing more.
- Follow the index depth map strictly; do not skip levels or read terminal resource files during traversal.
- Evaluate relevance at each index level before deciding whether to descend into a branch.
- When the query signals multiple branches, traverse all relevant ones and merge results.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Idempotency Check

No temp-state reuse applies in the inline-only contract. Always traverse from source indexes for the current query.

## Preflight

- Confirm the query is present and non-empty before reading any indexes.
- Start from `skf-root-index.json`; do not jump directly to terminal resources.
- Limit traversal to the branches actually signaled by the query.

## Index depth map

```
skf-root-index.json (Level 0)
└─ ai/ai-index.json (Level 1)
   └─ ai/plugins/plugins-index.json (Level 2)
      └─ ai/plugins/{name}/{name}-index.json (Level 3, one per plugin)
         ├─ skills/skills-index.json (Level 4)       → skills/{name}.md (Terminal)
         ├─ templates/templates-index.json (Level 4)  → templates/{name}.md (Terminal)
         ├─ patterns/ (Level 4, patterns-index.json)  → patterns/{name}.md (Terminal) [skf only]
         ├─ runbooks/ (Level 4, no sub-index — flat files) [skf only]
         └─ knowledge/ (Level 4, no sub-index — flat files)
```

> Note: `runbooks/` and `patterns/` are skf-specific sub-folders; custom plugins may have different sub-folder sets.

Constitution, project, and report resources branch from Level 0 directly:
```
skf-root-index.json (Level 0)
├─ constitution/constitution.md (Terminal)
├─ project/project.md (Terminal)
└─ reports/ (direct folder scan for report files)
```

## Step 1 — Read root index and identify relevant branches

Read `skf-root-index.json`. Analyze the query to determine which top-level branches are likely to contain relevant resources:

- Signals pointing to framework resources (skills, agents, flows, commands, templates): follow the `ai/` child.
- Signals pointing to governance, constraints, or principles: follow the `constitution/` child.
- Signals pointing to project requirements or technical specs: follow the `project/` child.
- Signals pointing to generated analysis outputs or prior reports: follow the `reports/` child.

If the query signals more than one branch, traverse all relevant branches and merge results.

**Script**: Use `resolve-skf-index-chain.py` to follow the index chain from root: `python3 ai/scripts/python/resolve-skf-index-chain.py --root-index skf-root-index.json --json`

> **If `skf-root-index.json` cannot be read**: Stop immediately and return a no-match result — set `Status: NO RELEVANT RESOURCES FOUND`, `Index path searched: skf-root-index.json`, and `Last index read: skf-root-index.json (unreadable)`. Do not guess or hardcode downstream paths.

## Step 2 — Traverse to the relevant domain index

For each relevant branch identified in Step 1:

- **`ai/` branch**: Read `ai/ai-index.json` → find the `plugins/` child → read `ai/plugins/plugins-index.json` → iterate over all plugin children; for each plugin read its root index (`ai/plugins/{name}/{name}-index.json`). Within each plugin index, identify only sub-folders relevant to the query and read only those.
- **`constitution/`**: Read `constitution/constitution.md` directly.
- **`project/`**: Read `project/project.md` directly.
- **`reports/`**: Inspect the `reports/` folder directly and evaluate report filenames for relevance.

**Progressive disclosure**: within each index, read only entries whose names or descriptions are relevant to the query. Do not follow all children.

**Scripts**: Use these tools for Step 2 operations:
- Extract children from a single index: `python3 ai/scripts/python/get-skf-index-children.py --index-path ai/ai-index.json --json`
- Verify target paths exist: `python3 ai/scripts/python/validate-skf-index-targets.py --input-file children.json --json`
- Pre-filter files by frontmatter fields (first pass): `python3 ai/scripts/python/search-by-frontmatter.py --root ai/plugins/skf/ --group <group> --format json`

> **If any intermediate index file is missing or unreadable**: Record the missing path in the traversal chain, stop that branch, and continue with any remaining branches. If all branches fail, return a no-match result with the partial path taken.
> **If an index file contains malformed JSON or is missing the expected `children` array**: Treat that branch as returning zero matches; note the malformed file in the no-match status rather than proceeding with partial data.
> **If a `children` entry's nested `index` field points to a file that does not exist**: Skip that sub-branch and include the entry at its current level only — do not error out.

## Step 3 — Evaluate relevance and select results

From each domain index's `children` array, evaluate each entry against the query:

- **High relevance**: name, description, group, or trigger closely matches the query terms. Include in results.
- **Moderate relevance**: partial match or related category. Include with lower confidence.
- **No relevance**: no meaningful connection to the query. Exclude.

If an entry has a nested `index` field pointing to a sub-index, descend only if the entry itself shows relevance to the query.

Return a filtered set of entries — only those deemed relevant. Do not return the full index listing unless the query is explicitly a broad listing request.

**Script**: Use `search-by-frontmatter.py` as a first-pass filter when the query maps cleanly to frontmatter fields (group, tier, tags): `python3 ai/scripts/python/search-by-frontmatter.py --root ai/plugins/skf/ --group <group> --format json`. For queries requiring semantic reasoning or cross-branch navigation, rely on AI relevance scoring instead.

## Step 4 — Return Navigation Result report

Produce and return the Navigation Result report using the template defined in `<output_format>`. Select the match template when at least one relevant entry was found; use the no-match template when no relevant entry was found.

The skill is complete when it returns a Navigation Result report with either a filtered matches table or a no-relevant-resources-found status.

Return the Navigation Result report inline. If the result cannot fit within the compact output budget after compaction, spill to the supplied output path or to `reports/orchestration-spill/traversal-report.md` and return that path.

**Script**: Use `parse-navigation-result.py` to render or parse a spilled Navigation Result table when needed.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Primary tool for reading index JSON files during traversal. Use it for every index read and stop at terminal paths rather than loading resource file bodies.
- **file_search / grep_search**: Fallback if an index file path cannot be determined from parent index entries alone. Prefer index traversal over direct file search.
- **create_file**: Only for optional spill fallback under `reports/orchestration-spill/` or an explicitly supplied spill path. No other files may be written.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| summary | `one-line summary` |
| output_path | optional spill path (default: `none`) |

Return a Navigation Result report. Do not add explanatory prose beyond what the template defines.

**Match result** (when at least one relevant entry was found):

```
## Navigation Result

Query: {the input query}
Index path taken: skf-root-index.json → {branches traversed}

### Matches ({count})
| Name | Path | Description | Relevance |
|------|------|-------------|-----------|
| {name} | {path} | {description} | high / moderate |
```

**No-match result** (when no relevant entry was found):

```
## Navigation Result

Query: {the input query}
Status: NO RELEVANT RESOURCES FOUND
Index path searched: {path taken}
Last index read: {filename}
```

**Field definitions:**
- `Query`: exact input query text — copied verbatim from the skill input
- `Index path taken` / `Index path searched`: sequence of index filenames read, separated by ` → `; always begins with `skf-root-index.json`
- `Name`: the `name` field from the matched index entry
- `Path`: the `path` value from the matched index entry (relative workspace path)
- `Description`: the `description` field from the matched index entry
- `Relevance`: `high` (name, description, group, or trigger closely matches query terms) or `moderate` (partial match or related category)
- `count`: integer — total number of rows in the Matches table
- `Last index read`: filename of the deepest index file reached before determining no match
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: query=`find the skills that govern prompt management and prompt storage`.
Expected output: Starts at `skf-root-index.json`, traverses only the `ai/` branch, narrows to the skills index, and returns the prompt-related skill paths with `high` or `moderate` relevance. It does not open the returned skill files.
</example>

<example>
Input: query=`show constitution files relevant to SSOT policy`.
Expected output: Traverses the `constitution/` branch, reads the constitution document, and returns the governance-related constitution content. No framework skill or project files are included.
</example>

<example type="counter">
Input: query=`find the exact wording in <skill-id> about Constitution loading`.
Expected behavior: Returns the path to the likely skill file and relevant index path, but does not open the skill body itself. The caller must read the returned file separately.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
