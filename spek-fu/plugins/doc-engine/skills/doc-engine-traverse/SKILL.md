---
name: doc-engine-traverse
description: "Traverse the documentation hierarchy to gather relevant information without loading the entire codebase into context."
---

# Doc-Engine Traverse

Traverse the documentation hierarchy to gather relevant information without loading the entire codebase into context.

<inputs>

## Inputs

- User request
- Task description

</inputs>

<outputs>

## Outputs

- Report file summarizing the gathered information, including module paths, tags, descriptions, and any other pertinent details.

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never skip directly to code. Always start at the index.
- If `spek-fu/project/code-docs/index.json` is absent, run `dokfu index` before traversing.
- If a module path saved to memory no longer resolves, note it as a potential orphan and continue.
- Do not load modules that are irrelevant to the current task.

</constraints>

<behavioral_anchors>

## Pillars

See `spek-fu/plugins/doc-engine/knowledge/pillars.md` for the shared Terseness, Progressive Disclosure, Deterministic Foundation, and AI Augmenting pillars.

## Scripts

| Command | Purpose |
|---|---|
| `dokfu tags --search <TAG>` | Find modules tagged with a specific tag |
| `dokfu index` | Build `spek-fu/project/code-docs/index.json` if absent |

## Flow

Index → Modules (section index) → Comments → Code

Always follow this order. Stop at the layer that gives sufficient context.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read the index

Read `spek-fu/project/code-docs/index.json`. It is a flat array of `{path, tags[], description}` entries.

- Use `dokfu tags --search <TAG>` to narrow entries by tag before reading the file.
- Scan descriptions to identify which module paths are relevant to the current task.
- Save the relevant `path` values to memory now — do not rely on recalling them later.

### 2. Read relevant modules

For each saved module path, open the file.

- Read the `## Sections` block first. Each bullet is a source filename — its H2 contains the `path:` of the specific file and a summary.
- Open only the H2 sections that are relevant. Each section's `path:` field tells you the exact source file it describes.
- Note any cross-references to other modules and add them to the relevant-paths list if warranted.

### 3. Follow code pointers

Each module's frontmatter contains a `code:` field pointing to the **source folder**.

- For specific files of interest, use the `path:` inside the relevant H2 section to locate the exact source file.
- Open the source file and scan the `dok-fu:` comment near the top to confirm the link, then read inline comments throughout.
- Comments are the highest-detail layer — read them when you need specifics about implementation.

### 4. Read code (last resort)

If comments are absent or insufficient, read the actual source code.

Keep reading narrow: target specific functions or blocks rather than the whole file.

### 5. Write a report file

After gathering all relevant information, compile it into a report file. This file should summarize the findings, including module paths, tags, descriptions, and any other pertinent details.

</workflow>

<done_conditions>

## Done Conditions

- The documentation hierarchy has been traversed and all relevant information has been gathered.

</done_conditions>


