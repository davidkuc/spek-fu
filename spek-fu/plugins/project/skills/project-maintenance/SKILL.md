---
name: project-maintenance
description: "Maintain the project plugin itself and verify the whole plugin is intact."
---

# Project Maintenance

Main entrypoint for updating the project plugin. Also verifies the whole plugin is intact.

## When to use

Use whenever the project plugin itself must change: a skill is added, renamed, or removed; templates change; or the plugin's integrity needs auditing.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Updated project plugin
- Verified project plugin integrity

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Terseness rules from the constitution apply to every file this skill touches: file-inventory entries stay one sentence, glossary entries stay short.
- Do not assume a pointer or inventory entry is missing — verify with a directory listing first.
- Never change or reuse an area's ID prefix; retire the registry row instead.

</constraints>

<behavioral_anchors>

## Behavioral Anchors

- Always verify the integrity of the project plugin after making any changes.
- Ensure that the file inventory and workflow doc are up to date and consistent.
- Follow the rules outlined in the constraints section, especially regarding terseness and verification of file existence.

</behavioral_anchors>

<workflow>

## Flow

### 1. Read plugin context

Read `spek-fu/plugins/project/project-workflow.md` (glossary and command reference) and `spek-fu/plugins/project/knowledge/file-inventory.md` (one-line description of every plugin file). These give the high-level map of the plugin before anything is touched.

Also read `knowledge/area-registry.md` and `knowledge/feature-format.md` for the area and feature-ID rules.

### 2. Execute the user's request

Make the requested change, then run the integrity checks below before finishing.

### 3. Integrity checks

Run after any plugin change.

- **File inventory** — `spek-fu/plugins/project/knowledge/file-inventory.md`
  - Add, remove, or update entries for any file added, removed, or repurposed.
  - One-sentence description of every file in the project plugin.
  - Each section describes all files in that specific folder.
  - Files located in subfolders have the folder name in their path definition.

- **Workflow doc** — `spek-fu/plugins/project/project-workflow.md`
  - "Choosing the right skill" section must list every skill with a one-line trigger condition.
  - Glossary must define any new term introduced.
  - Commands must be up to date and reflect all of the plugin's scripts' functionalities.

- **Area registry** — `spek-fu/plugins/project/knowledge/area-registry.md`
  - Every file in `spek-fu/project/project-docs/` has a row, and every row's file exists.
  - Prefixes are unique and unchanged.

- **Feature format** — `spek-fu/plugins/project/knowledge/feature-format.md`
  - Ensure that the feature format rules are followed and that any new features or changes comply with the established format.

### 4. Sync the framework README

Run the `framework-readme` skill to keep `spek-fu/README.md` in sync with this change.

</workflow>

<done_conditions>

## Done Conditions

- The project plugin has been updated and verified for integrity.

</done_conditions>
