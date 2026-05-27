---
name: "spec-implement"
description: "Executes a targeted phase (or explicit set of phases) from tasks.md within a spec-flow feature directory, using lazy context loading, progress tracking, and bounded task-failure escalation. Requires spec-flow artifacts: tasks.md, spec.md, and a resolved feature-dir. This is the implementation skill for the spec-flow pipeline. Defaults to the next single incomplete phase unless the user explicitly requests more. USE FOR: executing one implementation phase at a time from a tasks.md plan after spec-tasks-draft has completed; feature work with an active spec-flow branch and spec.md present. DO NOT USE FOR: generating tasks, drafting specs, evaluating spec quality, making architectural changes outside the task plan, or implementation without spec-flow artifacts — for non-spec-flow implementation, use impl-implement."
anti-scope: "Does not generate tasks, draft specs, modify design artifacts, or make architectural decisions beyond what tasks.md specifies. For task plan generation, use spec-tasks-draft. For implementation of a single task without orchestration, use impl-implement."
---

Consult the skill from `spek-fu/ai/plugins/spec-flow/skills/spec-implement.md`. Execute its full protocol exactly as described.
