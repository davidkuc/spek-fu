---
id: "spec-feature-analysis"
recommended-tier: "standard-agent"
version: 1.0
description: "Inspects all spec-flow pipeline artifacts in a feature directory, producing a Feature Analysis Report with artifact inventory, staleness signals, [NEEDS CLARIFICATION] marker counts, tasks state breakdown, cross-artifact consistency findings, and a readiness verdict. USE FOR: verifying all upstream artifacts are complete, coherent, and non-stale before starting implementation. DO NOT USE FOR: modifying artifacts, re-running upstream pipeline skills, or implementing the feature — consult the **spec-implement** skill for implementation."
anti-scope: "Does not modify spec.md, tasks.md, or any upstream pipeline artifact. Does not invoke other skills or re-run any upstream pipeline step. The only file this skill writes is feature-analysis-report.md."
tags:
  - "quality"
  - "analysis"
  - "readiness"
  - "reporting"
inputs:
  - "feature-dir: path to the feature directory to inspect (optional — resolved via Branch Detection)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "{feature-dir}/feature-analysis-report.md — Feature Analysis Report with readiness verdict, artifact inventory, staleness signals, marker counts, tasks state summary, and consistency findings"
  - "Execution status: ok, blocked, or fail"
  - "One-line summary in chat"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` via Branch Detection when `feature-dir` is absent; it cannot interact with the user when dispatched as a stateless subagent.

# Skill: spec-feature-analysis

<!-- SECTION 1: Identity (primacy position) -->
Inspects the complete set of spec-flow pipeline artifacts in a feature directory and produces a single-file **Feature Analysis Report** at `{feature-dir}/feature-analysis-report.md`. The report covers artifact existence and last-modification timestamps, `[NEEDS CLARIFICATION]` marker totals per artifact, tasks.md phase inventory and state counts, cross-artifact consistency findings (coverage gaps, terminology drift, and constitution alignment), and a three-tier **Readiness Verdict** (`READY` / `READY WITH WARNINGS` / `BLOCKED`). Re-invocations overwrite the prior report — this is a current-state snapshot, not a historical record.

**Scope boundary**: This skill reads and reports only — it does NOT modify spec.md, tasks.md, or any upstream pipeline artifact. It does NOT re-run any upstream skill or dispatch any pipeline step. For implementing the task plan, consult the **spec-implement** skill. For resolving clarification markers in spec.md, consult the **spec-clarification** skill.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER write to any file other than `{feature-dir}/feature-analysis-report.md` — WHY: this is a strictly read-only inspector; any mutation of an upstream artifact breaks the pipeline audit trail and corrupts the phase that produced it.
2. NEVER invoke any other skill, runbook, or dispatch any pipeline step — WHY: orchestration and re-execution are the user's role; this skill informs but does not act.
3. NEVER make recommendations that mutate state — only descriptive prose suggestions addressed to the user — WHY: instruction-phrased prose can mislead an automated agent into executing changes without user approval.
4. ALWAYS render the Readiness Verdict as the first substantive line of the written report — WHY: a user or agent scanning the output must see the verdict immediately; burying it in the body defeats the purpose of the inspection.
5. NEVER proceed if `feature-dir` cannot be resolved and the user declines to provide one — WHY: analysis with an unknown base path produces fabricated findings with no analytical value.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `ai/plugins/spec-flow/knowledge/skill-meta-rules.md` before acting.
- Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` whenever reading any artifact that may exceed a single `read_file` response.
- Apply `ai/plugins/spec-flow/knowledge/needs-clarification-protocol.md` when counting and categorizing `[NEEDS CLARIFICATION]` markers.

## Operational Anchors
- Before producing any output, verify it complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- This skill is read-only. Any impulse to edit spec.md, tasks.md, or any other pipeline artifact must be refused immediately.
- Re-invocations overwrite the prior report at the same fixed path — no timestamped variants.
- If `feature-dir` is not supplied, apply the **Branch Detection** procedure — do not guess paths.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `feature-dir`: if not provided as input, read `ai/plugins/spec-flow/knowledge/branch-detection.md` via `read_file` and apply the core procedure. If the user provides a path manually, use it. If the user declines to provide one, stop and report `blocked`.

  > **If `branch-detection.md` cannot be read**: apply the fallback — run `git branch --show-current`, extract the numeric prefix and feature name, and construct `feature-dir` as `features/<branch-name>`. If the command fails, stop and report `blocked — branch detection failed; supply feature-dir explicitly`.

- Verify that at least `{feature-dir}/spec.md` or `{feature-dir}/tasks.md` is present before continuing. If neither exists, stop and report `blocked — no analyzable artifacts found at <feature-dir>; run spec-feature-draft first`.

