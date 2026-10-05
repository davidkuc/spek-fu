# TDD Design Taxonomy

Rules `spec-tdd-draft` applies to normalize raw behaviors into TDD units, find risk, and sequence work.

## A. Behavior classification

Assign each test one target: `domain` | `use-case` | `adapter` | `ui` | `integration` | `contract`. If ambiguous: `[NEEDS CLARIFICATION: classify this test]`.

## B. BDD normalization

```
Test ID: TDD-###
Name: Given_<context>_When_<action>_Then_<outcome>

Given: preconditions, dependencies, inputs
When: single trigger
Then: observable, measurable outcome
```

Vague outcome → `[NEEDS CLARIFICATION]`. Unverifiable assertion → `UNTESTABLE — <reason>`.

## C. Red-phase integrity

Per unit, assess: fails before implementation? For the right reason? Precise done-condition? Assign `Strong` or `Weak (<reason>)`.

## D. Risk and ambiguity passes

Run each independently against the full TDD unit set. Each unique issue appears once, tagged with its primary `Type`:

| Pass | Flags | `Type` |
|---|---|---|
| Ambiguity | Unmeasurable constraints ("fast", "secure"), missing edge cases, unspecified error types | `AMBIGUITY` |
| Dependency Smell | Deep object graphs, global/static state, infrastructure in domain-layer tests | `GLOBAL_STATE` / `STATIC_DEPENDENCY` |
| Coverage Gaps | Requirements, data-model entities, and contract endpoints with no mapped test | *(listed in Coverage Mapping, not Section 4)* |
| Interaction Over-Mocking | Mock explosion risk; where state-based verification is more stable | `MOCK_EXPLOSION` |
| Order Dependency | Sequence dependencies, shared state, isolation violations — always `CRITICAL` severity | `TEST_FRAGILITY` |

## E. Severity scale

| Severity | Meaning |
|---|---|
| CRITICAL | Prevents safe implementation |
| HIGH | Strong design weakness |
| MEDIUM | Structural improvement needed |
| LOW | Minor clarity issue |

## F. Implementation waves

Group TDD units into four independently-greenable waves, in order: Core Domain Logic, Use Case / Application Layer, Infrastructure Adapters, Integration and Non-Functional Guarantees.
