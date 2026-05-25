---
id: "orch-orchestration-plan"
recommended-tier: "standard-agent"
version: 1.0
description: "Builds a structured orchestration plan using intake context (request scope, constraints, complexity tier) and pre-decomposed wave inputs. Produces a formal inline plan aligned with user intent and scope. Surfaces gaps explicitly."
anti-scope: "It does NOT execute any skill, ask the user questions, or read arbitrary workspace files. It operates only on caller-provided structured inputs plus optional spill fallback when the inline budget is exceeded."
tags:
  - "utility"
  - "orchestration"
  - "planning"
  - "wave"
inputs:
  - "intake-context: structured intake context (output of orch-intake-context; provides user request, scope, constraints, work-type classification, and complexity-tier) — required"
  - "wave-decomp: structured wave decomposition (output of orch-wave-decompose) — required"
  - "skill-inventory: structured skill inventory (output of orch-skill-resolve) — required"
  - "pattern-select-result: structured result from orch-pattern-select; provides required and advisory pattern IDs applicable to this orchestration — optional"
  - "governance: include | skip (optional; defaults to include if omitted)"
  - "planning-strategy-hint: optional hint about which planning strategy to use (optional)"
  - "Supplementary context such as iteration folder, constraints, and prior decisions (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Inline plan document with wave assignments, decisions, reasoning, and gaps"
  - "Optional spill path under spek-fu/reports/orchestration-spill/ when the compact inline budget is exceeded"
  - "The plan document uses the pre-decomposed waves from wave-decomp as its wave structure."
dispatch-variant: "compact"
---

# Skill: orch-orchestration-plan

<!-- SECTION 1: Identity (primacy position) -->
Builds a structured orchestration plan from intake context and pre-decomposed wave inputs. Uses intake context (user request, scope, constraints, work-type classification, complexity tier) to frame planning decisions. Produces a formal plan document aligned with user intent. Surfaces gaps explicitly.

**Scope boundary**: This skill produces a plan document only. It does NOT execute any skill or ask the user questions. Planning context (user request, scope, constraints, work-type, complexity tier), wave structure, and skill inventory must be provided by the caller as structured inputs.

**Agent tier dispatch**: Dispatch this skill using the tier that matches the `complexity-tier` input:
- `Complex` → `standard-agent`
- `Standard` → `standard-agent`
- `Simple` → `fast-agent`

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Operate ONLY on the caller-provided structured inputs `intake-context`, `wave-decomp`, `skill-inventory`, and `pattern-select-result` (if provided); all other context must be provided by the caller. WHY: this skill uses those structured inputs as the authoritative planning baseline. It does not perform discovery or load arbitrary workspace files.
2. Produce planning output only; execution remains the orchestrator's responsibility after plan approval. WHY: mixing planning and execution collapses the approval boundary.
3. Always surface unresolved inputs even when no gaps are found elsewhere. WHY: hidden gaps cause mid-execution failures.
4. Treat governance follow-on work as mandatory per `runbook-plan.md` unless the caller explicitly passes `governance: skip`. When skipped, record this decision in Gaps / Risks. WHY: governance actions should be explicit and caller-controlled rather than injected by convention.
5. When the request is ambiguous, assemble a best-effort plan and list ambiguities under Gaps / Risks — do not ask the user. WHY: clarification is the orchestrator's responsibility.
6. Do NOT substitute governance completeness checks for skill metadata resolution. Metadata lookup (skill paths and agent tiers) and governance coverage checks are different operations; using one as a fallback for the other produces incorrect planning output. WHY: this misuse pattern caused a Phase A implementation failure (B-3) and must be explicitly prohibited to prevent recurrence.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — produce a plan, nothing more.
- Plan from provided context only. If a skill, flow, or resource is mentioned but not in the provided context, surface it as a gap — do not look it up.
- Record reasoning and decisions for each planning choice so they are visible in the output.

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Confirm `intake-context`, `wave-decomp`, and `skill-inventory` inputs are present before proceeding.

> **If any required input is absent**: stop immediately; return `{"status": "blocked", "reason": "{field} input missing", "skill": "orch-orchestration-plan"}` — do not produce a partial plan.

- Use the supplied intake context, wave decomposition, and skill inventory directly.
- If `pattern-select-result` is provided:
  - Extract `required` pattern IDs and `advisory` pattern IDs.
  - If the payload is malformed, record as a gap but do not block planning.
