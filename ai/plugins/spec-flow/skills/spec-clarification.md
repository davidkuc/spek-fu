---
id: "spec-clarification"
recommended-tier: "standard-agent"
version: 1.0
description: "Conducts a structured multi-pass ambiguity scan on a feature spec file and resolves critical gaps through a configurable interactive questioning loop, accumulating all answers and writing to disk only after explicit user approval. USE FOR: reducing spec ambiguity before planning, detecting missing acceptance criteria, encoding clarifications into spec sections. DO NOT USE FOR: drafting new specs, producing implementation plans, or executing code changes."
anti-scope: "Does not create new spec files, produce implementation plans, or make code changes. For spec drafting use spec-feature-draft; for adversarial review use spec-devils-advocate."
tags:
  - "specification"
  - "clarification"
  - "requirements"
  - "quality"
inputs:
  - "spec_path: workspace-relative path to the spec.md file to clarify — resolved from feature branch if absent (optional)"
  - "config_path: workspace-relative path to the config file — defaults to ai/plugins/spec-flow/skills/config.json (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Updated spec file at the resolved FEATURE_SPEC path with all clarifications encoded in a single batch write"
  - "Completion report: passes completed, questions asked, sections touched, coverage summary table, suggested next command"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: spec-clarification

<!-- SECTION 1: Identity (primacy position) -->
Conducts a structured ambiguity and coverage scan on a feature specification file, identifies critical gaps across a taxonomy of nine specification categories, and resolves them through a configurable multi-pass interactive questioning loop. All accepted answers are accumulated in an **Answer Buffer** during the loop; nothing is written to disk until the user explicitly approves the complete set at the approval gate. Multiple passes allow each round of accepted answers to inform the next ambiguity scan, progressively narrowing the set of unresolved questions. Runtime parameters (questions per loop, number of loops, presentation mode, total budget) are loaded from `ai/plugins/spec-flow/skills/config.json` under the `spec-clarification` key rather than supplied as inline inputs.

**Scope boundary**: This skill clarifies an existing feature spec only. It does NOT draft new spec files, produce implementation plans, or make code changes.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER write to the spec file during the questioning loop — accumulate all answers in the **Answer Buffer** ONLY — WHY: deferred writes keep the approval gate meaningful; a partially written spec cannot be coherently reviewed before the user has seen all answers together.
2. NEVER write to the spec file without explicit user approval at the Step 5 approval gate — ONLY write after the gate returns "Approve all" — WHY: unapproved writes silently alter the spec and are difficult to reverse.
3. NEVER write to the spec file without confirming FEATURE_SPEC path from script output or explicit `spec_path` input — confirm path FIRST — WHY: writing to the wrong path silently corrupts unrelated spec files.
4. NEVER ask more questions per pass than `maxQuestionsPerLoop`, and never exceed `totalQuestionBudget` across all passes — WHY: exceeding the configured budget wastes user attention and signals that the spec is too underspecified for clarification alone.
5. NEVER reveal future queued questions in advance — WHY: sequential questioning preserves unbiased, independent user responses.
6. ALWAYS insert `[NEEDS CLARIFICATION: <specific question>]` into the spec for any unresolved high-impact ambiguity that exceeds the question budget — WHY: downstream rework risk must remain visible even when the quota is exhausted.
7. When `questionMode` is `sequential`, present EXACTLY ONE question at a time before processing its answer — WHY: batching in sequential mode produces rushed, lower-quality responses.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- If `spec_path` is absent, apply the **Branch Detection** procedure before calling `vscode_askQuestions`.
- Detect run state before acting: if an **Answer Buffer** is already populated in context, offer to resume; otherwise start fresh. If a `## Clarifications` section already exists in the spec, count its existing bullets against `totalQuestionBudget` before starting the loop.
- During each pass's scan, treat all entries in the **Answer Buffer** as if they were already incorporated into the spec — this determines which gaps remain open.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **`spec_path` resolution variant**.
> Apply it when `spec_path` is not supplied: resolve `FEATURE_DIR` per the core procedure, then set `spec_path = FEATURE_DIR/spec.md`.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `spec_path` and `config_path` from inputs. Apply default config path `ai/plugins/spec-flow/skills/config.json` if `config_path` is absent.
- Confirm run state: fresh start or resume from populated **Answer Buffer** in context.

