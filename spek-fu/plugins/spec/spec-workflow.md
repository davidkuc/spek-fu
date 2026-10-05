# spec: A spec-driven development workflow

This plugin provides a spec-driven development workflow. Use these skills to create and refine specifications, do extensive research, planning and automate development processes.

## Glossary

**Spec feature** - Framework development unit consisting of feature directory, branch and specs.

## How to use

### Model Tiers
**Fast** - Claude Haiku 4.5
**Medium** - Claude Sonnet 5  (Medium effort)
**Hard** - Claude Opus 5 (High effort)

Spec is divided into four phases: **Define** -> **Research** -> **Plan** -> **Implement**.

Skills are run sequentially. Some of them can possibly be run in parallel.
Each skill produces artifacts that are used by the next skill in the sequence - that's why it's important to keep this order.

Best if the skill `spec-feature-draft` is provided with an explicit path/reference to an existing project feature (drafted via the project plugin's `project-feature-draft` skill). Other skills can be run without any reference, since they autodetect required artifacts and report anything missing.

#### Basic Workflow

**Define**
- `spec-feature-draft`

**Plan**
- `spec-technical-draft`
- `spec-tasks-draft`

**Implement**
- `spec-manual-implement`

#### Advanced Workflow

**Define**
- `spec-feature-draft`

**Research**
- `spec-research` (Optional)
- `spec-devils-advocate` (Optional)
- `spec-clarification` (Optional)

**Plan**
- `spec-testability-draft` (Optional)
- `spec-technical-draft`
- `spec-tdd-draft` (Optional)
- `spec-tasks-draft`
- `spec-feature-analysis` (Optional)

**Implement**
- `spec-manual-implement`
- `spec-orchestrator` + `spec-implement` agents (Alternative)
- `spec-quick-planner` (Optional)

**Maintenance**
- `spec-maintenance` - Use whenever the spec plugin itself must change (skill/agent/knowledge/template added, renamed, or removed) or its integrity needs auditing.

### Choosing the right skill

Most of these skills are run sequentially.
Candidates for parellel work are marked with [P] tag.

0. `spec-owner` - Facade entrypoint; routes a free-form request to the correct sub-skill(s) below.
1. `spec-feature-draft` - Creates spec feature directory, initializes new branch and produces **feature spec**.
2. `spec-research` - Does detailed research against the **feature spec** and produces **research report** [P] (Parallel with `spec-devils-advocate`).
3. `spec-devils-advocate` - Does detailed risk-analysis against the **feature spec** and produces **devils report** [P] (Parallel with `spec-research`).
4. `spec-clarification` - Clarifies against the **research report** and **devils report** and updates the **feature spec** with clarifications.
5. `spec-testability-draft` - Does detailed testability analysis against the **feature spec** and produces a **testability report**.
6. `spec-technical-draft` - Creates a detailed technical plan using the **feature spec** and **testability report** and produces **technical plan + artifacts**.
7. `spec-tdd-draft` - Creates a list of tests to implement based on **feature spec** and **technical plan + artifacts** and produces a **tdd report**.
8. `spec-tasks-draft` - Creates the tasks based on **feature spec**, **technical plan + artifacts** and **tdd report** and produces a **tasks file**.
9. `spec-feature-analysis` - Runs an analysis against all artifacts in this spec feature.
10. `spec-manual-implement` - Implements one, several, or all selected tasks from the **tasks file** inline in the current session, spawning `framework-compounding-agent`/`doc-engine-executor` only for `[K-*]`/`[D-*]` tasks.
10. (Alternative) `spec-orchestrator` - Orchestrates the implementation of the feature, delegating `spec-implement-executor` subagents to implement tasks written in the **tasks file**.
11. (Optional) `spec-quick-planner` - Create a plan and append tasks for it into the existing **tasks file** to remediate newly emerged requirements or bugs.


## Commands reference

| Command | Purpose |
|---------|---------|
| | |