- If required intake context fields are missing (complexity-tier, request, scope), return blocked status with reason: "required field missing from intake-context".
- Record which optional planning inputs are absent so the missing context is surfaced later under Gaps / Risks.
- Decide whether governance follow-on work is explicitly required by the `governance` input parameter (defaults to include if omitted).

## Done conditions

- **inline plan** is done when the plan includes the required sections for its complexity tier, every referenced `skill-id` has passed Step 5a validation, and all unresolved inputs are surfaced under `Gaps / Risks`.
- **spill fallback** is done when an optional spill artifact has been written under `spek-fu/reports/orchestration-spill/` because the compact inline budget could not preserve required fidelity.

## Step 0 — Load and Leverage Intake Context for Planning

1. Extract all planning-relevant fields from the intake context: user request, scope, constraints, work-type classification, and complexity-tier.
2. Validate that `complexity-tier` is one of: `Simple`, `Standard`, `Complex`. If invalid or missing, return blocked status.
3. Use the intake context to frame planning decisions throughout the process:
   - **Request**: Understand what the user is asking for; inform scope validation in Step 1b.
   - **Scope**: Clarify what this orchestration addresses; inform concern enumeration in Step 1b.
   - **Constraints**: Apply any constraints (timing, dependencies, tooling) to task sequencing in Step 3.
   - **Work-type**: Inform strategy selection (Feature-Slice vs. Horizontal vs. Split) in Task Division Protocol.
   - **Complexity-tier**: Use to select output template in Step 5.
4. Do NOT recompute complexity from task scope — use only the tier provided in the intake context.

| Complexity | Wave count | Template |
|------------|------------|----------|
| **Simple** | 1–2 waves max | Minimal format — TL;DR + wave(s) + verification only. Omit Scope Summary table (use "Single concern — see TL;DR."), Further Considerations, and Gaps/Risks (omit if empty). Omit pre-QA and post-QA waves. |
| **Standard** | 3–4 waves | Standard template — implementation waves, verification, Governance Sync. Further Considerations is optional (include only if non-empty). |
| **Complex** | 4–5 waves | Full template — pre-QA wave, multi-implementation waves, post-QA wave, Governance Sync. All sections mandatory. |

Carry the classification label (`Simple`, `Standard`, or `Complex`) into Step 5 output as the `**Complexity**` field.

## Step 1 — Load Pre-Decomposed Waves and Build Skill Sequence

The wave structure is provided by the caller via `wave-decomp`. Use the scope and constraints from the intake context to validate and frame the wave assignments. Do NOT re-derive wave assignments or re-organize tasks into waves.

1. Use `wave-decomp`. This input contains the pre-decomposed wave and task assignments.
2. Use `skill-inventory`. Use only skills present in the inventory. Flag any needed skill not found there as a gap.
3. Map each task in the wave decomposition to its corresponding skill from the inventory.
4. Chain skills so required inputs are satisfied by prior outputs or provided context.
5. Apply skill minimization: remove any skill not contributing to a required output.
6. For each skill, derive its path using the convention `spek-fu/ai/plugins/skf/skills/{skill-id}.md`. **Always derive the agent tier from the `tier` field in `spek-fu/ai/plugins/skf/skills/skills-index.json`. Do not apply prefix-based fallback tier rules.**

Apply the Task Division Protocol below when building the plan from the wave assignments.

## Task Division Protocol

When building the plan from `wave-decompose.md`, apply these rules:

**Planning Strategies**:
- New feature/entity → **Feature-Slice**: all layers per feature before next; independent features may parallelize
- Refactor/migrate/replace → **Horizontal**: one layer at a time; compile-check-only allowed for shared contracts
- Mixed → **Split**: Feature-Slice for new, Horizontal for refactor, separate named phases

If `planning-strategy-hint` is provided, use it to select the strategy; otherwise derive the strategy from the work-type classification in the intake context and the nature of the tasks in `wave-decompose.md`.

**Build Checkpoints**:
After every phase touching compiled code, append a build verification step. Feature-slice always produces clean build. Horizontal may use compile-check-only for shared-contract phases.

**Task Granularity**:
- Aggregate when: same layer + same change type · create + immediate wiring · context cost > work cost
- Separate when: cross-layer · different context · prerequisite gate
- Smell check: >1 task per file or single-line task → merge candidate

