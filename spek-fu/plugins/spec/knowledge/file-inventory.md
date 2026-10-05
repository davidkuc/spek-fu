# Spec File Inventory

## Plugin Root

- `spec-workflow.md` - Glossary, phase order, and skill-selection guide for the spec-driven workflow.

## agents/

- `spec-implement-executor/AGENT.md` - Subagent that executes exactly one `task-id` via `spec-implement` and reports a fixed status vocabulary.

## knowledge/

- `ambiguity-taxonomy.md` - Controlled taxonomy of ambiguity categories `spec-clarification` scans specs against.
- `config.json` - Per-skill tunable limits (max findings, max loops, budgets, paths) read by most spec skills.
- `orchestration-format.md` - Shared format contract for how `spec-orchestrator` sequences and reports task dispatch.
- `pipeline-artifacts.md` - Registry of the artifact set produced across the Define/Research/Plan/Implement pipeline.
- `spec-sync-contract.md` - Contract describing how spec artifacts stay in sync as upstream documents change.
- `tdd-design-taxonomy.md` - Controlled taxonomy of test-design categories `spec-tdd-draft` classifies findings against.
- `testability-taxonomy.md` - Controlled taxonomy of testability categories `spec-testability-draft` classifies findings against.

## skills/

- `spec-clarification/SKILL.md` - Scans a feature spec for ambiguity and resolves critical gaps via a budgeted question loop.
- `spec-devils-advocate/SKILL.md` - Adversarially reviews a feature spec and produces a Devils Advocate Report.
- `spec-feature-analysis/SKILL.md` - Produces a read-only Feature Analysis Report with a readiness verdict.
- `spec-feature-draft/SKILL.md` - Generates a feature spec file and matching numbered branch/directory.
- `spec-implement/SKILL.md` - Executes a single delegated task from a feature's tasks.md and reports its result.
- `spec-manual-implement/SKILL.md` - Executes one, several, or all selected tasks from a feature's tasks.md inline and reports the results.
- `spec-orchestrator/SKILL.md` - Coordinates end-to-end multi-agent execution of a tasks.md, phase by phase.
- `spec-quick-planner/SKILL.md` - Generates a remediation plan and injects tasks into an existing tasks.md.
- `spec-research/SKILL.md` - Decomposes a spec into research dimensions and synthesizes a research report.
- `spec-tasks-draft/SKILL.md` - Generates a dependency-ordered tasks.md from a feature's design artifacts.
- `spec-tdd-draft/SKILL.md` - Translates a spec and technical plan into a TDD design report.
- `spec-technical-draft/SKILL.md` - Translates a spec into research, data-model, contracts, quickstart, and technical plan.
- `spec-testability-draft/SKILL.md` - Produces a Testability Assessment Report from a spec and Devils Advocate Report.

## templates/

- `devils-advocate-report-template.md` - Template for the Devils Advocate Report artifact.
- `feature-analysis-report-template.md` - Template for the Feature Analysis Report artifact.
- `quickstart-template.md` - Template for a feature's quickstart artifact.
- `remediation-plan-template.md` - Template for a quick-planner remediation plan.
- `spec-feature-template.md` - Template for a feature spec file.
- `spec-research-report-template.md` - Template for the research report artifact.
- `tasks-template.md` - Template for a feature's tasks.md.
- `tdd-report-template.md` - Template for the TDD design report artifact.
- `technical-plan-template.md` - Template for the technical plan artifact.
- `testability-assessment-report-template.md` - Template for the Testability Assessment Report artifact.
