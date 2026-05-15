---
id: PT023
version: 1.0
name: Parallelization
description: "Identify independent sub-tasks and dispatch them concurrently rather than sequentially. USE FOR: Workflows where multiple sub-tasks have no data dependencies and combined sequential latency is the bottleneck. DO NOT USE FOR: Dependent tasks with ordering requirements, tasks sharing mutable state, tasks too small to offset dispatch overhead."
category: decomposition
tags: [parallelization, concurrent, efficiency, throughput, independence]
signals: [parallel-tasks, large-task]
recommended-tier: all
prevents: "Sequential bottleneck — executing independent sub-tasks one after another introduces unnecessary latency and inflates context with accumulated intermediate results when the tasks have no data dependencies."
---

# Parallelization

## Reasoning

When multiple sub-tasks can each start with only the original input and have no dependency on each other's outputs, there is no reason to execute them sequentially. Sequential dispatch accumulates both latency (each task waits for the previous) and intermediate context (all prior results remain in the window). Parallel dispatch eliminates both.

The prerequisite is an explicit independence check: if task B needs task A's output, they are not independent and must remain sequential. If B and C can both start with the original input alone, they are candidates for parallelization.

In practice, parallel dispatch in orchestrators means issuing multiple `runSubagent` calls before waiting for any results, then aggregating once all complete. The orchestrator's job is to identify the independence boundary, not to serialize for convenience.

Pairs naturally with PT001 (Divide and Conquer): divide the work first, then parallelize the independent pieces.

## Examples

- Multi-file refactor: analyze each file in parallel; integrate results sequentially afterward.
- Research across multiple sources: all source-fetch sub-agents run concurrently; synthesis happens after all return.
- Verification suite: lint, type-check, and unit-test sub-agents run in parallel; results aggregated before reporting.
- Codebase migration: shared dependencies migrated first (sequentially), then independent modules migrated in parallel by separate sub-agents.
