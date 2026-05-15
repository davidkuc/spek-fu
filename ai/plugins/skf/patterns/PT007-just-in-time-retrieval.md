---
id: PT007
version: 1.0
name: Just-in-Time Retrieval
description: "Load context only when needed, not preemptively. USE FOR: Tasks operating over large codebases/docs where only a fraction is relevant per step. DO NOT USE FOR: Small projects where reading everything is cheap, tasks needing global view."
category: context-management
tags: [retrieval, lazy-loading, large-codebase, search]
signals: [large-codebase, context-overflow-risk]
recommended-tier: all
prevents: "Upfront context bloat — front-loading all possibly relevant context wastes the context window on material that turns out to be irrelevant to the actual steps taken."
exclusion-group: retrieval-strategy
---

# Just-in-Time Retrieval

## Reasoning

Front-loading "all the context the agent might need" wastes the context window on things that turn out to be irrelevant. Better: give the agent the ability to retrieve on demand (file search, grep, read_file) and trust it to fetch what it needs when it needs it.

This inverts the usual instinct of "give the AI as much context as possible." For large codebases, the right context for step 3 isn't knowable at step 1. Let the agent discover it.

## Examples

- Don't paste the whole codebase; give the agent grep + read_file and let it explore.
- Don't load all docs into the system prompt; let the agent search docs when it hits an unknown.
- In RAG agents: skip pre-retrieval; let the agent issue retrieval calls as part of reasoning.