**Dispatch Sizing**:
- Medium files (150–300 lines): ~4 files/dispatch
- Large (>400 lines): 1–2 files/dispatch
- Include related changes; don't defer to cleanup
- Extract shared >10-line blocks to knowledge files
- Splitting > retrying oversized batches

## Step 1b — Generate TL;DR and Scope Summary
1. **TL;DR**: Write a 1–2 sentence summary of what this orchestration accomplishes and the primary motivation. Derive from the user request and scope in the intake context.
2. **Scope Summary table**: Enumerate the distinct concerns this orchestration addresses. Use the scope and constraints from the intake context to identify distinct concerns. For each:
   - **ID**: C1, C2, C3...
   - **Concern**: One-line description of the problem or need
   - **Source**: Where it originates (e.g., user request, retrospective, governance gap, SSOT violation)
   - **Category**: Type of concern (e.g., Process, SSOT, Tooling, Knowledge, Cleanup, Logic)
3. If the orchestration addresses only a single concern, note: *"Single concern — see TL;DR."* instead of a table.

## Step 2 — Add Optional Governance Follow-On Work

After assembling the skill sequence, add governance or documentation follow-on work only when explicitly required by the caller.

1. **Check governance parameter**:
  - If `governance: skip` was passed by the caller, do not add governance-only follow-on work and record this decision in Gaps / Risks.
  - If `governance: include` was passed (or omitted, defaulting to include), add governance follow-on work as specified in the runbook.
  - Governance work is mandatory per `runbook-plan.md` Step 3 unless explicitly skipped.

2. **Append** any required follow-on skills to a final `Governance / Follow-On` wave.

3. **Deduplication**: If a follow-on skill already appears in the sequence, do not duplicate it. Note it as "already included at Step {N}."

4. **Wire inputs**: Follow-on skills receive their inputs from the outputs of all prior waves.

## Step 3 — Dependency Analysis and Wave Assignment

For each step in the sequence (including any optional follow-on skills from Step 2), classify by input dependency. Apply any timing or sequencing constraints from the intake context to inform wave assignment.

- **Wave 1**: all required inputs come from provided context alone; no inter-step dependencies.
- **Wave N**: all required inputs satisfied by completion of Wave N-1.
- **Sequential**: requires the specific output of a prior step — assign to the earliest wave satisfying all its inputs.

Optional governance follow-on skills: assign them to the final wave and label it `Governance / Follow-On`.

> **If a dependency conflict is detected** (a step requires input from a later-assigned wave): flag in Gaps / Risks as `⚠ wave conflict: step {N} depends on step {M} — wave assignment inconsistent` — list the conflict explicitly; do not silently reorder.

## Step 4 — Identify Gaps, Verification, and Further Considerations

**4.1 — Gaps / Risks**: Flag:
1. Any required skill input with no declared source (provided context, prior step output, or workspace convention).
2. Any skill marked "unverified" because `skill-inventory` was not provided.
3. Any skill capability limitation relevant to the request.
4. If orchestration is not read-only and any mandatory governance skill could not be included or verified, flag it.
5. If `governance: skip` was passed as a parameter, document that governance wave is omitted.
6. If `pattern-select-result` was provided but is malformed or incomplete, flag: `⚠ pattern-select-result unavailable — patterns not included in plan`.

List all under `Gaps / Risks`. Write *None identified.* if empty (or omit the section entirely for **Simple** tier).

**4.2 — Verification checklist**: For each wave output identified in Step 3, write one numbered verifiable claim — a specific state that can be confirmed by reading a file or running a search. Use the format: `**{Claim title}**: {How to verify}`. Do NOT write task descriptions; write state claims.

**4.3 — Further Considerations**: Identify any concerns mentioned in the intake context or user request that are explicitly out of scope, deferred, or flagged as follow-up work. List as numbered items with title and rationale. Write *None.* if empty (or omit for **Simple** tier; optional for **Standard** tier).

## Step 5 — Format Plan
Format the plan following the output structure defined in Section 6 (`<output_format>`). Section requirements vary by complexity tier (from Step 0):

1. **Header block**: User request and scope (from intake context), Matched flow, Confidence, Complexity, and Applicable Patterns (if pattern data was loaded). *All tiers.*
2. **TL;DR**: From Step 1b. *All tiers.*
3. **Scope Summary**: From Step 1b. — *Simple*: omit table; write "Single concern — see TL;DR." instead. — *Standard/Complex*: use table format unless single-concern.
4. **Wave sections**: One `### Wave N: {description}` per wave from Step 3. *All tiers.*
   - Each step: `**N.M {Skill Name}** (\`{skill-id}\`)` header, then `**Skill path**` and `**Agent tier**` lines, brief description, then Input / Output / Target files / Rationale sub-bullets.
   - Parallel steps: `*[parallel with N.M]*` annotation.
   - **Relevant files** block at end of each wave: list all files that wave's steps modify.
