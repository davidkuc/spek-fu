<!--
metadata:
  spec_file: [path to spec.md]
  technical_plan: [path to technical-plan.md]
  design_date: [YYYY-MM-DD]
  test_count: [total TDD units in Section 2]
  design_status: ok | blocked
-->

# TDD Implementation Design Report: [FEATURE NAME]

**Spec**: `[path to spec.md]`
**Technical Plan**: `[path to technical-plan.md]`

---

## 1. Test Inventory Summary

- Total Tests Identified: [X]
- Domain Tests: [X]
- Use Case Tests: [X]
- Adapter Tests: [X]
- Integration Tests: [X]
- Non-Functional Tests: [X]

---

## 2. Formalized TDD Test Specifications

### TDD-001 – Given_..._When_..._Then_...

**Given**: ...
**When**: ...
**Then**: ...

**Classification**: Domain / Use Case / Adapter / UI / Integration / Contract
**Red-Phase Integrity**: Strong / Weak (reason)
**Risks**: [reference Section 5 IDs, or none]

---

## 3. Coverage Mapping

| Requirement / Entity / Endpoint | Covered By | Gaps |
|---|---|---|

---

## 4. Carried Clarifications
<!-- Only include if spec.md, technical-plan.md, or upstream artifacts contain [NEEDS CLARIFICATION] markers. -->

- [NEEDS CLARIFICATION: <question carried forward>]

---

## 5. Risks and Ambiguities

| ID | Severity | Type | Test ID | Description | Required Clarification |
|---|---|---|---|---|---|

Type: `AMBIGUITY` \| `GLOBAL_STATE` \| `STATIC_DEPENDENCY` \| `MOCK_EXPLOSION` \| `TEST_FRAGILITY`. Labels per `spek-fu/plugins/spec/knowledge/tdd-design-taxonomy.md`.

---

## 6. Incremental TDD Implementation Plan

### Wave 1 – Core Domain Logic
- TDD-001

### Wave 2 – Use Case / Application Layer
- TDD-002

### Wave 3 – Infrastructure Adapters
- TDD-003

### Wave 4 – Integration and Non-Functional Guarantees
- TDD-004

---

## 7. Final Verdict

Implementation Readiness:
- [ ] SAFE TO PROCEED
- [ ] PROCEED WITH CAUTION
- [ ] BLOCKED (critical gaps)

[One paragraph justification. Explicit blocking reasons, if any.]
