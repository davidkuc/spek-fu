---
name: framework-maintenance
description: "Maintain the framework plugin itself and verify the whole plugin is intact."
---

# Framework Maintenance

Main entrypoint for updating the framework plugin. Also verifies the whole plugin is intact.

## When to use

Use whenever the framework plugin itself must change: a skill is added, renamed, or removed; scripts, knowledge files, or templates change; or the plugin's integrity needs auditing.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Updated framework plugin
- Verified framework plugin integrity

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Terseness rules from the constitution apply to every file this skill touches: file-inventory entries stay one sentence, glossary entries stay short.
- Do not assume a pointer or inventory entry is missing — verify with a directory listing first.

</constraints>

<behavioral_anchors>

## Behavioral Anchors

- Always verify the integrity of the framework plugin after making any changes.
- Ensure that the file inventory and workflow doc are up to date and consistent.
- Follow the rules outlined in the constraints section, especially regarding terseness and verification of file existence.

</behavioral_anchors>

<workflow>

## Flow

### 1. Read plugin context

Read `spek-fu/plugins/framework/framework-workflow.md` (glossary and command reference) and `spek-fu/plugins/framework/knowledge/file-inventory.md` (one-line description of every plugin file). These give the high-level map of the plugin before anything is touched.

### 2. Execute the user's request

Make the requested change, then run the integrity checks below before finishing.

### 3. Integrity checks

Run after any plugin change.

- **File inventory** — `spek-fu/plugins/framework/knowledge/file-inventory.md`
  - Add, remove, or update entries for any file added, removed, or repurposed.
  - One-sentence description of every file in the framework plugin.
  - Each section describes all files in that specific folder.
  - Files located in subfolders have the folder name in their path definition.

- **Workflow doc** — `spek-fu/plugins/framework/framework-workflow.md`
  - "How to use" section must list every skill with a one-line trigger condition.
  - Glossary must define any new term introduced.
  - Commands must be up to date and reflect all of the plugin's scripts' functionalities.

### 4. Sync the framework README

Run the `framework-readme` skill to keep `spek-fu/README.md` in sync with this change.

</workflow>

<done_conditions>

## Done Conditions

- The framework plugin has been updated and verified for integrity.

</done_conditions>
