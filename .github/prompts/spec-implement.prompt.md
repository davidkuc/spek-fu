---
name: "spec-implement"
description: "Executes a targeted phase (or explicit set of phases) from tasks.md, using lazy context loading, progress tracking, and bounded task-failure escalation. Defaults to the next single incomplete phase unless the user explicitly requests more. USE FOR: executing one implementation phase at a time from a tasks.md plan after spec-tasks-draft has completed. DO NOT USE FOR: generating tasks, drafting specs, evaluating spec quality, or making architectural changes outside the task plan."
anti-scope: "Does not generate tasks, draft specs, modify design artifacts, or make architectural decisions beyond what tasks.md specifies. For task plan generation, use spec-tasks-draft. For implementation of a single task without orchestration, use impl-implement."
---

Consult the skill from `ai/plugins/spec-flow/skills/spec-implement.md`. Execute its full protocol exactly as described.
