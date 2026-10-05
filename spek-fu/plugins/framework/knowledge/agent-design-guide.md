# Agent Design Guide

Format specification for writing an `AGENT.md` file.

## File location

`spek-fu/plugins/<plugin>/agents/<agent-name>/AGENT.md`

One folder per agent, named after the agent (kebab-case, prefixed with the plugin name, e.g. `doc-engine-executor`).

## Frontmatter

```yaml
---
name: <agent-name>
description: "<what it executes>. Use when <trigger condition>."
model: "<haiku|sonnet|opus>"
---
```

- `name` matches the agent's folder name.
- `description` is two clauses: what the agent executes, then when a dispatching agent should pick it. This is the text a parent agent reads to decide whether to invoke it.
- `model` default is "haiku".

## Structure

Every agent follows this section order. Optional sections may be omitted; required sections may not.

### 1. Title and summary

```
# <Agent Title> Subagent

<1-2 sentences: what it executes and who invokes it (parent agent/skill)>
```

### 2. `<inputs>` block

```
<inputs>

## Inputs

- Bullet list of inputs, with defaults stated for optional ones (e.g. "if omitted, run X to determine Y")

</inputs>
```

### 3. `<outputs>` block

```
<outputs>

## Status Outputs

- `ok`: <success condition>
- `ok (<qualifier>)`: <success with caveat, e.g. no-op>
- `blocked (<reason>)`: <recoverable stop condition — report and halt>
- `fail`: <unrecoverable error — report context and stop>

</outputs>
```

An agent reports a machine-readable outcome to its caller, not a list of produced artifacts — use `ok` / `blocked (...)` / `fail` vocabulary, not free-form prose.

### 4. `<constraints>` block

```
<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

1. Hard constraints and "never/always" statements specific to this agent.
2. Append a `WHY:` clause to a rule only when the reason isn't self-evident.

</constraints>
```

### 5. `<behavioral_anchors>` block

```
<behavioral_anchors>

## Pillars

See `spek-fu/plugins/<plugin>/knowledge/pillars.md` for shared pillars, or define inline if the plugin has none yet.

## <Selection Table> (optional)

| Situation | Workflow |
|---|---|
| <situation> | <internal workflow to use> |

## <Scripts/CLI Reference> (optional)

| Command | Purpose |
|---|---|

</behavioral_anchors>
```

Include a selection table only when the agent dispatches between multiple internal workflows (see doc-engine-executor's Skill Selection table).

### 6. `<workflow>` block

Single-mode agent:

```
<workflow>

## Steps

### 1. <Step name>

<Instruction>

</workflow>
```

Multi-mode agent (wraps several distinct execution paths): repeat a `## Workflow: <Name>` block per mode, each with its own `### Steps` and `### Rules`, separated by `---`.

### 7. `<done_conditions>` block

```
<done_conditions>

## Done Conditions

- One bullet per workflow mode: the observable signal that confirms it finished.

</done_conditions>
```

## Formatting conventions

- Same XML-style tags as skills (`<inputs>`, `<outputs>`, `<constraints>`, `<behavioral_anchors>`, `<workflow>`, `<done_conditions>`), blank line after opening tag and before closing tag.
- Headings inside tags start at `##`; step names inside `<workflow>` start at `###`; sub-workflow names use `## Workflow: <Name>`.
- Bullet lists over prose, per constitution terseness principle.
- Reference SSOT files (constitution, registries, shared pillars) by path instead of repeating their content.

## Checklist for a new agent

- [ ] Folder and `name` frontmatter match, kebab-case, plugin-prefixed.
- [ ] `description` states what it executes, then when to invoke it.
- [ ] `model` present only if a deliberate override.
- [ ] `<inputs>`, `<outputs>`, `<constraints>`, `<workflow>`, `<done_conditions>` all present.
- [ ] Status outputs use `ok` / `blocked (...)` / `fail` vocabulary, not free-form text.
- [ ] `<behavioral_anchors>` included if the agent shares pillars or dispatches between multiple internal workflows.
- [ ] No rule or fact duplicated from the constitution or plugin knowledge files — referenced instead.
- [ ] All prose within terseness limits (constitution `## AI Principles`).
