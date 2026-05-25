---
id: PT001
version: 1.0
name: Divide and Conquer
description: "Divide large or complex work into separate, smaller, independently executable pieces. USE FOR: Project-wide work, large tasks, complex multi-concern tasks. DO NOT USE FOR: Small tasks, quick fixes, tightly coupled problems that cannot be cleanly split."
category: decomposition
tags: [decomposition, parallel-execution, scale, batching]
signals: [large-task, context-overflow-risk, parallel-tasks]
recommended-tier: all
prevents: "Context overflow and quality degradation — large-batch work fills the context window, slowing the agent and degrading output quality."
exclusion-group: decomposition-primary
---

# Divide and Conquer

## Reasoning

Large context and complex problems quickly fill up the context of the AI agent, slowing its work and decreasing the quality of the results drastically. Dividing work into smaller batches allows to plan work in the best logical order, separate concerns, test each part separately and implement work in parallel (if possible).

## Examples

- Code migration: divide a large codebase migration into one module per wave; each wave is planned, executed, and tested before the next starts.
- Documentation overhaul: allocate one file per sub-agent pass rather than one mega-pass over all files simultaneously.
- Feature implementation: decompose into data model → API layer → UI layer; implement and verify each independently before integrating.
- Performance audit: one sub-agent per service analyzes its scope in parallel, reporting findings to the orchestrator.

