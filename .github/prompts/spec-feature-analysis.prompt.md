---
name: "spec-feature-analysis"
description: "Inspects all spec-flow pipeline artifacts in a feature directory, producing a Feature Analysis Report with artifact inventory, staleness signals, [NEEDS CLARIFICATION] marker counts, tasks state breakdown, cross-artifact consistency findings, and a readiness verdict. USE FOR: verifying all upstream artifacts are complete, coherent, and non-stale before starting implementation. DO NOT USE FOR: modifying artifacts, re-running upstream pipeline skills, or implementing the feature — consult the **spec-implement** skill for implementation."
anti-scope: "Does not modify spec.md, tasks.md, or any upstream pipeline artifact. Does not invoke other skills or re-run any upstream pipeline step. The only file this skill writes is feature-analysis-report.md."
---

Consult the skill from `spek-fu/ai/plugins/spec-flow/skills/spec-feature-analysis.md`. Execute its full protocol exactly as described.
