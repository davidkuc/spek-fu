---
id: "meta-skill-manage"
recommended-tier: "fast-agent"
version: 1.0
description: "Scaffolds, evaluates, and refines skill files in the AI framework. USE FOR: creating new skills from requirements, scoring skill drafts against the design catalogue, applying catalogue fixes until zero violations remain. DO NOT USE FOR: running skills, syncing documentation, or modifying files outside the skill directory."
anti-scope: "Does not run or invoke skills, handle documentation sync, or modify any file outside the skill directory without user approval."
tags:
  - "meta"
  - "skill"
  - "lifecycle"
  - "evaluation"
inputs:
  - "Operation to perform: create, evaluate, or refine (required)"
  - "Skill description — required for create (optional)"
  - "Group assignment — optional for create (optional)"
  - "Skill draft file path or content — required for evaluate and refine (optional)"
  - "Evaluation report path or content — required for refine (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Path to created or refined skill file (create and refine)"
  - "Evaluation report (evaluate and refine)"
  - "One-line summary"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: meta-skill-manage

<!-- SECTION 1: Identity (primacy position) -->
Scaffolds new skill files from requirements (create), scores skill drafts against the check/fix catalogue (evaluate), and applies catalogue fixes iteratively until zero violations remain (refine). Detailed operation procedures, question payloads, and authoring requirements are in `ai/plugins/skf/knowledge/skill-design-guide.md`.

**Scope boundary**: This skill manages skill file structure and content only. It does NOT run or invoke skills, sync documentation, or modify files outside the skill directory without user approval.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Require explicit user approval before writing to disk — create Step 8 gate, refine write gate. WHY: unapproved writes silently corrupt the AI framework and are difficult to reverse.
2. Read `ai/plugins/skf/knowledge/skill-design-guide.md` in full before evaluating or refining — use multi-pass reads. WHY: partial reads produce false-pass verdicts.
3. Keep evaluate strictly read-only — do not modify the draft. WHY: mixing evaluation and fixing destroys the audit trail.
4. Fix ONLY items flagged ❌ or ⚠️ during refine — do not refactor passing content. WHY: unbounded editing introduces regressions.
5. Resolve `operation` before proceeding — if absent, call `vscode_askQuestions`. WHY: undefined operation produces undefined behavior.
6. Skill filename slug must match the group prefix (e.g., `meta-` skills start with `meta-`). WHY: consistent naming is required for skill discovery.
7. Use only tags from `ai/plugins/skf/knowledge/skill-tags.md`, 3–4 total, first tag a primary category tag. WHY: canonical tags enable discovery and routing.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your next step complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY each operation's named steps — no unrequested catalogue checks or bonus improvements.
- Apply each catalogue check independently and conservatively: ⚠️ when partially satisfied, ❌ when clearly violated, ✅ only when fully satisfied.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

Load `ai/plugins/skf/knowledge/skill-design-guide.md` at the start of any operation for tag checks and authoring requirements.

## Preflight

- Resolve `operation` before loading any files or taking actions.
- **create** state: file absent → proceed from Step 1; file has content → resume at the Step 7 review loop; user confirms no changes needed → report "Skill already exists" and stop.
- **refine** state: zero violations in report → skip to Step 4; no report provided → stop and request one.

## Done conditions

- **create**: approved skill file exists at target path, `skill-groups.md` updated, documentation sync triggered.
- **evaluate**: full scored report returned, no files modified.
- **refine**: corrected draft approved, written, re-evaluated to zero violations (or blocked items reported after retry limit).

## Operation: create

### Step 1 — Gather description

If `skill description` not provided, ask via `vscode_askQuestions` using the `skill_description` payload below.

### Step 2 — Assign group

Read `ai/plugins/skf/knowledge/skill-groups.md`. Show available groups. If `group` not provided, ask via `vscode_askQuestions` using the `skill_group` payload.

### Step 3 — Gather requirements

Collect in a single `vscode_askQuestions` call using the `skill_requirements` payload. Resolve: skill name, trigger phrases, output type, external dependencies, failure modes.

### Step 4 — Assign tags

Read `ai/plugins/skf/knowledge/skill-tags.md`. Recommend 3–4 tags (primary category tag first). Ask via `vscode_askQuestions` using the `skill_tags` payload. Validate all selected tags are canonical — reject and re-ask if any are not.

### Step 4.5 — Determine GitHub prompt exposure

Ask via `vscode_askQuestions` using the `skill_prompt_exposure` payload. If user selects "Yes — expose as GitHub prompt", note this for Step 8. Skills exposed as prompts will be added to the `.github/prompts/` generation workflow.

### Step 5 — Draft skill file

