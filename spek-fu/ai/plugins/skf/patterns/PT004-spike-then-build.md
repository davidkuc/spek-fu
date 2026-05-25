---
id: PT004
version: 1.0
name: Spike Then Build
description: "Run a quick throwaway exploration to de-risk unknowns before committing to the real implementation. USE FOR: Tasks with significant unknowns (unfamiliar API, unclear data shape, uncertain feasibility). DO NOT USE FOR: Well-understood problems, tight deadlines on known territory."
category: planning
tags: [exploration, de-risk, unknowns, feasibility]
signals: [unfamiliar-territory, investigation, planning]
recommended-tier: all
prevents: "Wrong plan on unknowns — committing to a full implementation plan before validating feasibility on an unfamiliar problem produces a plan that is structurally wrong and expensive to abandon."
---

# Spike Then Build

## Reasoning

When the agent doesn't know enough to plan well, planning is wasted effort — the plan will be wrong. A spike is a deliberately disposable attempt that exists only to answer questions: "Does this API return what I think? Is this approach viable? What's the actual data shape?" The output of a spike is knowledge, not code.

After the spike, the real task starts with a clean context and concrete answers. Skipping the spike on an unfamiliar problem usually produces a half-built wrong solution that's harder to throw away than a deliberate prototype.

## Examples

- New API integration: write 20 lines that just hit the endpoint and print the response, then design the real client.
- Performance optimization: benchmark the naive version first to know where the actual bottleneck is.
- Library evaluation: build the smallest possible end-to-end example before committing to the dependency.
