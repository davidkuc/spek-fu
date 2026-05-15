---
id: skf-knowledge-skill-groups
title: "Skill Groups"
type: reference
tags: [skills, groups, reference, framework]
version: 1.0
---

# Skill Groups Knowledge DB

## Naming Convention

- **Pattern**: `{prefix}-{descriptive-name}`
- **Case**: All lowercase, hyphen-separated
- **Prefix**: 3–4 letter group code from the table below
- **Descriptive name**: Brief, action-oriented, no redundant suffixes (e.g., drop `-analysis` when prefix already implies analysis domain)
- **File name**: Matches the full prefixed skill name exactly (e.g., `ai/plugins/skf/skills/orch-index-traversal.md`)
- **`name:` field**: Matches the file name (without `.md` extension) exactly

## Assigning a New Skill to a Group

1. Read the skill's description and primary purpose
2. Match against group descriptions below — choose the group whose domain most naturally owns the skill
3. If the skill spans two groups, prefer the group that owns the **primary output** (e.g., a skill that analyzes then fixes → assign to the fix group, not the analysis group)
4. Apply the group prefix to the skill folder name
5. Add the skill to the Members column in this table
6. Update the Skill Count

## Groups

| Group | Prefix | Description |
|-------|--------|-------------|
| Governance | `gov` | Targeted governance changes to constitution, project, and ai-framework artifacts with per-change user approval
| Implementation | `impl` | Code execution and direct problem solving — implement, build, test, verify, and report results
| Meta/Framework | `meta` | Skill and agent lifecycle, framework maintenance, syncing, documentation upkeep, and knowledge management
| Orchestration | `orch` | Orchestration-core skills required for framework routing, pattern selection, execution validation, verification, reporting, and cleanup
