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
Inspects spec-flow pipeline artifacts in a feature directory and produces a **Feature Analysis Report** at `{feature-dir}/feature-analysis-report.md`. Covers artifact inventory, last-modification timestamps, `[NEEDS CLARIFICATION]` marker counts, tasks.md state, cross-artifact consistency findings, and a three-tier **Readiness Verdict** (`READY` / `READY WITH WARNINGS` / `BLOCKED`). Re-invocations overwrite the prior report.

**Scope boundary**: Reads and reports only. Does NOT modify specs, tasks, or any artifact. Does NOT re-run upstream skills. For implementation, consult **spec-implement**. For resolving markers, consult **spec-clarification**.

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
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/skill-meta-rules.md`.
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/paginated-read.md` for multi-read artifacts.
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/needs-clarification-protocol.md` for markers.

## Operational Anchors
- Verify output complies with all constraints before producing.
- Implement EXACTLY what this skill defines — no extras.
- This skill is read-only. Refuse impulses to edit artifacts.
- Re-invocations overwrite prior report at same fixed path — no timestamped variants.
- If `feature-dir` not supplied, apply **Branch Detection** — do not guess paths.

## Branch Detection

> See `spek-fu/ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `feature-dir`: if not provided, apply **Branch Detection**. If user declines, stop and report `blocked`.
  > **If branch-detection.md unreadable**: fallback — run `git branch --show-current`, extract prefix and name, construct `spek-fu/features/<branch-name>`. Fail if command fails.
- Verify at least `{feature-dir}/spec.md` or `{feature-dir}/tasks.md` present. If neither, stop and report `blocked`.

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

For each **present** artifact, retrieve last modification timestamp: `git log --format="%ai" -1 -- <path>` or fallback to `stat -c "%y" <path>` if untracked.

> **If timestamp command fails**: record as `unknown`, continue.

For `spec-file` specifically: use `grep_search` to record whether a `## Clarifications` section and a `## Assumptions` section are present.

Record all results in the **Artifact Inventory Table**.

## Step 3 — Detect staleness

Compare timestamps across upstream→downstream pairs when both present:
```
spec.md → devils-advocate/ → testability-assessment.md → tdd-designer/report.md
spec.md → research.md → data-model.md → contracts/
research.md → quickstart.md
All above → tasks.md
```

Staleness signal: upstream timestamp < downstream timestamp (downstream generated before upstream changed).

Record signals in table. If none exist, record `none detected`.

> **If timestamps unknown for both**: record `indeterminate`.

## Step 4 — Count `[NEEDS CLARIFICATION]` markers

Use `grep_search` with pattern `[NEEDS CLARIFICATION:` to count per artifact. Enumerate directories and count across files.

Record per-artifact counts and grand total in table. Record zero as `0`.

> **If `grep_search` fails**: record as `unknown`.

## Step 5 — Analyze tasks.md state

If `tasks-file` present, load and parse:
- **Phase inventory**: all `## Phase` headings with title and per-phase task count.
- **Task state**: global counts of `[ ]` (pending), `[X]` (complete), `[!]` (blocked).
- **Subtask count**: indented sub-items.
- **BDD tasks**: tasks matching `Implement TDD-` or BDD ID references.

Record in **Tasks Summary**.

> **If `tasks-file` unreadable/unparseable**: record counts as `unknown`.

## Step 6 — Cross-artifact consistency analysis

Load using paginated-read:
- **From spec**: Functional Requirements, Non-Functional Requirements, User Stories only.
- **From tasks**: all task descriptions and IDs.

Run detection passes (cap at 50 rows; overflow summarized in one line).

### Pass A — Coverage gaps
For each user story in spec, check if ≥1 task in tasks.md references it by story number or key phrase. Record unreferenced as `UNCOVERED` (HIGH severity).

### Pass B — Marker context
For each `[NEEDS CLARIFICATION:` marker, record artifact, line context, question text. Severity: `HIGH` in spec/tasks; `MEDIUM` otherwise.

