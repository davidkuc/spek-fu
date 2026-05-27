---
id: PT008
version: 1.0
name: Adversarial Review
description: "A second agent (or fresh instance) reviews the first agent's output with the explicit job of finding flaws. USE FOR: High-stakes outputs (production code, security-sensitive logic, public-facing content), final deliverables. DO NOT USE FOR: Drafts, exploratory work, low-stakes throwaway code."
category: verification
tags: [review, adversarial, quality-gate, security-sensitive]
signals: [high-stakes, final-deliverable, security-sensitive]
recommended-tier: standard-agent
prevents: "Author-bias self-review failure — an agent reviewing its own output has the prior reasoning in context and is biased toward confirming rather than challenging it; independent review catches defects the author cannot see."
exclusion-group: review-strategy
---

# Adversarial Review

## Reasoning

An agent reviewing its own work is biased toward confirming its previous conclusions — the original reasoning is in context and feels correct. A separate instance with a clean context and an explicit "find what's wrong" mandate catches issues the author missed.

The reviewer must be adversarial, not supportive. "Looks good, here are some minor suggestions" is failure mode. The prompt should explicitly say: assume something is wrong, find it, do not praise. In Copilot/VS Code, this can be a separate chat session or a dedicated reviewer skill.

## Examples

- Code review: reviewer agent is told "this code has at least one bug; find it" even if you don't know whether it does.
- Plan review: reviewer agent critiques the plan against requirements without seeing the author's reasoning.
- Security review: dedicated agent with security-focused system prompt examines diffs.
