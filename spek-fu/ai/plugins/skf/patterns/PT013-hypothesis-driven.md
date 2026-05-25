---
id: PT013
version: 1.0
name: Hypothesis Driven
description: "Force the agent to state a falsifiable hypothesis before investigating, then design actions to confirm or refute it. USE FOR: Debugging, root cause analysis, performance investigation, any 'why is this happening' question. DO NOT USE FOR: Implementation tasks, well-defined feature work, anything where the answer isn't an explanation."
category: reasoning
tags: [debugging, hypothesis, root-cause, investigation, falsifiable]
signals: [debugging, investigation]
recommended-tier: all
prevents: "Random investigation divergence — debugging without a stated hypothesis devolves into reading random files and trying random fixes; the agent accumulates context without converging on a root cause."
---

# Hypothesis Driven

## Reasoning

Without a stated hypothesis, debugging devolves into wandering — reading random files, trying random fixes, accumulating context without converging on an answer. A hypothesis is a commitment: "I think X is happening because of Y." It makes the next action obvious (test whether Y is true) and makes failure visible (if the test refutes Y, abandon the hypothesis instead of patching it).

The discipline is: state hypothesis → design minimal experiment → run experiment → update belief. Repeat until one hypothesis survives. This is the scientific method applied to debugging, and it's dramatically more efficient than "try things until it works."

## Examples

- "Tests fail intermittently. Hypothesis: race condition in the cache layer. Test: add logging to cache writes and run 100 times."
- "Endpoint is slow. Hypothesis: N+1 query in the user serializer. Test: log SQL queries for one request."
- "Feature broken in prod, works in staging. Hypothesis: env variable difference. Test: diff the env configs."
