---
name: project-clarification
description: "Scan the project docs for ambiguity across a fixed taxonomy and resolve critical gaps through a budgeted, multi-pass interactive question loop."
---

# Project Clarification

Runs a structured ambiguity scan on the project docs and resolves gaps through a configurable multi-pass question loop. Answers accumulate in an in-memory **Answer Buffer** during the loop and are written to the target docs only after the loop ends.

Taxonomy: `spek-fu/plugins/project/knowledge/project-ambiguity-taxonomy.md`
Config: `spek-fu/plugins/project/knowledge/config.json`

## When to use

Run manually, optionally after `project-research` and/or `project-devils-advocate`, when the project docs need ambiguity reduced. Does not mint or renumber feature IDs (`project-functional-docs` owns those), sync shipped features, or change code. Part of the audit track in `project-workflow.md`.

<inputs>

## Inputs

- `target` (optional; a doc path or area name; defaults to the whole doc set)
- `spek-fu/plugins/project/knowledge/config.json` (`project-clarification.*`, `paths.reportsRoot`)
- `project-research-report.md` / `project-devils-advocate-report.md` under `spek-fu/project/reports/`, if present

</inputs>

<outputs>

## Outputs

- Resolved target doc(s) updated in place: targeted edits plus a `## Clarifications` section per touched doc; no writes until the loop ends
- Completion report: passes run, questions asked/answered, docs touched, coverage summary

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never write to any doc during the question loop — accumulate every answer in the in-memory **Answer Buffer** only; write once, after the loop ends.
- Never write before the resolved target path(s) are confirmed (Step 2).
- Write only to docs in the resolved target set; never create, rename, or renumber feature IDs, and never edit `code-docs/`, `contracts/`, or `spec-features/`.
- Never ask more than `maxQuestionsPerLoop` questions in one pass, or exceed the total budget (`maxQuestionsPerLoop` * `maxLoops`).
- Never reveal queued questions in advance; in `sequential` mode ask exactly one question per `AskUserQuestion` call.
- Match the surrounding doc's language in inline edits; write the `## Clarifications` section in English.
- Insert `[NEEDS CLARIFICATION: <question>]` at the point of uncertainty for any unresolved high-impact ambiguity that exceeds the budget.
- An existing `## Clarifications` section never decrements the budget — each invocation gets the full budget.

</constraints>

<behavioral_anchors>

## Pillars

**Terseness** — every question, answer, and summary uses the fewest sentences that preserve meaning, per constitution `## AI Principles`.

**Answer-Buffer-First** — the loop only ever mutates memory; disk changes happen in a single pass at the end so the docs are never left half-clarified.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read config

Read `spek-fu/plugins/project/knowledge/config.json`. Extract `project-clarification.maxQuestionsPerLoop` (default `5`, clamp 1–10), `maxLoops` (default `10`), `questionMode` (default `sequential`; `sequential` or `batch`). Missing file/key: apply defaults, note the warning in the completion report. Compute `totalQuestionBudget` = `maxQuestionsPerLoop` * `maxLoops`.

### 2. Resolve target

Use `target` if given, otherwise the whole doc set (`project.md`, `technical.md`, `roadmap.md`, `project-docs/*.md`, `user-flows/*.md`). Confirm each file exists.

> If `project.md` or the `target` is missing: stop, report `blocked`.
> If a file exists but can't be read: stop, report `fail`.

### 3. Load docs and supplementary reports

Read the in-scope docs in full. Initialize an empty **Answer Buffer**: `{ question, answer, category, target_doc, target_section }[]`. Load any research and devils-advocate reports found under `spek-fu/project/reports/` and hold their open questions and findings as prioritization input for Step 4.

> If the docs have no gaps or markers on inspection: report `ok — no ambiguities`, stop.

### 4. Multi-pass clarification loop

Repeat for up to `maxLoops` passes, or until the queue is empty, the budget is exhausted, or the user signals stop (`done`/`stop`/`good`/`no more`):

1. **Scan**: evaluate the docs (treating **Answer Buffer** entries as already incorporated) against `spek-fu/plugins/project/knowledge/project-ambiguity-taxonomy.md`.
2. **Queue**: build a prioritized list of candidate questions, capped at `min(maxQuestionsPerLoop, remaining budget)`, excluding anything already in the **Answer Buffer** or an existing `## Clarifications` section. If empty, exit the loop.
3. **Ask**: `sequential` — one question per `AskUserQuestion` call, each with a recommended option and brief reasoning; `yes`/`recommended`/`suggested` accepts the recommendation. `batch` — one call carrying the full pass queue.
4. **Record**: append each accepted answer to the **Answer Buffer**.
5. **Deduct**: subtract questions asked from the remaining budget.

> If `AskUserQuestion` returns without an answer (dismissed): treat as early termination, proceed to Step 5 with the current **Answer Buffer**.

### 5. Write to docs

Show the user a numbered summary table (`# | Category | Question | Accepted Answer | Target Doc/Section`) of the **Answer Buffer**.

> If the buffer is empty: skip the write, proceed to Step 6.

Apply each entry, in order:

- Ensure the target doc has a `## Clarifications` section (last section, after any `## Related User Flows`); create `### Session YYYY-MM-DD` if absent; append `- Q: <question> → A: <accepted answer>`.
- Apply the answer to its target section, replacing the ambiguous statement rather than duplicating it.

For any high-impact category still unresolved past the budget, insert `[NEEDS CLARIFICATION: <specific question>]` at the point of uncertainty.

> If any edit fails: stop immediately, report `fail — write to <doc> failed at entry N: <error>`, list applied vs. unapplied entries.

### 6. Validate and report

Confirm: one `## Clarifications` bullet per answer, no duplicates; questions asked ≤ `totalQuestionBudget`; no unresolved vague placeholders remain unmarked; no contradictions with other docs; feature IDs untouched; only new headings are `## Clarifications` / `### Session YYYY-MM-DD`.

Report: passes run / `maxLoops`, questions asked / `totalQuestionBudget`, questions answered, docs touched, and a coverage table (one row per taxonomy category: Resolved / Deferred / Clear / Outstanding) with a suggested next step.

</workflow>

<done_conditions>

## Done Conditions

- Target docs written with all **Answer Buffer** entries applied, or left untouched if no ambiguities were found.
- No write occurred before the loop ended; no feature ID changed.
- Questions asked never exceeded `maxQuestionsPerLoop` per pass or `totalQuestionBudget` overall.
- Unresolved high-impact ambiguities beyond budget carry a `[NEEDS CLARIFICATION: ...]` marker.
- Completion report given: passes, questions asked/answered, docs touched, coverage summary.

</done_conditions>
