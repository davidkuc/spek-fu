---
name: "spec-clarification"
description: "Conducts a structured multi-pass ambiguity scan on a feature spec file and resolves critical gaps through a configurable interactive questioning loop, accumulating all answers in an in-memory Answer Buffer and writing them to the spec file after the question loop completes. USE FOR: reducing spec ambiguity before planning, detecting missing acceptance criteria, encoding clarifications into spec sections. DO NOT USE FOR: drafting new specs, producing implementation plans, or executing code changes."
anti-scope: "Does not create new spec files, produce implementation plans, or make code changes. For spec drafting use spec-feature-draft; for adversarial review use spec-devils-advocate."
---

Consult the skill from `ai/plugins/spec-flow/skills/spec-clarification.md`. Execute its full protocol exactly as described.
