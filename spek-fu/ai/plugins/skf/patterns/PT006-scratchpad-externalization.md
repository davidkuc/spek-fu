---
id: PT006
version: 1.0
name: Scratchpad Externalization
description: "Write intermediate state to a file/note instead of carrying it in context. USE FOR: Long tasks with reusable intermediate artifacts (plans, todo lists, findings, decisions). DO NOT USE FOR: One-shot tasks, ephemeral reasoning that won't be referenced again."
category: context-management
tags: [externalization, working-memory, artifacts, persistence]
signals: [reusable-intermediate, long-running-session, planning]
recommended-tier: all
prevents: "Context exhaustion and mid-task amnesia — carrying all accumulated state in the context window exhausts the window and causes the agent to lose earlier findings as the task progresses."
---

# Scratchpad Externalization

## Reasoning

Context is a scarce resource; the filesystem is not. When the agent produces something it might need to reference later — a plan, a list of files to process, accumulated findings — writing it to a file lets the agent re-read only the relevant part on demand instead of carrying everything forward.

This is especially powerful in VS Code / Copilot workflows where the agent has file I/O. A `PLAN.md` or `TODO.md` becomes a durable working memory the agent can update, check off, and consult — surviving across context resets and even across sessions.

## Examples

- `PLAN.md` at the start of a multi-step refactor; agent updates it after each step.
- `FINDINGS.md` during code investigation; agent appends discoveries instead of repeating them in chat.
- `TODO.md` with checkboxes during a large migration; agent re-reads it when picking the next file.
- Sub-agent output written to `analysis-<id>.md` so the orchestrator passes a path instead of pasting content.
