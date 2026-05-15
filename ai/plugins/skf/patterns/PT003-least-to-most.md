---
id: PT003
version: 1.0
name: Least to Most
description: "Solve the simplest sub-problem first, then use its solution as scaffolding for the next harder one. USE FOR: Problems with clear difficulty gradient where later steps build on earlier ones (algorithms, proofs, layered systems). DO NOT USE FOR: Independent parallel tasks, problems without natural ordering."
category: decomposition
tags: [scaffolding, difficulty-gradient, sequential, bootstrapping]
signals: [difficulty-gradient, sequential-steps]
recommended-tier: all
prevents: "Hard-problem hallucination — jumping to complex problems without easier sub-problem scaffolding causes plausible-sounding wrong answers because the model lacks concrete worked examples to generalize from."
exclusion-group: decomposition-primary
---

# Least to Most

## Reasoning

LLMs perform better on hard problems when easier sub-problems are solved first and kept in context as worked examples. The model essentially teaches itself the pattern on the easy case, then generalizes. This is different from Divide and Conquer (which splits into independent pieces) — here the order matters because each step's output informs the next.

The key signal: if you can rank sub-problems from "obviously trivial" to "the actual hard part," this pattern applies. If sub-problems are peers, use Divide and Conquer.

## Examples

- Math: solve for 2 variables before tackling the full system of 5.
- Codebase migration: migrate a leaf module with no dependencies first, then work upward.
- Algorithm design: write the brute-force O(n²) solution, then optimize using its correctness as a test oracle.
