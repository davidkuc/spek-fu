---
name: doc-engine-update
description: "Synchronize documentation with recent changes in the codebase."
---

# Doc-Engine Update

Synchronize documentation with recent changes in the codebase.

Readability bar: `## AI Principles` section of `spek-fu/constitution/constitution.md`. All rewritten prose and comments this skill produces follow that guide's rules.

## When to run

Run Update after any batch of source file edits — before committing or after a feature branch lands.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Updated documentation for the changed source files

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Change only what changed. Do not rewrite unaffected sections or comments.
- Never exceed terseness limits.
- Never invent tags not present in `spek-fu/plugins/doc-engine/knowledge/tags.registry.json`.
- If `dokfu changes` returns a file that has no doc pointer, switch to the **Enrich** skill for that file.
- Write rewritten prose and comments in plain language, per the `## AI Principles` section of `spek-fu/constitution/constitution.md`.

</constraints>

<behavioral_anchors>

## Pillars

See `spek-fu/plugins/doc-engine/knowledge/pillars.md` for the shared Terseness, Progressive Disclosure, Deterministic Foundation, and AI Augmenting pillars.

## Scripts

| Command | Purpose |
|---|---|
| `dokfu changes [--since <REF>]` | List source files changed since ref (git primary, manifest fallback) |
| `dokfu doctor` | Validate pointers, tags, and index freshness; report broken/orphaned |
| `dokfu doctor --fix-index` | Rebuild index if stale |
| `dokfu doctor --fix-pointers` | Repair broken pointer comments for rename candidates |
| `dokfu index` | Rebuild `spek-fu/project/code-docs/index.json` after all modules are updated |

</behavioral_anchors>

<workflow>

## Steps

### 1. Get the changed files

```
dokfu changes [--since <REF>]
```

This returns a list of source file paths that changed since the given git ref (default: last commit). If git is unavailable, it falls back to the sha256 manifest comparison.

If the list is empty, documentation is up to date. Stop.

### 2. For each changed file

#### 2a. Read the source file

- Locate the `dok-fu:` pointer comment near the top.
- If the pointer is absent, treat the file as unenriched and run the **Doc-Engine Enrich** (`doc-engine-enrich`) skill instead.
- If the pointer target no longer exists (broken pointer), run `dokfu doctor` — it will identify rename candidates matched by `dokfu_id`. Run `dokfu doctor --fix-pointers` to repair, then reload the file and continue.

#### 2b. Open the linked doc module

Follow the pointer path from the comment. Open `spek-fu/project/code-docs/<mirrored-folder-path>.md`.

- Read the `## Sections` block to orient yourself. Each bullet is a source filename.
- Find the H2 section whose `path:` matches the changed source file.
- Identify whether that section needs updating.

#### 2c. Update the affected section

Rewrite only the section whose `path:` matches the changed file. Preserve all other sections verbatim.

Terseness limits: ≤ 3 sentences and ≤ 5 bullet points per section. The `path:` line itself does not count toward those limits.

#### 2c-i. Re-check the module's Glossary

If the rewrite introduces a term the module's `## Glossary` does not yet define, add it there before moving on — a folder's files changing is exactly when an undefined term would otherwise land. Follow the entry rules in the `## AI Principles` section of `spek-fu/constitution/constitution.md`; skip terms already in the shared glossary in `spek-fu/plugins/doc-engine/doc-engine-workflow.md`. Leave the glossary untouched if the change introduces no new term.

#### 2d. Update inline code comments

If the change introduces new logic, parameters, or patterns, update or add a 1-sentence inline comment in the source file at the relevant location.

Do not touch comments that are still accurate.

#### 2e. Update frontmatter (if needed)

If the change affects the module's `tags` or `description`, update those fields in the frontmatter. Use only tags from `spek-fu/plugins/doc-engine/knowledge/tags.registry.json`.

### 3. Refresh the index

After all affected modules are updated, run:

```
dokfu index
```

This regenerates `spek-fu/project/code-docs/index.json` from the current frontmatter of all modules.

### 4. Validate

Run `dokfu doctor` to confirm no broken pointers, unknown tags, or stale index remain. Resolve any reported issues before finishing. If doctor reports broken pointers with rename candidates, run `dokfu doctor --fix-pointers` before finalizing.

</workflow>

<done_conditions>

## Done Conditions

- All changed source files have their corresponding documentation sections updated.
- The index has been refreshed and validated.
- No broken pointers, unknown tags, or stale index entries remain.

</done_conditions>
