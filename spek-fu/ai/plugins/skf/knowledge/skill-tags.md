# Skill Tag Library

**Status**: Active  
**Scope**: Canonical tag vocabulary for all SKF skill files and `skills-index.json`

All skills MUST use only tags defined here. Tags are intentionally compact and reusable. Each skill SHOULD use 3-4 tags, and the first tag SHOULD identify the skill's primary category.

---

## Usage

This file is the canonical tag vocabulary referenced by:
- **`meta-skill-manage`** — validates that new or refined skills use only defined tags during the evaluate and refine operations.
- **`skill-design-guide`** — enforces tag conformance rules (correct count, leading category tag) against this vocabulary.
- **`orch-pattern-select`** — uses the **Signals** section to validate that `task-signals` inputs match the canonical signal vocabulary before pattern matching.

---

## Categories

Categories describe the primary concern a skill addresses. Each skill SHOULD lead with one category tag.

| Category | Description | Example Skills |
|---|---|---|
| `governance` | Applies or enforces governance, constitution, or SSOT policy | `gov-update` |
| `implementation` | Executes or coordinates change work and direct fixes | `impl-implement`, `gov-update` |
| `meta` | Maintains the SKF framework itself: agents, skills, prompts, knowledge, deployment, or indices | `meta-skill-manage` |
| `planning` | Produces plans, decomposes scope, or structures execution work before implementation | `orch-orchestration-plan`, `orch-pre-execution-validation` |
| `quality` | Reviews, audits, validates, or verifies artifacts | `orch-wave-verification`, `orch-final-orchestration-validation` |
| `specification` | Captures or reasons about requirements and expected behavior when present in workflow artifacts | `impl-implement`, `orch-orchestration-plan` |
| `utility` | Supplies orchestration helpers, workflow-state helpers, summaries, bundles, and environment setup | `orch-resume-detect`, `orch-wave-decompose` |

---

## Tags

Tags describe the artifact, action, or specialization of a skill. Skills may mix one category tag with up to three supporting tags.

