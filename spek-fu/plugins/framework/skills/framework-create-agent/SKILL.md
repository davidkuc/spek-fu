---
name: framework-create-agent
description: "Create a new AGENT.md file for a plugin from user requirements, following the agent design guide and template."
---

# Framework Create Agent

Create a new `AGENT.md` file for a plugin from user requirements, following the agent design guide and template.

Format specification: `spek-fu/plugins/framework/knowledge/agent-design-guide.md`
Template: `spek-fu/plugins/framework/templates/agent-template.md`

<inputs>

## Inputs

- User's requirements for the agent (purpose, trigger/when to invoke, inputs/outputs, rules, workflow steps)
- Target plugin the agent belongs to (e.g. `doc-engine`, `framework`)

</inputs>

<outputs>

## Outputs

- A new `AGENT.md` at `spek-fu/plugins/<plugin>/agents/<agent-name>/AGENT.md`
- Any new knowledge files at `spek-fu/plugins/<plugin>/knowledge/*.md` (only if needed)
- Any new template files at `spek-fu/plugins/<plugin>/templates/*.md` (only if needed)
- A pointer file at `.claude/agents/<agent-name>/AGENT.md`
- A pointer file at `.github/agents/<agent-name>.agent.md`

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never write an `AGENT.md` without first reading the agent design guide and template.
- Never invent a section structure — follow the template's section order exactly; omit only sections marked optional.
- Never skip clarification: if any required input is missing or ambiguous, ask the user before drafting (constitution `## AI Principles` → Ambiguity).
- Status outputs (`## Status Outputs`) must use `ok` / `blocked (...)` / `fail` vocabulary — never a free-form artifact list (that belongs on skills, not agents).
- Knowledge and template files always live under the target plugin's shared `knowledge/` and `templates/` folders, never inside the agent's own folder.
- Agent folder and `name` frontmatter must match, kebab-case, prefixed with the target plugin name.
- Do not duplicate content already present in the constitution or the target plugin's existing knowledge files — reference it instead.
- The two pointer files use different shapes: `.claude/agents/<agent-name>/AGENT.md` (folder) vs `.github/agents/<agent-name>.agent.md` (flat file) — do not conflate them.

</constraints>

<workflow>

## Steps

### 1. Gather requirements

Collect from the user, asking clarification questions in loops until each is unambiguous:

- Target plugin (must exist under `spek-fu/plugins/`)
- Agent name (kebab-case, prefixed with the plugin name)
- Two-clause description: what it executes, and when a dispatching agent should pick it
- Model override, if any (default: inherit from caller)
- Expected inputs and status outputs (`ok` / `blocked (...)` / `fail` cases)
- Hard rules / constraints specific to the agent
- Workflow: single-mode steps, or multiple named internal workflows if the agent wraps several distinct execution paths
- Done conditions per workflow mode

Do not proceed to drafting while any of the above is missing or unclear.

### 2. Read references

Read `spek-fu/plugins/framework/knowledge/agent-design-guide.md` and `spek-fu/plugins/framework/templates/agent-template.md` in full before drafting.

### 3. Check for shared conventions

List existing agents under `spek-fu/plugins/<plugin>/agents/` and skim their frontmatter and section names to keep tone and terminology consistent within the plugin. Do not copy their rules verbatim unless the user's requirements genuinely overlap.

### 4. Draft the agent

Fill the template's sections in order (title/summary, `<inputs>`, `<outputs>`, `<constraints>`, `<behavioral_anchors>` if applicable, `<workflow>`, `<done_conditions>`) using the gathered requirements. Use one `## Workflow: <Name>` block per mode if the agent dispatches between several, else a single `## Steps` block. Keep prose within constitution terseness limits.

### 5. Split if oversized

Move detailed reference material or reusable boilerplate to `spek-fu/plugins/<plugin>/knowledge/<topic>.md` or `templates/<topic>.md`, replacing it in the agent with a one-line path pointer. Recount and repeat until the file reads cleanly.

### 6. Create the files

Write the final `AGENT.md` and any split-out knowledge/template files to disk.

### 7. Create pointer files

Run `python spek-fu/plugins/framework/scripts/regenerate-pointer-files.py` to (re)generate `.claude/agents/<agent-name>/AGENT.md` and `.github/agents/<agent-name>.agent.md` from the new agent's frontmatter.

### 8. Self-validate

Check the new agent against the agent-design-guide's `## Checklist for a new agent`. Report any unmet item and fix it before finishing.

</workflow>

<done_conditions>

## Done Conditions

- `AGENT.md` exists at `spek-fu/plugins/<plugin>/agents/<agent-name>/AGENT.md`.
- All template sections present in the correct order; optional sections included only when needed.
- Status outputs use `ok` / `blocked (...)` / `fail` vocabulary.
- Any overflow content lives in a plugin knowledge/template file, referenced from the agent by path.
- Pointer files exist at `.claude/agents/<agent-name>/AGENT.md` and `.github/agents/<agent-name>.agent.md`.
- The agent-design-guide checklist passes for the new agent.

</done_conditions>