## Done conditions

- **ok**: `{feature-dir}/feature-analysis-report.md` written (or overwritten) and a one-line summary shown in chat.
- **blocked**: `feature-dir` cannot be resolved, or no analyzable artifacts exist.
- **fail**: unrecoverable I/O error prevents report creation — state the error explicitly.

## Step 1 — Resolve artifact paths

Derive the nine tracked artifact paths from `feature-dir`:

| Alias | Path |
|-------|------|
| `spec-file` | `{feature-dir}/spec.md` |
| `devils-advocate-dir` | `{feature-dir}/devils-advocate/` |
| `testability-report` | `{feature-dir}/test-expert/testability-assessment.md` |
| `tdd-report` | `{feature-dir}/tdd-designer/report.md` |
| `research-file` | `{feature-dir}/research.md` |
| `data-model-file` | `{feature-dir}/data-model.md` |
| `contracts-dir` | `{feature-dir}/contracts/` |
| `quickstart-file` | `{feature-dir}/quickstart.md` |
| `tasks-file` | `{feature-dir}/tasks.md` |

> **If `feature-dir` cannot be resolved at this step**: stop and report `status: blocked`. State the missing path explicitly.

## Step 2 — Build artifact inventory

For each artifact slot in the path table, check existence:
- Files: use `file_search` with the exact relative path.
- Directories (`devils-advocate-dir`, `contracts-dir`): use `list_dir`; record file count if present (e.g., `present — 2 files`).

For each **present** artifact, retrieve the last modification timestamp by running:
```
git log --format="%ai" -1 -- <path>
```
Fall back to `stat -c "%y" <path>` if the file is untracked.

> **If a timestamp command fails for an artifact**: record its timestamp as `unknown` and continue.

For `spec-file` specifically: use `grep_search` to record whether a `## Clarifications` section and a `## Assumptions` section are present.

Record all results in the **Artifact Inventory Table**.

## Step 3 — Detect staleness

Compare timestamps across these upstream→downstream pairs when both are present:

```
spec.md → devils-advocate/ → testability-assessment.md → tdd-designer/report.md
spec.md → research.md → data-model.md → contracts/
research.md → quickstart.md
All of the above → tasks.md
```

A **staleness signal** is triggered when: timestamp of upstream artifact < timestamp of downstream artifact. This means the downstream was generated before the upstream was last changed.

Record all signals in the **Staleness Signals Table**. If none exist, record `none detected`.

> **If timestamps are `unknown` for both artifacts in a pair**: skip the pair and record `indeterminate — timestamps unavailable`.

## Step 4 — Count `[NEEDS CLARIFICATION]` markers

For each present artifact (excluding directories), use `grep_search` with the pattern `[NEEDS CLARIFICATION:` to count occurrences. For `devils-advocate-dir` and `contracts-dir`, enumerate their files via `list_dir` and count across all contained files.

Record per-artifact counts and a grand total in the **Marker Count Table**. Record zero as `0`.

> **If `grep_search` fails for an artifact**: record the count as `unknown` for that artifact and continue.

## Step 5 — Analyze tasks.md state

If `tasks-file` is present, load it using the paginated-read procedure and parse:

- **Phase inventory**: all `## Phase` headings with their title and per-phase task count.
- **Task state counts**: global counts of `[ ]` (pending), `[X]` (complete), and `[!]` (blocked) markers.
- **Subtask count**: indented sub-items (lines starting with two or more spaces followed by `- [ ]`, `- [X]`, or `- [!]`).
- **BDD test task count**: tasks whose description matches `Implement TDD-` or references a BDD test ID.

Record in the **Tasks Summary**.

> **If `tasks-file` cannot be loaded or parsed**: record all task state counts as `unknown` and continue.

## Step 6 — Cross-artifact consistency analysis

Load the following using the paginated-read procedure:

**From `spec-file`** (if present): Functional Requirements, Non-Functional Requirements, and User Stories sections only.

**From `tasks-file`** (if present): all task descriptions and their IDs.

Perform these detection passes. Cap total findings at 50 rows; summarize any overflow in a single line.

### Pass A — Coverage gaps
For each user story in spec.md, check whether at least one task in tasks.md references it by user story number or a key noun phrase from its goal. Record stories with zero associated tasks as `UNCOVERED` (severity: `HIGH`).

### Pass B — Marker context
For each `[NEEDS CLARIFICATION:` marker found in Step 4, record the artifact, approximate line context, and the question text. Severity: `HIGH` if in `spec-file` or `tasks-file`; `MEDIUM` for other artifacts.

