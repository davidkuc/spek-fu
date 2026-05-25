---
title: "[Skill Title]"
description: '[Verb] [object/target], [producing what output]. Consult this skill when [trigger condition]. [Exclusion boundary — what it does NOT do, with redirect to sibling skill if applicable.]'
recommended-tier: "[fast-agent | standard-agent | large-context-agent]"
anti-scope: "[What this skill does NOT do — paired exclusion for the description above.]"
tags:
  - "[tag-1]"
  - "[tag-2]"
id: skf-template-skill-template
category: framework
version: 1.0
dispatch-variant: "[full | compact]"
inputs:
  - "[Input description (required)]"
  - "[Optional input description (optional)]"
outputs:
  - "[Execution result code]"
  - "[One-line summary for inline return]"
---

# Skill: [skill-name]

<!-- SECTION 1: Identity (primacy position) -->
[One-paragraph summary of what the skill does, what it produces, and what agent should consult it.]

**Scope boundary**: This skill [specific scope — e.g., reads and reports only / creates only / modifies only X]. It does NOT [adjacent action to exclude — e.g., apply fixes / create new files / modify governance]. For [excluded action], use [<!-- replace with actual sibling skill id when known -->].

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER [primary scope overreach prohibition] — WHY: [rationale].
2. NEVER [secondary prohibition — e.g., modify files outside designated path] — WHY: [rationale].
3. ALWAYS [required gate — e.g., read inputs before producing output] — WHY: [rationale].
4. When [predictable failure condition], [specific fallback action rather than guessing].
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- If inputs are ambiguous or missing, use `vscode_askQuestions` rather than guessing.
- [Idempotency rule if applicable: detect first-run vs. resume vs. already-complete state before acting.]
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Inputs

| Field | Type | Required | Enum | Description |
|---|---|---|---|---|
| [field-name] | string | yes | value1 \| value2 | [Description of input field] |
| [optional-field] | [type] | no | — | [Description of optional field] |

**Source**: [where inputs typically come from — caller, iteration folder, workspace convention].

## Step 1 — [First step title]

[Step instructions. Include tool names explicitly.]

> **If [predictable failure]**: [specific action to take]

## Step 2 — [Second step title]

[Step instructions.]

## Step N — [Final step title]

[Step instructions. Include output template if this step produces structured output:]

```
Status: SUCCESS | PARTIAL | BLOCKED | FAILED
What changed: <concise description>
Verification: <how you confirmed it>
```

## Outputs

| Field | Type | Enum | Description |
|---|---|---|---|
| status | string | ok \| blocked \| fail | Execution result code |
| summary | string | — | One-line summary for inline return |

**Format**: [file/JSON/markdown/structured text]. **Destination**: [where output is written].

The skill is complete when [done condition — name the artifact, state, or user confirmation].

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **[tool-name]**: [When and how to use it for this skill. Include activation requirement.]
- **[tool-name]**: [When and how to use it.]
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Canonical JSON Template** (required first element):

```json
{
  "status": "ok | blocked | fail",
  "skill_id": "[skill-name]",
  "wave": "N",
  "step": "N.M",
  "output_path": "path/to/artifact",
  "summary": "one-line summary of what was done"
}
```

**Rules**:
- `status` is one of: `ok`, `blocked`, `fail`
- `skill_id` matches the skill name from frontmatter
- `wave` and `step` are taken from the dispatch prompt
- `output_path` is omitted if the skill produced no file artifact
- `summary` is a single line (no newlines) suitable for inline reporting
- For large artifacts (>20 KB), first compact wording while preserving meaning; if fidelity still cannot fit, write full result to `reports/orchestration-spill/{wave}-{step}-{skill-id}-output.json`

**Prose Format** (optional, for additional context):

[Exact output template with field names, order, and allowed values:]

```
[Field 1]: [allowed values or format]
[Field 2]: [allowed values or format]
[Field 3]: [allowed values or format]
```

[State any format invariants — e.g., "every finding must include a file path and line reference".]
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: [realistic input — skill name, scope, relevant context]
Expected output: [complete ideal output showing constraints applied, format followed, done condition met]
</example>

<example>
Input: [second realistic input covering a different case]
Expected output: [complete ideal output]
</example>

<example type="counter">
Input: [input that should trigger a constraint, e.g., scope overreach request]
Expected behavior: Skill detects constraint violation. Responds: "[constrained refusal or redirect — e.g., 'This skill is read-only. To apply fixes, use [fix-skill].']"
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never [scope overreach prohibition]** — [what the agent must NOT do]. WHY: [rationale].
- **Never [prohibition 2]** — [concrete action to avoid]. WHY: [rationale].
- **Prefer [positive framing]** over [negative alternative] — [rationale].
- **Always verify** output against `<constraints>` before reporting completion.

</reminders>