5. **Wave Verification Checkpoint** between each wave: bulleted checklist of expected outputs to confirm before the next wave. *All tiers.*
6. **Final Wave: Governance Sync**: mandatory skills from Step 2 (or labeled "skippable" with reason). *All tiers (unless skipped).*
7. **Verification**: From Step 4 — numbered, verifiable state claims. *All tiers.*
8. **Decisions**, **Reasoning**: *All tiers.* — **Further Considerations**: *Simple*: omit if empty. *Standard*: optional, include only if non-empty. *Complex*: mandatory. — **Gaps / Risks**: *Simple*: omit if empty. *Standard/Complex*: mandatory (write *None identified.* if empty).
9. **Relevant Files (Complete)**: table listing every file touched across all waves. *All tiers.*

Return the plan inline as the canonical output. If the plan cannot stay within the compact output budget after removing nonessential wording, an optional spill artifact under `spek-fu/reports/orchestration-spill/` is allowed.

> **Manual wave structure validation**: After writing the plan, review the wave structure manually: confirm wave headings are sequential (Wave 1, 2, 3...), each wave contains at least one step, no duplicate wave numbers exist, and a TL;DR/Summary section is present.

## Step 5a — Validate Skill IDs

Before returning the plan, cross-check all `skill-id` values present in the plan:

1. Extract every `skill-id` appearing in skill step headers (format: `` `{skill-id}` ``).
2. If `skill-registry` was provided: validate each ID against it.
   - **Auto-correctable** (clear typo, nearest-match ≥90% similarity with a single obvious candidate): correct silently; note the correction in Gaps / Risks.
   - **Unresolvable** (no clear nearest match, or multiple candidates): flag in Gaps / Risks as `⚠ unresolvable skill-id: {id} — manual resolution required`; do not silently substitute.

> **If skill-id validation cannot be performed** (skill-registry provided but unreadable, or conflicting registry entries): flag all affected IDs as `⚠ validation incomplete — registry issue` and proceed with the plan rather than blocking.
3. If `skill-registry` was not provided: validate each ID against the prefix convention. Any ID whose group prefix is not one of `{meta, gov, qa, spec, plan, impl, util}` should be flagged as `⚠ unverified skill-id: {id} — non-standard prefix`.
4. If all IDs pass validation, note `All skill-ids validated.` in Gaps / Risks (or omit if no other gaps).

> **Manual validation alternative**: If automated validation is not available, after writing the plan, manually verify each `skill-id:` reference by checking it matches an entry in `spek-fu/ai/plugins/skf/skills/skills-index.json`.

## Step 5b — Output Budget Check

> Markdown structure validation: Before returning, verify the plan document includes required markdown sections. Required sections: `# Orchestration Plan:` title, `## TL;DR`, `## Scope Summary`, numbered `### Wave` sections, `### Verification`, `### Decisions`, and `### Reasoning`. If any required section is missing, surface it as a gap rather than returning an incomplete plan.

Before returning the plan:

1. Compact wording aggressively while preserving meaning.
2. Remove redundant explanatory prose that duplicates structured fields.
3. If the plan still exceeds the compact output budget and fidelity would be lost, write a spill artifact under `spek-fu/reports/orchestration-spill/` and return the spill path alongside the compact summary.

The skill is complete when the plan is produced and returned to the caller.

## Manual Planning Checks

Perform the deterministic planning checks directly from the provided context.

| Step | Method | Guidance |
|------|--------|----------|
| Step 1 item 6: Derive skill paths and agent tiers | Manual resolution | Derive each skill path with the documented convention `spek-fu/ai/plugins/skf/skills/{skill-id}.md`, then read the provided skill registry or skills index excerpt to confirm the agent tier. |
| Step 2: Validate governance follow-on work | Manual review | Check whether the caller explicitly requested governance or documentation follow-on work and whether those steps are already present in the sequence before adding them. |
| Step 3: Detect wave conflicts | Manual comparison | Inspect the planned target files and prerequisites for each step in the same wave. Flag conflicts when two parallel steps modify the same file or require mutually exclusive preconditions. |

