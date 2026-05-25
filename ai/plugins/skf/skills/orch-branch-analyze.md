---
id: "orch-branch-analyze"
recommended-tier: "fast-agent"
version: 1.0
description: "Analyzes all files in a single framework branch and produces a structured summary of their relevance to the current orchestration context. Designed for parallel dispatch \u2014 one instance per branch produced by the upstream branching step. USE FOR: reading and summarizing framework files in a single domain branch; assessing file-level relevance against a stated goal; producing per-branch input for orchestrator planning."
anti-scope: "It does NOT group or split entries, does NOT traverse indexes, and does NOT modify any framework file. Each instance is designed to run concurrently with other branch-analysis instances \u2014 one instance per branch file."
tags:
  - "utility"
  - "framework"
  - "branching"
  - "analysis"
inputs:
  - "Path to one framework-traversal-branched-###.json spill file or equivalent structured branch payload (required)"
  - "Free-form context summary of the orchestration request (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Structured branch analysis payload"
  - "Analysis Summary block emitted inline in chat"
dispatch-variant: "compact"
---


# Skill: orch-branch-analyze

<!-- SECTION 1: Identity (primacy position) -->
Receives one `framework-traversal-branched-###.json` branch file or equivalent branch payload and a context summary, reads every file listed in the branch, assesses each file's relevance against the context, and returns a structured branch analysis payload. Returns an Analysis Summary block to the caller.

**Scope boundary**: This skill reads and analyzes files in a single branch only. It does NOT group or split entries, does NOT traverse indexes, and does NOT modify any framework file. Each instance is designed to run concurrently with other branch-analysis instances — one instance per branch file or payload.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Read framework files only — do not modify, create, or delete framework files. WHY: QA analysis and mutation are separate responsibilities; mixing them corrupts the audit trail.
2. Include every entry from the branch file in the analysis output even when a file cannot be read. WHY: silent omissions cause planning gaps that the orchestrator cannot detect.
3. Record unreadable files as `unreadable` instead of inferring or guessing their content. WHY: fabricated content produces false relevance assessments that corrupt downstream planning.
4. Process only the entries in the single branch file provided. WHY: this skill is designed for isolated per-branch operation; mixing entries defeats parallel dispatch isolation.
5. ALWAYS preserve the branch sequence number in the returned analysis payload. WHY: the orchestrator matches branch analysis results to branch inputs by sequence number.
6. If the branch file contains zero entries, write an analysis file with an empty `findings` array and return a summary noting zero files analyzed. WHY: an empty branch is valid; the caller must receive a well-formed (albeit empty) result.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Prioritize factual, file-grounded assessments — every relevance verdict must cite specific content from the file, not just the file's name or description.
- Implement EXACTLY and ONLY what this skill defines — read each file, assess relevance, write the report, return the summary block. Nothing more.
- When relevance is ambiguous, mark it `moderate` and include a brief note explaining the uncertainty rather than forcing a binary verdict.
- Keep per-file summaries concise (≤3 sentences) — the goal is actionable signal for planning, not exhaustive documentation.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve the branch input before reading entries.
- Confirm the branch context used for relevance scoring comes from the branch file when available.

## Analysis file schema

```json
{
  "branch": "###",
  "domain": "<domain name>",
  "context": "<context summary used for relevance assessment>",
  "analyzed_count": <number of entries successfully read>,
  "unreadable_count": <number of entries that could not be read>,
  "findings": [
    {
      "name": "<entry name>",
      "path": "<workspace-relative path>",
      "relevance": "<high | moderate | low | unreadable>",
      "summary": "<≤3-sentence factual summary of file content>",
      "key_facts": ["<fact 1>", "<fact 2>"],
      "relevance_reason": "<one sentence explaining why this relevance verdict was assigned>"
    }
  ],
  "branch_conclusion": "<2–4 sentence synthesis: which files in this branch are most relevant to the context and why>"
}
```

## Relevance scale

| Value | Meaning |
|-------|---------|
| `high` | File directly addresses the stated context — contains rules, definitions, or workflows that the orchestration must consult or modify. |
| `moderate` | File is related to the context domain but does not directly constrain or define the work — useful background. |
| `low` | File exists in the domain but has no meaningful bearing on the stated context. |
| `unreadable` | File could not be read (missing, permission error, binary). Content assumed absent. |

## Step 1 — Load branch file

Read the branch file at the path provided in `branch-file`. Extract: `branch`, `domain`, `context`, `entries`.

> **If the branch file cannot be read**: Halt and return the Analysis Error block (see `<output_format>`). Do not proceed to Step 2.

> **If `entries` is empty or absent**: Skip directly to Step 4 with zero findings.

## Step 2 — Read and analyze each file

For each entry in `entries`:

1. Read the file at `entry.path` using `read_file`.
   > **If the file cannot be read**: Record `relevance: "unreadable"`, `summary: "File could not be read: <error>"`, `key_facts: []`, and `relevance_reason: "File is inaccessible."`. Increment `unreadable_count`. Continue to the next entry.
