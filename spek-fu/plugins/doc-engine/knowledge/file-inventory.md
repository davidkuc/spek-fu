# Doc-Engine File Inventory


## Plugin Root

`doc-engine-workflow.md` - Top-level glossary and command reference explaining Doc-Engine's pointer/index/tag system and how to choose between the Traverse, Enrich, and Update skills.

## agents/

- `doc-engine-executor` - subagent that runs the Traverse, Enrich, or Update workflows end-to-end against a given scope, with non-negotiable constraints on tags, pointers, and terseness.

## knowledge/

- `dok-fu.config.json` - JSON configuration listing docs/source directories, source file globs, exclude globs, the pointer comment token, per-extension comment markers, and paths to the registry/manifest.

- `format.md` - Canonical format specification for doc module frontmatter/body, the `## Glossary` and `## Sections` blocks, source-file pointer comments, and index entries.

- `tags.registry.json` - Controlled vocabulary of tags (e.g. `auth`, `http`, `cli`) with one-line explanations, used to validate module frontmatter tags.

## scripts/

- `dokfu.py` - CLI entry point that wires the `index`, `tags`, `doctor`, and `changes` subcommands to their implementations in the `dokfu` package.

- `requirements.txt` - Declares the single Python dependency (`pyyaml`) needed to run the dokfu scripts.

- `dokfu/__init__.py` - Package marker exposing the `dokfu` package version and author metadata.

- `dokfu/changes.py` - Detects changed source files via `git diff` (primary) or a SHA-256 manifest comparison (fallback), and reads/writes that manifest.

- `dokfu/common.py` - Shared utilities for config loading, YAML frontmatter parsing, source file walking, doc/source path mapping, and pointer-comment helpers used across the whole package.

- `dokfu/doctor.py` - Validates the documentation system by checking for broken/orphaned pointers, unknown tags, and a stale index, returning structured problem reports.

- `dokfu/index.py` - Builds and writes the flat `index.json` from all doc module frontmatter, and can check whether the on-disk index is stale.

- `dokfu/pointers.py` - Extracts and validates the two-way pointer link between a doc module's `code:` field and a source file's `dok-fu:` comment.

- `dokfu/tags.py` - Loads the tag registry and provides tag listing, tag-based doc search, and tag validation against the registry.

## skills/

- `doc-engine-enrich/SKILL.md` - Skill defining the Enrich workflow: detecting undocumented source files and adding pointer comments, module sections, and index entries within terseness limits.

- `doc-engine-traverse/SKILL.md` - Skill defining the Traverse workflow: navigating index → modules → comments → code to gather context with minimal loading.

- `doc-engine-update/SKILL.md` - Skill defining the Update workflow: using `dokfu changes` to find stale docs and resynchronizing only the affected module sections and comments.

- `doc-engine-maintenance/SKILL.md` - Skill defining the Maintenance workflow: the entrypoint for changing the doc-engine plugin itself and auditing that pointers, inventory, and scripts stay intact.

## templates/

- `module.md.tmpl` - Placeholder template for scaffolding a new doc module file with frontmatter, `## Sections`, `## Glossary`, and a single file section.

## Outside Plugin Directory

- `spek-fu/project/code-docs/.dokfu-manifest.json` - Manifest file for tracking documentation state and synchronization across the documentation system.

- `spek-fu/project/code-docs/index.json` - Flat index of all doc modules built from frontmatter, containing paths, tags, and descriptions for quick reference.

- `spek-fu/project/code-docs/root.md` - Doc module documenting source files located at the project root, using the standard Doc-Engine module format.