### Pass C — Inconsistency detection
- **Terminology drift**: identify the same concept named differently across spec.md and tasks.md (e.g., `user profile` vs `member account`). Severity: `MEDIUM`.
- **Missing data entities**: entities prominently named in spec.md Functional Requirements but absent from tasks.md. Severity: `HIGH`.
- **Conflicting requirements**: two requirements within spec.md that contradict each other. Severity: `CRITICAL`.

Assign a finding ID using the prefix of its category (`A1`, `B1`, `C1`, …).

> **If spec.md is absent**: skip passes A and C; record `spec.md absent — coverage and consistency analysis skipped` in the findings section.

## Step 7 — Compute readiness verdict

Apply in order — the first matching condition determines the verdict:

1. **`BLOCKED`** — if any of the following:
   - `spec-file` absent.
   - `tasks-file` absent.
   - Any `CRITICAL` finding from Pass C.

2. **`READY WITH WARNINGS`** — if not BLOCKED and any of the following:
   - Total `[NEEDS CLARIFICATION]` marker count > 0.
   - Any staleness signal detected.
   - Any `HIGH` finding from passes A, B, or C.
   - Any intermediate pipeline artifact absent (`devils-advocate-dir`, `testability-report`, `tdd-report`, `research-file`, `data-model-file`, `contracts-dir`, `quickstart-file`).

3. **`READY`** — otherwise: all required and intermediate artifacts present, zero markers, no staleness, no HIGH or CRITICAL findings.

## Step 8 — Write report

Load `ai/plugins/spec-flow/templates/feature-analysis-template.md` using the paginated-read procedure.

> **If `feature-analysis-template.md` cannot be read**: compose the **Feature Analysis Report** using this hardcoded section order — Readiness Verdict, Artifact Inventory, Staleness Signals, Marker Counts, Tasks Summary, Consistency Findings, Next Actions. Record the template read failure in the report header.

Check whether `{feature-dir}/feature-analysis-report.md` already exists using `file_search`.
- **If absent**: use `create_file` to write the report.
- **If present**: use `run_in_terminal` to run `rm "{feature-dir}/feature-analysis-report.md"`, then use `create_file` to write the fresh report.

> **If the write fails**: report `status: fail` with the exact error message; do not attempt a retry.

After writing, state in chat:
> "**Feature Analysis Report** written to `{feature-dir}/feature-analysis-report.md`. Verdict: `<verdict>`."

The skill is complete when `{feature-dir}/feature-analysis-report.md` exists on disk and the completion message has been shown.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load spec.md, tasks.md, templates, knowledge files, and any present artifact. Apply `ai/plugins/spec-flow/knowledge/paginated-read.md` for any file that may span multiple reads.
- **file_search**: Verify artifact existence and locate the feature directory before loading.
- **list_dir**: Enumerate `devils-advocate/` and `contracts/` directory contents to detect presence and file counts.
- **grep_search**: Count `[NEEDS CLARIFICATION:` markers per artifact; detect section headings in spec.md; detect terminology and entity references across artifacts for Pass C.
- **run_in_terminal**: Retrieve modification timestamps (`git log`, `stat`); remove a prior report before overwriting in Step 8.
- **vscode_askQuestions**: Collect `feature-dir` via Branch Detection when not supplied as input.
- **create_file**: Write `feature-analysis-report.md` in Step 8 only, after any prior version has been removed.
- Do NOT use tools not listed here unless the skill explicitly escalates.
- Do NOT use any write tool on spec.md, tasks.md, or any artifact outside `{feature-dir}/feature-analysis-report.md`.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Rules**:
- `status` is one of: `ok`, `blocked`, `fail`
- `output_path` is the absolute path to the written report, or `null` if aborted before writing
- `summary` is a single line suitable for inline reporting

**Completion message** (shown in chat after Step 8):
```
Feature Analysis Report written to `{feature-dir}/feature-analysis-report.md`. Verdict: <READY | READY WITH WARNINGS | BLOCKED>.
```

**Blocked message** (shown when blocked):
```
BLOCKED: spec-feature-analysis requires <missing input or artifact>. <Corrective action>.
```

