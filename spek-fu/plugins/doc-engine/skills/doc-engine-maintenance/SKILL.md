---
name: doc-engine-maintenance
description: "Maintain the doc-engine plugin itself and verify the whole framework is intact."
---

# Doc-Engine Maintenance

Main entrypoint for updating the doc-engine plugin. Also verifies the whole framework is intact.

## When to use

Use whenever the doc-engine plugin itself must change: a skill/agent is added, renamed, or removed; scripts, knowledge files, or templates change; or the framework's integrity needs auditing.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs
- Updated doc-engine plugin
- Verified doc-engine plugin integrity

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

- Always verify the integrity of the doc-engine plugin after making any changes.
- Ensure that the file inventory, workflow doc, tags registry, and scripts are all up to date and consistent.
- Follow the rules outlined in the constraints section, especially regarding terseness and verification of file existence.

</behavioral_anchors>

<workflow>

## Flow

### 1. Read plugin context

Read `spek-fu/plugins/doc-engine/doc-engine-workflow.md` (glossary and command reference) and `spek-fu/plugins/doc-engine/knowledge/file-inventory.md` (one-line description of every plugin file). These give the high-level map of the plugin before anything is touched.

### 2. Execute the user's request

Make the requested change, then run the integrity checks below before finishing.

### 3. Integrity checks

Run after any plugin change.

- **File inventory** — `spek-fu/plugins/doc-engine/knowledge/file-inventory.md`
  - Add, remove, or update entries for any file added, removed, or repurposed.
  - One-sentence description of every file in the doc-engine plugin.
  - Each section describes all files in that specific folder. 
  - File located in subfolders have the folder name in their path definition.

- **Workflow doc** — `spek-fu/plugins/doc-engine/doc-engine-workflow.md` 
  - "How to use" section must list every skill with a one-line trigger condition.
  - Glossary must define any new term introduced.
  - Commands must be up to date and reflect all of the doc-engines's scripts functionalities.

- **Tags registry** — if a change affects doc module tags, confirm `spek-fu/plugins/doc-engine/knowledge/tags.registry.json` still covers them.

- **Scripts** — run `python spek-fu/plugins/doc-engine/scripts/dokfu.py doctor` to confirm the documentation system (index, pointers, tags) is still valid.

### 4. Sync the framework README

Run the `framework-readme` skill to keep `spek-fu/README.md` in sync with this change.

</workflow>

<done_conditions>

## Done Conditions

- The doc-engine plugin has been updated and verified for integrity.

</done_conditions>




