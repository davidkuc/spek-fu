# Pattern Tag Library

**Version**: 1.0  
**Status**: Active  
**Scope**: Canonical tag and signal vocabulary for all SKF pattern files and `patterns-index.json`

All patterns MUST use only tags and signals defined here. To add a new tag or signal, update this file first, then the pattern.

---

## Categories

Categories describe the primary concern a pattern addresses. Each pattern belongs to exactly one category.

| Category | Description | Example Patterns |
|---|---|---|
| `decomposition` | How to split large or complex work into smaller independent pieces | PT001, PT002, PT003, PT023 |
| `planning` | How to define success criteria and assess feasibility before execution | PT004, PT010 |
| `context-management` | How to preserve, prune, or retrieve information across session length | PT005, PT006, PT007 |
| `verification` | How to validate, review, and confirm correctness of outputs | PT008, PT009, PT025 |
| `reasoning` | How to structure intermediate thought processes for accuracy | PT011, PT012, PT013 |
| `routing` | How to select or dispatch tasks to correctly scoped agents or specialists | PT019 |
| `output-format` | How to shape, constrain, or control the structure of agent outputs | PT014, PT015, PT016 |
| `error-handling` | How to recover from failure, define fallbacks, and degrade gracefully | PT026 |

---

## Tags

Tags describe the technique, mechanism, or structural characteristic of a pattern. A pattern may have 2–6 tags. Tags are not exclusive.

| Tag | Meaning |
|---|---|
| `decomposition` | Pattern breaks work into smaller units |
| `parallel-execution` | Pattern enables sub-tasks to run concurrently |
| `scale` | Pattern helps manage large-scale workflows |
| `batching` | Pattern groups related work for efficiency |
| `chaining` | Pattern passes output of one step as input to the next |
| `sequential` | Pattern enforces ordered step execution |
| `pipeline` | Pattern uses multi-stage transformation pipelines |
| `deterministic` | Pattern produces predictable, reproducible outputs |
| `scaffolding` | Pattern builds from easy to hard progressively |
| `difficulty-gradient` | Pattern matches task difficulty to agent capability level |
| `bootstrapping` | Pattern seeds a complex task with simpler solved sub-tasks |
| `exploration` | Pattern investigates unknowns before committing to an approach |
| `de-risk` | Pattern validates risky assumptions early |
| `unknowns` | Pattern explicitly handles uncertainty |
| `feasibility` | Pattern tests viability before full investment |
| `context` | Pattern involves managing context window content |
| `pruning` | Pattern removes irrelevant content from context |
| `efficiency` | Pattern reduces wasted context or compute |
| `summarization` | Pattern compresses content to essential form |
| `externalization` | Pattern stores working state outside the context window |
| `working-memory` | Pattern treats context as a scratchpad with limits |
| `artifacts` | Pattern creates persistent intermediate files |
| `persistence` | Pattern preserves state across context boundaries |
| `retrieval` | Pattern fetches content on-demand rather than upfront |
| `lazy-loading` | Pattern defers resource acquisition until needed |
| `large-codebase` | Pattern applies to repositories too large for full context |
| `search` | Pattern relies on targeted search rather than full read |
| `review` | Pattern dispatches an independent review pass |
| `adversarial` | Pattern deliberately challenges the primary output |
| `quality-gate` | Pattern enforces a pass/fail threshold before proceeding |
| `security-sensitive` | Pattern applies extra scrutiny to security-relevant outputs |
| `evaluation` | Pattern scores or critiques an output systematically |
| `optimization` | Pattern improves output quality through iteration |
| `loop` | Pattern repeats until a termination condition is met |
| `critique` | Pattern generates targeted criticism of outputs |
| `testing` | Pattern requires executable verification of outputs |
| `execution-verification` | Pattern runs code or queries to confirm correctness |
| `validation` | Pattern checks output against expected behavior |
| `executable` | Pattern applies to outputs that can be run |
| `self-correction` | Pattern makes agent re-examine failed approaches |
| `recovery` | Pattern restores progress after a failure or contradiction |
| `adaptive` | Pattern adjusts approach based on intermediate results |
| `meta-cognition` | Pattern reasons about its own reasoning process |
| `reflection` | Pattern pauses to reassess before continuing |
| `requirements` | Pattern grounds work in explicit success criteria |
| `definition-of-done` | Pattern requires an explicit done condition |
| `verification` | Pattern ties planning or execution to explicit verification activity |
| `checklist` | Pattern uses a verification checklist |
| `step-by-step` | Pattern makes reasoning explicit at each step |
| `reasoning` | Pattern involves structured intermediate reasoning steps |
| `chain-of-thought` | Pattern uses CoT-style explicit reasoning |
| `transparency` | Pattern makes intermediate steps visible |
| `action` | Pattern combines reasoning with tool execution |
| `tool-use` | Pattern explicitly orchestrates tool calls |
| `grounded` | Pattern grounds reasoning in real data from tools |
| `debugging` | Pattern aids in root-cause investigation |
| `hypothesis` | Pattern forms and tests explicit hypotheses |
| `root-cause` | Pattern drives toward a root cause rather than symptoms |
| `investigation` | Pattern explores evidence systematically |
| `falsifiable` | Pattern requires hypotheses to be testable |
| `structured-output` | Pattern enforces a defined output schema |
| `schema` | Pattern uses explicit schema definitions |
| `integration` | Pattern enables downstream system consumption |
| `parsing` | Pattern produces machine-parseable output |
| `contract` | Pattern treats output format as a binding interface |
| `length` | Pattern controls output length explicitly |
| `budget` | Pattern assigns token or word budgets |
| `brevity` | Pattern suppresses unnecessary verbosity |
| `conciseness` | Pattern minimizes output to essential content |
| `compression` | Pattern reduces output size without losing meaning |
| `constraints` | Pattern applies explicit suppression constraints |
| `negative-constraints` | Pattern uses "do not" instructions |
| `suppression` | Pattern directly suppresses unwanted model behaviors |
| `precision` | Pattern increases output specificity |
| `dispatch` | Pattern dispatches sub-tasks to specialist agents |
| `specialist` | Pattern assigns narrow, focused roles to agents |
| `orchestration` | Pattern coordinates multiple agents |
| `delegation` | Pattern hands off sub-tasks to specialized agents |
| `multi-domain` | Pattern spans tasks across more than one domain |
| `parallelization` | Pattern enables concurrent execution of independent tasks |
| `concurrent` | Pattern runs multiple tasks simultaneously |
| `throughput` | Pattern maximizes tasks completed per unit time |
| `independence` | Pattern explicitly checks for task independence |
| `fallback` | Pattern defines backup approaches |
| `resilience` | Pattern maintains progress through partial failures |
| `error-handling` | Pattern manages failure modes explicitly |
| `chain` | Pattern defines an ordered sequence of alternatives |
| `alternatives` | Pattern maintains a set of alternative approaches |