## Done conditions

- **Clarification complete**: spec file written to disk with all approved answers; completion report produced.
- **No ambiguities found**: all taxonomy categories are Clear after the first scan; completion report produced with suggestion to proceed to planning.
- **Blocked**: spec file path cannot be resolved; blocked with instruction to run spec creation skill or supply `spec_path` directly.
- **Cancelled at approval**: user declines at the approval gate; completion report produced with `output_path: null`; spec file unchanged.
- **Early termination**: user signals stop during the loop; proceed to Step 5 with whatever is in the **Answer Buffer**.

## Step 1 — Load configuration

Read the config file at the resolved `config_path` using `read_file`. Extract the `spec-clarification` key and read the following fields, applying defaults for any absent values:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `maxQuestionsPerLoop` | `5` | Maximum questions to ask in a single pass |
| `maxLoops` | `3` | Maximum number of analysis-question passes |
| `questionMode` | `sequential` | Presentation mode: `sequential` or `batch` |
| `totalQuestionBudget` | `10` | Cumulative question ceiling across all passes |

Clamp `maxQuestionsPerLoop` to the range 1–10; reject values outside this range with a fail status.
Validate `questionMode` is one of `sequential` or `batch`. If invalid, default to `sequential` and warn.

> **If the config file cannot be read or the `spec-clarification` key is absent**: apply all defaults and proceed. Log a warning in the completion report.

## Step 2 — Resolve spec path

If `spec_path` is provided, use it directly.

If `spec_path` is absent, apply the **Branch Detection** procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md` (**`spec_path` resolution variant**): resolve `FEATURE_DIR`, then set `spec_path = FEATURE_DIR/spec.md`.

> **If the user provides a path**: use it as `spec_path` and proceed.
> **If the user selects "Switch to a feature branch first" or declines**: stop, report `blocked`, and instruct the user to check out the feature branch and re-run.

## Step 3 — Load spec file

Read the spec file at the resolved path using multi-pass `read_file` calls until the response is shorter than the page size.

Count any existing `## Clarifications` section bullets and subtract that count from `totalQuestionBudget`.

Initialize the **Answer Buffer**: an empty ordered list of `{ question, answer, category, target_section }` entries.

> **If the spec file cannot be read or does not exist**: stop, report `blocked`, and instruct the user to run **spec-feature-draft** to create it first.

## Step 4 — Multi-pass clarification loop

**Exit condition**: no unresolved questions remain, `totalQuestionBudget` exhausted, `maxLoops` reached, or user signals stop.
**Max passes**: `maxLoops` (from config, default 3).

### 4.1 — Ambiguity and coverage scan

Evaluate the spec against each taxonomy category below, treating all entries in the **Answer Buffer** as if they were already incorporated. For each category, assign: **Clear**, **Partial**, or **Missing**.

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

Build or update the internal **Coverage Map** (do not output it unless no questions will be generated). For each **Partial** or **Missing** category, add a candidate question opportunity unless the clarification would not materially change implementation or validation strategy, or is better deferred to planning.

### 4.2 — Build prioritized question queue

Internally generate a prioritized queue of candidate questions for this pass, capped at `min(maxQuestionsPerLoop, remaining totalQuestionBudget)`. Apply these constraints:

- Include only questions whose answers materially impact: architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation.
- Ensure category coverage balance: address the highest-impact unresolved categories first.
- Exclude questions already answered in the **Answer Buffer** or in the existing `## Clarifications` section.
- If more categories remain unresolved than the pass budget allows, select by (Impact × Uncertainty) heuristic.
- Do NOT output the full question queue in advance.

If the queue is empty: exit the loop and proceed to Step 5.

### 4.3 — Questioning round

Behavior depends on `questionMode`:

