---
name: framework-create-plugin
description: "Ask clarification questions and scaffold a new plugin's folder structure with a draft workflow file."
---

# Framework Create Plugin

Scaffolds a new plugin under `spek-fu/plugins/<plugin-name>/` and drafts its `*-workflow.md` entry point.

Plugin structure spec (SSOT): `spek-fu/README.md` → `## Plugin Structure`.
Workflow template: `spek-fu/plugins/framework/templates/workflow-template.md`

<inputs>

## Inputs

- Plugin name (kebab-case)
- One-sentence purpose/description of the plugin
- Whether an initial agent is wanted, and its name/purpose (created later, not by this skill)
- Whether an initial skill is wanted, and its name/purpose (delegated to `framework-create-skill` after scaffold)
- List of commands/scripts the plugin will expose, if known

</inputs>

<outputs>

## Outputs

- New folders `agents/`, `knowledge/`, `scripts/`, `skills/`, `templates/` under `spek-fu/plugins/<plugin-name>/`
- A draft `spek-fu/plugins/<plugin-name>/<plugin-name>-workflow.md`, copied from the workflow template

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never skip clarification: if plugin name or purpose is missing or ambiguous, ask the user before scaffolding (constitution `## AI Principles` → Ambiguity).
- Never overwrite an existing plugin — if `spek-fu/plugins/<plugin-name>/` already exists, halt and ask the user to confirm or rename.
- Never create an initial agent or skill yourself — record the requested name/purpose as a note in the drafted workflow file for later manual creation.
- Empty scaffolded folders are left untracked (no `.gitkeep`) — they populate naturally as skills/agents/scripts are added.

</constraints>

<workflow>

## Steps

### 1. Gather requirements

Ask in loops until unambiguous:

- Plugin name (kebab-case)
- One-sentence purpose
- Known commands/scripts the plugin will expose (or none yet)

### 2. Check for collision

Check `spek-fu/plugins/<plugin-name>/` doesn't already exist. If it does, halt and ask the user to confirm reuse or pick a different name.

### 3. Scaffold folders

Create `spek-fu/plugins/<plugin-name>/agents/`, `knowledge/`, `scripts/`, `skills/`, `templates/`.

### 4. Draft the workflow file

Copy `spek-fu/plugins/framework/templates/workflow-template.md` to `spek-fu/plugins/<plugin-name>/<plugin-name>-workflow.md`, then:

- Title: plugin name + one-sentence purpose.
- `## How to use`: short prose on the entry point, followed by a bullet per skill (once skills exist).
- `### Choosing the right skill`: a situation → skill bullet list or table; leave empty (with a `TODO` comment) if no skills exist yet.
- `## Commands reference`: a `| Command | Purpose |` table filled with any known commands, or left with just the header if none yet.
- If an initial agent or skill was requested, add a bullet note under `## How to use` recording its name/purpose for later creation (with a `TODO` comment).

### 5. Self-validate

Confirm all 5 folders exist, the workflow file exists and follows the template's section order, and no plugin-structure spec was duplicated from the README.

</workflow>

<done_conditions>

## Done Conditions

- `spek-fu/plugins/<plugin-name>/` contains all 5 subfolders.
- `spek-fu/plugins/<plugin-name>/<plugin-name>-workflow.md` exists with Title, Glossary, How to use (with Choosing the right skill), and Commands reference sections.
- Any requested agent/skill is recorded as a note, not fabricated by this skill.

</done_conditions>
