# Framework

This plugin is the core of the Spek-Fu framework.

## Glossary

**Compound knowledge** - Lessons learned during AI work submitted by the human or AI itself.

**Compound patterns** - Patterns extracted from repeating compound knowledge entries.

## How to use

To create a new plugin:
1. Use `framework-create-plugin` skill to scaffold plugin.
2. Use `framework-create-owner` to create the plugin's owner (facade) skill, so a routing entrypoint exists from the start.
3. Use `framework-create-skill` and `framework-create-agent` to create the skills and agents needed for your specific plugin requirements.
4. Use `framework-create-maintenance` to create the maintenance skill for this plugin. Make sure the whole plugin is defined properly before creating this skill.

To add a lesson into compound knowledge database:
1. Do some extended work.
2. After finishing the work, in the same session run the `framework-compounding-write` skill.

After some time the `compound-knowledge` file will gather a significant amount of entries, which will be a good reason to run the `framework-compounding-patterns` skill to extract patterns from those entries.

### Choosing the right skill

**Route a framework-plugin request to the right skill (facade)** -> Use `framework-owner` skill
**Create a new plugin** -> Use `framework-create-plugin` skill
**Create a plugin's owner (facade) skill** -> Use `framework-create-owner` skill
**Create a skill** -> Use `framework-create-skill` skill
**Create an agent** -> Use `framework-create-agent` skill
**Create a maintenance skill** -> Use `framework-create-maintenance` skill
**Record a learning** -> Use `framework-compounding-write` skill
**Look up relevant learnings** -> Use `framework-compounding-read` skill
**Extract patterns from learnings** -> Use `framework-compounding-patterns` skill
**Update the framework plugin** -> Use `framework-maintenance` skill
**Sync `spek-fu/README.md`** -> Use `framework-readme` skill (run automatically by every plugin's `<plugin>-maintenance` skill)

## Commands reference

| Command | Purpose |
|---|---|
| `python spek-fu/plugins/framework/scripts/regenerate-pointer-files.py` | Rewrite every `.claude`/`.github` skill and agent pointer file from its source `SKILL.md`/`AGENT.md`, and delete stale ones. |
| `python spek-fu/plugins/framework/scripts/export-framework.py [--target <project-path>]` | Export a fresh copy of the framework into `spek-fu-export/` (no argument) or into an existing project (`--target`), then regenerate its pointer files. Re-running on a project updates the framework and keeps project data. |
