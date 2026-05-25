---
id: "orch-final-orchestration-validation"
recommended-tier: "fast-agent"
version: 1.0
description: "Reads all artifacts produced by an orchestration run and produces a final quality report covering completeness, consistency, and correctness. USE FOR: end-of-orchestration quality gate before closure; verifying that all planned outputs were actually produced and meet basic quality criteria."
anti-scope: "It does NOT apply fixes, perform per-wave verification, or analyze the framework's internal consistency outside the scope of the current run's artifacts."
tags:
  - "quality"
  - "orchestration"
  - "quality-gate"
  - "reporting"
inputs:
  - "Inline orchestration summary text or structured orchestration state (required)"
  - "Explicit list of file paths to check (required)"
  - "Path to the relevant iteration spec.md (optional)"
  - "Path to the relevant iteration plan.md (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Overall quality gate result: ok, blocked, or fail"
  - "Inline final quality report"
  - "One-line summary of the quality assessment"
dispatch-variant: "full"
---

# Skill: orch-final-orchestration-validation

<!-- SECTION 1: Identity (primacy position) -->
Reads the orchestration summary, all artifact files produced during the run, and the relevant specs and plans, then produces a Final Quality Report covering three dimensions: **Completeness** (all planned artifacts exist), **Consistency** (artifacts reference each other correctly and use canonical terms), and **Correctness** (no obvious errors, unfilled placeholders, or contradictions). This is a read-only gate skill — it reports findings; it does not fix them.

**Scope boundary**: This skill reads and reports across all produced artifacts in one orchestration run. It does NOT apply fixes, perform per-wave verification, or analyze the framework's internal consistency outside the scope of the current run's artifacts.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Read orchestration artifacts freely to assess quality — NEVER write to, modify, or delete them. WHY: QA and remediation are separate responsibilities; mixing them bypasses review gates.
2. Include every planned artifact in the report, even when it is absent — do NOT omit any planned artifact from the report, including absent ones. WHY: a missing artifact is a completeness failure; omitting it from the report hides the failure.
3. Read the file before assessing it — do not mark PASS from file name or description alone. WHY: placeholder files or trivially short files that match the expected name produce false PASS verdicts.
4. ALWAYS produce a report even if the orchestration was only partially completed — mark missing artifacts as ABSENT and continue; do NOT halt or skip report writing because some artifacts are missing. WHY: Closure phase runs even on partial completion; a partial report is more useful than no report.
5. When a file contains unfilled template placeholders (e.g., `{TODO}`, `[placeholder]`, `{{field}}`), always flag them as correctness failures — do NOT pass or exempt a file with unfilled placeholders, regardless of other quality signals. WHY: placeholders indicate incomplete generation that will mislead downstream consumers.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your report complies with all rules in `<constraints>` above.
- Prioritize factual, file-grounded verdicts — every finding must cite a specific file path and the evidence that drove the verdict.
- Implement EXACTLY and ONLY what this skill instructs — no extra check dimensions, no unrequested fixes or scope extensions. The three valid dimensions are Completeness, Consistency, and Correctness; do not add, merge, or expand beyond them.
- Anti-drift: if you discover an issue in a file not listed in the artifact manifest, note it as a tangential finding — do not expand the report scope to cover unrequested files.
- Keep findings actionable — every non-PASS finding must include a Recommendation field with a concrete next step.

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve the orchestration summary input and the initial artifact list before loading files.
- Classify the run as blocked or ready before artifact checks by checking whether the orchestration summary is readable.
- If the orchestration summary is missing, stop before artifact checks and return the blocked status.

## Step 1 — Load orchestration context

1. Read the orchestration summary from `orchestration-summary` input.
2. Read the spec file if provided.
3. Read the plan file if provided.
4. Compile the full artifact list: combine the `artifact-list` input with any additional artifact paths found in the summary, spec, or plan. Deduplicate.

> **If the orchestration summary cannot be read**: Halt and return: `Status: BLOCKED — orchestration-summary not found at {path}. Caller action: ensure orchestrator completed Step 25 before invoking this skill.`

## Step 2 — Completeness check

For each planned artifact in the compiled artifact list:

1. Verify the file exists at the stated path using `read_file`.
2. Verify it is non-trivially populated (more than 5 non-blank lines after stripping frontmatter).
3. Record: **PRESENT** | **ABSENT** | **EMPTY**.

> **If a file is absent or empty**: Record as completeness FAIL with path and note "File not found" or "File is empty/trivial".

## Step 3 — Consistency check

For each PRESENT artifact:

1. Check that all cross-references are valid: if the file mentions another artifact by path or name, verify that target exists in the artifact list.
2. Check that skill-id references appear in `spek-fu/ai/plugins/skf/skills/skills-index.json`.
3. Record: **PASS** | **WARN** (minor inconsistency) | **FAIL** (broken reference or wrong canonical term).

> **If skills-index.json cannot be read**: Note the gap in the report and skip the sub-checks that require them; do not halt.

