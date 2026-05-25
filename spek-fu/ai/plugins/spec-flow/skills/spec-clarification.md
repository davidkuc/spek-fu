---
id: "spec-clarification"
recommended-tier: "standard-agent"
version: 1.0
description: "Conducts a structured multi-pass ambiguity scan on a feature spec file and resolves critical gaps through a configurable interactive questioning loop, accumulating all answers in an in-memory Answer Buffer and writing them to the spec file after the question loop completes. USE FOR: reducing spec ambiguity before planning, detecting missing acceptance criteria, encoding clarifications into spec sections. DO NOT USE FOR: drafting new specs, producing implementation plans, or executing code changes."
anti-scope: "Does not create new spec files, produce implementation plans, or make code changes. For spec drafting use spec-feature-draft; for adversarial review use spec-devils-advocate."
tags:
  - "specification"
  - "clarification"
  - "requirements"
  - "quality"
inputs:
  - "spec-file: workspace-relative path to the spec.md file to clarify — resolved from feature branch if absent (optional)"
  - "config-path: workspace-relative path to the config file — defaults to spek-fu/ai/plugins/spec-flow/skills/config.json (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Updated spec file at the resolved `spec-file` path with all clarifications encoded through sequential approved edits"
  - "Short chat summary: 2–4 sentence plain-prose recap of what was clarified and any outstanding gaps"
  - "Completion report: passes completed, questions asked, sections touched, coverage summary table, suggested next command"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: spec-clarification

<!-- SECTION 1: Identity (primacy position) -->
Conducts a structured ambiguity scan on a feature specification file and resolves gaps through a configurable multi-pass interactive questioning loop. Answers accumulate in an **Answer Buffer** during the loop, then write to the spec file after completion. Multiple passes progressively narrow unresolved questions. Runtime parameters load from `spek-fu/ai/plugins/spec-flow/skills/config.json` under `spec-clarification` rather than inline inputs.

**Scope boundary**: Clarifies existing specs only. Does NOT draft new specs, produce plans, or make code changes.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER write to the spec file during the questioning loop — accumulate all answers in the **Answer Buffer** ONLY — WHY: writing mid-loop produces an incoherent partial spec that cannot be reviewed as a whole before the session ends.
2. NEVER write to the spec file without confirming the resolved `spec-file` path from Branch Detection or explicit `spec-file` input — confirm path FIRST — WHY: writing to the wrong path silently corrupts unrelated spec files.
3. NEVER ask more questions per pass than `maxQuestionsPerLoop`, and never exceed `totalQuestionBudget` across all passes — WHY: exceeding the configured budget wastes user attention and signals that the spec is too underspecified for clarification alone.
4. NEVER reveal future queued questions in advance — WHY: sequential questioning preserves unbiased, independent user responses.
5. ALWAYS insert `[NEEDS CLARIFICATION: <specific question>]` into the spec for any unresolved high-impact ambiguity that exceeds the question budget — WHY: downstream rework risk must remain visible even when the quota is exhausted.
6. When `questionMode` is `sequential`, present EXACTLY ONE question at a time before processing its answer — WHY: batching in sequential mode produces rushed, lower-quality responses.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/skill-meta-rules.md` before acting.
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/paginated-read.md` whenever reading config, specs, or knowledge files.
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/needs-clarification-protocol.md` whenever creating, carrying, or resolving `[NEEDS CLARIFICATION]` markers.

## Operational Anchors
- If `spec-file` is absent, apply **Branch Detection** before calling `vscode_askQuestions`.
- Detect run state: offer resume if **Answer Buffer** is populated; otherwise start fresh. Existing `## Clarifications` section does not decrement budget — each invocation gets full budget.
- During scans, treat **Answer Buffer** entries as incorporated into the spec to determine remaining gaps.

## Branch Detection

> See `spek-fu/ai/plugins/spec-flow/knowledge/branch-detection.md` — **`spec-file` resolution variant**.
> Apply it when `spec-file` is not supplied: resolve `feature-dir` per the core procedure, then set `spec-file = {feature-dir}/spec.md`.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `spec-file` and `config-path`. Apply default `spek-fu/ai/plugins/spec-flow/skills/config.json` if absent.
- Detect run state: if spec contains no gaps and no markers, report `ok — no ambiguities` and stop. Otherwise proceed.

## Done conditions

- **Clarification complete**: spec file written to disk with all answers from the **Answer Buffer**; completion report produced.
- **No ambiguities found**: all taxonomy categories are Clear after the first scan; completion report produced with suggestion to proceed to planning.
- **Blocked**: spec file path cannot be resolved; blocked with instruction to run spec creation skill or supply `spec-file` directly.
- **Early termination**: user signals stop during the loop; proceed to Step 5 with whatever is in the **Answer Buffer**.

## Step 1 — Load configuration

Read the config file at the resolved `config-path` using `read_file`. Extract the `spec-clarification` key and read the following fields, applying defaults for any absent values:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `maxQuestionsPerLoop` | `5` | Maximum questions to ask in a single pass |
| `maxLoops` | `10` | Maximum number of analysis-question passes |
| `questionMode` | `sequential` | Presentation mode: `sequential` or `batch` |
| `totalQuestionBudget` | `10` | Cumulative question ceiling across all passes |