2. Assess relevance against the `context` summary using the relevance scale above.
3. Write a factual `summary` (≤3 sentences) of what the file actually contains.
4. Extract 1–4 `key_facts`: specific named items (skill IDs, rule numbers, constraint text, step names) that are most pertinent to the context.
5. Write one `relevance_reason` sentence citing specific content that drove the verdict.

## Step 3 — Assemble branch analysis

Assemble the full analysis object per the schema above. Set `analyzed_count` to the number of entries with relevance ≠ `unreadable`. Set `unreadable_count` to the count of unreadable entries.

Write the `branch_conclusion` field last, after all individual findings are complete. Synthesize: which 1–3 files in this branch are most relevant to the context, and what the orchestrator should prioritize reading or acting on.

## Step 4 — Return Analysis Summary

Return the Analysis Summary block defined in `<output_format>`. The skill is complete when the branch analysis payload and the Analysis Summary block have been returned.

Aggregate the overall verdict manually from the completed finding set: if every analyzed entry is acceptable, return `ok`; if the branch cannot be analyzed because required files are unreadable, return `blocked`; otherwise return `fail` with the concrete blocking findings.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Read the branch file input and each framework file listed in the branch entries. Primary tool — no other discovery needed.
- **create_file**: Use only for optional spill fallback under `reports/orchestration-spill/` when the branch analysis cannot fit inline.
- No search, traversal, or mutation tools — this skill reads listed files and writes one output file only.
- Do not use terminal script helpers in this skill; determine output state and the branch verdict directly from the files already in scope.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-branch-analyze` |
| wave | `N` |
| step | `N.M` |
| output_path | `none` or `reports/orchestration-spill/...` |
| summary | one-line summary of what was done |

Return the Analysis Summary block to the caller. Do not add explanatory prose beyond what the template specifies. The full structured findings are returned inline unless a spill fallback is required.

**Field definitions:**

| Field | Type | Allowed values |
|-------|------|----------------|
| `{###}` | string | Three-digit zero-padded sequence number matching the input branch file |
| `{domain}` | string | Domain label from the branch file |
| `{analyzed_count}` | integer | Count of entries with relevance not equal to `unreadable` |
| `{unreadable_count}` | integer | Count of entries that could not be read |
| `{name}` | string | Entry name from the branch file |
| `{relevance}` | enum | `high`, `moderate`, `low`, or `unreadable` |
| `{key_facts}` | string | 1–4 key facts joined by `"; "` |
| `{branch_conclusion}` | string | 2–4 sentence synthesis of most relevant files and orchestrator priorities |

**Standard run:**

```
## Analysis Summary — Branch ### ({domain})

Files analyzed: {analyzed_count}  
Files unreadable: {unreadable_count}

| File | Relevance | Key Facts |
|------|-----------|----------|
| {name} | {relevance} | {key_facts joined by "; "} |

**Branch Conclusion**: {branch_conclusion}

Analysis output: inline branch-analysis state
```

**Empty branch:**

```
## Analysis Summary — Branch ### ({domain})

Status: NO ENTRIES — branch file contained zero entries. Analysis file written with empty findings.
```

**Analysis error:**

```
## Analysis Error — Branch ###

Could not read branch file: {path}
Error: {message}
Caller action required: verify the upstream branching step completed successfully.
```
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: branch-file="reports/orchestration-spill/framework-traversal-branched-{###}.json" with domain="skills", context="Add a new utility skill for removing stale workflow temp files", 6 entries including two utility skills, one implementation skill, skills-index.json, and README.md.
Expected output: Reads branch file. Reads all 6 files fully. Scores the two utility skills as `high` (both are directly relevant to authoring a new utility skill). Scores skills-index.json as `high` (registration pattern needed). Scores the implementation skill as `moderate` (useful background for skill structure). Scores README as `low`. Returns inline branch analysis with all 6 findings and a branch_conclusion referencing the most relevant files. Returns Analysis Summary table with 6 rows.
</example>

<example>
Input: branch-file="reports/orchestration-spill/framework-traversal-branched-{###}.json" with domain="constitution", context="Add a new utility skill", 3 entries.
Expected output: Reads branch file. Reads 3 constitution files. Finds no direct relevance between the constitution sub-files and adding a utility skill. All scored `low`. branch_conclusion="The constitution domain contains governance rules that do not directly bear on authoring a utility skill. None of these files require orchestrator attention for this task." Returns Analysis Summary with 3 low-relevance rows.
</example>

<example type="counter">
Input: After analysis completes, caller asks: "Great — now update one of the related files to add the new skill to its examples."
Expected behavior: Skill responds: "orch-branch-analyze is a read-only skill. File updates are out of scope for this skill. To modify the file, dispatch the appropriate implementation workflow with the required changes."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
