---
id: "spec-technical-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Executes the technical planning workflow against a validated feature spec, producing research.md, data-model.md, typed API contracts, and quickstart.md. USE FOR: translating an approved feature spec into a phased technical design plan with resolved ambiguities and typed API contracts. DO NOT USE FOR: authoring the initial feature spec, running tests, or executing implementation work."
anti-scope: "Does not author or modify the feature spec, run tests, or execute implementation work."
tags:
  - "specification"
  - "planning"
  - "requirements"
  - "feature"
inputs:
  - "feature-dir: path to the feature directory containing spec.md (optional)"
  - "User arguments — optional guidance or overrides for the planning workflow (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "research.md — resolved technical unknowns with decisions and rationale ({feature-dir})"
  - "data-model.md — entities, fields, relationships, and validation rules ({feature-dir})"
  - "contracts/ — OpenAPI or GraphQL schema files per user action ({feature-dir}/contracts/)"
  - "quickstart.md — developer onboarding guide for the feature ({feature-dir})"
  - "Execution status report: ok, blocked, or fail"
dispatch-variant: "full"
---

# Skill: spec-technical-draft

<!-- SECTION 1: Identity (primacy position) -->
Executes the technical planning workflow for a validated feature spec, producing a phased set of technical design artifacts: resolved technical research, a data model, typed API contracts, and a quickstart guide. The workflow runs in two phases — Phase 0 resolves all ambiguities in the technical context via targeted research before any design work begins; Phase 1 generates the design artifacts from confirmed decisions. The skill stops and reports after Phase 1 is complete.

**Scope boundary**: This skill translates an existing, validated feature spec into technical planning artifacts only. It does NOT author or modify the feature spec itself, run tests, or execute implementation work.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER proceed from Phase 0 to Phase 1 if any `[NEEDS CLARIFICATION: <question>]` markers remain unresolved — WHY: unresolved ambiguities cascade directly into contracts and data models, producing expensive downstream rework.
2. NEVER invent or assume technical details to fill a `[NEEDS CLARIFICATION]` marker — WHY: fabricated decisions produce false confidence in research.md and corrupt every artifact derived from it.
3. ALWAYS treat `{feature-dir}/tdd-designer/report.md` as authoritative for test scope and shape when it exists — WHY: the test contract is locked upstream and must not be contradicted by planning decisions.
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

> See `ai/plugins/spec-flow/knowledge/branch-detection.md` — **core procedure**.
> Apply it when `feature-dir` is not supplied as input.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight
- Inspect user arguments — empty arguments are valid and require no action.
- Check disk for `research.md`, `data-model.md`, and `contracts/` to determine run state: not started / Phase 0 in progress / Phase 0 complete / Phase 1 in progress / complete.
- Declare the detected run state before proceeding.

## Done conditions
- **Phase 0 complete**: `{feature-dir}/research.md` exists with zero unresolved `[NEEDS CLARIFICATION]` markers.
- **Phase 1 complete**: `{feature-dir}/data-model.md`, at least one file in `{feature-dir}/contracts/`, and `{feature-dir}/quickstart.md` exist; constitution gate categories pass.
- **Blocked**: any `[NEEDS CLARIFICATION]` markers remain unresolved, or constitution gate violations are found — report blockers and stop.

## Step 1 — Resolve paths

Resolve required paths:
- Resolve `feature-dir` via **Branch Detection** first: apply the core procedure from `ai/plugins/spec-flow/knowledge/branch-detection.md`. If the user provides a path, use it as `feature-dir`. If the user declines, stop and report `blocked`.

Derive:
- `spec` = `{feature-dir}/spec.md`
- `testability-report` = `{feature-dir}/test-expert/testability-assessment.md`
- `tdd-designer-report` = `{feature-dir}/tdd-designer/report.md`

Use absolute paths for all subsequent file operations.

> **If `spec` does not exist at `{feature-dir}/spec.md`**: stop and report the missing path — do not continue with a non-existent spec.

## Step 2 — Load context

Read the following files using multi-pass `read_file` calls (advance `startLine` and repeat until the response is shorter than the page size):
1. `spec` — the feature spec
2. `testability-report` — load only if it exists on disk
3. `tdd-designer-report` — load only if it exists on disk
4. `constitution/constitution.md`
5. `constitution/ai-behavior.md`
6. `constitution/coding-standards.md`
7. `constitution/testing-guidelines.md`
8. `constitution/governance.md`
9. `constitution/project-constraints.md`
10. `ai/plugins/spec-flow/templates/quickstart-template.md`

> **If `tdd-designer-report` does not exist**: note its absence and continue with test scope treated as undefined.
> **If `testability-report` does not exist**: note its absence and continue with structural testing guidance treated as incomplete.

## Step 3 — Technical context and constitution gate evaluation

Build the technical context from the loaded spec and any available testability artifacts:
- For each unknown or ambiguous technical detail: insert `[NEEDS CLARIFICATION: <specific question>]` at the exact point of uncertainty in `research.md`.
- Do NOT invent values for unknown fields.
- If `tdd-designer-report` exists, incorporate its testing contract and risk notes into the technical context; treat it as authoritative for test scope.
- If `testability-report` exists, incorporate its structural testing risks into the technical context and later design artifacts.

Evaluate the planned work against the constitution gate categories below using the actual project files:
- `constitution/ai-behavior.md`
- `constitution/coding-standards.md`
- `constitution/testing-guidelines.md`
- `constitution/governance.md`
- `constitution/project-constraints.md`

If any gate is violated: stop with ERROR, report the specific violations, and do not proceed.

## Step 4 — Phase 0: Research

