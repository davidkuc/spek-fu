---
id: "meta-knowledge-distillation"
recommended-tier: "fast-agent"
version: 1.1
description: "Runs a single combined flow that first consolidates duplicate or near-duplicate lessons in `knowledge-database.md`, then distills the cleaned lesson set into reusable PT0xx pattern files. USE FOR: cleaning up the knowledge database and promoting general-recurring lessons to patterns in one pass. DO NOT USE FOR: recording or retrieving lessons, implementing tasks, or modifying non-pattern files outside the distillation flow."
anti-scope: "Does NOT record or retrieve lessons — use meta-knowledge-manage for that. Does NOT implement tasks. Modifies `knowledge-database.md` (merging duplicates and removing promoted lessons) and `ai/plugins/skf/patterns/` (writing new pattern files). Does not modify any other files."
tags:
  - "meta"
  - "patterns"
  - "lifecycle"
  - "framework"
inputs:
  - "Knowledge database file path (optional, defaults to ai/plugins/skf/knowledge/knowledge-database.md)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Duplicate/similar lessons merged in knowledge-database.md"
  - "Pattern file(s) written at ai/plugins/skf/patterns/PTxxx-name.md"
  - "patterns-index.json updated with new entries"
  - "Promoted lessons removed from knowledge-database.md"
  - "One-line summary"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions when invoked directly. When dispatched as a stateless subagent, approval steps are bypassed and the skill runs non-interactively.

# Skill: meta-knowledge-distillation

<!-- SECTION 1: Identity (primacy position) -->
Runs a single combined pipeline against `knowledge-database.md`: first consolidates duplicate or near-duplicate lessons into refined entries, then classifies the cleaned lesson set and distills viable general-recurring clusters into reusable PT0xx pattern files. The merge phase scans all lessons for duplicates or near-duplicates, drafts a single consolidated entry for each merge group, and replaces the originals. The distill phase classifies each remaining lesson as project-specific (stays in the database) or general-recurring (promoted to a pattern), clusters related general-recurring lessons, and creates one PT0xx file per viable cluster of three or more related lessons.

**Scope boundary**: This skill modifies `knowledge-database.md` (merging duplicates and removing promoted lessons) and `ai/plugins/skf/patterns/` (writing new pattern files). It does not record new lessons or perform any implementation work. For recording or surfacing lessons, use **meta-knowledge-manage**.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER delete a lesson from `knowledge-database.md` without first successfully writing its replacement (a pattern file for distill, or a merged lesson entry for merge) — WHY: removing a lesson before its replacement is written permanently destroys institutional knowledge with no recovery path.
2. NEVER assign a new PT0xx ID without reading `patterns-index.json` first to find the current highest ID — WHY: ID collisions corrupt the pattern index and break routing.
3. ALWAYS use only tags, categories, and signals from `ai/plugins/skf/patterns/pattern-tags.md` when writing pattern files — WHY: non-canonical tags break index routing and discovery.
4. NEVER promote a lesson cluster with fewer than 3 related lessons to a pattern — WHY: fewer than 3 is insufficient evidence of a general-recurring pattern; the lessons should accumulate further before generalization.
5. NEVER write a pattern file or commit a merge without explicit user approval, except when dispatched as a stateless subagent — WHY: unapproved writes silently alter the orchestration routing database and are hard to reverse.
6. When `vscode_askQuestions` is unavailable and the skill is NOT in subagent mode: halt before writing any file and report "Cannot write — approval tool unavailable."
7. NEVER merge lessons that describe distinct, non-overlapping problems even if they share surface-level vocabulary — WHY: false merges lose nuance and degrade knowledge quality.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your response complies with all rules in `<constraints>` above.
- Run the full combined flow (merge then distill) — do not skip phases or add unrequested side effects.
- When dispatched as a stateless subagent: run the full workflow but skip all `vscode_askQuestions` approval gates — treat each gate as approved and proceed.
- When invoked directly as a slash command: never skip an approval gate.
- Idempotency: before writing a pattern file, check whether a file at the target path already exists — if it does, report the conflict and skip rather than overwrite.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- The knowledge database path defaults to `ai/plugins/skf/knowledge/knowledge-database.md` if not provided.

## Done condition

