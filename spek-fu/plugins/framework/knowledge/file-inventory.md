# Framework File Inventory

## Plugin Root

- `framework-workflow.md` - Top-level glossary and command reference explaining the framework plugin and how to choose between its skills.

## knowledge/

- `agent-design-guide.md` - Format specification for writing an `AGENT.md` file.
- `compound-knowledge.md` - Shared log of `L-{id}` learnings recorded across plugin work.
- `compound-patterns.md` - Shared log of `P-{id}` patterns extracted from recurring compound-knowledge entries.
- `skill-design-guide.md` - Format specification for writing a `SKILL.md` file.

## scripts/

- `export-framework.py` - Exports a fresh copy of the framework to `spek-fu-export/` or into an existing project, then regenerates pointer files.
- `regenerate-pointer-files.py` - Rewrites every `.claude`/`.github` skill and agent pointer file from its source `SKILL.md`/`AGENT.md`, and deletes stale ones.

## skills/

- `framework-compounding-patterns/SKILL.md` - Extracts recurring patterns from `compound-knowledge.md` and merges the duplicate learnings that fed them.
- `framework-compounding-read/SKILL.md` - Matches input against `compound-knowledge.md` and returns the relevant learnings.
- `framework-compounding-write/SKILL.md` - Appends one or more learnings as stable-ID entries to `compound-knowledge.md`.
- `framework-create-agent/SKILL.md` - Creates a new `AGENT.md` file for a plugin from user requirements.
- `framework-create-maintenance/SKILL.md` - Scaffolds a `<plugin>-maintenance` skill for a target plugin.
- `framework-create-owner/SKILL.md` - Scaffolds a `<plugin>-owner` facade skill for a target plugin.
- `framework-create-plugin/SKILL.md` - Scaffolds a new plugin's folder structure with a draft workflow file.
- `framework-create-skill/SKILL.md` - Creates a new `SKILL.md` file for a plugin from user requirements.
- `framework-maintenance/SKILL.md` - Main entrypoint for updating the framework plugin and verifying its integrity.
- `framework-readme/SKILL.md` - Owns `spek-fu/README.md` and keeps it synchronized with the current state of the framework.

## templates/

- `agent-template.md` - Boilerplate structure for a new `AGENT.md` file.
- `compound-knowledge-entry-template.md` - Boilerplate structure for a single `L-{id}` learning entry.
- `compound-pattern-template.md` - Boilerplate structure for a single `P-{id}` pattern entry.
- `export/` - Fresh-template files (`constitution.md`, `compound-*`, `project.md`, `roadmap.md`, `technical.md`, code-docs index/root, `python.gitignore`) used by `export-framework.py`.
- `file-inventory-template.md` - Boilerplate structure for a plugin's `file-inventory.md`.
- `maintenance-skill-template.md` - Boilerplate structure for a plugin's `<plugin>-maintenance` `SKILL.md`.
- `owner-skill-template.md` - Boilerplate structure for a plugin's `<plugin>-owner` `SKILL.md`.
- `skill-template.md` - Boilerplate structure for a new `SKILL.md` file.
- `workflow-template.md` - Boilerplate structure for a plugin's `<plugin>-workflow.md` entry point.