**Sequential**: Present EXACTLY ONE question per `vscode_askQuestions` call. After receiving each answer:
1. Analyze available options. Determine the **recommended option** based on best practices, risk reduction, and alignment with explicit spec goals.
2. Include the "Recommended" option with brief reasoning. If the user replies `yes`, `recommended`, or `suggested`, use the stated recommendation.
3. Add the accepted `{ question, answer, category, target_section }` entry to the **Answer Buffer**.
4. Advance to the next question in the pass queue.

**Batch**: Present all pass-queue questions in a single `vscode_askQuestions` call. After receiving all answers, add each `{ question, answer, category, target_section }` entry to the **Answer Buffer** in order.

Stop the round when:
- All pass questions are answered, OR
- User replies `done`, `stop`, `good`, or `no more`, OR
- Pass question budget exhausted.

### 4.4 — Loop control

After the questioning round:
- Deduct the number of questions asked this pass from the remaining `totalQuestionBudget`.
- If the user signalled stop → exit loop, proceed to Step 5.
- If `totalQuestionBudget` is now zero → exit loop, proceed to Step 5.
- If this was the last allowed pass (`maxLoops`) → exit loop, proceed to Step 5.
- Otherwise → continue to the next pass (return to 4.1 with the updated **Answer Buffer**).

## Step 5 — Approval gate

⛔ **STOP — User approval required before writing to disk.**

Present a numbered summary table of all entries in the **Answer Buffer**:

```
| # | Category | Question | Accepted Answer | Target Section |
|---|----------|----------|-----------------|----------------|
| 1 | ...      | ...      | ...             | ...            |
```

Call `vscode_askQuestions` with the `approval_gate` payload (see Question Payloads below).

- If **"Approve all — write to disk"**: proceed to Step 6.
- If **"Revise an answer"**: ask which item number to revise, collect the replacement answer, update the **Answer Buffer** entry, re-present the table, and repeat this step.
- If **"Cancel — discard"**: produce the completion report with `output_path: null` and stop without writing.

> **If the Answer Buffer is empty**: skip to Step 7 and report no ambiguities found.

## Step 6 — Batch write to disk

Apply all **Answer Buffer** entries to the spec in a single edit sequence using `replace_string_in_file`:

For each entry in order:

1. **Clarifications section**: ensure a `## Clarifications` section exists just after the highest-level overview section. Under it, create (if absent) a `### Session YYYY-MM-DD` subheading for today's date. Append: `- Q: <question> → A: <accepted answer>`.

2. **Section-specific update** — apply the answer to the most appropriate section:
   - Functional ambiguity → update or add a bullet in Functional Requirements.
   - User interaction / actor distinction → update User Stories or Actors subsection with clarified role, constraint, or scenario.
   - Data shape / entities → update Data Model; add fields, types, relationships; note added constraints succinctly.
   - Non-functional constraint → add or modify a measurable criterion in Non-Functional / Quality Attributes; convert vague adjective to metric or explicit target.
   - Edge case / negative flow → add a bullet under Edge Cases / Error Handling; create the subsection if absent.
   - Terminology conflict → normalize the term across the spec; retain the original with `(formerly referred to as "X")` once if needed.

3. If any entry's clarification invalidates an earlier ambiguous statement, replace that statement rather than duplicating it. Leave no contradictory text.

For any unresolved high-impact categories that exceeded the question budget, insert `[NEEDS CLARIFICATION: <specific question>]` into the spec at the point of uncertainty before completing the write.

After all entries are applied, write the fully updated spec to disk (atomic overwrite of FEATURE_SPEC).

> **If the write fails**: report the error and stop. Do not report completion without confirming disk state.

## Step 7 — Final validation

After the write, validate the spec:

- `## Clarifications` section contains exactly one bullet per accepted answer (no duplicates).
- Total questions asked across all passes ≤ `totalQuestionBudget`.
- No unresolved vague placeholders remain for the categories addressed.
- No contradictory earlier statement survives.
- Markdown structure valid; only allowed new headings are `## Clarifications` and `### Session YYYY-MM-DD`.
- Terminology consistent across all updated sections.

## Step 8 — Report completion

Produce the completion report as defined in `<output_format>`.

The skill is complete when the spec file is written to disk and the completion report is shown to the user, or when the user has cancelled at the approval gate (spec unchanged, report produced).

