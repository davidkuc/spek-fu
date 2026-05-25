---
id: PT011
version: 1.0
name: Chain of Thought
description: "Instruct the agent to show step-by-step reasoning before answering. USE FOR: Multi-step logic, math, planning, debugging, any task where the answer depends on a chain of inferences. DO NOT USE FOR: Single-fact lookups, simple transformations, tasks already handled by reasoning models (which do this internally)."
category: reasoning
tags: [step-by-step, reasoning, chain-of-thought, transparency]
signals: [multi-step-logic, debugging, planning]
recommended-tier: fast-agent, standard-agent
prevents: "Plausible-wrong-answer — skipping intermediate reasoning causes the model to jump to a confident but incorrect conclusion; visible reasoning steps expose errors before they propagate."
exclusion-group: reasoning-loop
---

# Chain of Thought

## Reasoning

Forcing intermediate reasoning steps improves accuracy on problems requiring more than one inference. Without it, the model often jumps to a plausible-sounding wrong answer. With it, errors become visible and correctable.

Two cautions: modern reasoning models (o1, Claude with extended thinking, etc.) already do this internally — explicit "think step by step" prompts can hurt them. And for trivial tasks, CoT just adds latency and tokens without benefit. Use it where the problem genuinely has steps.

## Examples

- Debugging: "Walk through what each line does, then identify where behavior diverges from expectation."
- Estimation: "Break the calculation into stages and show each."
- Planning: "List the steps in order with their dependencies before executing."
