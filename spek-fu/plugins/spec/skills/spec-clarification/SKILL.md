---
name: spec-clarification
description: "Scan a feature spec for ambiguity across a fixed taxonomy and resolve critical gaps through a budgeted, multi-pass interactive question loop."
---

# Spec Clarification

Runs a structured ambiguity scan on a feature spec and resolves gaps through a configurable multi-pass question loop. Answers accumulate in an in-memory **Answer Buffer** during the loop and are written to `spec-file` only after the loop ends.

Taxonomy: `spek-fu/plugins/spec/knowledge/ambiguity-taxonomy.md`
Config: `spek-fu/plugins/spec/knowledge/config.json`

## When to use

Optional step in the Define phase, after `spec-feature-draft` (and optionally `spec-research` / `spec-devils-advocate`), when a spec needs ambiguity reduced before planning. Does not draft new specs, produce plans, or make code changes.

<inputs>

## Inputs

- `spec-file` (optional; branch-detected if absent)
- `spek-fu/plugins/spec/knowledge/config.json` (`spec-clarification.*`)
- `spec-research-report.md` / `devils-advocate-report.md`, if present next to `spec-file`

</inputs>

<outputs>

## Outputs

- `spec-file` updated in place: `## Clarifications` section plus targeted section edits, no writes until the loop ends
- Completion report: passes run, questions asked/answered, sections touched, coverage summary

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never write to `spec-file` during the question loop — accumulate every answer in the in-memory **Answer Buffer** only; write once, after the loop ends.
- Never write before the resolved `spec-file` path is confirmed (Step 2).
- Never ask more than `maxQuestionsPerLoop` questions in one pass, or exceed the total question budget (`maxQuestionsPerLoop` * `maxLoops`) across all passes.
- Never reveal queued questions in advance; in `sequential` mode ask exactly one question per `AskUserQuestion` call.
- Insert `[NEEDS CLARIFICATION: <question>]` at the point of uncertainty for any unresolved high-impact ambiguity that exceeds the budget.
- An existing `## Clarifications` section never decrements the total question budget — each invocation gets the full budget.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every question, answer, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Answer-Buffer-First** — the loop only ever mutates memory; disk changes happen in a single pass at the end so the spec is never left half-clarified.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/spec/knowledge/config.json`. Extract `spec-clarification.maxQuestionsPerLoop` (default `5`, clamp 1–10), `maxLoops` (default `10`), `questionMode` (default `sequential`, must be `sequential` or `batch`). Missing file/key: apply defaults, note the warning in the completion report. Compute `totalQuestionBudget` = `maxQuestionsPerLoop` * `maxLoops`.

### 2. Resolve spec file

If `spec-file` is provided, use it. Otherwise run `git branch --show-current` and resolve `spek-fu/project/spec-features/<branch-name>/spec.md`.

> If no match or the file doesn't exist: stop, report `blocked`, instruct the user to run `spec-feature-draft` first or supply `spec-file` directly.
> If the file exists but can't be read: stop, report `fail`.

### 3. Load spec and supplementary artifacts

Read `spec-file` in full. Initialize an empty **Answer Buffer**: `{ question, answer, category, target_section }[]`. Check `spec-file`'s directory for `spec-research-report.md` and `devils-advocate-report.md`; load any that exist and hold their open questions / findings as prioritization input for Step 4.

> If the spec has no gaps or markers on inspection: report `ok — no ambiguities`, stop.

### 4. Multi-pass clarification loop

Repeat for up to `maxLoops` passes, or until the queue is empty, the budget is exhausted, or the user signals stop (`done`/`stop`/`good`/`no more`):

1. **Scan**: evaluate the spec (treating **Answer Buffer** entries as already incorporated) against `spek-fu/plugins/spec/knowledge/ambiguity-taxonomy.md`.
2. **Queue**: build a prioritized list of candidate questions, capped at `min(maxQuestionsPerLoop, remaining budget)`, excluding anything already in the **Answer Buffer** or an existing `## Clarifications` section. If empty, exit the loop.
3. **Ask**: `questionMode: sequential` — one `AskUserQuestion` call per question, each with a recommended option and brief reasoning; a reply of `yes`/`recommended`/`suggested` accepts the recommendation. `questionMode: batch` — one `AskUserQuestion` call carrying the full pass queue.
4. **Record**: append each accepted answer to the **Answer Buffer** as `{ question, answer, category, target_section }`.
5. **Deduct**: subtract questions asked from the remaining budget.

> If `AskUserQuestion` returns without an answer (dismissed): treat as early termination, proceed to Step 5 with the current **Answer Buffer**.

### 5. Write to spec

Show the user a numbered summary table (`# | Category | Question | Accepted Answer | Target Section`) of the **Answer Buffer**.

> If the buffer is empty: skip the write, proceed to Step 6 and report no ambiguities found.

Apply each entry to `spec-file`, in order:

- Ensure `## Clarifications` exists after the overview; create `### Session YYYY-MM-DD` if absent; append `- Q: <question> → A: <accepted answer>`.
- Apply the answer to its target section (Functional Requirements, User Stories/Actors, Data Model, Quality Attributes, Edge Cases/Error Handling, or normalize terminology), replacing the ambiguous statement rather than duplicating it.

For any high-impact category still unresolved past the budget, insert `[NEEDS CLARIFICATION: <specific question>]` at the point of uncertainty.

> If any edit fails (string not found, permission/disk error): stop immediately, report `fail — write to <spec-file> failed at entry N: <error>`, list applied vs. unapplied entries.

### 6. Validate and report

Confirm: one `## Clarifications` bullet per answer, no duplicates; questions asked ≤ `totalQuestionBudget`; no unresolved vague placeholders remain unmarked; no contradictions; only new headings are `## Clarifications` / `### Session YYYY-MM-DD`.

Report: passes run / `maxLoops`, questions asked / `totalQuestionBudget`, questions answered, sections touched, and a coverage table (one row per taxonomy category: Resolved / Deferred / Clear / Outstanding) with a suggested next command.

</workflow>

<done_conditions>

## Done Conditions

- `spec-file` written with all **Answer Buffer** entries applied, or left untouched if no ambiguities were found.
- No write occurred before the loop ended.
- Questions asked never exceeded `maxQuestionsPerLoop` per pass or `totalQuestionBudget` overall.
- Unresolved high-impact ambiguities beyond budget carry a `[NEEDS CLARIFICATION: ...]` marker.
- Completion report given: passes, questions asked/answered, sections touched, coverage summary.

</done_conditions>
