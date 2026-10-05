# Testability Taxonomy

Six analytical models used by `spec-testability-draft` to grade a spec's testability. Applied internally; only the resulting labels and findings are written to the report.

## A. Verifiability

Per requirement: Can behavior be observed? Outcome asserted? Success/failure measurable? Deterministic trigger?

Labels: `DIRECTLY TESTABLE` | `CONDITIONALLY TESTABLE` | `NON-TESTABLE` | `UNDEFINED`

## B. Controllability

Per dependency: Can it be replaced? Side effects injectable? State resettable? Time controlled? Failures simulated?

Labels: `HIGH CONTROL` | `MEDIUM CONTROL` | `LOW CONTROL` | `ZERO CONTROL`

## C. Isolation

Per risk: Unit isolation supported? Mock boundaries present? Ports/adapters used? Pure domain core? Deterministic execution?

Labels: `HIGH ISOLATION` | `MEDIUM ISOLATION` | `LOW ISOLATION` | `ZERO ISOLATION`

## D. Testing Strategy Geometry

Determine test shape (Pyramid / Trophy / Honeycomb / Ice Cream Cone), expected unit/integration/E2E ratio, and cost-of-failure detection timing.

## E. Risk Inversion Pass

Per module/component: How does it fail? Where does flakiness originate? Over-mocking risk? Where does 80% of defects concentrate? What's impossible to stress/load test?

## F. Anti-Pattern Detection

- **Technical**: flaky test risk, hard-coded test data, over-mocking, happy-path bias, Inspector, Secret Catcher, Loudmouth.
- **Architectural**: God object, spaghetti coupling, local hero environment.
- **Cultural**: automation overload, one-and-done, security theatre.

## Severity scale (Risk Findings)

`CRITICAL` (not testable) | `HIGH` (brittle/flaky risk) | `MEDIUM` (expensive) | `LOW` (improvement opportunity)
