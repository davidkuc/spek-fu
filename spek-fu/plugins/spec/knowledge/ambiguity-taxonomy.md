# Ambiguity Taxonomy

Categories `spec-clarification` scans a spec against. For each, assign **Clear**, **Partial**, or **Missing**.

| Category | Inspect for |
|----------|-------------|
| Functional Scope & Behavior | Core user goals, success criteria, explicit out-of-scope declarations, role differentiation |
| Domain & Data Model | Entities, attributes, relationships, identity rules, lifecycle/state transitions, scale assumptions |
| Interaction & UX Flow | Critical user journeys, error/empty/loading states, accessibility or localization notes |
| Non-Functional Quality Attributes | Performance targets, scalability limits, reliability/uptime expectations, observability signals, security & privacy posture, compliance constraints |
| Integration & External Dependencies | External services/APIs and their failure modes, data import/export formats, protocol/versioning assumptions |
| Edge Cases & Failure Handling | Negative scenarios, rate limiting, conflict resolution |
| Constraints & Tradeoffs | Technical constraints, explicit tradeoffs, rejected alternatives |
| Completion Signals | Acceptance criteria testability, measurable Definition of Done indicators |
| Misc / Placeholders | TODO markers, unresolved decisions, vague adjectives lacking quantification |
| Documented Assumptions | Scan the spec's `## Assumptions` section. Promote any entry with broader scope, design impact, or testability implications to a candidate question. Undocumented assumptions count as **Missing**. |

If a `spec-research-report.md` or `devils-advocate-report.md` exists next to `spec-file`, cross-reference its open questions, `[NEEDS FURTHER RESEARCH: ...]` markers, low-confidence findings, or HIGH-severity findings against these categories — mark the touched category(ies) at least **Partial**, and prioritize them first when building the question queue.

For each **Partial** or **Missing** category, add a question candidate unless clarification wouldn't materially impact implementation or is better deferred. Apply an (Impact × Uncertainty) heuristic when more categories qualify than the remaining budget allows.