| Tag | Meaning |
|---|---|
| `agent` | Skill primarily targets agent definitions or agent-specific review |
| `governance` | Skill primarily targets governance, constitution, or SSOT policy work |
| `implementation` | Skill primarily targets direct execution or implementation work |
| `meta` | Skill primarily targets framework maintenance and authoring workflows |
| `planning` | Skill primarily targets planning or decomposition work |
| `quality` | Skill primarily targets audit, review, validation, or verification work |
| `specification` | Skill primarily targets specification and requirements work |
| `utility` | Skill primarily provides supporting workflow mechanics |
| `adversarial` | Skill deliberately challenges assumptions or outputs |
| `advisory` | Skill advises or recommends rather than directly applies changes |
| `alignment` | Skill checks alignment between framework artifacts and project needs |
| `analysis` | Skill analyzes evidence and reports findings without applying changes |
| `approval` | Skill requires explicit approval before changes are applied |
| `artifacts` | Skill works across multiple artifacts or artifact bundles |
| `branching` | Skill analyzes or creates framework branches and parallel work splits |
| `build` | Skill performs concrete implementation work that may include build or test execution |
| `capture` | Skill records or persists structured knowledge from current work |
| `clarification` | Skill resolves ambiguity or incomplete intent |
| `cleanup` | Skill removes stale workflow state or housekeeping artifacts |
| `closure` | Skill closes a phase, workflow, or reporting loop |
| `coherence` | Skill checks consistency across related artifacts |
| `compliance` | Skill audits artifacts against explicit rules or standards |
| `consistency` | Skill checks for contradictions or internal inconsistency within a scope |
| `constitution` | Skill specifically targets constitution-tier governance files |
| `context` | Skill captures or reconstructs working context |
| `database` | Skill reads from or writes to a structured database-style store |
| `decomposition` | Skill breaks work into tasks or smaller execution units |
| `deployment` | Skill synchronizes artifacts to runtime or deployment targets |
| `devcontainer` | Skill is specific to the devcontainer runtime environment |
| `discovery` | Skill discovers files, paths, or structure before acting |
| `environment` | Skill resolves runtime environment or toolchain context |
| `evaluation` | Skill scores or assesses an artifact against review criteria |
| `feature` | Skill centers on feature-level specification work |
| `fixes` | Skill applies focused corrective changes |
| `flow-design` | Skill operates on flow design documents or formal workflow representations |
| `formalism` | Skill uses formal notations or modeling structures |
| `framework` | Skill targets the SKF framework or framework-level structure |
| `gate` | Skill acts as a pass/fail checkpoint before later execution |
| `index` | Skill operates on index traversal, discovery, or synchronization |
| `initialization` | Skill prepares a workspace or workflow for later steps |
| `intake` | Skill gathers initial context at the start of a workflow |
| `iteration` | Skill targets iteration artifacts or iteration-scoped planning |
| `knowledge` | Skill manages knowledge artifacts or lesson stores |
| `lifecycle` | Skill handles create/evaluate/refine lifecycle management |
| `navigation` | Skill helps route users or agents through framework structure |
| `optimization` | Skill improves an artifact or framework against explicit criteria |
| `orchestration` | Skill targets orchestrators, wave execution, or coordination structure |
| `patterns` | Skill selects or bundles reusable orchestration patterns |
| `plan` | Skill targets execution plans or plan validation |
| `problem-solving` | Skill focuses on bounded direct solution work |
| `prompt` | Skill manages command prompts or prompt-like framework artifacts |
| `quality-gate` | Skill serves as a final or high-level quality checkpoint |
| `readiness` | Skill determines whether a spec or artifact is ready to advance |
| `refinement` | Skill improves or sharpens an existing artifact |
| `reporting` | Skill's primary output is a structured report or verdict |
| `requirements` | Skill centers on explicit requirements or acceptance criteria |
| `resume` | Skill detects resumable state from prior work |
| `review` | Skill performs a review rather than direct implementation |
| `risk` | Skill focuses on risk discovery, challenge, or mitigation |
| `selection` | Skill selects among patterns, options, or routes |
| `signals` | Skill uses matching signals or heuristics for routing |
| `skill` | Skill targets SKF skill definitions or skill-level QA |
| `specification` | Skill targets specifications and spec artifacts |
| `ssot` | Skill checks single-source-of-truth compliance |
| `subagent` | Skill prepares work for dispatch to subordinate agents |
| `summary` | Skill compresses workflow state into a concise summary artifact |
| `sync` | Skill synchronizes authoritative artifacts with derived files |
| `tasks` | Skill generates, tracks, or structures task lists |
| `tdd` | Skill structures test-driven specification work |
| `testing` | Skill focuses on tests, test cases, or test design |
| `utility` | Skill provides supporting workflow mechanics rather than primary authoring |
| `validation` | Skill validates inputs, structure, or execution readiness |
| `verification` | Skill verifies that work satisfies expected results |
| `wave` | Skill targets wave planning, summaries, or verification |
| `workflow-state` | Skill reads or maintains resumable workflow state |

---

## Signals

Signals describe observable task or workflow cues that indicate a skill category or tag should be considered during routing.

| Signal | Meaning | Example trigger |
|---|---|---|
| `governance-change` | Task modifies governance, constitution, or SSOT artifacts | Update constitution language, enforce SSOT rules |
| `implementation-work` | Task needs direct execution or a targeted fix | Apply a change, solve a defect, run build/test steps |
| `framework-maintenance` | Task updates SKF framework assets | Create an agent, sync an index, capture a prompt |
| `planning-needed` | Task requires decomposition or execution planning before work starts | Build an orchestration plan, generate tasks |
| `quality-review` | Task requires auditing, validation, optimization, or verification | QA a skill, review an orchestration design |
| `specification-work` | Task centers on specs, requirements, or tests | Draft a spec, clarify ambiguity, design tests |
| `utility-support` | Task needs workflow support rather than primary artifact authoring | Resume detection, wave summary, environment setup |
| `approval-gate` | Change application requires explicit approval before write | Governance updates, high-risk shared artifacts |
| `index-drift` | Navigation or index files may be out of sync with disk state | Sync an index after file changes |
| `branching-analysis` | Work may benefit from framework branches or parallel splits | Assess branch relevance, create framework branch |
| `environment-setup` | Execution depends on environment or toolchain resolution | Resolve devcontainer state before work begins |
| `resume-detection` | Existing workflow state may need to be resumed safely | Re-enter an orchestration run after interruption |
| `wave-output` | A wave needs bundling, verification, or summarization | Generate a wave summary or verification report |
| `pattern-routing` | Task needs pattern selection or wave-level pattern bundling | Select patterns for an orchestration plan |
| `artifact-cross-check` | Multiple artifacts must be checked together for consistency | Compare spec/plan/tasks/checklist coherence |
