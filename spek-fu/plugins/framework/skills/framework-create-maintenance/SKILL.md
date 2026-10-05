---
name: framework-create-maintenance
description: "Create a maintenance skill for a specified plugin that gathers its full context and keeps it self-consistent."
---

# Framework Create Maintenance

Scaffolds a `<plugin>-maintenance` skill for a target plugin — the entrypoint for changing that plugin itself and auditing its integrity.

Skill format spec: `spek-fu/plugins/framework/knowledge/skill-design-guide.md`
Skill template: `spek-fu/plugins/framework/templates/skill-template.md`
Maintenance skill template: `spek-fu/plugins/framework/templates/maintenance-skill-template.md`
File inventory template: `spek-fu/plugins/framework/templates/file-inventory-template.md`

<inputs>

## Inputs

- Target plugin name (must already exist under `spek-fu/plugins/`)

</inputs>

<outputs>

## Outputs

- A new `SKILL.md` at `spek-fu/plugins/<plugin>/skills/<plugin>-maintenance/SKILL.md`
- `spek-fu/plugins/<plugin>/knowledge/file-inventory.md` — created from the template if missing, left untouched if already present
- A pointer file at `.claude/skills/<plugin>-maintenance/SKILL.md`
- A pointer file at `.github/skills/<plugin>-maintenance/SKILL.md`
- A "How to use" bullet added to `spek-fu/plugins/<plugin>/<plugin>-workflow.md` announcing the new maintenance skill

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never scaffold a maintenance skill for a plugin that doesn't exist under `spek-fu/plugins/` — halt and ask the user to confirm the name (constitution `## AI Principles` → Ambiguity).
- Never invent an integrity check the target plugin has no matching file or script for — a registry or self-check-command bullet is included only when discovered during inventory.
- Never skip the file-inventory bootstrap — every maintained plugin must have a `knowledge/file-inventory.md` before its maintenance skill is written.
- Follow the skill-design-guide's section order and 150-line limit exactly, same as `framework-create-skill`.
- Do not duplicate content already present in the constitution or the target plugin's existing knowledge files — reference it instead.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every rule, step, and check written for the new maintenance skill uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Self-Auditing Plugins** — every plugin gets a maintenance skill, so integrity auditing is a first-class habit for the whole framework.

</behavioral_anchors>

<workflow>

## Steps

### 1. Gather the target plugin

Confirm `spek-fu/plugins/<plugin>/` exists. If missing or ambiguous, halt and ask the user to confirm or pick a different plugin.

### 2. Inventory the plugin

List `agents/`, `knowledge/`, `scripts/`, `skills/`, `templates/`, and the `<plugin>-workflow.md` file. Note:

- Any knowledge file that is a controlled vocabulary/registry a skill validates against.
- Any script exposing a self-check/doctor-style command.
- Whether `knowledge/file-inventory.md` already exists.

### 3. Bootstrap the file inventory

If `knowledge/file-inventory.md` is missing, create it from `spek-fu/plugins/framework/templates/file-inventory-template.md`, filling one-line entries for every file found in step 2, omitting empty-folder sections. If it already exists, leave it as-is.

### 4. Draft the maintenance skill

Fill `spek-fu/plugins/framework/templates/maintenance-skill-template.md`, using `doc-engine-maintenance/SKILL.md` as the structural exemplar:

- `name`/`description`/title use the target plugin's name.
- "Read plugin context" step points at the plugin's own workflow file and `file-inventory.md`.
- Integrity checks always include file-inventory + workflow-doc; add one bullet per registry/script discovered in step 2; omit both conditional bullets entirely if none exist.

### 5. Split if oversized

Same rule as `framework-create-skill`: if the draft exceeds 150 lines, move overflow to a `spek-fu/plugins/<plugin>/knowledge/` or `templates/` file and replace it in the skill with a one-line pointer. Recount; repeat until under 150 lines.

### 6. Create the files

Write the final `SKILL.md`, and the bootstrapped `file-inventory.md` if step 3 created one.

### 7. Create pointer files

Run `python spek-fu/plugins/framework/scripts/regenerate-pointer-files.py` to (re)generate `.claude/skills/<plugin>-maintenance/SKILL.md` and `.github/skills/<plugin>-maintenance/SKILL.md` from the new skill's frontmatter.

### 8. Register in the workflow doc

Add a "How to use" bullet to `spek-fu/plugins/<plugin>/<plugin>-workflow.md` naming the new `<plugin>-maintenance` skill and its trigger condition, mirroring `doc-engine-workflow.md`'s own maintenance bullet.

### 9. Self-validate

Check the new skill against the skill-design-guide's `## Checklist for a new skill`, plus: every file or script named in the drafted integrity checks actually exists in the plugin.

</workflow>

<done_conditions>

## Done Conditions

- `SKILL.md` exists at `spek-fu/plugins/<plugin>/skills/<plugin>-maintenance/SKILL.md`, under 150 lines.
- `spek-fu/plugins/<plugin>/knowledge/file-inventory.md` exists.
- Pointer files exist at `.claude/skills/<plugin>-maintenance/SKILL.md` and `.github/skills/<plugin>-maintenance/SKILL.md`.
- `<plugin>-workflow.md`'s "How to use" section lists the new maintenance skill.
- Every integrity check in the drafted skill references a real file or script in the plugin.

</done_conditions>
