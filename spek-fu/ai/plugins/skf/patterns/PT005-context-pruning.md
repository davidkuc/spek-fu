---
id: PT005
version: 1.0
name: Context Pruning
description: "Actively remove irrelevant content from context before the next reasoning step. USE FOR: Long-running agent sessions, tasks where earlier exploration produced large dead-end outputs, multi-turn workflows accumulating tool noise. DO NOT USE FOR: Short tasks, when full history is needed for audit/correctness."
category: context-management
tags: [context, pruning, efficiency, summarization]
signals: [long-running-session, context-overflow-risk]
recommended-tier: all
prevents: "Lost-in-the-middle attention degradation — stale tool outputs and abandoned-approach transcripts compete for model attention and degrade reasoning quality even when not actively referenced."
---

# Context Pruning

## Reasoning

Every token in context competes for the model's attention. Stale tool outputs, abandoned approaches, and verbose error logs degrade reasoning quality even when they're "just sitting there" — this is the lost-in-the-middle effect. Long contexts also slow inference and inflate cost.

Pruning is the deliberate act of summarizing or dropping content that no longer serves the current goal. In an orchestrator, this means the dispatcher decides what summary to pass to the next sub-agent, not the full history. In a single agent, this means asking the model to produce a "state summary" and continuing from that summary instead of the raw transcript.

## Examples

- After a failed file-search exploration, summarize "searched X, Y, Z — none relevant; the answer is likely in module M" and drop the raw search results.
- In Copilot agent mode, after fixing a bug across 10 files, summarize the changes made and continue with the summary rather than carrying full diffs.
- In an orchestrator: sub-agent returns 5KB of analysis; dispatcher passes only the 3-line conclusion to the next sub-agent.
