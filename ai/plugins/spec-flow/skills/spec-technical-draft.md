---
id: "spec-technical-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Executes the implementation planning workflow against a validated feature spec, producing research.md, data-model.md, typed API contracts, and quickstart.md. USE FOR: translating an approved feature spec into a phased technical design plan with resolved ambiguities and typed API contracts. DO NOT USE FOR: authoring the initial feature spec, running tests, or executing implementation work."
anti-scope: "Does not author or modify the feature spec, run tests, or execute implementation work."
tags:
  - "specification"
  - "planning"
  - "requirements"
  - "feature"
inputs:
  - "User arguments — optional guidance or overrides for the planning workflow (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "research.md — resolved technical unknowns with decisions and rationale (SPECS_DIR)"
  - "data-model.md — entities, fields, relationships, and validation rules (SPECS_DIR)"
  - "contracts/ — OpenAPI or GraphQL schema files per user action (SPECS_DIR/contracts/)"
  - "quickstart.md — developer onboarding guide for the feature (SPECS_DIR)"
  - "Execution status report: ok, blocked, or fail"
dispatch-variant: "full"
---

# Skill: spec-technical-draft

<!-- SECTION 1: Identity (primacy position) -->
Executes the implementation planning workflow for a validated feature spec, producing a phased set of technical design artifacts: resolved technical research, a data model, typed API contracts, and a quickstart guide. The workflow runs in two phases — Phase 0 resolves all ambiguities in the technical context via targeted research before any design work begins; Phase 1 generates the design artifacts from confirmed decisions. The skill stops and reports after Phase 1 is complete.

**Scope boundary**: This skill translates an existing, validated feature spec into a technical plan. It does NOT author or modify the feature spec itself, run tests, or execute implementation work. For test design, consult the TDD designer upstream pipeline before re-running this skill.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER proceed from Phase 0 to Phase 1 if any `[NEEDS CLARIFICATION: <question>]` markers remain unresolved — WHY: unresolved ambiguities cascade directly into contracts and data models, producing expensive downstream rework.
2. NEVER invent or assume technical details to fill a `[NEEDS CLARIFICATION]` marker — WHY: fabricated decisions produce false confidence in research.md and corrupt every artifact derived from it.
3. ALWAYS treat the TDD designer report as authoritative for test scope and shape — WHY: the test contract is locked upstream and must not be contradicted by planning decisions.
4. ALWAYS ERROR on constitution gate violations and stop — do not silently continue past a failed gate — WHY: violations propagate to all downstream implementation work.
5. ALWAYS use the exact literal marker `[NEEDS CLARIFICATION: <specific question>]` — no abbreviations or alternative formats — WHY: consistent syntax enables automated detection and resolution tracking.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- If user arguments are ambiguous or contradictory, apply them narrowly and do not expand scope.
- Before creating any output file, check whether it already exists: if `research.md` is complete → skip Phase 0; if `data-model.md` partially exists → read and update in place rather than recreate.

## Branch Detection

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **`SPECS_DIR` alias variant**.
> Apply it when `SPECS_DIR` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight
- Inspect user arguments — empty arguments are valid and require no action.
- Check disk for `research.md`, `data-model.md`, and `contracts/` to determine run state: not started / Phase 0 in progress / Phase 0 complete / Phase 1 in progress / complete.
- Declare the detected run state before proceeding.

## Done conditions
- **Phase 0 complete**: `SPECS_DIR/research.md` exists with zero unresolved `[NEEDS CLARIFICATION]` markers.
- **Phase 1 complete**: `SPECS_DIR/data-model.md`, at least one file in `SPECS_DIR/contracts/`, and `SPECS_DIR/quickstart.md` exist; **IMPL_PLAN** updated; agent context updated; Constitution Check passes.
- **Blocked**: any `[NEEDS CLARIFICATION]` markers remain unresolved, or constitution gate violations are found — report blockers and stop.

## Step 1 — Environment setup

Resolve required paths:
- Resolve **SPECS_DIR** via **Branch Detection** first: apply the `SPECS_DIR` alias variant from `ai/plugins/spec-flow/knowledge/branch-detection.md`. If the user provides a path, use it as `SPECS_DIR`. If the user declines, stop and report `blocked`.
- Call `vscode_askQuestions` with header `impl_plan` to collect **IMPL_PLAN** (absolute path to implementation plan file if it exists).

