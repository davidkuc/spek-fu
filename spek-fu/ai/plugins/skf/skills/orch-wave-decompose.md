---
id: "orch-wave-decompose"
recommended-tier: "fast-agent"
version: 1.0
description: "Decomposes a task into an ordered wave plan. Reads inline intake context, applies wave organization rules, and returns a structured wave decomposition inline. USE FOR: before orchestration planning — decomposing task scope into sequenced waves with dependencies declared. DO NOT USE FOR: plan authoring, skill assignment, or agent tier selection."
anti-scope: "Does NOT build the formal orchestration plan document, assign skills per task, or select agent tiers."
tags:
  - "planning"
  - "orchestration"
  - "decomposition"
  - "wave"
inputs:
  - "Structured intake context object (required)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Structured wave decomposition"
  - "Execution status: ok or blocked"
dispatch-variant: "compact"
---

# Skill: orch-wave-decompose

**Dispatch variant**: compact  
**Recommended tier**: standard-agent

Decomposes a task into an ordered wave plan. Reads the inline intake context, applies wave organization rules and planning strategies, and returns a structured wave decomposition used as input for the orchestration planning step.

**Scope boundary**: This skill produces the wave decomposition only. It does NOT build the formal orchestration plan document, assign skills per task, or select agent tiers.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER produce anything beyond a wave decomposition document — WHY: producing plan content or skill assignments bypasses the formal planning step and breaks the orchestration contract.
2. NEVER probe the filesystem for additional context beyond the provided intake context — WHY: arbitrary reads introduce unreviewed inputs that corrupt the decomposition baseline.
3. ALWAYS ensure every wave has a clear, single goal; NEVER combine unrelated work in one wave — WHY: mixed-goal waves produce ambiguous verification criteria and undermine wave-level acceptance checking.
4. ALWAYS declare inter-wave dependencies explicitly; NEVER leave dependency ambiguous — WHY: undeclared dependencies create silent ordering assumptions that cause wave execution failures.
5. NEVER invent skill IDs or agent tiers in the decomposition — WHY: those identifiers belong to the planning step; inventing them here corrupts downstream plan construction.
6. ALWAYS return the wave decomposition inline as the canonical output — WHY: downstream orchestration steps now consume structured state directly.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- Done condition: wave decomposition returned inline; each wave has a goal, task list, and dependency declaration.
- If intake context has undeterminable scope → surface ambiguity as a named gap in the wave decomposition rather than blocking.
- Wave count targets: Simple (1–2 waves), Standard (3–4 waves), Complex (4–6 waves).

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

1. Confirm `intake-context` is provided. If absent, return blocked immediately — do NOT probe the filesystem.
2. Use the supplied intake context directly.

## Done conditions

- **ok** is done when the wave decomposition is returned inline, each wave has a goal, a tasks table, and an explicit dependency declaration.
- **blocked** is done when `intake-context` is absent — report blocked status with reason and stop without writing any file.

---

## Step 1 — Identify Actions

Break the work into concrete, independently dispatchable actions.

**An action is**: a single targeted change to one or a small set of related files, producing a verifiable output with a clear acceptance criterion.

**Not an action**: vague tasks ("update documentation") · mixed skill domains · no defined output · unbounded scope.

Apply these task granularity rules:
- **Aggregate when**: same layer + same change type · create + immediate wiring · context cost > work cost
- **Separate when**: cross-layer · different context · prerequisite gate
- **Smell check**: >1 task per file in same domain or single-line task → merge candidate

---

## Step 2 — Select Planning Strategy

Based on the task description from intake context:

| Request type | Strategy |
|---|---|
| New feature/entity | **Feature-Slice**: all layers per feature before next; independent features may parallelize |
| Refactor/migrate/replace | **Horizontal**: one layer at a time; compile-check-only allowed when shared contract changes |
| Mixed | **Split**: Feature-Slice for new, Horizontal for refactor, separate named phases |

Apply the selected strategy to the action list.

---

## Step 3 — Organize into Waves

Group actions into execution waves.

**Principles**:
- Each wave must be independently verifiable
- Order: dependencies first, independent work parallel within wave, verification last
- Never co-locate tasks with shared target files in the same parallel slot
- Wave count targets: Simple (1–2 waves), Standard (3–4 waves), Complex (4–6 waves)

