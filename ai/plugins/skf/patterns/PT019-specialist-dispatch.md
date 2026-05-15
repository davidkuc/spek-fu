---
id: PT019
version: 1.0
name: Specialist Dispatch
description: "Orchestrator delegates each sub-task to a sub-agent with a narrow, role-specific system prompt. USE FOR: Tasks crossing distinct domains (research + code + review), workflows benefiting from clean context per role. DO NOT USE FOR: Single-domain tasks, tasks too small to justify dispatch overhead."
category: routing
tags: [dispatch, specialist, orchestration, delegation, multi-domain]
signals: [multi-domain, sequential-steps, large-task]
recommended-tier: all
prevents: "Role confusion and attention dilution — a single agent juggling multiple roles (planner, coder, reviewer) dilutes attention across role-specific instructions and produces lower-quality outputs than focused specialists."
---

# Specialist Dispatch

## Reasoning

A single agent juggling multiple roles (planner, coder, reviewer, doc-writer) carries the instructions for all of them in one context, diluting attention and increasing the chance of role confusion. Dispatching each sub-task to a specialist with a focused system prompt produces sharper results.

The orchestrator's job is reduced to: choose the right specialist, package the task, integrate the result. Each specialist gets a clean context window, role-specific instructions, and a constrained tool set (see Tool Whitelisting). This also makes the system testable — each specialist can be evaluated independently.

## Examples

- Orchestrator dispatches: "Researcher" sub-agent gathers info → "Architect" designs solution → "Implementer" writes code → "Reviewer" critiques.
- Codebase migration: dispatcher per-module to a "Migrator" sub-agent with module context only.
- Documentation: "Extractor" pulls API surface → "Writer" drafts docs → "Editor" polishes.