**Prerequisites**: Constitution gate categories pass.

**Skip condition**: If `{feature-dir}/research.md` already exists with zero `[NEEDS CLARIFICATION]` markers, skip this step and proceed to Step 5.

1. **Extract research tasks**: For each `[NEEDS CLARIFICATION]` marker in the technical context → one research task. For each dependency → one best-practices research task. For each integration point → one patterns research task.
2. **Dispatch research agents**: Launch one subagent per research task (or batch closely related tasks). Each task prompt: `Research {unknown} for {feature context}` or `Find best practices for {tech} in {domain}`.
3. **Consolidate findings** into `{feature-dir}/research.md` using this format per decision:

```
## [Decision topic]
**Decision**: [what was chosen]
**Rationale**: [why chosen]
**Alternatives considered**: [what else was evaluated]
```

> **If research agents return conflicting results on a decision**: document all options in `research.md` under that decision and insert `[NEEDS CLARIFICATION: <specific question for user>]` — do not choose arbitrarily.

> **If any `[NEEDS CLARIFICATION]` markers remain in `research.md` after consolidation**: stop, present the unresolved markers to the user, and do not proceed to Phase 1.

**Output**: `{feature-dir}/research.md` with all `[NEEDS CLARIFICATION]` markers resolved.

## Step 5 — Phase 1: Data model

**Prerequisites**: `{feature-dir}/research.md` complete with zero unresolved markers.

Extract entities from the feature spec and `research.md`. Write `{feature-dir}/data-model.md` containing:
- Entity name, fields, and field types
- Relationships between entities
- Validation rules derived from requirements
- State transitions where applicable

> **If an entity's field types or relationships cannot be determined from the spec and research**: insert `[NEEDS CLARIFICATION: <question>]` in `data-model.md` at the ambiguous point, stop, and do not proceed to contracts.

## Step 6 — Phase 1: API contracts

**Prerequisites**: `{feature-dir}/data-model.md` complete with zero unresolved markers.

For each user action in the feature spec → define one endpoint. Use standard REST or GraphQL patterns as appropriate. Write schema files to `{feature-dir}/contracts/` (OpenAPI YAML or GraphQL SDL).

## Step 7 — Phase 1: Quickstart

1. Use `ai/plugins/spec-flow/templates/quickstart-template.md` as the scaffold.
2. Write `{feature-dir}/quickstart.md` — a developer onboarding guide covering setup steps, key endpoints, example requests, and manual verification instructions for the feature.
3. Re-evaluate the constitution gate categories using the completed design artifacts. If new violations are found: ERROR, report them, and do not mark the skill complete.

## Step 8 — Report

Present the completion report (see `<output_format>`). Include **BRANCH** name, `feature-dir`, constitution gate categories checked, and the list of all generated or updated artifacts.

The skill is complete when `{feature-dir}/research.md`, `{feature-dir}/data-model.md`, at least one `{feature-dir}/contracts/` file, and `{feature-dir}/quickstart.md` exist on disk, and the constitution gate categories pass.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **read_file**: Load `spec`, `testability-report`, `tdd-designer-report`, constitution files, `quickstart-template.md`, and `research.md`. Use multi-pass reads — advance `startLine` and repeat until the response is shorter than the page size.
- **vscode_askQuestions**: Collect `feature-dir` from the user in Step 1 when Branch Detection cannot resolve automatically.
- **create_file**: Write `research.md`, `data-model.md`, contract schema files, and `quickstart.md` to `feature-dir`. Only after prerequisites in each phase step are confirmed.
- **runSubagent**: Dispatch research agents in Phase 0 (Step 4). Batch closely related tasks into one subagent call.
- Do NOT use tools not listed here unless explicitly escalating.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Completion report**:

```
Branch: <branch-name>
feature-dir: <absolute-path>
Artifacts:
  - {feature-dir}/research.md        [created | updated | skipped]
  - {feature-dir}/data-model.md      [created | updated | skipped]
  - {feature-dir}/contracts/<file>   [created | updated | skipped]
  - {feature-dir}/quickstart.md      [created | updated | skipped]
Constitution gate categories checked:
  - ai-behavior.md
  - coding-standards.md
  - testing-guidelines.md
  - governance.md
  - project-constraints.md
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
Input: Feature spec exists at `{feature-dir}/spec.md`; `tdd-designer/report.md` exists; no prior planning artifacts on disk.
Expected behavior: Resolves `feature-dir`, loads the spec, optional testability artifacts, constitution files, and quickstart template. Constitution gate categories pass. Dispatches two research agents; consolidates findings into research.md with all markers resolved. Generates data-model.md (four entities), writes contracts/create-item.yaml and contracts/list-items.yaml, writes quickstart.md from the template scaffold, re-evaluates constitution gate categories (passes), and reports completion with artifact list and branch name.
</example>

<example>
Input: Feature spec exists; no `tdd-designer/report.md`; `{feature-dir}/research.md` already exists with zero unresolved markers.
Expected behavior: Notes the missing TDD artifact, treats test scope as undefined, and continues. Detects research.md is complete — skips Phase 0. Proceeds to Phase 1: generates data-model.md, contracts/, and quickstart.md. Reports completion.
</example>

<example type="counter">
Input: Phase 0 produces research.md but two `[NEEDS CLARIFICATION]` markers remain because research agents returned conflicting options.
Expected behavior: Skill detects unresolved markers. Reports: "BLOCKED — 2 `[NEEDS CLARIFICATION]` markers remain in research.md. Resolve these before re-running Phase 1." Lists the specific unresolved questions. Does not proceed to Phase 1.
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