### Pass C — Inconsistency detection
- **Terminology drift**: same concept named differently across spec/tasks (e.g., `user profile` vs `member account`). MEDIUM.
- **Missing data entities**: entities in spec but not in tasks. HIGH.
- **Conflicting requirements**: contradictions in spec. CRITICAL.

> **If spec absent**: skip A and C; record `spec absent — coverage and consistency skipped`.

## Step 7 — Compute readiness verdict

Apply in order — first match determines verdict:

1. **`BLOCKED`** — if any:
   - spec or tasks missing, OR
   - Any CRITICAL finding.

2. **`READY WITH WARNINGS`** — if not BLOCKED and any:
   - Markers > 0, OR
   - Staleness detected, OR
   - HIGH findings, OR
   - Intermediate artifact missing.

3. **`READY`** — otherwise: all artifacts present, zero markers, no staleness, no HIGH/CRITICAL.

## Step 8 — Write report

Load template at `spek-fu/ai/plugins/spec-flow/templates/feature-analysis-template.md`.

> **If template missing**: use hardcoded order — Readiness Verdict, Artifact Inventory, Staleness Signals, Marker Counts, Tasks Summary, Consistency Findings, Next Actions.

Check if report exists; if yes, delete it first. Then write fresh report.

> **If write fails**: report `fail` with error; do not retry.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load artifacts, templates, knowledge. Apply paginated-read for multi-read files.
- **file_search**: Verify artifact existence.
- **list_dir**: Enumerate directories.
- **grep_search**: Count markers, detect section headings, detect terminology/entities.
- **run_in_terminal**: Retrieve modification timestamps.
- **create_file**: Write report after removing any prior version.
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

**BLOCKED message**:
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
Input: `feature-dir` = `spek-fu/features/005-user-auth`; all artifacts present, no markers, no staleness, all stories covered.
Expected: Verdict `READY`, report written to feature dir, chat: "Feature Analysis Report written to `spek-fu/features/005-user-auth/feature-analysis-report.md`. Verdict: `READY`."
</example>

<example>
Input: `feature-dir` = `spek-fu/features/003-payment-flow`; spec has 2 markers, tasks.md older than spec (staleness), intermediates present.
Expected: Verdict `READY WITH WARNINGS`, report documents warnings, suggests "Re-run `/spec-tasks-draft`."
</example>

<example>
Input: `feature-dir` not supplied; current git branch is `007-search-feature`.
Expected behavior: Skill applies Branch Detection, derives `feature-dir = spek-fu/features/007-search-feature/`, proceeds with full analysis, writes report at `spek-fu/features/007-search-feature/feature-analysis-report.md`.
</example>

<example>
Input: `feature-dir` = `spek-fu/features/002-reporting`; tasks.md missing.
Expected: Verdict `BLOCKED`, report documents blocker, suggests "Run `/spec-tasks-draft`."
</example>

<example type="counter">
Input: `feature-dir` = `spek-fu/features/001-user-profile`; spec.md contains 3 `[NEEDS CLARIFICATION]` markers; user asks the skill to resolve the markers inline.
Expected behavior: Skill counts markers and documents them in the report. Refuses to modify spec.md. Responds: "BLOCKED from modifying spec.md — this skill is strictly read-only. To resolve clarification markers, consult the **spec-clarification** skill."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- Constraint 1 — write ONLY to `{feature-dir}/feature-analysis-report.md`; never modify any upstream artifact.
- Constraint 2 — do NOT invoke other skills, runbooks, or steps.
- Constraint 3 — prose suggestions informational only; never phrase as automated actions.
- Constraint 4 — **Readiness Verdict** is first substantive line of report.
- Constraint 5 — stop and report `blocked` if `feature-dir` unresolvable.
- Never act on partially read files — read to EOF before using content.

</reminders>