Derive:
- `SPEC` = `SPECS_DIR/spec.md`
- `TDD_DESIGNER_REPORT` = `SPECS_DIR/tdd-designer/report.md`

Use absolute paths for all subsequent file operations.

> **If `SPEC` does not exist at `SPECS_DIR/spec.md`**: stop and report the missing path — do not continue with a non-existent spec.

## Step 2 — Load context

Read the following files using multi-pass `read_file` calls (advance `startLine` and repeat until the response is shorter than the page size):
1. `SPEC` — the feature spec
2. `TDD_DESIGNER_REPORT` (only if it exists on disk)
3. `constitution/constitution.md` — the spek-fu constitution
4. **IMPL_PLAN** — the plan template (already copied)

> **If `TDD_DESIGNER_REPORT` does not exist**: note its absence and present the following proposal to the user before continuing: "The TDD designer report is missing. For best results, run the upstream pipeline in order before re-running this skill: `/speckit.devils-advocate` → `/speckit.test-expert` → `/speckit.tdd-designer`. The skill will continue, but test scope will be treated as undefined."

## Step 3 — Technical Context and Constitution Check

Fill the **Technical Context** section of **IMPL_PLAN**:
- For each unknown or ambiguous technical detail: insert `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty.
- Do NOT invent values for unknown fields.
- If `TDD_DESIGNER_REPORT` exists, incorporate its testing contract and risk notes into the Technical Context; treat it as authoritative for test scope.

Fill the **Constitution Check** section of **IMPL_PLAN** by evaluating each constitution gate against the spec:
- If any gate is violated: stop with ERROR, report the specific violations, and do not proceed.

## Step 4 — Phase 0: Research

**Prerequisites**: Technical Context filled; constitution check passes.

**Skip condition**: If `SPECS_DIR/research.md` already exists with zero `[NEEDS CLARIFICATION]` markers, skip this step and proceed to Step 5.

1. **Extract research tasks**: For each `[NEEDS CLARIFICATION]` marker in the Technical Context → one research task. For each dependency → one best-practices research task. For each integration point → one patterns research task.
2. **Dispatch research agents**: Launch one subagent per research task (or batch closely related tasks). Each task prompt: `Research {unknown} for {feature context}` or `Find best practices for {tech} in {domain}`.
3. **Consolidate findings** into `SPECS_DIR/research.md` using this format per decision:

```
## [Decision topic]
**Decision**: [what was chosen]
**Rationale**: [why chosen]
**Alternatives considered**: [what else was evaluated]
```

> **If research agents return conflicting results on a decision**: document all options in `research.md` under that decision and insert `[NEEDS CLARIFICATION: <specific question for user>]` — do not choose arbitrarily.

> **If any `[NEEDS CLARIFICATION]` markers remain in `research.md` after consolidation**: stop, present the unresolved markers to the user, and do not proceed to Phase 1.

**Output**: `SPECS_DIR/research.md` with all `[NEEDS CLARIFICATION]` markers resolved.

## Step 5 — Phase 1: Data Model

**Prerequisites**: `SPECS_DIR/research.md` complete with zero unresolved markers.

Extract entities from the feature spec and `research.md`. Write `SPECS_DIR/data-model.md` containing:
- Entity name, fields, and field types
- Relationships between entities
- Validation rules derived from requirements
- State transitions where applicable

> **If an entity's field types or relationships cannot be determined from the spec and research**: insert `[NEEDS CLARIFICATION: <question>]` in `data-model.md` at the ambiguous point, stop, and do not proceed to contracts.

## Step 6 — Phase 1: API Contracts

**Prerequisites**: `SPECS_DIR/data-model.md` complete with zero unresolved markers.

For each user action in the feature spec → define one endpoint. Use standard REST or GraphQL patterns as appropriate. Write schema files to `SPECS_DIR/contracts/` (OpenAPI YAML or GraphQL SDL).

## Step 7 — Phase 1: Quickstart

1. Write `SPECS_DIR/quickstart.md` — a developer onboarding guide covering setup steps, key endpoints, and example requests for the feature based on template `ai/plugins/spec-flow/templates/quickstart-template.md`.
2. Re-evaluate the **Constitution Check** section of **IMPL_PLAN** using the completed design artifacts. If new violations are found: ERROR, report them, and do not mark the skill complete.

## Step 8 — Report

Present the completion report (see `<output_format>`). Include **BRANCH** name, **IMPL_PLAN** path, and list of all generated or updated artifacts.

The skill is complete when `SPECS_DIR/research.md`, `SPECS_DIR/data-model.md`, at least one `SPECS_DIR/contracts/` file, and `SPECS_DIR/quickstart.md` exist on disk, and the Constitution Check passes.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load SPEC, TDD_DESIGNER_REPORT, constitution.md, IMPL_PLAN, and research.md. Use multi-pass reads — advance `startLine` and repeat until the response is shorter than the page size.
- **vscode_askQuestions**: Collect SPECS_DIR and IMPL_PLAN from the user in Step 1.
- **create_file**: Write `research.md`, `data-model.md`, contract schema files, and `quickstart.md` to SPECS_DIR. Only after prerequisites in each phase step are confirmed.
- **replace_string_in_file**: Update **IMPL_PLAN** sections (Technical Context, Constitution Check) in place. Do not recreate **IMPL_PLAN** from scratch.
- **runSubagent**: Dispatch research agents in Phase 0 (Step 4). Batch closely related tasks into one subagent call.
- Do NOT use tools not listed here unless explicitly escalating.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `spec-technical-draft` |
| wave | `N` |
| step | `N.M` |
| output_path | `SPECS_DIR` or `null` |
| summary | one-line summary of phase completed |

**Completion report**:

```
Branch: <branch-name>
IMPL_PLAN: <absolute-path>
Artifacts:
  - SPECS_DIR/research.md        [created | updated | skipped]
  - SPECS_DIR/data-model.md      [created | updated | skipped]
  - SPECS_DIR/contracts/<file>   [created | updated | skipped]
  - SPECS_DIR/quickstart.md      [created | updated | skipped]
