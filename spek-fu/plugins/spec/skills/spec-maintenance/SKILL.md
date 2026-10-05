---
name: spec-maintenance
description: "Maintain the spec plugin itself and verify the whole plugin is intact."
---

# Spec Maintenance

Main entrypoint for updating the spec plugin. Also verifies the whole plugin is intact.

## When to use

Use whenever the spec plugin itself must change: a skill/agent is added, renamed, or removed; knowledge files or templates change; or the plugin's integrity needs auditing.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Updated spec plugin
- Verified spec plugin integrity

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

- Always verify the integrity of the spec plugin after making any changes.
- Ensure that the file inventory, workflow doc, and knowledge registries are all up to date and consistent.
- Follow the rules outlined in the constraints section, especially regarding terseness and verification of file existence.

</behavioral_anchors>

<workflow>

## Flow

### 1. Read plugin context

Read `spek-fu/plugins/spec/spec-workflow.md` (glossary and phase/skill map) and `spek-fu/plugins/spec/knowledge/file-inventory.md` (one-line description of every plugin file). These give the high-level map of the plugin before anything is touched.

### 2. Execute the user's request

Make the requested change, then run the integrity checks below before finishing.

### 3. Integrity checks

Run after any plugin change.

- **File inventory** — `spek-fu/plugins/spec/knowledge/file-inventory.md`
  - Add, remove, or update entries for any file added, removed, or repurposed.
  - One-sentence description of every file in the spec plugin.
  - Each section describes all files in that specific folder.
  - Files located in subfolders have the folder name in their path definition.

- **Workflow doc** — `spek-fu/plugins/spec/spec-workflow.md`
  - "How to use" section must list every skill with a one-line trigger condition, and keep the Define/Research/Plan/Implement ordering intact.
  - Glossary must define any new term introduced.
  - Commands must be up to date and reflect all of the plugin's scripts' functionalities.

- **Skill config registry** — if a change adds, renames, or removes a skill's tunable limits, confirm `spek-fu/plugins/spec/knowledge/config.json` still covers them.

- **Ambiguity taxonomy** — if a change affects the categories `spec-clarification` scans for, confirm `spek-fu/plugins/spec/knowledge/ambiguity-taxonomy.md` still covers them.

- **Orchestration format** — if a change affects how `spec-orchestrator` sequences or reports task dispatch, confirm `spek-fu/plugins/spec/knowledge/orchestration-format.md` still matches.

- **Pipeline artifacts registry** — if a change adds, renames, or removes a pipeline artifact, confirm `spek-fu/plugins/spec/knowledge/pipeline-artifacts.md` still covers it.

- **Spec sync contract** — if a change affects how spec artifacts stay in sync with upstream documents, confirm `spek-fu/plugins/spec/knowledge/spec-sync-contract.md` still matches.

- **TDD design taxonomy** — if a change affects the categories `spec-tdd-draft` classifies findings against, confirm `spek-fu/plugins/spec/knowledge/tdd-design-taxonomy.md` still covers them.

- **Testability taxonomy** — if a change affects the categories `spec-testability-draft` classifies findings against, confirm `spek-fu/plugins/spec/knowledge/testability-taxonomy.md` still covers them.

### 4. Sync the framework README

Run the `framework-readme` skill to keep `spek-fu/README.md` in sync with this change.

</workflow>

<done_conditions>

## Done Conditions

- The spec plugin has been updated and verified for integrity.

</done_conditions>