All duplicate/similar lessons consolidated in `knowledge-database.md`, all viable general-recurring clusters (3+ related lessons) written as PT0xx pattern files, promoted lessons removed from `knowledge-database.md`, and `patterns-index.json` updated. Project-specific and non-promoted lessons remain untouched.

---

## Step 1 — Load databases

Read `knowledge-database.md` in full using multi-pass reads: read from line 1 with a generous range; if the response fills the page, advance `startLine` and read again; repeat until the response is shorter than the page size. Parse all `## L-NNN:` lesson blocks (ID, title, tags, Trigger, Context, Solution).

Read `patterns-index.json` in full to determine the current highest PT0xx ID and verify which patterns already exist.

> **If `knowledge-database.md` is missing or empty**: stop and report "knowledge-database.md not found or empty — nothing to process."

> **If `patterns-index.json` cannot be read**: stop and report "Cannot read patterns-index.json — cannot safely assign IDs."

> **If fewer than 2 lessons exist**: skip to Step 5 — nothing to merge.

## Step 2 — Identify merge candidates

Compare all lessons pairwise. Mark a pair as **merge candidates** when they meet at least two of the following criteria:
- Same or nearly identical Trigger condition
- Same or highly overlapping Solution
- Shared tags covering the same problem domain
- One lesson is a strict subset of the other

Do NOT mark lessons as merge candidates based on surface vocabulary similarity alone — the underlying problem must be the same or a refinement of the same problem.

Group overlapping candidates into **Merge Groups** (one group may contain more than two lessons).

Produce a **Merge Candidate Table**:

| Group | Lesson IDs | Titles | Overlap Rationale |
|-------|-----------|--------|-------------------|
| M-1   | L-003, L-011 | ... | ... |

> **If no merge candidates are found**: note "No duplicates found — skipping merge phase." and proceed to Step 5.

## Step 3 — Draft merged lessons

For each Merge Group, draft a single consolidated `## L-NNN:` lesson block:
- Assign the lowest existing lesson ID from the group (e.g., if merging L-003 and L-011, the merged entry keeps ID L-003).
- Title: the most precise and general title across the group.
- Tags: union of all tags from the group, deduplicated.
- Trigger: synthesized from all triggers — capture the full range of conditions that activate this lesson.
- Context: synthesized from all context fields — preserve all distinct nuances.
- Solution: synthesized from all solutions — keep the most complete and actionable guidance.

Present each draft inline using the standard lesson block format.

## Step 4 — Merge approval gate (skipped in subagent mode)

Present the **Merge Candidate Table** and all **Merged Lesson Drafts**. Ask via `vscode_askQuestions`:

```json
{
  "header": "merge_approval",
  "question": "Review the proposed lesson merges above. Select an action:",
  "options": [
    { "label": "Approve all — apply all proposed merges", "recommended": true },
    { "label": "Approve individually — review each merge before applying" },
    { "label": "Cancel — skip merges and proceed to distillation" }
  ],
  "allowFreeformInput": true
}
```

- **Approve all**: apply all merges and proceed to Step 5.
- **Approve individually**: for each group, call `vscode_askQuestions` with header `merge_N_approval`, question "Approve merge of [IDs]?", options `[{ "label": "Approve" }, { "label": "Skip" }]` before applying that merge; then proceed to Step 5.
- **Cancel**: skip all merges and proceed to Step 5 with the original lesson set.
- **Subagent mode**: skip this step; treat all groups as approved.

For each approved Merge Group:
1. Write the consolidated lesson entry to `knowledge-database.md`, replacing the block with the lowest lesson ID in the group.
2. Remove all other lesson blocks in the group from `knowledge-database.md`.

> **Apply one merge group at a time**: complete the write-and-remove cycle for each group before starting the next — WHY: partial writes followed by an error must leave the database in a consistent state.

> **If any write to `knowledge-database.md` fails**: stop immediately, report which groups were not applied, and leave the remaining lesson blocks unchanged.

## Step 5 — Classify lessons

Using the current state of `knowledge-database.md` (post-merge), classify each remaining lesson:

- **project-specific**: context-bound to this project, workflow, or team — e.g., names a specific file path, references a one-time configuration error, or describes a project-specific system. Remains in `knowledge-database.md` unchanged.
- **general-recurring**: describes a reusable, broadly applicable problem-and-fix pattern that would apply across different projects or orchestration contexts. Candidate for pattern promotion.