Clamp `maxQuestionsPerLoop` to the range 1–10; reject values outside this range with a fail status.
Validate `questionMode` is one of `sequential` or `batch`. If invalid, default to `sequential` and warn.

> **If the config file cannot be read or the `spec-clarification` key is absent**: apply all defaults and proceed. Log a warning in the completion report.

## Step 2 — Resolve spec path

If `spec-file` is provided, use it directly.

If `spec-file` is absent, apply the **Branch Detection** procedure from `spek-fu/ai/plugins/spec-flow/knowledge/branch-detection.md` (**`spec-file` resolution variant**): resolve `feature-dir`, then set `spec-file = {feature-dir}/spec.md`.

> **If the user provides a path**: use it as `spec-file` and proceed.
> **If the user selects "Switch to a feature branch first" or declines**: stop, report `blocked`, and instruct the user to check out the feature branch and re-run.
> **If `git branch --show-current` fails or returns empty** (not on a feature branch, git unavailable, or detached HEAD): stop, report `blocked — branch detection returned no match; check out the feature branch first and re-run`.

## Step 3 — Load spec file

Apply `spek-fu/ai/plugins/spec-flow/knowledge/paginated-read.md` to load the spec file at the resolved `spec-file` path fully.

Treat any existing `## Clarifications` section as a historical record only — do NOT decrement `totalQuestionBudget` based on its bullet count. Each invocation receives the full `totalQuestionBudget` configured in `config.json`.

Initialize the **Answer Buffer**: start with an empty in-memory ordered list of `{ question, answer, category, target_section }` entries.

> **If the spec file cannot be read or does not exist**: stop, report `blocked`, and instruct the user to run **spec-feature-draft** to create it first.

## Step 4 — Multi-pass clarification loop

**Exit condition**: unresolved questions resolved, budget exhausted, max loops reached, or user signals stop.
**Max passes**: `maxLoops` (default 10).

### 4.1 — Ambiguity and coverage scan

Evaluate the spec against each taxonomy category, treating **Answer Buffer** entries as incorporated. For each, assign: **Clear**, **Partial**, or **Missing**.

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
| Documented Assumptions | Scan the `## Assumptions` section of the spec. For each `[ASSUMPTION: ...]` entry that has broader scope, design impact, or testability implications, promote it to a candidate question. Treat undocumented assumptions as **Missing** coverage. |

Build the **Coverage Map** internally. For each **Partial** or **Missing** category, add a question candidate unless clarification wouldn't materially impact implementation or is better deferred.

### 4.2 — Build prioritized question queue

Generate a prioritized queue capped at `min(maxQuestionsPerLoop, remaining budget)`. Apply constraints:

- Include only questions materially impacting: architecture, data modeling, task decomposition, test design, UX, operational readiness, compliance.
- Balance coverage: address highest-impact unresolved categories first.
- Exclude already-answered questions in **Answer Buffer** or `## Clarifications`.
- Apply (Impact × Uncertainty) heuristic if more categories remain than budget allows.

If the queue is empty: exit the loop and proceed to Step 5.

### 4.3 — Questioning round

Behavior depends on `questionMode`:

**Sequential**: Present EXACTLY ONE question per `vscode_askQuestions` call. After receiving each answer:
1. Analyze available options. Determine the **recommended option** based on best practices, risk reduction, and alignment with explicit spec goals.
2. Include the "Recommended" option with brief reasoning. If the user replies `yes`, `recommended`, or `suggested`, use the stated recommendation.
3. Add the accepted `{ question, answer, category, target_section }` entry to the **Answer Buffer**.
4. Advance to the next question in the pass queue.

> **If `vscode_askQuestions` returns without answer** (dismissed or cancelled): treat as early termination — proceed to Step 5 with current **Answer Buffer**.

**Batch**: Present all pass-queue questions in a single `vscode_askQuestions` call. After receiving all answers, add each `{ question, answer, category, target_section }` entry to the **Answer Buffer** in order.

Stop the round when:
- All pass questions answered, OR
- User replies `done`/`stop`/`good`/`no more`, OR
- Pass budget exhausted.

### 4.4 — Loop control

After questioning:
- Deduct questions asked from remaining budget.
- If user signalled stop → exit, proceed to Step 5.
- If budget now zero → exit, proceed to Step 5.
- If last pass → exit, proceed to Step 5.
- Otherwise → next pass (return to 4.1).

## Step 5 — Write to disk

Present a numbered summary table of all entries in the **Answer Buffer** in a single chat message:

```
| # | Category | Question | Accepted Answer | Target Section |
|---|----------|----------|-----------------|----------------|
| 1 | ...      | ...      | ...             | ...            |
```

> **If the Answer Buffer is empty**: skip to Step 6 and report no ambiguities found.

Apply all **Answer Buffer** entries to the spec using `replace_string_in_file`, one change at a time:

For each entry in order:

1. **Clarifications section**: ensure `## Clarifications` exists after the overview. Create `### Session YYYY-MM-DD` subheading if absent. Append: `- Q: <question> → A: <accepted answer>`.

