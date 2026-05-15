---
id: PT026
version: 1.0
name: Fallback Chain
description: "Define an ordered list of approaches; if the primary approach fails, try the next in sequence rather than stopping. USE FOR: Tasks with known alternative solution paths, integration tasks with unreliable components, any workflow where failure of one approach should not terminate execution. DO NOT USE FOR: Tasks with only one valid approach, tasks where retrying a failed approach is harmful, tasks where each attempt has destructive side effects."
category: error-handling
tags: [fallback, resilience, recovery, error-handling, chain, alternatives]
signals: [unfamiliar-territory, investigation, large-task]
recommended-tier: all
prevents: "Single-approach failure cascade — attempting one approach, encountering failure, and terminating the task when viable alternatives exist; a fallback chain ensures graceful degradation to the next viable option."
---

# Fallback Chain

## Reasoning

Most tasks have more than one viable approach, but agents often behave as if they have exactly one. When the primary approach fails (tool unavailable, approach infeasible, unexpected data shape), the agent stops rather than pivoting. A fallback chain makes the pivot explicit and ordered.

The chain has three properties: (1) ordered — approaches are tried in preference order, not randomly; (2) bounded — the chain terminates at the last fallback rather than looping indefinitely; (3) decisive — each fallback has an explicit trigger condition, not "when the agent feels like trying something else."

Distinguish from PT025 (Self-Correction): PT025 is for re-examining an incorrect approach based on new understanding. PT026 is for executing a pre-defined backup plan when the primary approach fails for a known, expected reason. Use PT025 when the assumption behind the approach needs revising; use PT026 when the backup plan was already anticipated.

## Examples

- API integration: primary = call production endpoint → fallback 1 = call staging endpoint → fallback 2 = load from local cache → final fallback = return partial results with a flag.
- File search: primary = semantic search → fallback = exact grep → fallback = directory listing traversal → final = prompt the user.
- Code generation: primary = use preferred library → fallback = use standard library equivalent → fallback = implement a minimal version inline.
- Spec retrieval: primary = read from known path → fallback = search index for matching entry → fallback = prompt user for path.
