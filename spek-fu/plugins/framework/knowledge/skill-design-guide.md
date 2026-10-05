# Skill Design Guide

Format specification for writing a `SKILL.md` file.

## File location

`spek-fu/plugins/<plugin>/skills/<skill-name>/SKILL.md`

One folder per skill, named after the skill (kebab-case, prefixed with the plugin name, e.g. `doc-engine-enrich`).

## Frontmatter

```yaml
---
name: <skill-name>
description: "<one-sentence description of what the skill does>"
---
```

- `name` matches the skill's folder name.
- `description` is one sentence, action-first (verb-led), no trailing detail.

## Structure

Every skill follows this section order. Optional sections may be omitted; required sections may not.

### 1. Title and summary

```
# <Skill Title>

<One-sentence restatement of the description, or a short expanded summary>
```

May be followed by short pointer lines to shared reference files, e.g.:

```
Format specification: `path/to/format.md`
```

### 2. `## When to use` / `## When to run` (optional)

Short prose describing the trigger condition(s) for invoking this skill. Use when the skill's name alone doesn't make the trigger obvious.

### 3. `<inputs>` block

```
<inputs>

## Inputs

- Bullet list of inputs the skill expects (e.g. user request, task description)

</inputs>
```

### 4. `<outputs>` block

```
<outputs>

## Outputs

- Bullet list of artifacts/state the skill produces

</outputs>
```

### 5. `<constraints>` block

```
<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Hard constraints and "never/always" statements specific to this skill.
- Reference the constitution or other SSOT files instead of restating their rules.

</constraints>
```

### 6. `<behavioral_anchors>` block

```
<behavioral_anchors>

## Pillars

**<Pillar Name>** — one-line definition, followed by bullets if the pillar has sub-rules.

## Scripts

| Command | Purpose |
|---|---|
| `<command>` | <what it does> |

</behavioral_anchors>
```

Use this block for cross-cutting principles (e.g. terseness limits, progressive disclosure) shared across multiple skills in the same plugin, and for a table of scripts the skill relies on. Copy the pillar text verbatim across skills that share it — do not paraphrase differently each time (SSOT).

### 7. `<workflow>` block

```
<workflow>

## Steps

### 1. <Step name>

<Prose and/or code blocks describing exactly what to do>

### 2. <Step name>
...

</workflow>
```

Numbered `###` steps, each a self-contained instruction. Sub-steps use `#### 2a.`, `#### 2b.`, etc. Include literal shell commands in fenced code blocks where the step runs a script.

### 8. `<done_conditions>` block

```
<done_conditions>

## Done Conditions

- Checklist of observable conditions that confirm the skill's task is complete.

</done_conditions>
```

## Formatting conventions

- Custom XML-style tags (`<inputs>`, `<outputs>`, `<constraints>`, `<behavioral_anchors>`, `<workflow>`, `<done_conditions>`) wrap the corresponding `##` sections, with a blank line after the opening tag and before the closing tag.
- Headings inside the tags always start at `##`; step names inside `<workflow>` start at `###`.
- Bullet lists over prose paragraphs wherever possible, per the terseness principle.
- Reference SSOT files (constitution, registries, config) by path instead of repeating their content.
- Keep every rule/step to the fewest sentences that preserve meaning — no restating what's already said elsewhere in the file.

## Checklist for a new skill

- [ ] Folder and `name` frontmatter match, kebab-case, plugin-prefixed.
- [ ] `description` is one sentence.
- [ ] `<inputs>`, `<outputs>`, `<constraints>`, `<workflow>`, `<done_conditions>` all present.
- [ ] `<behavioral_anchors>` included if the skill shares pillars/scripts with sibling skills.
- [ ] No rule or fact duplicated from the constitution or plugin knowledge files — referenced instead.
- [ ] All prose within terseness limits (constitution `## AI Principles`).
