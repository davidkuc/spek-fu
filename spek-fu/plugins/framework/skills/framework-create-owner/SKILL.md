---
name: framework-create-owner
description: "Scaffold a <plugin>-owner facade skill that routes requests to a plugin's sub-skills by reading its workflow file."
---

# Framework Create Owner

Scaffolds a `<plugin>-owner` skill for a target plugin — the facade entrypoint that routes free-form requests to whichever sub-skill(s) apply.

Skill format spec: `spek-fu/plugins/framework/knowledge/skill-design-guide.md`
Skill template: `spek-fu/plugins/framework/templates/skill-template.md`
Owner skill template: `spek-fu/plugins/framework/templates/owner-skill-template.md`

<inputs>

## Inputs

- Target plugin name (must already exist under `spek-fu/plugins/` with a `<plugin>-workflow.md`)

</inputs>

<outputs>

## Outputs

- A new `SKILL.md` at `spek-fu/plugins/<plugin>/skills/<plugin>-owner/SKILL.md`
- A pointer file at `.claude/skills/<plugin>-owner/SKILL.md`
- A pointer file at `.github/skills/<plugin>-owner/SKILL.md`
- A "Choosing the right skill" bullet added to `spek-fu/plugins/<plugin>/<plugin>-workflow.md`, listed first

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never scaffold an owner skill for a plugin that doesn't exist under `spek-fu/plugins/`, or that has no `<plugin>-workflow.md` yet — halt and ask the user to confirm (constitution `## AI Principles` → Ambiguity).
- The drafted owner skill must never hardcode the plugin's sub-skill list or trigger conditions — it always reads them fresh from `<plugin>-workflow.md` at run time.
- Follow the skill-design-guide's section order and 150-line limit exactly, same as `framework-create-skill`.
- Do not duplicate content already present in the constitution or the target plugin's existing knowledge files — reference it instead.
- If the plugin already has an owner skill, halt and ask the user to confirm before overwriting it.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every rule, step, and pillar written for the new owner skill uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**SSOT Routing** — every owner skill built by this skill reads its plugin's routing table fresh from `<plugin>-workflow.md`; this skill never bakes a snapshot of that list into the drafted file.

</behavioral_anchors>

<workflow>

## Steps

### 1. Gather the target plugin

Confirm `spek-fu/plugins/<plugin>/` and `spek-fu/plugins/<plugin>/<plugin>-workflow.md` exist. If missing or ambiguous, halt and ask the user to confirm or pick a different plugin. If `spek-fu/plugins/<plugin>/skills/<plugin>-owner/` already exists, halt and confirm before overwriting.

### 2. Read references

Read `spek-fu/plugins/framework/knowledge/skill-design-guide.md` and `spek-fu/plugins/framework/templates/owner-skill-template.md` in full before drafting.

### 3. Draft the owner skill

Fill `owner-skill-template.md` with the target plugin's name throughout (`name`, title, all `<plugin>` references). Leave the "When to use" line generic — it must describe the plugin's domain only by pointing at `<plugin>-workflow.md`, never by enumerating its skills inline.

### 4. Split if oversized

Same rule as `framework-create-skill`: if the draft exceeds 150 lines, move overflow to a `spek-fu/plugins/<plugin>/knowledge/` file and replace it with a one-line pointer. Recount; repeat until under 150 lines.

### 5. Create the files

Write the final `SKILL.md` to `spek-fu/plugins/<plugin>/skills/<plugin>-owner/SKILL.md`.

### 6. Create pointer files

Run `python spek-fu/plugins/framework/scripts/regenerate-pointer-files.py` to (re)generate `.claude/skills/<plugin>-owner/SKILL.md` and `.github/skills/<plugin>-owner/SKILL.md`.

### 7. Register in the workflow doc

Add `<plugin>-owner` as the first bullet under `<plugin>-workflow.md`'s "Choosing the right skill" section, describing it as the facade entrypoint.

### 8. Self-validate

Check the new skill against the skill-design-guide's `## Checklist for a new skill`, plus: confirm the drafted skill contains no hardcoded skill names or trigger conditions outside of referencing `<plugin>-workflow.md`.

</workflow>

<done_conditions>

## Done Conditions

- `SKILL.md` exists at `spek-fu/plugins/<plugin>/skills/<plugin>-owner/SKILL.md`, under 150 lines.
- Pointer files exist at `.claude/skills/<plugin>-owner/SKILL.md` and `.github/skills/<plugin>-owner/SKILL.md`.
- `<plugin>-workflow.md`'s "Choosing the right skill" section lists `<plugin>-owner` as its first bullet.
- The drafted skill reads its plugin's skill list fresh from `<plugin>-workflow.md` rather than hardcoding it.

</done_conditions>