Produce a **Classification Table**:

| Lesson ID | Title | Classification | Rationale |
|-----------|-------|----------------|-----------|
| L-001     | ...   | project-specific / general-recurring | ... |

## Step 6 — Cluster general-recurring lessons

Group general-recurring lessons by theme. A **viable cluster** requires 3 or more related lessons sharing a common problem domain or mechanism.

For each viable cluster, draft a **Pattern Abstract**:
- Proposed pattern name (kebab-case slug, e.g., `explicit-gate-before-write`)
- Category (from `pattern-tags.md` categories)
- Tags (2–6 from `pattern-tags.md` tags)
- Signals (from `pattern-tags.md` signals)
- Reasoning: one paragraph — what problem does this pattern solve, why is it recurring
- Examples: 3–4 concrete, realistic examples

> **If no viable clusters exist**: report "No viable pattern clusters found — minimum 3 related lessons required per cluster. No patterns written." and stop.

> **If a proposed cluster has fewer than 3 related lessons**: do not create a pattern for it; note it in the output summary as "skipped (fewer than 3 lessons)."

## Step 7 — Pattern approval gate (skipped in subagent mode)

Present the **Classification Table** and all **Pattern Abstracts**. Ask via `vscode_askQuestions`:

```json
{
  "header": "pattern_distill_approval",
  "question": "Review the proposed patterns above. Select an action:",
  "options": [
    { "label": "Approve all — write all proposed patterns", "recommended": true },
    { "label": "Approve individually — review each pattern before writing" },
    { "label": "Cancel — do not write any patterns" }
  ],
  "allowFreeformInput": true
}
```

- **Approve all**: proceed to Step 8 for all clusters.
- **Approve individually**: for each cluster, call `vscode_askQuestions` with header `pattern_N_approval`, question "Approve pattern: [name]?", options `[{ "label": "Approve" }, { "label": "Skip" }]` before writing that pattern.
- **Cancel**: stop and report "No patterns written."
- **Subagent mode**: skip this step; treat all clusters as approved.

## Step 8 — Assign IDs

For each approved cluster: find the highest existing PT ID in `patterns-index.json` children array. Assign the next sequential numeric ID (e.g., if highest is PT026, assign PT027). Do not reuse IDs of existing patterns.

## Step 9 — Write pattern files

For each approved cluster, write `ai/plugins/skf/patterns/PTxxx-name.md` using this template:

```markdown
---
id: PTxxx
version: 1.0
name: Pattern Name
description: "[one-sentence description following PT0xx description convention: what it does, USE FOR, DO NOT USE FOR]"
category: [category]
tags: [tag1, tag2, tag3]
signals: [signal1, signal2]
recommended-tier: all
prevents: "[What failure mode this pattern prevents and why]"
---

# Pattern Name

## Reasoning

[One paragraph: why this problem recurs across projects and what applying this pattern achieves.]

## Examples

- [Concrete example 1]
- [Concrete example 2]
- [Concrete example 3]
```

> **If the target file already exists**: skip this pattern, report the conflict, continue with remaining patterns.

> **If the write fails**: stop. Do not remove any lessons from `knowledge-database.md` for this cluster.

## Step 10 — Update patterns-index.json

For each successfully written pattern file, append a new entry to the `children` array in `patterns-index.json`:

```json
{
  "name": "PTxxx",
  "type": "file",
  "path": "ai/plugins/skf/patterns/PTxxx-name.md",
  "description": "[pattern description matching frontmatter]",
  "recommended-tier": "all"
}
```

> **If `patterns-index.json` cannot be updated**: stop. Do not delete any lessons.

## Step 11 — Remove promoted lessons

For each lesson successfully promoted to a written pattern: remove its complete `## L-NNN:` block from `knowledge-database.md` (from the heading line through the trailing `---` separator). Do NOT remove lessons from clusters that were skipped, cancelled, or whose pattern write failed.

Project-specific lessons are never modified.

> **If `knowledge-database.md` cannot be written**: report which lessons were not removed; leave the file unchanged.