Constitution Check: PASS | FAIL
Gate violations: <list or "none">
```

**Blocked report**:

```
Status: BLOCKED
Phase: <Phase 0 | Phase 1 | Constitution Check>
Reason: <specific cause>
Unresolved items:
  - [NEEDS CLARIFICATION: <question>]
Next action: <what the user must resolve before re-running>
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: Feature spec exists at SPECS_DIR/spec.md; TDD designer report exists; no prior planning artifacts on disk.
Expected behavior: Runs setup script and loads all context files. Fills Technical Context in IMPL_PLAN with two NEEDS CLARIFICATION markers for unknown integration patterns. Constitution check passes. Dispatches two research agents; consolidates findings into research.md with all markers resolved. Generates data-model.md (four entities), writes contracts/create-item.yaml and contracts/list-items.yaml, writes quickstart.md. Runs agent context update. Re-evaluates constitution check (passes). Reports completion with artifact list and branch name.
</example>

<example>
Input: Feature spec exists; no TDD designer report; SPECS_DIR/research.md already exists with zero unresolved markers.
Expected behavior: Proposes upstream pipeline to user (TDD report missing). Detects research.md is complete — skips Phase 0. Proceeds to Phase 1: generates data-model.md, contracts/, and quickstart.md. Reports completion.
</example>

<example type="counter">
Input: Phase 0 produces research.md but two [NEEDS CLARIFICATION] markers remain because research agents returned conflicting options.
Expected behavior: Skill detects unresolved markers. Reports: "BLOCKED — 2 [NEEDS CLARIFICATION] markers remain in research.md. Resolve these before re-running Phase 1." Lists the specific unresolved questions. Does not proceed to Phase 1.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never proceed to Phase 1 with unresolved `[NEEDS CLARIFICATION]` markers** — stop and report every unresolved marker. WHY: unresolved ambiguities corrupt contracts and data models.
- **Never invent values for unknown technical details** — insert the literal marker and stop. WHY: fabricated decisions produce false confidence that cascades to all downstream artifacts.
- **Never act on a partially read catalogue or spec file** — use multi-pass `read_file` until end of file is confirmed before evaluating. WHY: partial reads produce incomplete technical context and missed constitution gates.
- **Always ERROR on constitution gate violations** — do not silently continue past a failed gate. WHY: violations propagate to all downstream implementation work.

</reminders>
