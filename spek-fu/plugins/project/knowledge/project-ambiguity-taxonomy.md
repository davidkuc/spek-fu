# Project Ambiguity Taxonomy

Categories `project-clarification` scans the project docs against. For each, assign **Clear**, **Partial**, or **Missing**.

| Category | Inspect for |
|----------|-------------|
| Purpose & Value | `project.md` Cel / Dlaczego / Wartość: who the project serves, the problem, measurable value |
| Scope & Anti-scope | Explicit in/out of scope, deliberate MVP limits, roles and what each may do |
| Functional Feature Definition | Each `## Functional` entry is one user-observable sentence; no internal mechanics; no duplicate or overlapping features across areas |
| Domain & Data Model | Entities, identity rules, lifecycle/state transitions, ownership across areas |
| Architecture & Technology Decisions | `technical.md` and area `## Technical`: decisions stated with rationale, rejected alternatives, `Consciously Omitted` coverage |
| Cross-Cutting & Operations | Security and privacy posture, observability, deployment, environments, failure handling, rate limits |
| User Flow Completeness | Critical journeys covered by `user-flows/`; error, empty, and edge paths; links from areas resolve |
| Roadmap & Sequencing | Phase ordering rationale, dependencies between PF entries, status accuracy |
| Terminology & Area Boundaries | One term per concept (including PL/EN drift); area ownership per `knowledge/area-registry.md` unambiguous |
| Placeholders & Assumptions | TODO markers, `[NEEDS CLARIFICATION]`, vague adjectives lacking quantification, undocumented assumptions (count as **Missing**) |

If a `project-research-report.md` or `project-devils-advocate-report.md` exists under the reports root, cross-reference its open questions, `[NEEDS FURTHER RESEARCH: ...]` markers, drift verdicts, low-confidence findings, and HIGH-or-above risks against these categories. Mark each touched category at least **Partial** and queue it first.

For each **Partial** or **Missing** category, add a question candidate unless clarification would not materially change what the docs promise or is better deferred. Apply an (Impact × Uncertainty) heuristic when more categories qualify than the remaining budget allows.
