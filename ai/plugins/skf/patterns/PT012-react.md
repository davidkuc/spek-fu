---
id: PT012
version: 1.0
name: ReAct
description: "Interleave reasoning ('Thought') with tool use ('Action') and observation in a loop. USE FOR: Tasks requiring external information or environment interaction (search, file ops, API calls). DO NOT USE FOR: Pure reasoning with all info already in context, single-tool one-shot calls."
category: reasoning
tags: [reasoning, action, tool-use, loop, grounded]
signals: [large-codebase, investigation, unfamiliar-territory]
recommended-tier: all
prevents: "Blind action or pure-reasoning loop — acting on tools without a stated reason produces unfocused tool use; reasoning in circles without grounding in real data produces plans that diverge from reality."
exclusion-group: reasoning-loop
---

# ReAct

## Reasoning

ReAct (Reason + Act) structures agent loops as: think about what to do → take an action → observe the result → think again. This prevents two failure modes: blind action (calling tools without a plan) and pure reasoning (planning forever without grounding in real data).

For VS Code / Copilot agents, this is essentially the default agent loop, but making it explicit in instructions improves discipline. The model is told: never act without a stated reason; never reason in circles without acting.

## Examples

- File investigation: "Thought: I need to find where X is defined. Action: grep -r 'def X'. Observation: found in foo.py:42. Thought: now I need to see how it's called…"
- Bug hunt: alternates between reading code and running tests, with a stated hypothesis driving each action.
- API exploration: each call is preceded by what the agent expects to learn from it.