**Wave template**:
```
Wave {N} — {goal}
  [parallel] Step N.1: {target file(s)} → {action} → {output}
  [parallel] Step N.2: {target file(s)} → {action} → {output}
  Dependencies: {explicit inter-wave dependencies or "none"}
```

**Build Checkpoints**: After any wave touching compiled/executable code, mark a build-verification step. Feature-slice always produces clean build per phase. Horizontal may use compile-check-only for shared-contract + immediate implementation.

---

## Step 4 — Apply Dispatch Sizing

Review each wave for batch size compliance:
- Medium files (150–300 lines): ~4 files/dispatch
- Large (>400 lines): 1–2 files/dispatch
- Parallel dispatch safe when tasks target distinct files/directories
- Serialize tasks targeting the same file; combine into single dispatch

Adjust wave task assignments if any task exceeds sizing limits.

---

## Step 5 — Return wave decomposition

**Document format**:
```markdown
# Wave Decomposition

**Generated from**: inline intake-context
**Complexity tier**: {tier}
**Planning strategy**: {strategy}
**Total waves**: {N}

## Wave 1 — {goal}

### Tasks
| Step | Target | Action | Output | Notes |
|------|--------|--------|--------|-------|
| 1.1 | {file(s)} | {action} | {output path/description} | [parallel] or [sequential] |

### Dependencies
Inter-wave dependencies: {explicit list or "none"}

---

## Wave {N} — {goal}
[same structure]

---

## Verification Checklist
- [ ] Each wave has exactly one goal
- [ ] All inter-wave dependencies declared
- [ ] No file appears in multiple parallel slots within same wave
- [ ] Dispatch sizing applied
```

The skill is complete when the structured wave decomposition has been returned inline, all waves have a goal, a tasks table, and an explicit dependency declaration, and the verification checklist is present.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- No state-writing or search tools are permitted for this skill.
- Prohibited: All search tools (`file_search`, `grep_search`, `semantic_search`), edit tools, execution tools.
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|---|---|
| status | `ok` \| `blocked` |
| skill_id | `orch-wave-decompose` |
| wave | `{N}` |
| step | `{M}` |
| output_path | `none` |
| summary | one-line description |

```
## Wave Decomposition Complete

Status: ok | blocked
Output: inline wave decomposition
Waves: {N}
Strategy: {strategy}
Complexity: {tier}
```

**On BLOCKED** (missing input or unreadable context):
```
## Wave Decomposition — BLOCKED

Status: blocked
Reason: {description — e.g., "intake-context not provided" or "intake-context malformed"}
Next action: {what the caller should do to unblock}
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: intake-context with request "Add OAuth login to the API", complexity tier "Standard — single feature, 3 layers affected (data model, service, endpoint)".
Expected behavior: Returns inline wave decomposition using Feature-Slice strategy with 3 waves: Wave 1 — data layer (model + migration), Wave 2 — service layer (auth logic), Wave 3 — API layer (endpoint + verification). Build checkpoint marked after Wave 2. All inter-wave dependencies declared explicitly. Dispatch sizing applied per layer file count.
</example>

<example>
Input: intake-context.md with request "Refactor payment module and add subscription service", complexity tier "Complex — cross-module refactor plus new feature, 6+ files affected".
Expected behavior: Returns inline wave decomposition using Mixed (Split) strategy: Horizontal phase for the payment refactor (one layer at a time, 3 waves), Feature-Slice phase for the subscription service (all layers per feature, 2 waves). 5 waves total. Build checkpoint marked after the refactor phase. All inter-wave dependencies declared. Dispatch sizing reduces large-file waves to 1–2 files per dispatch step.
</example>

<example type="counter">
Input: `intake-context` is absent (not provided by caller).
Expected behavior: Returns blocked immediately without probing the filesystem. Reports: "Status: blocked. Reason: intake-context not provided. Next action: Supply the structured intake context." No file is written.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **NEVER produce plan content, skill assignments, or agent tier selections** — this skill produces a wave decomposition document only. WHY: those outputs belong to the planning step that consumes the decomposition.
- **NEVER read files beyond the provided intake context** — WHY: arbitrary reads corrupt the decomposition baseline with unreviewed inputs.
- **ALWAYS return the wave decomposition inline** — WHY: downstream orchestration steps now depend on the structured handoff object rather than a temp path.
- **Always verify** output against `<constraints>` before reporting completion.

</reminders>