2. **Section-specific update** — apply the answer to the appropriate section:
   - Functional ambiguity → update Functional Requirements.
   - User interaction → update User Stories or Actors.
   - Data shape → update Data Model.
   - Non-functional constraint → add to Quality Attributes (convert vague terms to metrics).
   - Edge case → add to Edge Cases / Error Handling.
   - Terminology → normalize across spec.

3. Replace earlier ambiguous statements rather than duplicating. Leave no contradictions.

For any unresolved high-impact categories that exceeded the question budget, apply `spek-fu/ai/plugins/spec-flow/knowledge/needs-clarification-protocol.md` and insert `[NEEDS CLARIFICATION: <specific question>]` into the spec at the point of uncertainty before completing the write.

After all entries are applied, confirm the sequential edits fully reflect the accepted answers in `spec-file`.

> **If any `replace_string_in_file` call fails** during the batch write (string not found, permission error, or disk error): stop immediately, report `fail — write to <spec-file> failed at entry N: <error>`, list which entries were successfully applied and which were not, and do not report completion.

## Step 6 — Final validation

Validate the spec:
- `## Clarifications` contains one bullet per answer (no duplicates).
- Questions asked ≤ `totalQuestionBudget`.
- No unresolved vague placeholders remain.
- No contradictions survive.
- Valid Markdown; only new headings: `## Clarifications`, `### Session YYYY-MM-DD`.
- Terminology consistent.

## Step 7 — Report completion

Produce the completion report as defined in `<output_format>`.

The skill is complete when the spec file is written to disk, the short chat summary is shown, and the completion report is shown to the user.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **vscode_askQuestions**: User input — one Q at a time (sequential) or all at once (batch).
- **read_file**: Config, spec, and devcontainer guidelines. Apply paginated-read for multi-read files.
- **replace_string_in_file**: Apply **Answer Buffer** updates to spec in Step 5 only.
- **run_in_terminal**: Branch Detection in Step 2 when `spec-file` is absent.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Short Chat Summary** (output immediately before the Completion Report, in plain prose, 2–4 sentences):

> Clarified `{spec-file}` over N pass(es), resolving N question(s) across [category list]. [One sentence on the most significant change made.] [One sentence on any outstanding gaps or suggested next step.]

**Completion Report**:

```
## Clarification Session Complete

Passes completed:   N / maxLoops
Questions asked:    N / totalQuestionBudget
Questions answered: N
Sections touched:   [list of section names]

### Coverage Summary

| Category | Status |
|----------|--------|
| Functional Scope & Behavior         | Resolved / Deferred / Clear / Outstanding |
| Domain & Data Model                 | Resolved / Deferred / Clear / Outstanding |
| Interaction & UX Flow               | Resolved / Deferred / Clear / Outstanding |
| Non-Functional Quality Attributes   | Resolved / Deferred / Clear / Outstanding |
| Integration & External Dependencies | Resolved / Deferred / Clear / Outstanding |
| Edge Cases & Failure Handling       | Resolved / Deferred / Clear / Outstanding |
| Constraints & Tradeoffs             | Resolved / Deferred / Clear / Outstanding |
| Completion Signals                  | Resolved / Deferred / Clear / Outstanding |
| Misc / Placeholders                 | Resolved / Deferred / Clear / Outstanding |
| Documented Assumptions              | Resolved / Deferred / Clear / Outstanding |

### Deferred / Outstanding Items
[List any categories with Deferred or Outstanding status and rationale]

### Suggested Next Command
[Recommend proceeding to planning, running clarification again, or noting risk]
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: Run spec clarification on current branch spec, default config.
Expected behavior: Reads config (max 5 q/loop, 10 loops, sequential, budget 10). Detects `spec-file` via Branch Detection. Pass 1: finds Partial on Non-Functional, Missing on Edge Cases; asks 2 questions. Pass 2: 1 remaining question on Completion Signals. User approves all 3 answers. Reports 2 passes, 3/10 questions, 3 sections touched.
</example>

<example>
Input: spec-file=spek-fu/features/003-payment-gateway/spec.md, batch mode, 4 q/loop, 2 loops.
Expected behavior: Pass 1 finds 4 Partial/Missing categories; presents all 4 in batch. Pass 2 re-analyzes — all Clear. Exits, writes answers. Reports 2 passes, 4/10 questions.
</example>

<example type="counter">
Input: Clarify the spec and write each answer immediately as it is accepted.
Expected behavior: Skill proceeds with the multi-pass questioning loop, accumulates answers in the in-memory Answer Buffer only — no writes occur during the loop — then presents a summary table and writes all answers to the spec in one batch at Step 5.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
- Constraint 1 — keep writes out of the questioning loop; use the **Answer Buffer** only.
- Constraint 2 — confirm the resolved `spec-file` before writing.
- Constraint 3 — stay within `maxQuestionsPerLoop` and `totalQuestionBudget`.
- Constraint 5 — insert explicit markers for high-impact ambiguities that exceed the question budget.
- Constraint 6 — honor sequential mode by asking exactly one question at a time.
</reminders>
