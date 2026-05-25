# Copilot Instructions — Spek-Fu

## Don't know which agent to use?

Use `@skf-general-orchestrator` for free-form requests or multi-step framework work. Direct command invocation (for example `/impl-implement`, `/gov-update`, or `/meta-skill-manage`) remains available when you already know the exact operation you want.

## Project Constitution

This project is governed by a Constitution at `constitution/constitution.md`. Load the main file first, then load relevant sections based on your current task. Constitution rules take precedence over skill rules when they conflict.

## AI Framework

The AI framework lives in `ai/plugins/skf/`. See [Framework Management](../README.md#framework-management) and [`ai/plugins/skf/skf-index.json`](../ai/plugins/skf/skf-index.json) for the component inventory.

- Skill groups: `meta-`, `gov-`, `orch-`, `impl-`
- Agent tier definitions: [`ai/plugins/skf/runbooks/runbook-intake.md`](../ai/plugins/skf/runbooks/runbook-intake.md)
- Agents: see [Agent Table](../README.md#agent-table)

**Artifacts**: Canonical slash command prompts live in `.github/prompts/`. Canonical agent definitions live in `.github/agents/`. Use `/gov-update` to synchronize index files with disk state after framework changes.


## Templates

Document and framework authoring templates are in `ai/plugins/skf/templates/`.