## Summary: Intake Context Leverage

Throughout planning (Steps 0–5), the intake context is leveraged to:
- **Frame scope**: User request and scope inform TL;DR and Concern Summary.
- **Classify complexity**: Complexity tier determines output template.
- **Inform strategy**: Work-type classification guides Feature-Slice vs. Horizontal strategy selection.
- **Apply constraints**: Timing and dependency constraints from intake context inform wave sequencing.
- **Validate assumptions**: Scope and constraints validate wave decomposition against user intent.

The plan produced is aligned with the user's request and scope as captured in the intake context.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **create_file**: Use only for optional spill fallback under `spek-fu/reports/orchestration-spill/` when the compact output budget is exceeded.
- Do not use deleted helper scripts in this skill; perform metadata, governance, and wave-conflict checks directly from the caller-provided context.
</tools>

<!-- SECTION 6: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-orchestration-plan` |
| wave | `N` |
| step | `N.M` |
| output_path | `none` or `spek-fu/reports/orchestration-spill/...` |
| summary | one-line summary of what was done |

Minimum required sections (in order):

```
# Orchestration Plan: {request summary}

**Complexity**: Simple | Standard | Complex
**Applicable patterns** — Required: [IDs] | Advisory: [IDs]  *(omit if no pattern data)*

## TL;DR
{1–2 sentence summary}

## Scope Summary
{table or "Single concern — see TL;DR."}

### Wave 1: {description}
*Rationale: ...*

**1.1 skill-name** (`group`)
**Skill path**: `spek-fu/ai/plugins/skf/skills/{skill-id}.md`
**Agent tier**: {fast-agent | standard-agent | large-context-agent}
{Brief description.}
- Input: ...
- Output: ...
- Target files: ...
- Rationale: ...

**Relevant files:**
- `path/to/file` — create | modify | delete

### Wave Verification Checkpoint
- [ ] {Output from 1.1 confirmed}

### Final Wave: Governance Sync
**N.1 documentation-sync** [or "skippable — read-only orchestration: {reason}"]
...

### Verification
1. **Claim**: How to verify

### Decisions
### Reasoning
### Further Considerations
### Gaps / Risks

### Relevant Files (Complete)
| File | Change |
|------|--------|
| `path` | create / modify / delete |
```
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: requirements=`Update two README files and regenerate one skills index after a batch rename`, skill-inventory provided, governance omitted.
Expected output: Classifies the task as Standard, assembles a short multi-wave plan, injects the Governance Sync wave, validates each skill-id, and returns a plan with verification checkpoints and relevant files.
</example>

<example>
Input: requirements=`Audit skill quality only`, skill-inventory omitted, governance=`skip` with reason `read-only audit`.
Expected output: Classifies the task as Simple or Standard based on scope, marks planned skills as unverified where appropriate, records the governance skip reason in Gaps / Risks, and returns a read-only plan without execution steps.
</example>

<example type="counter">
Input: requirements missing, only a vague note saying `do the framework stuff`.
Expected behavior: Stops in preflight, reports that `requirements` is missing, and does not invent waves, skills, or files.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- Read ONLY the caller-provided structured planning inputs; NEVER load the runbook Dispatch Contract sections, `orchestration-plan-template.md`, or any other file.
- ALWAYS dispatch this skill using the agent tier matching `complexity-tier`: Complex → `large-context-agent`; Standard → `standard-agent`; Simple → `fast-agent`.
- ALWAYS use `wave-decomp` and `skill-inventory` from the provided inputs before building the plan. Do NOT re-decompose waves from scratch.
- Always include Gaps / Risks when unresolved inputs remain (Simple tier may omit the section only when truly empty).
- Include mandatory governance skills unless the orchestration is purely read-only or `governance: skip` is set; record any skip reason in Gaps / Risks.
- ALWAYS classify task complexity in Step 0 — wave count and section set must match the assigned tier.
- ALWAYS generate a TL;DR (all tiers) and Scope Summary (Standard/Complex; Simple: use single-concern note).
- ALWAYS include Verification checklist (Step 4.2) — do not omit even when empty.
- Further Considerations: mandatory for Complex; optional for Standard (omit if empty); omit for Simple if empty.
- ALWAYS run Step 5a skill-id validation before returning the plan.
- ALWAYS perform the Step 5b output budget check before returning the plan.
</reminders>
