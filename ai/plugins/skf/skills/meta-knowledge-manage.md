---
id: "meta-knowledge-manage"
recommended-tier: "fast-agent"
version: 1.0
description: "Appends lessons to, retrieves lessons from, and searches `knowledge-database.md` files. USE FOR: recording lessons from user-requested fixes, surfacing advisory lessons before tasks, keyword search across lessons. DO NOT USE FOR: implementing tasks, applying code changes, or managing other documentation."
anti-scope: "Does NOT implement tasks, apply code changes, or manage any file other than `knowledge-database.md`."
tags:
  - "meta"
  - "capture"
  - "database"
  - "framework"
inputs:
  - "Operation to perform: write, read, or search (required)"
  - "Task description — required for read and search (optional)"
  - "Lesson text to record — required for write (optional)"
  - "Knowledge database file paths — required for read and write (optional)"
  - "Keyword search query — required for search (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Operation result: recorded, found, or not_found"
  - "Matching lesson objects (for read and search)"
  - "distillation-recommended: true — emitted in write output when lesson count >= knowledgeDistillationThreshold (optional)"
dispatch-variant: "compact"
---

# Skill: meta-knowledge-manage

<!-- SECTION 1: Identity (primacy position) -->
Manages the knowledge database across all plugin `knowledge-database.md` files. Supports three operations: `write` (append a lesson), `read` (surface advisory lessons for a task), and `search` (keyword lookup). This skill is the sole authorized path for recording, retrieving, and searching institutional lessons.

**Scope boundary**: This skill operates ONLY on `knowledge-database.md` files. It does NOT implement tasks, apply code changes, or manage any other documentation.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER write a lesson without explicit human approval — ONLY append to disk after `vscode_askQuestions` returns Approve. WHY: unverified lessons corrupt institutional knowledge and are difficult to reverse.
2. NEVER record internal reasoning, implementation obstacles, or speculative content — WHY: lessons must be reusable, human-verifiable problem-and-fix patterns only.
3. When `read` finds no matches, skip output silently. When `search` finds no matches, return `No lessons found matching '{query}'.` — WHY: `read` is advisory surfacing — empty results add noise; `search` is a direct user query — silence would be misleading.
4. ALWAYS apply case-insensitive matching for `search` across all lesson fields — WHY: keyword casing varies across authors.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot be dispatched as a stateless subagent.

- Before producing any output, verify your response complies with all rules in `<constraints>` above.
- Implement EXACTLY the operation requested — do not combine operations or add unrequested side effects.
- Present `read` results as advisory guidance, never as mandatory constraints.
- If a proposed lesson is speculative or lacks Trigger/Context/Solution fields, report the gap rather than recording a flawed entry.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve the requested `operation` before reading or writing any file.
- Confirm required inputs are present: database paths (write/read) or search query (search).

## Done conditions

- **write**: approved lesson appended to the designated knowledge database. When the total lesson count after appending is >= `knowledgeDistillationThreshold`, the output summary carries `distillation-recommended: true` for the orchestrator to act on — no dispatch or gate is triggered by this skill.
- **read**: matching lessons surfaced inline, or skipped silently when none found.
- **search**: matching lessons returned inline, or no-matches message returned.

## Configuration

Read `config.json` in this skill's folder:
- `maxRevisionAttempts` — max revision loops before halting (write).
- `maxLessonsToSurface` — max lessons to return (read).

---

## Operation: write

### Step 1 — Read and validate database

Read `knowledge-database.md` at the provided path. Parse `## L-NNN:` headings to find the next lesson ID (start at `0` if empty). Scan existing titles and Trigger fields for near-duplicates — if found, stop and report; otherwise proceed.

**Lesson count guard**: Count `L-###` occurrences. If >= 100, prepend `⚠️ Knowledge database has {count} lessons (>= 100 threshold). Consider pruning before adding more.` Always proceed regardless.

### Step 2 — Draft candidate lesson

Formulate a lesson using this template:

```
## L-{id}: [Lesson Title]

**Tags**: `tag-1`, `tag-2`

**Trigger**: [What caused the problem — max 1 sentence]

**Context**: [Description of the situation — max 1 sentence]

**Solution**: [What actions were taken — max 1 sentence]

---
```

Use 2–6 short tags from the lesson domain. Each field: max 1 sentence. Describe a reusable pattern, not a one-time quirk.

### Step 3 — Verify and write

⛔ STOP — present the candidate lesson via `vscode_askQuestions` using the payload below:

```json
{
  "header": "lesson_approval",
  "question": "Review the lesson above. How would you like to proceed?",
  "options": [
    { "label": "Approve — record lesson", "recommended": true },
    { "label": "Reject — do not record" },
    { "label": "Edit — make changes first" }
  ],
  "allowFreeformInput": true
}
```

Response mapping:
- **Approve** → append the lesson to `knowledge-database.md` before the final newline. After appending, count total `L-###` occurrences in the file. If the count >= `knowledgeDistillationThreshold` (from `config.json`), include `distillation-recommended: true` in the output summary. Confirm: `Lesson #[N] recorded in [path].`
- **Edit** → incorporate corrections from freeform field, re-present. Stop if `maxRevisionAttempts` reached; report that no lesson was recorded.
- **Reject** → stop. Report that no lesson was recorded.

> **If `vscode_askQuestions` is unavailable**: halt before writing. Report: "Cannot record lesson — verification tool unavailable."

---

## Operation: read

### Step 1 — Load databases

For each provided path, read `knowledge-database.md` in full. Skip missing or empty files silently.

### Step 2 — Match and surface

Evaluate each lesson against the task description:

- **Strong match**: Trigger or Context directly describes the same domain, workflow pattern, file type, or technology → include.
- **Weak or no match** → discard.

Select up to `maxLessonsToSurface` strong matches. If none → skip output silently.

### Step 3 — Return advisory output

Format matching lessons per the `read` template in Section 6.

---

## Operation: search

### Step 1 — Load databases

Load all `knowledge-database.md` files from the provided paths. Skip missing or empty files silently.

### Step 2 — Match and return

Search each lesson's Trigger, Context, Solution, and title for the query keywords (case-insensitive). Return all matches per the `search` template in Section 6. If no matches → return `No lessons found matching '{query}'.`

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **vscode_askQuestions**: write Step 3 only — present candidate lesson for Approve / Edit / Reject. Required gate before any disk write. If unavailable, halt before writing and report.
- **read_file**: load `knowledge-database.md` in all operations. Read the full file in one call when possible.
- **grep_search**: search operation — locate candidate lesson blocks by keyword.
- **replace_string_in_file**: write Step 3 (after Approve) — append approved lesson to `knowledge-database.md`. Use ONLY after user approval.
- Do NOT modify any file other than the designated `knowledge-database.md` paths provided as input.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `meta-knowledge-manage` |
| wave | `N` |
| step | `N.M` |
| output_path | path or `null` |
| summary | one-line summary |

**write** (after approval):
```
Lesson #[N] recorded in [knowledge-database path].
```
Prepend `⚠️ Knowledge database has {count} lessons (>= 100 threshold). Consider pruning before adding more.` if triggered.

**read** (when matches found):
```
## Relevant Lessons from Knowledge Databases

> The following lessons from previous work are relevant to this task. They are advisory only — apply judgment on whether they apply.

- **[lesson #[N]] [Lesson Title]** (from [source database])
  - Trigger: [trigger text]
  - Context: [context text]
  - Solution: [solution text]
```
If no matches: produce no output.

**search** (when matches found):
```
- **[lesson #[N]] [Lesson Title]** (from [source database])
  - Trigger: [trigger text]
  - Context: [context text]
  - Solution: [solution text]
```
If no matches: `No lessons found matching '{query}'.`

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: operation=write, lesson-description="Skill frontmatter fields must match the schema in constitution.md; fix was to validate frontmatter against the canonical schema before merging."
Expected behavior: Reads knowledge-database.md, determines next ID. Drafts lesson with Trigger/Context/Solution. Presents via vscode_askQuestions. On Approve, appends lesson and reports "Lesson #N recorded in ai/plugins/skf/knowledge/knowledge-database.md."
</example>

<example>
Input: operation=read, task-description="Updating SKILL.md frontmatter fields across multiple skill files."
Expected behavior: Reads all knowledge-database.md files at provided paths. Returns up to maxLessonsToSurface strong matches as advisory guidance with the advisory prefix. If no relevant matches exist, produces no output.
</example>

<example type="counter">
Input: operation=write, lesson-description="I think maybe the agent got confused about context windows."
Expected behavior: Skill identifies the proposed lesson as speculative — no concrete Trigger/Context/Solution pattern. Reports: "This lesson lacks a verifiable pattern. Provide a concrete Trigger, Context, and Solution before proceeding." Does not advance to the verification step.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
## Rules

- **Never write a lesson without explicit human approval** — unverified lessons corrupt institutional knowledge.
- **Never record speculative or internal-reasoning content** — only reusable, human-verifiable problem-and-fix patterns.
- **`read` with no matches: skip silently. `search` with no matches: return the explicit no-results message.**
</reminders>
