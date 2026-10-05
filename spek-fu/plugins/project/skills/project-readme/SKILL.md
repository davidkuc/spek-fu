---
name: project-readme
description: "Owns the repo-root README.md and keeps its setup, run, test, and dev commands synchronized with the repository."
---

# Project Readme

Owns `README.md` in the repo root: a command cheat sheet for developers, built from `spek-fu/plugins/project/templates/project-readme-template.md`.

Template: `spek-fu/plugins/project/templates/project-readme-template.md`

## When to use

Run after any change that affects how developers set up, run, test, lint, or deploy the project — a script, dependency, port, config file, or required tool is added, renamed, or removed. Also run on request or when `README.md` is missing.

<inputs>

## Inputs

- Current `README.md` (may not exist)
- What changed, if the user says so (otherwise scan the git history of the whole repo)
- Repo command sources: `package.json` files, `*.ps1`/`*.sh` scripts, `docker-compose*`, `*.sln`/`*.csproj`, `pyproject.toml`, `Cargo.toml`, `.env.example`, hooks, CI config

</inputs>

<outputs>

## Outputs

- Created or updated `README.md` in the repo root

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never add a command, tool, script, port, or path that isn't confirmed in a repo file; never run commands to check them.
- Minimal diff: change only outdated or missing content; keep hand-written additions and sections outside the template.
- Follow the template's section order. Required: title and description, purpose line, Table of Contents, Requirements, Setup, Run, Tests. Omit optional sections the repo has no content for.
- The Table of Contents is always present, lists every `##` section in file order, and nests `###` entries.
- Group related commands in one thematic block with short `# ->` comments where not obvious; one fence per shell, in the shell the repo uses.
- State the shell and the directory commands run from near the top.
- Never write secrets; point to the file or variable that holds them.
- Do not duplicate content from other docs (SSOT) — link to the file instead.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every sentence, comment, and table cell uses the fewest words that preserve meaning, per constitution `## AI Principles`.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read current README

Read `README.md` in full, if it exists. Note its language, shell, and any sections not in the template.

### 2. Read the template

Read `spek-fu/plugins/project/templates/project-readme-template.md`.

### 3. Gather repo state

Read the command sources listed under Inputs. Collect: required tools, install/restore steps, run and stop commands, URLs and ports, test commands per layer, lint/format commands, deploy and cleanup scripts, config files and variables.

### 4. Diff

Compare the README with the collected state:

- **Missing** — commands or tools in the repo but not in the README.
- **Stale** — commands, flags, paths, or versions in the README that no longer exist or differ.
- **Structure** — sections out of template order, missing required sections, Table of Contents out of sync.

If a needed fact is not in any repo file, mark `[NEEDS CLARIFICATION]` and ask the user before writing it.

### 5. Update or create

- No `README.md`: fill the template with the collected state.
- Otherwise: apply only the diffs from step 4.

Regenerate the Table of Contents last so it matches the final headings.

### 6. Write the file

Save `README.md` only if content changed. Report added, changed, and removed entries in one short list.

</workflow>

<done_conditions>

## Done Conditions

- `README.md` exists in the repo root with all required template sections in order.
- Every command, tool, script, and path in it is confirmed in a repo file.
- The Table of Contents matches the headings.
- Hand-written content outside the outdated parts is preserved.

</done_conditions>