**Report sections written to disk**:
```markdown
## Readiness Verdict: <READY | READY WITH WARNINGS | BLOCKED>

<One-sentence explanation of the primary factor driving the verdict.>

---

## Artifact Inventory

| Artifact | Status | Last Modified | Notes |
|----------|--------|---------------|-------|
| spec.md | present / absent | <timestamp or —> | |
| spec.md — ## Clarifications | present / absent | — | |
| spec.md — ## Assumptions | present / absent | — | |
| devils-advocate/ | present (N files) / absent | <timestamp of most recent or —> | |
| test-expert/testability-assessment.md | present / absent | <timestamp or —> | |
| tdd-designer/report.md | present / absent | <timestamp or —> | |
| research.md | present / absent | <timestamp or —> | |
| data-model.md | present / absent | <timestamp or —> | |
| contracts/ | present (N files) / absent | <timestamp of most recent or —> | |
| quickstart.md | present / absent | <timestamp or —> | |
| tasks.md | present / absent | <timestamp or —> | |

---

## Staleness Signals

| Upstream Artifact | Downstream Artifact | Signal |
|-------------------|---------------------|--------|
| | | stale / current / indeterminate |

*(none detected)*

---

## [NEEDS CLARIFICATION] Marker Counts

| Artifact | Count |
|----------|-------|
| spec.md | 0 |
| devils-advocate report(s) | 0 |
| testability-assessment.md | 0 |
| tdd-designer/report.md | 0 |
| research.md | 0 |
| data-model.md | 0 |
| tasks.md | 0 |
| **Total** | **0** |

---

## Tasks Summary

| Metric | Value |
|--------|-------|
| Phases | N |
| Pending [ ] | N |
| Complete [X] | N |
| Blocked [!] | N |
| Subtasks | N |
| BDD test tasks | N |

---

## Consistency Findings

| ID | Severity | Category | Location | Finding | Suggestion |
|----|----------|----------|----------|---------|------------|

*(none detected)*

---

## Next Actions

- <Prose suggestion for each BLOCKED or CRITICAL/HIGH finding>
- Run `/spec-feature-analysis` again after resolving issues to confirm readiness.
```
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: `feature-dir` = `features/005-user-auth`; all 9 artifact slots present; no `[NEEDS CLARIFICATION]` markers; no staleness signals; every user story in spec.md has a corresponding task in tasks.md.
Expected behavior: Skill builds the full artifact inventory, records zero markers and zero staleness signals, finds no uncovered user stories, computes verdict `READY`, writes the report to `features/005-user-auth/feature-analysis-report.md`, states: "Feature Analysis Report written to `features/005-user-auth/feature-analysis-report.md`. Verdict: `READY`."
</example>

<example>
Input: `feature-dir` = `features/003-payment-flow`; spec.md present with 2 `[NEEDS CLARIFICATION]` markers; tasks.md present but its git timestamp predates the last commit to spec.md (staleness signal); all intermediate artifacts present.
Expected behavior: Skill counts 2 markers in spec.md, detects tasks.md staleness relative to spec.md, computes verdict `READY WITH WARNINGS`, writes report documenting both warnings, suggests "Re-run `/spec-tasks-draft` — spec.md was modified after tasks.md was generated." Reports in chat: "Feature Analysis Report written to `features/003-payment-flow/feature-analysis-report.md`. Verdict: `READY WITH WARNINGS`."
</example>

<example>
Input: `feature-dir` not supplied; current git branch is `007-search-feature`.
Expected behavior: Skill applies Branch Detection, derives `feature-dir = features/007-search-feature/`, proceeds with full analysis, writes report at `features/007-search-feature/feature-analysis-report.md`.
</example>

<example>
Input: `feature-dir` = `features/002-reporting`; spec.md present; tasks.md absent; all other intermediate artifacts present.
Expected behavior: Skill detects tasks.md as absent, computes verdict `BLOCKED`, writes the report documenting the blocker with suggestion "Run `/spec-tasks-draft` to generate tasks.md before proceeding to implementation." Reports in chat: "BLOCKED: tasks.md is absent — run /spec-tasks-draft first."
</example>

<example type="counter">
Input: `feature-dir` = `features/001-user-profile`; spec.md contains 3 `[NEEDS CLARIFICATION]` markers; user asks the skill to resolve the markers inline.
Expected behavior: Skill counts markers and documents them in the report. Refuses to modify spec.md. Responds: "BLOCKED from modifying spec.md — this skill is strictly read-only. To resolve clarification markers, consult the **spec-clarification** skill."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- Constraint 1 — write ONLY to `{feature-dir}/feature-analysis-report.md`; never modify any upstream artifact.
- Constraint 2 — do NOT invoke any other skill, runbook, or pipeline step.
- Constraint 3 — prose suggestions are informational only; never phrase them as automated or imperative actions.
- Constraint 4 — **Readiness Verdict** must be the first substantive line of the written report.
- Constraint 5 — stop and report `blocked` if `feature-dir` cannot be resolved.
- Never act on a partially read knowledge file, template, or artifact — read to end of file before using content.

</reminders>
