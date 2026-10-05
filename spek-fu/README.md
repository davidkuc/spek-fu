# Spek-Fu

Spek-Fu is a spec-driven development framework for AI coding agents. It organizes work into plugins, each owning a phase of the software lifecycle: defining and implementing features, documenting code, and keeping project-level knowledge in sync with what has actually shipped.

## Prerequisites

- Python

## Glossary

**Constitution** - `spek-fu/constitution/constitution.md`. The fixed set of behavioral and software-development principles every AI agent in this project must follow.

**Plugin** - A module-sized, self-contained unit of the framework, living under `spek-fu/plugins/<name>/`, following the Plugin Structure above.

**Skill** - A single documented AI instruction set (`SKILL.md`) that performs one unit of work within a plugin.

**Agent** - An orchestration subagent (`AGENT.md`) that executes a plugin end-to-end, choosing the right skill based on context.

**Workflow** - The `<plugin>-workflow.md` file describing how a plugin's skills fit together and which one to use when.

**Maintenance skill** - The skill in a plugin (e.g. `*-maintenance`) responsible for keeping that plugin itself internally consistent when it changes.

**Project feature** - A high-level sketch of a planned feature, produced by `spec-project-feature` and tracked in `spek-fu/project/roadmap.md`.

**Spec feature** - A framework development unit consisting of a feature directory (under `spek-fu/project/spec-features/`), a matching git branch, and the specs/artifacts produced through the spec phases.

**Compound knowledge** - Lessons learned during AI work, submitted by the human or the AI itself, stored for reuse across sessions (framework plugin).

**Compound patterns** - Recurring patterns extracted from repeated compound knowledge entries.

**Durable knowledge** - Facts about the project that stay true after a feature ships (functional behavior, architecture decisions, user-facing flows, roadmap status). Belongs in project docs.

**Ephemeral knowledge** - Facts specific to how a feature was built or planned (task breakdowns, in-progress notes) that should not be copied into project docs.

**Doc module** - A single doc file at `spek-fu/project/code-docs/<mirrored-folder>.md` documenting one source directory, linked to it via a two-way pointer (doc-engine plugin).

**Drift** - The state where a doc module, code comment, or index entry no longer accurately reflects the current source code.

## High-Level Flow

### Feature Lifecycle
The feature lifecycle, in order.
`[P]` marks steps that can run in parallel.
`[O]` marks steps that are optional.

**Define**
1. `project-feature-draft` - sketch and register a project feature.
2. `spec-feature-draft` - draft the feature spec, branch, and feature directory.

**Research**
3. `spec-research` `[P]` `[O]` - fact-find against the feature spec.
4. `spec-devils-advocate` `[P]` `[O]` - risk-review the feature spec.
5. `spec-clarification` `[O]` - resolve gaps using both reports.

**Plan**
6. `spec-testability-draft` `[O]` - assess testability.
7. `spec-technical-draft` - produce the technical plan and artifacts.
8. `spec-tdd-draft``[O]` - produce the TDD test design.
9. `spec-tasks-draft` - generate the dependency-ordered tasks file.
10. `spec-feature-analysis` `[O]` - verify all artifacts are consistent and ready.

**Implement**
11. `spec-manual-implement` - Implements one, several, or all selected tasks from the **tasks file** inline in the current
12. `spec-quick-planner` `[O]` - append remediation tasks for emergent bugs or requirements.

**Document** (after a spec feature ships)
13. `project-functional-docs`, `project-technical-docs`, `project-user-flows` `[P]` - extract durable knowledge from the shipped feature into project docs.

`doc-engine-traverse` and `doc-engine-enrich` run ad hoc throughout - traverse when exploring unfamiliar code, enrich when new files lack docs or pointers.

### Boostrapping a new plugin

**Bootstrapping a new plugin** (framework plugin, independent of the feature lifecycle)

1. `framework-create-plugin` - scaffold the plugin folder and draft workflow.
2. `framework-create-skill` / `framework-create-agent` - add its skills and agents.
3. `framework-create-maintenance` - add its maintenance skill once the plugin is complete.
4. `framewwork-create-owner` - adds the plugin's owner entrypoint skill.

### Maintaining a plugin

Run whenever a plugin's skills, agents, scripts, knowledge files, or templates change, or its integrity needs auditing.

1. Change the plugin's files.
2. Run that plugin's `<plugin>-maintenance` skill (`framework-maintenance`, `doc-engine-maintenance`, `project-maintenance`, or `spec-maintenance`) - verifies the plugin's file inventory and workflow doc stay accurate.
3. The maintenance skill invokes `framework-readme` as its final step to keep this README in sync.

### Not sure what skill to use?

Each plugin has a `<plugin>-owner` owner skill which serves as a entrypoint to the plugin. It selects the appropriate skills based user request and uses them to fulfill the users request.

## Plugins

| Plugin | Purpose |
|---|---|
| `spec` | Spec-driven development workflow: define, research, plan, and implement features through a sequence of skills producing spec artifacts (feature spec, research/devils-advocate/testability reports, technical plan, TDD design, tasks file), then orchestrates implementation. |
| `doc-engine` | Documentation workflow system connecting source code and docs through two-way pointers, a searchable index, and a controlled tag vocabulary. Traverses, enriches, and updates code documentation in `spek-fu/project/code-docs`. |
| `project` | Keeps project-level documentation (`project.md`, `technical.md`, `roadmap.md`, `project-docs/`, `user-flows/`) in sync with shipped spec features, separating durable from ephemeral knowledge. |
| `framework` | Core of Spek-Fu itself: scaffolds new plugins, skills, agents, and maintenance skills; manages the compound-knowledge learning database. |

See each plugin's `*-workflow.md` for its detailed skill sequence and glossary.

## Framework Map

`spek-fu/constitution/` - Fundamental principles for the project.
`spek-fu/plugins/` - Module-sized plugins with skills, agents and scripts.
`spek-fu/project/` - Project documentation - architecture, features, roadmap, user flows, code documentation.

## Plugin Structure

```
agents/ - Orchestration subagents that execute the plugin.
knowledge/ - Specific knowledge the plugin's skills rely on.
scripts/ - Scripts, tools etc.
skills/ - AI instructions.
templates/ - Template files.
*-workflow.md - Documented workflow for this plugin.
```