---
# id-exception: this template uses 'dispatch-manifest-template' instead of 'skf-template-*' — intentional, matches the artifact type it governs
id: dispatch-manifest-template
title: "Dispatch Manifest Template — Markdown Format"
category: framework
version: 1.0
---

# Dispatch Manifest Template

This template defines the canonical markdown format for all `runSubagent` dispatch calls. Use the **Full** variant for `impl-*`, `gov-*`, and any skill whose `dispatch-variant` is `full`. Use the **Compact** variant for `orch-*`, `meta-*`, and any skill whose `dispatch-variant` is `compact`.

---

## Full Variant (impl-*, gov-*, or any skill marked `full`)

```
## Dispatch Manifest

### Identity
- **Skill**: {skill-id}
- **Function**: {skill description — one sentence}
- **Anti-scope**: {what the skill does NOT do}

### Skill
- **Path**: `ai/plugins/skf/skills/{skill-id}.md`
- **Instruction**: Read this file. It defines your COMPLETE workflow. Follow its Steps sequence exactly.

### Task
{Verbatim task description from the orchestration plan — never paraphrased.}

### Context
- **Phase scope**: {Wave N, Step M — one-sentence wave goal}
- **Affected paths**: {list of relevant file paths}
- **Spec excerpt**: {direct quote or path reference, or "none"}
- **Prior wave output**: {path or summary of relevant prior outputs, or "none"}

### Constraints
- {Runtime constraint 1}
- {Runtime constraint 2 — e.g., "Do not modify files not listed under task or context."}
- **Required patterns**: {list of binding PT-IDs, or none}

### Advisory
- **Recommended patterns**: {list of advisory PT-IDs, or none}

### Output Format
{Expected output structure — describe what the subagent should return inline and/or write to .orchestration-temp/}

### Inputs
{Skill inputs from skill inventory — file paths or inline content}
```

---

## Compact Variant (orch-*, meta-*)

```
## Dispatch Manifest

### Skill
- **Path**: `ai/plugins/skf/skills/{skill-id}.md`
- **Instruction**: Read this file. It defines your COMPLETE workflow. Follow its Steps sequence exactly.

### Task
{Verbatim task description — never paraphrased.}

### Context
- **Phase scope**: {Wave N, Step M — one-sentence wave goal}
- **Affected paths**: {list of relevant file paths}
- **Prior wave output**: {path or summary of relevant prior outputs, or "none"}

### Constraints
- {Runtime constraint 1}
- {Runtime constraint 2}

### Inputs
{Skill inputs from skill inventory}
```

---

## Variant Selection Rules

| Skill prefix | Variant |
|---|---|
| `impl-*`, `gov-*`, or any skill marked `full` | Full (Identity + Advisory + Output Format sections required) |
| `orch-*`, `meta-*` read-mode | Compact (omit Identity, Advisory, Output Format) |

---

## Field Ownership

| Field | Owner | Source |
|---|---|---|
| Identity.* | Skill inventory | `.orchestration-temp/skill-inventory.md` |
| Skill.path | Skill inventory | `.orchestration-temp/skill-inventory.md` |
| Task | Orchestrator | Orchestration plan (verbatim) |
| Context.* | Orchestrator | Orchestration plan + wave context |
| Constraints.runtime | Orchestrator | Wave context |
| Constraints.required-patterns | Orchestrator | Pattern bundle |
| Advisory.recommended-patterns | Orchestrator | Pattern bundle |
| Output Format | Skill inventory | `.orchestration-temp/skill-inventory.md` |
| Inputs | Skill inventory | `.orchestration-temp/skill-inventory.md` |

---

## Subagent Response Format

Every subagent must return a response in this markdown format:

```
## Dispatch Response

- **Status**: {ok | blocked | fail}
- **Skill**: {skill-id}
- **Wave**: {N}
- **Step**: {N.M}
- **Output path**: {path/to/artifact or none}
- **Summary**: {one-line description — no newlines}
```

**Rules**:
- `Status` is one of: `ok`, `blocked`, `fail`
- `Skill` matches the skill id from frontmatter
- `Wave` and `Step` are taken from the dispatch prompt's Constraints section
- `Output path` is omitted or set to `none` if no file artifact was produced
- `Summary` is a single line suitable for inline reporting
- If artifact exceeds 20 KB, write to `.orchestration-temp/{wave}-{step}-{skill-id}-output.md` first, then reference path in Output path
