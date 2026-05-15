---
id: PT015
version: 1.0
name: Length Budget
description: "State explicit length limits (word count, line count, section count). USE FOR: Outputs that tend to bloat (summaries, reviews, explanations), workflows where downstream context is constrained. DO NOT USE FOR: Tasks where completeness matters more than brevity (full implementations, comprehensive docs)."
category: output-format
tags: [length, budget, brevity, conciseness, compression]
signals: [bloat-prone, context-overflow-risk, downstream-consumer]
recommended-tier: all
prevents: "Response bloat and context inflation — without a stated budget, agents over-explain by default, burying the actual answer and inflating context for all downstream steps."
---

# Length Budget

## Reasoning

Without a budget, agents over-explain. They restate the problem, add caveats, list alternatives nobody asked for, and produce a 2000-word answer to a 200-word question. This bloats context for downstream steps and buries the actual answer.

A stated budget is a forcing function. "In 3 bullets" or "under 100 words" makes the model prioritize. Budgets are also a quality signal: if the agent can't compress to the budget, the task probably wasn't well-defined.

## Examples

- Code review summary: "Top 3 issues, one sentence each."
- Sub-agent report: "Conclusion in ≤50 words; details in linked file."
- Commit message: "Subject ≤72 chars; body ≤3 lines."
- Plan: "≤7 steps; merge or drop anything beyond."
