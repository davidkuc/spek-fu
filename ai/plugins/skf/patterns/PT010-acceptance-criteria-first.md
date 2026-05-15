---
id: PT010
version: 1.0
name: Acceptance Criteria First
description: "Define the checklist of 'done' before starting the work. USE FOR: Any task with multiple requirements, deliverables that will be reviewed, work where 'done' is ambiguous. DO NOT USE FOR: Trivial single-step tasks, exploratory work without a defined endpoint."
category: planning
tags: [requirements, definition-of-done, verification, checklist]
signals: [ambiguous-done, multi-domain, final-deliverable]
recommended-tier: all
prevents: "Drifting done and hallucinated success — without an explicit criteria checklist, agents declare completion when they run out of obvious next steps, not when actual requirements are met."
---

# Acceptance Criteria First

## Reasoning

Without explicit criteria, "done" drifts. The agent declares completion when it feels finished, which often means "when it ran out of obvious next steps" — not when the actual requirements are met. Worse, ambiguous goals invite hallucinated success: the agent confidently reports done while half the requirements are missed.

Forcing the agent to write the acceptance criteria first (and reference them at the end) creates a verifiable contract. The end-of-task check becomes mechanical: walk the list, mark each item, justify any unmet ones.

## Examples

- Before coding: "List the criteria this implementation must satisfy. Check each one at the end."
- Before writing a doc: "List sections required and audience needs. Verify all are addressed."
- In an orchestrator: dispatcher generates acceptance criteria; sub-agent reports back against them; dispatcher verifies before accepting.