Read `ai/plugins/skf/templates/skill-template.md` as the scaffold. Consult `ai/plugins/skf/knowledge/skill-design-guide.md` for 8-section authoring requirements, required frontmatter fields (§4), and the 8-section quick reference table (§2). Produce a complete skill file — all 8 sections populated, no placeholders.

### Step 6 — Evaluate draft

Run `evaluate` internally on the draft. If ❌ errors exist, run `refine` internally before presenting.

### Step 7 — Review loop (bounded, max 5 iterations)

**Exit condition**: user approves or explicitly cancels.

Present draft and evaluation table. Ask via `vscode_askQuestions` using the `skill_draft_review` payload. Incorporate feedback, re-evaluate, re-present. Repeat until approved or cancelled.

> **If loop stalls after 5 iterations**: stop, report state, ask how to proceed.

### Step 8 — Write and confirm

⛔ **STOP — Approval gate required (Step 7 must return "Approve").**

1. Write `ai/plugins/skf/skills/{skill-name}.md` with approved content.
2. Update `ai/plugins/skf/knowledge/skill-groups.md`: add skill to group section, increment skill count.
3. If `skill_prompt_exposure` = "Yes — expose as GitHub prompt":
   - Generate `.github/prompts/{skill-name}.prompt.md` with YAML frontmatter (name, description, anti-scope) and body directing users to consult `ai/plugins/skf/skills/{skill-name}.md`.
   - Document that `ai/scripts/python/generate-prompt-files.py` will be updated to include this skill in automated prompt generation (coordinate with `/gov-update` for index sync).
   - Update `ai/scripts/python/generate-prompt-files.py` to include new skill github prompt in its flow
4. Confirm: "Skill `{skill-name}` created at `ai/plugins/skf/skills/{skill-name}.md`." Include prompt exposure status in confirmation. Signal documentation sync to orchestrator.

---

## Operation: evaluate

### Step 1 — Load rules

Read `ai/plugins/skf/knowledge/skill-design-guide.md` in full (multi-pass until response is shorter than page size).

> **If `skill-design-guide.md` cannot be read**: stop and report the path — do not proceed.

### Step 2 — Apply checks

Extract every catalogue entry from Section 10 (including the tag validation rules at the end of that section). Do not skip any entry — mark N/A if inapplicable. Produce a scored row per entry.

### Step 3 — Produce report

Produce the Evaluation Report defined in `<output_format>`. Do not suggest fixes or modify the draft.

---

## Operation: refine

### Step 1 — Load report and draft

Read the evaluation report and skill draft. Read `ai/plugins/skf/knowledge/skill-design-guide.md` in full.

> **If the evaluation report is absent**: stop and request it before proceeding.

### Step 2 — Check for violations

Zero ❌ and zero ⚠️ → skip to Step 4, return draft unchanged with note.

### Step 3 — Apply fixes (bounded, max 3 passes)

**Exit condition**: zero violations on re-evaluation.

For each ❌ and ⚠️: read the catalogue fix instruction, apply to the draft at the precise location. Do not fix beyond flagged items. Re-run evaluate internally after all fixes. Repeat until zero violations or max passes reached.

> **If violations remain after 3 passes**: stop, report remaining violations, ask how to proceed.

### Step 4 — Produce refined output

Produce the Refinement Summary defined in `<output_format>` followed by the full corrected draft.

⛔ **STOP — Call `vscode_askQuestions` before writing to disk.**

After writing, verify `skill-groups.md` reflects the updated skill definition.

## Question Payloads

Copy these verbatim when calling `vscode_askQuestions`. Replace `{placeholder}` values with context-derived recommendations before calling.

### `skill_description`

```json
{
  "header": "skill_description",
  "question": "Describe what this skill does — its purpose, inputs, outputs, and main operations.",
  "allowFreeformInput": true
}
```

### `skill_group`

```json
{
  "header": "skill_group",
  "question": "Which group should this skill belong to?",
  "options": [
    { "label": "meta — framework management" },
    { "label": "gov — governance and policy updates" },
    { "label": "qa — quality analysis and reporting" },
    { "label": "spec — specification creation and review" },
    { "label": "plan — planning and task breakdown" },
    { "label": "impl — implementation and execution" },
    { "label": "util — utility (cross-skill services)" }
  ],
  "allowFreeformInput": true
}
```

### `skill_requirements`

```json
{
  "header": "skill_requirements",
  "question": "Complete the requirements for the new skill.",
  "allowFreeformInput": true
}
```

Resolve in one pass: (1) skill name (lowercase-hyphenated with group prefix), (2) trigger phrases, (3) output type (file / report / update / other), (4) external dependencies (scripts called, templates read), (5) failure modes.

### `skill_tags`