The skill is complete when all merges are applied, all approved patterns are written, `patterns-index.json` is updated, and promoted lessons are removed from `knowledge-database.md`.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Step 1 — load `knowledge-database.md`, `patterns-index.json`, and `pattern-tags.md` using multi-pass reads until end of file is confirmed.
- **vscode_askQuestions**: Steps 4 and 7 — collect merge and pattern approval decisions interactively. Skip entirely when in subagent mode.
- **create_file**: Step 9 — write new PT0xx pattern files. Only used after approval (or in subagent mode).
- **replace_string_in_file**: Steps 4, 10, and 11 — replace and remove lesson blocks in `knowledge-database.md`; update `patterns-index.json`; remove promoted lessons from `knowledge-database.md`.
- **file_search**: Step 9 — verify a target pattern file does not already exist before writing.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `meta-knowledge-distillation` |
| wave | `N` |
| step | `N.M` |
| output_path | path(s) to written pattern file(s), or `null` |
| summary | one-line summary of what was done |

**On completion**:
```
Merge groups applied: [N]
  - M-1: [merged lesson ID] — consolidated from [L-NNN, L-NNN, ...]
  - ...
Lessons removed (duplicates consolidated): [N]
Merge groups skipped or cancelled: [N]
Patterns written: [N]
  - PTxxx: [pattern name] (promoted from lessons: L-NNN, L-NNN, ...)
  - ...
Lessons removed (promoted to patterns): [N]
Lessons retained (project-specific): [N]
Clusters skipped (fewer than 3 lessons): [N]
```

**When dispatched on distillation-recommended signal** (include in summary):
```
Dispatched on: distillation-recommended signal from meta-knowledge-manage
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: knowledge-database.md contains 14 lessons — L-004 and L-009 are near-duplicate "always read context.md before starting orchestration" entries; 5 other lessons are classified as general-recurring with 3 related to approval-gate-before-write patterns
Expected behavior: Step 1 loads both databases. Step 2 identifies L-004 and L-009 as merge candidates. Step 3 drafts a merged L-004 block. Step 4 presents the merge for approval; on approval replaces L-004 and removes L-009. Step 5 classifies the 13 remaining lessons. Step 6 clusters the 3 gate-related lessons into a viable cluster and drafts an "Explicit Gate Before Write" Pattern Abstract. Step 7 presents for approval; on approval proceeds. Step 8 assigns PT027. Step 9 writes PT027-explicit-gate-before-write.md. Step 10 appends entry to patterns-index.json. Step 11 removes L-003, L-007, L-011. Reports: "Merge groups applied: 1. M-1: L-004 — consolidated from L-004, L-009. Lessons removed (duplicates): 1. Patterns written: 1 — PT027. Lessons removed (promoted): 3. Lessons retained (project-specific): 9. Clusters skipped: 1."
</example>

<example>
Input: knowledge-database.md contains 5 lessons — no duplicates, only 2 general-recurring lessons on the same topic
Expected behavior: Step 2 finds no merge candidates; notes "No duplicates found — skipping merge phase" and proceeds to Step 5. Step 6 finds the cluster has only 2 lessons — does not create a pattern. Reports: "Merge groups applied: 0. Patterns written: 0. Clusters skipped (fewer than 3 lessons): 1."
</example>

<example type="counter">
Input: knowledge-database.md contains two lessons that share the word "always verify" in their titles but address completely different verification domains (one about file existence, one about index ID uniqueness)
Expected behavior: Step 2 does not mark these as merge candidates — the problems are distinct. Proceeds to Step 5 and classifies each lesson independently. Reports: "Merge groups applied: 0."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never delete a lesson from `knowledge-database.md` without a successfully written replacement** — for distill this means a written pattern file; for merge this means a written consolidated lesson entry.
- **Never assign a PT0xx ID without reading `patterns-index.json` first** — WHY: ID collisions corrupt the pattern index and break orchestration routing.
- **Never use tags, categories, or signals not defined in `pattern-tags.md`** — WHY: non-canonical tags break discovery and routing in the pattern index.
- **Never act on a partially read `knowledge-database.md` or `pattern-tags.md`** — read each file to the end of file before classifying lessons or assigning tags.
- **Never merge lessons that address distinct problems** — surface vocabulary overlap is not sufficient; the underlying problem-and-fix must be the same or a refinement of the same problem.

</reminders>
