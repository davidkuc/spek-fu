---
id: PT009
version: 1.0
name: Test Before Trust
description: "Require the agent to verify its output by execution (run tests, compile, lint, query) before declaring done. USE FOR: Code, queries, scripts, configurations — anything executable. DO NOT USE FOR: Pure prose, design discussions, opinion-based content."
category: verification
tags: [testing, execution-verification, validation, executable]
signals: [executable-output, code-generation]
recommended-tier: all
prevents: "Hallucinated correctness — without execution, 'done' is a guess based on plausible appearance; the agent confidently ships code that doesn't compile, queries that return the wrong shape, and configs that fail to load."
---

# Test Before Trust

## Reasoning

LLMs hallucinate plausible-looking code that doesn't compile, queries that return the wrong shape, and configurations that fail to load. Without execution, "done" is a guess. With execution, "done" is verified.

The pattern is: write → run → read output → fix if broken → repeat until green. Embed this loop in the agent's instructions explicitly. In Copilot agent mode and VS Code, the agent has terminal access — use it. "I believe this works" is not acceptable; "I ran it and got the expected output" is.

## Examples

- After writing a function, the agent must run its tests before reporting completion.
- After writing a SQL query, the agent runs EXPLAIN or a LIMIT 1 to verify it parses and returns expected columns.
- After editing config, the agent restarts the service or runs a validator.
- After a refactor, the agent runs the full test suite and reports the actual output, not "tests should pass."
