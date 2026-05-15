---
id: PT016
version: 1.0
name: Negative Constraints
description: "Explicitly state what the output must NOT contain or do. USE FOR: Outputs with consistent failure modes (preamble, apologies, hedging, forbidden patterns), high-precision contexts. DO NOT USE FOR: Open creative tasks where constraints stifle quality."
category: output-format
tags: [constraints, negative-constraints, suppression, precision]
signals: [known-failure-mode, bloat-prone]
recommended-tier: all
prevents: "Trained-default override — positive instructions often fail to suppress trained tendencies (preamble, apologies, over-explanation); negative constraints directly target and suppress specific unwanted behaviors."
---

# Negative Constraints

## Reasoning

Models have strong defaults that positive instructions don't always override. "Be concise" loses to the trained tendency to add preamble; "give me the answer" loses to "Sure! Here's what you asked for…" Negative constraints — "do not start with 'Sure'", "do not apologize", "do not include explanations" — directly suppress the unwanted behavior.

The same applies to code: "do not use library X", "do not modify tests", "do not add comments" prevent specific failure modes that positive framing misses.

## Examples

- "Do not preamble. Start with the answer."
- "Do not modify any file outside src/. Do not add new dependencies."
- "Do not use any external libraries; standard library only."
- "Do not include reasoning in the output; reasoning goes in <thinking> tags only."
