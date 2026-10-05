# Project — maintain the project documentation

## Glossary

- **Durable knowledge** - facts about the project that stay true after a feature ships (functional behavior, architecture decisions, user-facing flows, roadmap status).
- **Ephemeral knowledge** - facts specific to how a feature was built or planned (task breakdowns, in-progress notes, implementation detail that doesn't outlive the feature) that should NOT be copied into project docs.
- **Project docs** - `spek-fu/project/project.md`, `spek-fu/project/technical.md`, `spek-fu/project/project-docs/`, `spek-fu/project/roadmap.md`, `spek-fu/project/user-flows/`.
- **Area** - one subject file under `spek-fu/project/project-docs/`; the list of areas and their ID prefixes is `knowledge/area-registry.md`.
- **Functional feature** - one thing a user can do, see, or rely on, written as one sentence in an area's `## Functional` list; internal mechanics are not features.
- **Feature ID** - a feature's permanent label, `<AREA-PREFIX>-<NN>` such as `ENG-07`; allocated in order per area and never reused.
- **Owner area** - the single area whose `## Functional` list defines a feature; other areas point at the ID instead of repeating it.
- **Project README** - the repo-root `README.md`: setup, run, test, and dev commands for developers.
- **Project feature** - a minimal, high-level sketch of a planned feature, registered in the roadmap; produced by `project-feature-draft`.
- **Audit track** - the standalone skills (`project-research`, `project-devils-advocate`, `project-clarification`, `project-documentation-analysis`) that check the project docs themselves, independent of any shipped feature.
- **Audit report** - a report written under `spek-fu/project/reports/<skill>/` by an audit-track skill.
- **Reality baseline** - what the docs are verified against: `code-docs/` first, real source only where `code-docs/` is silent.

## How to use

This plugin keeps the project-level documentation in sync with what has actually shipped. Its goal is to take what shipped, separate durable knowledge from ephemeral knowledge, and write the durable knowledge into the right project doc:

- `project.md` - functional high-level overview of the project.
- `technical.md` - technical high-level overview of the project.
- `project-docs/` - per-area functional feature list (numbered IDs) plus per-feature technical detail; each file links to doc-engine modules in `spek-fu/project/code-docs` and user flows in `project/user-flows`.
- `roadmap.md` - roadmap of the project.
- `user-flows/` - step-by-step user scenarios for achieving something in the application.
- `README.md` (repo root) - developer command cheat sheet; owned by `project-readme`, not fed by shipped features.
- `reports/` - audit reports written by the audit-track skills.

`project-functional-docs`, `project-technical-docs`, and `project-user-flows` all take a shipped spec feature directory as their only input.

### Choosing the right skill

- `project-owner` - facade entrypoint; reads this section and routes a request to whichever skill(s) below apply. Use when the right skill isn't obvious or multiple skills are needed at once.
- `project-feature-draft` - drafts a minimal project feature sketch and registers it in `roadmap.md`; first step before spec work begins on a new feature idea.
- `project-functional-docs` - syncs `project.md`, `roadmap.md`, and `project-docs/*.md` `## Functional` feature lists from a shipped feature.
- `project-technical-docs` - syncs `technical.md` and `project-docs/*.md` `## Technical` sections; needs the area's feature IDs to exist first.
- `project-user-flows` - this skill writes `user-flows/*.md` scenarios.
- `project-readme` - maintains the repo-root `README.md` (setup, run, test, and dev commands); run after any change to scripts, tools, or config, independent of spec features.
- `project-research` - audit track; verifies the project docs against `code-docs/`/source and online sources, writes `reports/project-research/`; read-only on docs.
- `project-devils-advocate` - audit track; adversarially reviews vision, scope, architecture, and the docs themselves, writes `reports/project-devils-advocate/`; read-only on docs.
- `project-clarification` - audit track; resolves ambiguity in the project docs through a budgeted question loop and writes answers into the target docs; run after the research and devils-advocate reports when available.
- `project-documentation-analysis` - audit track; read-only readiness check (inventory, staleness, markers, ID/cross-reference integrity, shipped-feature coverage), writes `reports/project-documentation-analysis/`; can run alone at any time.
- `project-maintenance` - use whenever the project plugin itself must change (skill added/renamed/removed, templates changed) or its integrity needs auditing.

For one area, always run `project-functional-docs` before `project-technical-docs` — the functional list is the ID registry the technical skill reads.

The audit track is standalone and takes an optional target (a doc or area) instead of a shipped feature. Recommended order: `project-research` + `project-devils-advocate` `[P]` (parallel) → `project-clarification` → `project-documentation-analysis`.

## Commands reference

| Command | Purpose |
| --- | --- |

