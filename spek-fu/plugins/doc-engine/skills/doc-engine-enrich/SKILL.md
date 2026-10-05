---
name: doc-engine-enrich
description: "Detect undocumented parts of the codebase and fill the gaps within terseness limits."
---

# Doc-Engine Enrich

Detect undocumented parts of the codebase and fill the gaps within terseness limits.

Format specification: `spek-fu/plugins/doc-engine/knowledge/format.md`

Readability bar: `## AI Principles` section of `spek-fu/constitution/constitution.md`. All new section prose and pointer comments this skill writes follow that guide's rules — plain language within the terseness limits, no jargon left undefined.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Enriched documentation for the targeted codebase

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never invent tags. Use only tags present in `spek-fu/plugins/doc-engine/knowledge/tags.registry.json`.
- Never exceed terseness limits: 1 sentence in index, 3 sentences / 5 bullets per section, 1 sentence per comment.
- Do not create a doc module for files in `exclude_globs` (from config).
- If `dokfu doctor` still reports issues after enrichment, re-run and address remaining items.
- Write new section prose and pointer comments in plain language, per the `## AI Principles` section of `spek-fu/constitution/constitution.md` — this applies whenever this skill generates content, not only when a human rewrites it.

</constraints>

<behavioral_anchors>

## Pillars

See `spek-fu/plugins/doc-engine/knowledge/pillars.md` for the shared Terseness, Progressive Disclosure, Deterministic Foundation, and AI Augmenting pillars.

## Scripts

| Command | Purpose |
|---|---|
| `dokfu doctor` | Identify files with missing pointers, modules, or index entries |
| `dokfu doctor --fix-pointers` | Repair broken pointer comments for rename candidates |
| `dokfu index` | Rebuild `spek-fu/project/code-docs/index.json` after enrichment |

## What "enriched" means

A source file is fully enriched when all three of the following are true:

1. The file contains a `dok-fu:` pointer comment near the top, pointing to its parent module.
2. The parent module (`spek-fu/project/code-docs/<mirrored-folder>.md`) exists and has an H2 section for this specific file (with a `path:` line and valid frontmatter).
3. `spek-fu/project/code-docs/index.json` has an entry for that module.

</behavioral_anchors>

<workflow>

## Steps

### 1. Identify scope

Use `dokfu doctor` to get a list of files with missing pointers, missing modules, or missing index entries. Work through that list. If `dokfu doctor` reports rename candidates (broken pointer with a `dokfu_id` match), run `dokfu doctor --fix-pointers` first — these are not documentation gaps, they are pointer repairs.

If targeting a specific file or directory, scope the check manually: read the file, inspect for a `dok-fu:` comment, look up the mirrored doc path, check the index.

### 2. Add a code pointer (if missing)

Insert a single comment line near the top of the source file (after any shebang or package declaration, before imports):

```
<comment-token> dok-fu: spek-fu/project/code-docs/<mirrored-folder-path>.md
```

All files within the same folder point to the **same module**. Use the correct comment token for the file's extension (from `spek-fu/plugins/doc-engine/knowledge/dok-fu.config.json` → `comment_map`).

One sentence only. No extra explanation in the comment itself.

### 3. Create the doc module (if missing)

A module covers a **folder**, not a single file. If `spek-fu/project/code-docs/<mirrored-folder-path>.md` does not exist, create it using `spek-fu/plugins/doc-engine/templates/module.md.tmpl` as the template.

Frontmatter fields to populate:

- `dokfu_id`: slugified folder path (e.g. `src-auth`)
- `code`: repo-relative path to the **source folder**
- `tags`: one or more tags from `spek-fu/plugins/doc-engine/knowledge/tags.registry.json`; reject any tag not in the registry
- `description`: one sentence maximum describing the folder/component; this is the index description

Immediately after populating frontmatter, add the module's `## Glossary` section between `## Sections` and the first file section. Fill it with a bullet per module-specific term the folder's files and comments actually use, in the form `- **term** - Definition in one or two sentences.` Skip any term the shared glossary in `spek-fu/plugins/doc-engine/doc-engine-workflow.md` already defines, and never duplicate that shared glossary. If the module defines no terms of its own, the section body is exactly `No module-specific terms.` — see the `## AI Principles` section of `spek-fu/constitution/constitution.md` for the full entry rules. The term count is uncapped.

### 4. Add a section for the file (if missing)

Each H2 section in the module documents one specific source file. If the module exists but has no section for this file:

1. Append a new H2 whose header is the **filename**.
2. First line of the section body: `path: <repo-relative-path-to-file>`
3. Then ≤ 3 sentences and ≤ 5 bullet points describing the file.
4. Update the `## Sections` bullet list at the top of the module body.

Section links use relative file paths. Example: `[filename.py](src/component/filename.py)` where the path matches the `path:` field of that section.

### 5. Refresh the index

After all files in scope are enriched, run:

```
dokfu index
```

Verify the new entries appear with correct tags and description.

</workflow>

<done_conditions>

## Done Conditions

- All source files have a `dok-fu:` comment pointing to the correct module.
- All modules have the required frontmatter and a `## Glossary` section.
- Each source file has a corresponding section in its module.
- The `## Sections` list at the top of each module is up to date.
- The index reflects all modules with correct tags and descriptions.

</done_conditions>



