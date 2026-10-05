---
name: <plugin>-maintenance
description: "Maintain the <plugin> plugin itself and verify the whole plugin is intact."
---

# <Plugin Title> Maintenance

Main entrypoint for updating the <plugin> plugin. Also verifies the whole plugin is intact.

## When to use

Use whenever the <plugin> plugin itself must change: a skill/agent is added, renamed, or removed; scripts, knowledge files, or templates change; or the plugin's integrity needs auditing.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Updated <plugin> plugin
- Verified <plugin> plugin integrity

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

- Always verify the integrity of the <plugin> plugin after making any changes.
- Ensure that the file inventory, workflow doc, <REGISTRY_OR_SCRIPT_ARTIFACTS> and scripts are all up to date and consistent.
- Follow the rules outlined in the constraints section, especially regarding terseness and verification of file existence.

</behavioral_anchors>

<workflow>

## Flow

### 1. Read plugin context

Read `spek-fu/plugins/<plugin>/<plugin>-workflow.md` (glossary and command reference) and `spek-fu/plugins/<plugin>/knowledge/file-inventory.md` (one-line description of every plugin file). These give the high-level map of the plugin before anything is touched.

### 2. Execute the user's request

Make the requested change, then run the integrity checks below before finishing.

### 3. Integrity checks

Run after any plugin change.

- **File inventory** — `spek-fu/plugins/<plugin>/knowledge/file-inventory.md`
  - Add, remove, or update entries for any file added, removed, or repurposed.
  - One-sentence description of every file in the <plugin> plugin.
  - Each section describes all files in that specific folder.
  - Files located in subfolders have the folder name in their path definition.

- **Workflow doc** — `spek-fu/plugins/<plugin>/<plugin>-workflow.md`
  - "How to use" section must list every skill with a one-line trigger condition.
  - Glossary must define any new term introduced.
  - Commands must be up to date and reflect all of the plugin's scripts' functionalities.

<!-- ONE BULLET PER REGISTRY FILE DISCOVERED DURING INVENTORY, NAMED EXPLICITLY. OMIT ENTIRELY IF THE PLUGIN HAS NONE.
- **<Registry name>** — if a change affects <what the registry controls>, confirm `spek-fu/plugins/<plugin>/knowledge/<registry-file>` still covers them.
-->

<!-- ONE BULLET IF THE PLUGIN'S SCRIPTS EXPOSE A SELF-CHECK/DOCTOR COMMAND. OMIT ENTIRELY IF NONE EXISTS.
- **Scripts** — run `<self-check command>` to confirm the plugin's tooling is still valid.
-->

### 4. Sync the framework README

Run the `framework-readme` skill to keep `spek-fu/README.md` in sync with this change.

</workflow>

<done_conditions>

## Done Conditions

- The <plugin> plugin has been updated and verified for integrity.

</done_conditions>