## Question Payloads

### `approval_gate`

```json
{
  "header": "approval_gate",
  "question": "Review all collected answers in the table above. How would you like to proceed?",
  "options": [
    { "label": "Approve all — write to disk", "recommended": true, "description": "Write all accepted answers to the spec in one batch pass" },
    { "label": "Revise an answer", "description": "Update one or more answers before writing" },
    { "label": "Cancel — discard", "description": "Discard all collected answers; spec file unchanged" }
  ],
  "allowFreeformInput": false
}
```

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **vscode_askQuestions**: All user input — one question at a time in sequential mode, all pass questions in one call in batch mode, and the approval gate at Step 5. Required; do not prompt via plain text.
- **read_file**: Load the config file (Step 1, single read sufficient), load the spec file (Step 3, multi-pass until end of file confirmed), load `ai/plugins/skf/knowledge/devcontainer-guidelines.md` in devcontainer environments.
- **replace_string_in_file**: Apply all **Answer Buffer** updates to FEATURE_SPEC in Step 6 only, after the approval gate.
- **run_in_terminal**: Run the prerequisites check script in Step 2 — only when `spec_path` is absent.
- Do NOT use tools not listed here unless the skill explicitly escalates.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Standard Field Table**:

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `spec-clarification` |
| wave | `N` |
| step | `N.M` |
| output_path | path to updated spec file or `null` |
| summary | one-line summary of what was done |

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

### Deferred / Outstanding Items
[List any categories with Deferred or Outstanding status and rationale]

### Suggested Next Command
[Recommend proceeding to planning, running clarification again, or noting risk]
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: Run spec clarification on the current feature branch spec, default config.
Expected behavior: Reads config from `ai/plugins/spec-flow/skills/config.json` under the `spec-clarification` key (max 5 questions/loop, 3 loops, sequential, budget 10). Runs prerequisites script to locate FEATURE_SPEC. Loads spec. Pass 1: scans — finds Partial on Non-Functional and Missing on Edge Cases. Asks 2 questions sequentially, adds both to Answer Buffer. Pass 2: re-analyzes treating buffer answers as already applied — 1 remaining question on Completion Signals. Asks it, adds to buffer. Pass 3: re-analyzes — all categories Clear. Queue empty, exits loop. Presents 3-row approval table. User selects "Approve all". Writes all 3 answers to spec in one batch pass. Reports 2 passes completed, 3/10 questions asked, 3 sections touched.
</example>

<example>
Input: spec_path=specs/3-payment-gateway/spec.md, config has questionMode=batch, maxQuestionsPerLoop=4, maxLoops=2.
Expected behavior: Reads config, loads spec directly from supplied path. Pass 1: scans — finds 4 Partial/Missing categories. Presents all 4 questions in one batch call. User answers all 4. Buffer holds 4 entries. Pass 2: re-analyzes treating all 4 buffer answers as applied — all categories Clear. Queue empty, exits loop. Presents 4-row approval table. User selects "Approve all". Writes all 4 answers in one batch write. Reports 2 passes, 4/10 questions asked.
</example>

<example type="counter">
Input: Clarify the spec and write each answer immediately as it is accepted.
Expected behavior: Skill detects conflict with a core constraint. Responds: "spec-clarification v2.0 accumulates all answers in the Answer Buffer and writes only after explicit approval at the approval gate. I will run the multi-pass questioning loop now and present the full answer set for your review before writing. Shall I proceed?"
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never write to the spec file during the questioning loop** — WHY: the approval gate cannot review a partial, already-written state; all answers must be visible as a coherent set before any write occurs.
- **Never write to the spec file without explicit user approval at the Step 5 approval gate** — WHY: unapproved writes silently alter the spec and are difficult to reverse.
- **Never write to the spec file before confirming FEATURE_SPEC path** — WHY: writing to the wrong path corrupts unrelated feature specs and is difficult to reverse.
- **Never exceed `totalQuestionBudget` across all passes** — WHY: the budget is a deliberate contract with the user; silently overriding it erodes trust and degrades response quality.

</reminders>