---

## Operational Tags

Use these tags for infrastructure, runtime environment, and execution-mechanics patterns.

| Tag | Meaning |
|---|---|
| `devcontainer` | Pattern is specific to dev container environments and their constraints |
| `terminal` | Pattern depends on terminal execution behavior or terminal session state |
| `bash` | Pattern is specific to bash shell usage or bash-compatible command composition |
| `pwsh` | Pattern is specific to PowerShell usage or PowerShell-compatible command composition |
| `indexing` | Pattern depends on index files, traversal, or index-driven discovery |
| `dispatch` | Pattern dispatches sub-tasks to specialist agents |
| `knowledge` | Pattern depends on structured knowledge retrieval or knowledge-store updates |
| `orchestration` | Pattern coordinates multiple agents or workflow stages |
| `environment` | Pattern adapts to runtime environment detection or environment-specific behavior |
| `toolchain` | Pattern depends on tool availability, activation, or execution ordering |
| `automation` | Pattern relies on deterministic scripts or automated validation steps |

---

## Signals

Signals describe observable properties of the task or context that indicate a pattern should be considered. A pattern may list 1–4 signals. Signals are used by `orch-pattern-select` to match patterns to incoming tasks.

| Signal | Meaning | Example trigger |
|---|---|---|
| `large-task` | Task spans many files, steps, or domains | >10 files, >5 execution steps |
| `context-overflow-risk` | Task risks filling the context window | Long sessions, codebase-wide reads |
| `parallel-tasks` | Multiple sub-tasks with no data dependencies | Independent module changes |
| `sequential-steps` | Sub-tasks must be executed in a fixed order | Output of step N is input of step N+1 |
| `multi-domain` | Task touches more than one domain or skill group | Code + docs + tests + deployment |
| `difficulty-gradient` | Task complexity increases significantly across sub-tasks | Trivial → complex progression |
| `unfamiliar-territory` | Domain or codebase is unknown; feasibility is uncertain | First time in a new codebase |
| `investigation` | Task requires evidence gathering before a solution path is known | Bug hunt, root cause analysis |
| `planning` | Task requires deliberate up-front planning | Architectural design, multi-phase work |
| `long-running-session` | Session has many prior turns or large accumulated context | >20 messages or many tool calls |
| `reusable-intermediate` | Intermediate results will be referenced multiple times | Shared output across >1 wave |
| `large-codebase` | Codebase is too large to read in full | Repos with >100 files |
| `high-stakes` | Output will influence a critical system or decision | Production code, security design |
| `final-deliverable` | Output is the complete, user-facing artifact | Spec, architecture doc, full implementation |
| `security-sensitive` | Output involves authentication, authorization, or data protection | Auth flows, access control logic |
| `executable-output` | Output is expected to be run (code, queries, scripts) | All implementation tasks |
| `code-generation` | Task produces code as its primary deliverable | Feature implementation |
| `ambiguous-done` | Success criteria are implicit or unverified | Requirements said "improve performance" |
| `multi-step-logic` | Task involves multi-step reasoning chains | Complex algorithm design |
| `debugging` | Task involves diagnosing a failure or unexpected behavior | Bug reproduction, test failure analysis |
| `downstream-consumer` | Another agent, system, or step consumes this output | Wave N → Wave N+1 handoff |
| `bloat-prone` | Agent is likely to over-explain or produce verbose output | Summaries, executive reports |
| `known-failure-mode` | Agent has a documented tendency to fail in a specific way | Known hallucination pattern, suppressed tendency |
