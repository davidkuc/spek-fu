---
name: framework-create-skill
description: "Create a new skill file for a plugin from user requirements, following the skill design guide and template."
---

# Framework Create Skill

Create a new skill file for a plugin from user requirements, following the skill design guide and template.

Format specification: `spek-fu/plugins/framework/knowledge/skill-design-guide.md`
Template: `spek-fu/plugins/framework/templates/skill-template.md`

<inputs>

## Inputs

- User's requirements for the skill (purpose, trigger, inputs/outputs, rules, workflow steps)
- Target plugin the skill belongs to (e.g. `doc-engine`, `framework`)

</inputs>

<outputs>

## Outputs

- A new `SKILL.md` at `spek-fu/plugins/<plugin>/skills/<skill-name>/SKILL.md`
- Any new knowledge files at `spek-fu/plugins/<plugin>/knowledge/*.md` (only if needed)
- Any new template files at `spek-fu/plugins/<plugin>/templates/*.md` (only if needed)
- A pointer file at `.claude/skills/<skill-name>/SKILL.md`
- A pointer file at `.github/skills/<skill-name>/SKILL.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never write a `SKILL.md` without first reading the skill design guide and template.
- Never invent a section structure — follow the template's section order exactly; omit only sections marked optional.
- Never skip clarification: if any required input is missing or ambiguous, ask the user before drafting (constitution `## AI Principles` → Ambiguity).
- A `SKILL.md` MUST NOT exceed 150 lines. If a draft exceeds this, move detailed reference material to a knowledge file and reusable boilerplate to a template file, replacing it in the skill with a one-line pointer to the new file's path.
- Knowledge and template files always live under the target plugin's shared `knowledge/` and `templates/` folders, never inside the skill's own folder.
- Skill folder and `name` frontmatter must match, kebab-case, prefixed with the target plugin name.
- Do not duplicate content already present in the constitution or the target plugin's existing knowledge files — reference it instead.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every rule, step, and pillar written for the new skill uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Slim Skills** — a `SKILL.md` is a short entry point; anything that would push it over 150 lines belongs in a knowledge or template file instead.

</behavioral_anchors>

<workflow>

## Steps

### 1. Gather requirements

Collect from the user, asking clarification questions in loops until each is unambiguous:

- Target plugin (must exist under `spek-fu/plugins/`)
- Skill name (kebab-case, prefixed with the plugin name)
- One-sentence description
- Trigger condition (when the skill should be used)
- Expected inputs and outputs
- Hard rules / constraints specific to the skill
- Workflow steps (what the skill actually does, in order)
- Done conditions (how to know the task is complete)

Do not proceed to drafting while any of the above is missing or unclear.

### 2. Read references

Read `spek-fu/plugins/framework/knowledge/skill-design-guide.md` and `spek-fu/plugins/framework/templates/skill-template.md` in full before drafting.

### 3. Check for shared conventions

List existing skills under `spek-fu/plugins/<plugin>/skills/` and skim their frontmatter and section names to keep tone and terminology consistent within the plugin. Do not copy their rules verbatim unless the user's requirements genuinely overlap.

### 4. Draft the skill

Fill the template's sections in order (title/summary, `When to use` if the name doesn't make the trigger obvious, `<inputs>`, `<outputs>`, `<constraints>`, `<behavioral_anchors>` if applicable, `<workflow>`, `<done_conditions>`) using the gathered requirements. Keep prose within constitution terseness limits.

### 5. Split if oversized

Count the drafted file's lines. If it exceeds 150:

1. Identify the largest self-contained block that isn't core workflow logic (e.g. a format spec, a long example, boilerplate structure).
2. Move it to `spek-fu/plugins/<plugin>/knowledge/<topic>.md` (reference material) or `spek-fu/plugins/<plugin>/templates/<topic>.md` (reusable boilerplate to fill in).
3. Replace the moved block in the skill with a one-line pointer: `` `spek-fu/plugins/<plugin>/knowledge/<topic>.md` ``.
4. Recount; repeat until under 150 lines.

### 6. Create the files

Write the final `SKILL.md` and any split-out knowledge/template files to disk.

### 7. Create pointer files

Run `python spek-fu/plugins/framework/scripts/regenerate-pointer-files.py` to (re)generate `.claude/skills/<skill-name>/SKILL.md` and `.github/skills/<skill-name>/SKILL.md` from the new skill's frontmatter.

### 8. Self-validate

Check the new skill against the skill-design-guide's `## Checklist for a new skill`. Report any unmet item and fix it before finishing.

</workflow>

<done_conditions>

## Done Conditions

- `SKILL.md` exists at `spek-fu/plugins/<plugin>/skills/<skill-name>/SKILL.md`, under 150 lines.
- All template sections present in the correct order; optional sections included only when needed.
- Any overflow content lives in a plugin knowledge/template file, referenced from the skill by path.
- Pointer files exist at `.claude/skills/<skill-name>/SKILL.md` and `.github/skills/<skill-name>/SKILL.md`.
- The skill-design-guide checklist passes for the new skill.

</done_conditions>
