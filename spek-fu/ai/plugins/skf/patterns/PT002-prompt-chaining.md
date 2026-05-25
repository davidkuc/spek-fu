---
id: PT002
version: 1.0
name: Prompt Chaining
description: "Pass the output of one prompt as the input to the next, building a deterministic pipeline. USE FOR: Multi-stage transformations where each step has a clear, verifiable output (e.g. extract → summarize → format). DO NOT USE FOR: Single-shot tasks, exploratory work where the next step depends on judgment, or when steps could run in parallel."
category: decomposition
tags: [chaining, sequential, pipeline, deterministic]
signals: [sequential-steps, multi-domain]
recommended-tier: all
prevents: "Instruction crowding and attention dilution — a single mega-prompt covering multiple transformation stages causes the model to lose focus across stages, producing lower quality than staged prompts."
exclusion-group: decomposition-primary
---

# Prompt Chaining

## Reasoning

When a task has natural sequential stages, chaining each stage as a separate prompt produces higher quality than one mega-prompt. Each stage gets a fresh, focused context window — no instruction crowding, no attention dilution. Failures become diagnosable: you can inspect intermediate outputs and re-run only the broken link instead of the whole task.

The trade-off is rigidity. Chains assume the pipeline is known up front. If the agent needs to dynamically decide what to do next, use Divide and Conquer (dispatching sub-agents) or a reasoning loop instead.

## Examples

- Document Q&A: extract relevant passages → summarize each passage → synthesize final answer.
- Code refactor: parse current structure → propose new structure → generate diff → write tests.
- Research: gather sources → extract claims → verify claims → write report.
