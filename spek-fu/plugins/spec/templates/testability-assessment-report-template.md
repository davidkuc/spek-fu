<!--
metadata:
  spec_file: [path to assessed spec]
  devils_advocate_report: [path to source report]
  assessment_date: [YYYY-MM-DD]
  findings_count: [total findings in Risk Findings]
  assessment_status: ok | blocked
-->

# Testability Assessment Report: [FEATURE NAME]

**Spec**: `[path to spec.md]`
**Devils Advocate Report**: `[path to devils-advocate-report.md]`

---

## Executive Summary

- Overall Testability Grade: [A–F]
- Primary Structural Weakness: [weakness]
- Primary Structural Strength: [strength]
- Risk Level: Low | Medium | High | Critical
- Expected Testing Cost Curve: [shape and why]

---

## Requirement-Level Testability

| Requirement Key | Verifiability | Why / Why Not | Required Change |
| --------------- | -------------- | ------------- | --------------- |

Verifiability labels: `DIRECTLY TESTABLE` \| `CONDITIONALLY TESTABLE` \| `NON-TESTABLE` \| `UNDEFINED`

---

## Non-Functional Verifiability

| NFR | Measurable? | Observable? | Missing Instrumentation | Risk |
| --- | ----------- | ----------- | ----------------------- | ---- |

Explicitly address: Performance, Security, Reliability, Scalability, Observability, Resilience.

---

## Architectural Testability

Scores (each X/10 with one-line reasoning):
- Isolation Score
- Controllability Score
- Observability Score
- Determinism Score

Identify: missing dependency injection, concrete-bound abstractions, global state, entangled side-effects.

---

## Carried Clarifications
<!-- Only include if spec.md or the devils-advocate report contains [NEEDS CLARIFICATION] markers. -->

- [NEEDS CLARIFICATION: <question carried forward>]

---

## Risk Findings

| ID | Severity | Verifiability | Controllability | Isolation | Location | Problem | Required Change |
| -- | -------- | ------------- | ---------------- | --------- | -------- | ------- | --------------- |

Labels per `spek-fu/plugins/spec/knowledge/testability-taxonomy.md`. Cap at `maxFindings` (config); summarize overflow below the table.

---

## Testing Strategy Projection

- Recommended model: Pyramid | Trophy | Hybrid
- Required unit coverage depth
- Integration boundaries
- Contract testing necessity
- E2E test scope

---

## Cost of Doing Nothing
<!-- Address: future flakiness risk, refactor resistance, debugging difficulty, defect escape probability, maintenance burden. -->

[Assessment]

---

## Final Verdict

One of: `Test-Ready` | `Conditionally Testable` | `Structurally Fragile` | `Architecturally Hostile to Testing`

[One paragraph justification.]