```json
{
  "header": "skill_tags",
  "question": "Select skill tags (3\u20134, primary category tag first). Recommended: {category_tag}, {tag1}, {tag2}, {tag3}",
  "options": [
    { "label": "{category_tag}", "recommended": true },
    { "label": "{supporting_tag_1}" },
    { "label": "{supporting_tag_2}" },
    { "label": "{supporting_tag_3}" }
  ],
  "multiSelect": true,
  "allowFreeformInput": true
}
```

Replace `{category_tag}` and `{tag1}`\u2013`{tag3}` with recommendations derived from the skill's purpose and group. After the user responds, validate every selected tag against `skill-tags.md`. Reject non-canonical tags and re-ask \u2014 do not accept a tag that is not in the canonical vocabulary.
### `skill_prompt_exposure`

```json
{
  "header": "skill_prompt_exposure",
  "question": "Should this skill be exposed as a user-facing GitHub command/prompt?",
  "options": [
    { "label": "Yes — expose as GitHub prompt", "description": "Add to .github/prompts/ and generate-prompt-files.py workflow" },
    { "label": "No — internal dispatch only", "description": "Skill used by orchestrator/other skills, not direct user command" }
  ],
  "allowFreeformInput": false
}
```
### `skill_draft_review`

```json
{
  "header": "skill_draft_review",
  "question": "Review the skill draft above. How would you like to proceed?",
  "options": [
    { "label": "Approve \u2014 write to disk", "recommended": true },
    { "label": "Change steps" },
    { "label": "Adjust outputs" },
    { "label": "Add rules" },
    { "label": "Fix description" },
    { "label": "Something else" }
  ],
  "allowFreeformInput": true
}
```


</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **vscode_askQuestions**: All user input and approval gates — required, do not prompt via plain text.
- **read_file**: Load `skill-design-guide.md`, `skill-groups.md`, `skill-tags.md`, `skill-template.md`, and skill drafts. Read to end of file for catalogues and rule sources.
- **file_search**: Locate existing skill files or verify directory paths before creating.
- **create_file**: Write approved skill files — create Step 8 only, after approval gate.
- **replace_string_in_file**: Apply corrections to existing skill files — refine Step 3 only, after write gate.
- Do NOT use tools not listed here unless explicitly escalating.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `meta-skill-manage` |
| wave | `2` |
| step | `N.M` |
| output_path | path or `null` |
| summary | one-line summary |

**create**:
```
Skill `{skill-name}` created at `ai/plugins/skf/skills/{skill-name}.md`.
skill-groups.md updated: {group} count incremented.
```

**evaluate**:
```
## Evaluation Report: {skill-name}
Overall: ✅ Pass / ⚠️ Warnings / ❌ Failures

| ID | Rule | Status | Finding |
|----|------|--------|---------|
| CAT-NNN | {rule} | ✅/⚠️/❌/N/A | {finding} |

Errors (❌): N | Warnings (⚠️): N | Passed (✅): N | N/A: N

### Findings
{Each ❌ and ⚠️ with catalogue ID, rule, and location in draft}
```
Read-only — no fix suggestions included.

**refine**:
```
## Refinement Summary: {skill-name}
Violations fixed: N

| Fix | Catalogue ID | Location | Change |
|-----|-------------|----------|---------|

## Final Evaluation
{All ✅ or N/A}
```
Followed by full corrected skill file draft.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: Create a new implementation skill for summarising deployment logs.
Expected behavior: Asks for description (if not inline), reads skill-groups.md and assigns group, gathers requirements via single question call, reads skill-tags.md and confirms tag set, reads skill-template.md and skill-design-guide.md to draft complete 8-section file, runs evaluate internally (all ✅), presents draft for review, on Approve writes file, updates skill-groups.md, signals documentation sync.
</example>

<example>
Input: Evaluate skill draft at `ai/plugins/skf/skills/{candidate-skill}.md`.
Expected behavior: Reads skill-design-guide.md in full (multi-pass). Applies all catalogue entries including tag validation rules in Section 10 — ✅/⚠️/❌/N/A per row. Returns scored evaluation report with summary counts and findings. No files modified.
</example>

<example type="counter">
Input: Evaluate a skill and fix any issues you find.
Expected behavior: Declines to combine operations. Responds: "evaluate is strictly read-only. I'll run evaluate and return the violation report. To apply fixes, invoke the refine operation with that report. Shall I run evaluate now?"
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never write to disk without explicit user approval** — create Step 8 gate and refine write gate are mandatory.
- **Never modify the draft during evaluate** — evaluate is read-only; fixes belong in refine.
- **Always read `skill-design-guide.md` in full** — never act on a partial read of a catalogue or ruleset.
- **Always validate tags against the canonical vocabulary** — reject non-canonical tags, ensure 3–4 tags with a primary category tag first.

</reminders>