## Step 4 — Correctness check

For each PRESENT artifact:

1. Scan for unfilled placeholders: patterns like `{TODO}`, `[placeholder]`, `{{field}}`, `<insert ...>`, `TBD`, `FIXME`. Flag each occurrence with file path and line content.
2. Verify the file's stated purpose matches its actual content (e.g., a spec file should contain problem statement, requirements, constraints — not just headings).
3. If a spec/plan was provided, verify the artifact addresses the relevant requirements it was supposed to satisfy.
4. Record: **PASS** | **WARN** (minor gap) | **FAIL** (placeholder present, content does not match stated purpose).

## Step 5 — Aggregate status

Compute overall-status:
- `PASS` — all Completeness, Consistency, and Correctness checks are PASS.
- `PASS-WITH-WARNINGS` — no FAIL verdicts, but at least one WARN.
- `FAIL` — at least one FAIL verdict in any dimension.

## Step 6 — Return Final Quality Report

Return the report inline in chat.

The skill is complete when the report has been returned inline.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Primary tool — read orchestration summary, spec, plan, skills-index.json and every artifact file. Read large files in increments (increment startLine until response < page size) before assessing.
- **file_search**: Discover artifact files if the artifact list must be inferred from the iteration folder or explicit artifact roots.
- **grep_search**: Scan files for placeholder patterns (`{TODO}`, `[placeholder]`, etc.) and cross-reference targets.
- Do NOT use edit or execute tools — this skill is read-only except for writing the report file.
- Use `read_file` and `grep_search` to perform completeness, placeholder, and verdict checks directly; do not rely on terminal helper scripts.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-final-orchestration-validation` |
| wave | `N` |
| step | `N.M` |
| output_path | `none` |
| summary | one-line quality assessment |

Return the Final Quality Report inline in chat using the template below. Provide the full report, not a summary.

**Field definitions:**
- `Date`: ISO 8601 date of the run (e.g., `2026-04-13`)
- `Run goal`: One-line goal copied verbatim from the orchestration summary
- `Artifacts checked`: Integer count of artifacts evaluated
- `Overall status`: Exactly one of `PASS` | `PASS-WITH-WARNINGS` | `FAIL` (see Step 5 for derivation rules)
- Per-artifact `Status` in Completeness: Exactly one of `PRESENT` | `ABSENT` | `EMPTY`
- Per-artifact `Status` in Consistency: Exactly one of `PASS` | `WARN` | `FAIL`
- Per-artifact `Status` in Correctness: Exactly one of `PASS` | `WARN` | `FAIL`
- `Finding`: Required for any non-PASS row; must cite file path and evidence
- `Recommended action`: Required for every FAIL or WARN row

**Required sections** (in this order): Completeness table → Consistency table → Correctness table → Summary & Recommendations.

```markdown
# Final Quality Report

Date: {date}
Run goal: {one-line goal from orchestration summary}
Artifacts checked: {count}
Overall status: PASS | PASS-WITH-WARNINGS | FAIL

---

## Completeness

| Artifact | Status | Note |
|----------|--------|------|
| {path} | PRESENT / ABSENT / EMPTY | {note if not PRESENT} |

---

## Consistency

| Artifact | Status | Finding |
|----------|--------|----------|
| {path} | PASS / WARN / FAIL | {description} — {file reference if applicable} |

---

## Correctness

| Artifact | Status | Finding |
|----------|--------|----------|
| {path} | PASS / WARN / FAIL | {description} — {file:line if applicable} |

---

## Summary & Recommendations

Overall: {PASS | PASS-WITH-WARNINGS | FAIL}

{For each FAIL or WARN finding, one recommendation:}
- [{path}] — {Recommended action to resolve the finding}
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: inline orchestration summary (states goal "Add a new utility skill", lists 3 produced artifacts: the new skill file, skills-index.json (updated)); explicit list of file paths includes those three files.
Expected output: Reads the summary and the listed artifacts. Completeness: all 3 PRESENT. Consistency: the new skill file references a valid indexed skill-id -> PASS; skills-index.json new entry name matches file name -> PASS. Correctness: scan for placeholders — none found; content matches stated purpose -> all PASS. Overall: PASS. Returns full report inline.
</example>

<example>
Input: inline orchestration summary (states 4 artifacts); artifact-list includes one file that does not exist; another file contains `{{skill-description}}` placeholder.
Expected output: Completeness: 3 PRESENT, 1 ABSENT → FAIL. Correctness: file with `{{skill-description}}` → FAIL (unfilled placeholder at line X). Overall: FAIL. Report includes two recommendations: "Create the missing file at {path}" and "Fill placeholder `{{skill-description}}` in {file} line {N}."
</example>

<example type="counter">
Input: After the report is produced, caller says: "Fix the placeholder in the generated skill file."
Expected behavior: Skill responds: "orch-final-orchestration-validation is read-only. To fix the placeholder, dispatch the appropriate implementation workflow with the relevant context."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
</reminders>
