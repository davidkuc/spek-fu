---
id: skf-runbook-shared
title: "Shared Dispatch, Escalation & Retry Protocols"
version: 1.0
---

# Shared Runbook Protocols

Referenced by all phase runbooks. Re-read the Dispatch Contract at each phase entry.

---

## Dispatch Contract

The orchestrator's only action tools are `runSubagent`, `vscode/askQuestions`, `todo`, `read_file` (allowlisted paths), and `web`. If the orchestrator needs information or needs to mutate state, it MUST construct a dispatch and delegate via `runSubagent`. See the **DELEGATE-OR-STOP** protocol in the agent file.

Every `runSubagent` call is clean-slate — subagents inherit nothing from the orchestrator.

> **Normative reference**: `spek-fu/ai/plugins/skf/templates/dispatch-manifest-template.md` defines the canonical markdown manifest format. `spek-fu/ai/plugins/skf/templates/wave-summary-template.md` defines the canonical wave summary format.

## Dispatch Manifest Templates

The orchestrator builds dispatch manifests from the inline `skill-inventory` returned by `spek-fu/ai/plugins/skf/skills/orch-skill-resolve.md` in Phase 2. No external script is required.

**Variant selection**: `impl-*` and `gov-*` use the **Full** template by default. `orch-*` and `meta-*` use the **Compact** template by default. When in doubt, check the `dispatch-variant` field in the skill inventory entry and follow it.

**How to use**: Copy the appropriate template below. Replace every `<skill-inventory: fieldname>` value by reading the matching field from the skill's entry in the cached inline `skill-inventory`. Replace every `<RUNTIME: ...>` value with the appropriate value from the orchestration plan / wave context.

### Full Manifest (impl-*, gov-*, or any skill marked `full`)

```
## Dispatch Manifest

### Identity
- **Skill**: {skill-id}
- **Function**: {skill description — one sentence}
- **Anti-scope**: {what the skill does NOT do}

### Skill
- **Path**: `spek-fu/ai/plugins/skf/skills/{skill-id}.md`
- **Instruction**: Read this file. It defines your COMPLETE workflow. Follow its Steps sequence exactly.

### Task
{Verbatim task description from the orchestration plan — never paraphrased.}

### Context
- **Phase scope**: {Wave N, Step M — one-sentence wave goal}
- **Affected paths**: {list of relevant file paths}
- **Spec excerpt**: {direct quote or path reference, or "none"}
- **Prior wave output**: {path or compact structured summary of relevant prior outputs, or "none"}
- **Devcontainer guidelines** (include if env=devcontainer): path `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` — apply all devcontainer operational rules.

### Constraints
- {Runtime constraint 1}
- {Runtime constraint 2 — e.g., "Do not modify files not listed under task or context."}
- **Required patterns**: {list of binding PT-IDs, or none}

### Advisory
- **Recommended patterns**: {list of advisory PT-IDs, or none}

### Output Format
{Expected output structure — describe what the subagent should return inline; durable report paths are allowed only for final reports or oversize spill fallback}

### Inputs
{Skill inputs from skill inventory — file paths or inline content}
```

### Compact Manifest (orch-*, meta-*)

```
## Dispatch Manifest

### Skill
- **Path**: `spek-fu/ai/plugins/skf/skills/{skill-id}.md`
- **Instruction**: Read this file. It defines your COMPLETE workflow. Follow its Steps sequence exactly.

### Task
{Verbatim task description — never paraphrased.}

### Context
- **Phase scope**: {Wave N, Step M — one-sentence wave goal}
- **Affected paths**: {list of relevant file paths}
- **Prior wave output**: {path or compact structured summary of relevant prior outputs, or "none"}
- **Devcontainer guidelines** (include if env=devcontainer): path `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` — apply all devcontainer operational rules.

### Constraints
- {Runtime constraint 1}
- {Runtime constraint 2}

### Inputs
{Skill inputs from skill inventory}
```

### Subagent Response Format

Subagents must return a markdown-structured response inline as the primary output.

```
## Dispatch Response

- **Status**: {ok | blocked | fail}
- **Skill**: {skill-id}
- **Wave**: {N}
- **Step**: {N.M}
- **Output path**: {path/to/artifact or none}
- **Summary**: {one-line description — no newlines}
- **State**: {compact structured payload or `none`}
```

**Rules**:
- `Status` is one of: `ok`, `blocked`, `fail`
- `Skill` matches the skill id from frontmatter
- `Wave` and `Step` are taken from the dispatch prompt
- `Output path` is omitted if no durable file artifact was produced
- `Summary` is a single line (no newlines) suitable for inline reporting
- `State` is the canonical orchestration handoff object for downstream phases
- If payload exceeds 20 KB after compaction, first compress wording and remove nonessential prose. If fidelity still cannot fit, spill to `spek-fu/reports/orchestration-spill/{wave}-{step}-{skill-id}-output.{ext}` and return the spill path in `Output path`

### Manifest Variants

| Skill prefix | Variant | Sections |
|---|---|---|
| `impl-*`, `gov-*`, or any skill marked `full` | Full 8-section | Identity → Skill → Task → Context → Constraints → Advisory → Output Format → Inputs |
| `orch-*`, `meta-*` read-mode | Compact 4-section | Skill → Task → Context → Constraints → Inputs |
| `Explore` agent | Natural language | Free-form prompt |

### Resolve-and-Fill Pipeline

The orchestrator builds dispatch manifests from skill metadata in the inline `skill-inventory` using the templates defined in **Dispatch Manifest Templates** above. No external script is required.

1. Select the appropriate template variant based on skill prefix (see Dispatch Manifest Templates above)
2. Fill `{field}` values by reading the matching field from the skill's entry in the inline `skill-inventory`
3. Fill `<RUNTIME: ...>` placeholders with task-specific values from the orchestration plan

### Field Ownership

**Script-filled**: `identity.*`, `skill.path`, `constraints.static`, `output-format`, `preflight`, `tools.*`, `inputs`

**Orchestrator-filled**: `task`, `context.*` (cite paths — never paste file contents), `constraints.runtime`, `constraints.required-patterns`, `advisory.recommended-patterns`

### Hybrid Content Strategy

IDENTITY is injected inline (role anchor). SKILL contains only the file path — the subagent reads the skill file itself. Never paste full skill bodies or file contents into manifests.

| Tier | Agent | Model |
|---|---|---|
| 1 | `fast-agent` | Claude Haiku 4.5 |
| 2 | `standard-agent` | Claude Sonnet 4.6 |
| 3 | `large-context-agent` | GPT-5.4 |

The `skf-general-orchestrator` runs at Tier 2.

> **Tier selection is advisory**: the orchestrator selects the appropriate agent tier for each dispatch based on task complexity, context, and the `recommended-tier` field in the inline `skill-inventory`. No prefix routing table overrides this judgment.

### Anti-Patterns

| Don't | Why |
|---|---|
| Paste full files in CONTEXT | Subagent reads files itself |
| Paraphrase skill descriptions | Use frontmatter verbatim |
| Omit IDENTITY in full manifest | Loses role anchor |
| Omit SKILL section | Causes improvisation |
| Forward orchestrator conversation state | Contaminates clean dispatch |
| Parallel-dispatch conflicting file writers | Race conditions |

---

## Escalation Policy

**Rule**: After retry budget exhausted or structural blocker → escalate via `vscode/askQuestions`. Never invent further approaches, silently skip, or continue past failure.

**Triggers**: retry budget exhausted · hard structural blocker · plan revision limit reached · incoherent wave output · scope unresolvable after bounded clarification.

**Escalation question template**:

```json
{
  "header": "orchestration_escalation",
  "question": "Escalation required at {phase} Phase, Step {step}. Please choose an option:",
  "options": [
    { "label": "Retry with different approach" },
    { "label": "Skip this step and continue" },
    { "label": "Abort — preserve completed work" }
  ],
  "allowFreeformInput": true
}
```

**Escalation details presented to user**:
- **Phase**: {Intake | Planning | Execution | Closure}
- **Step**: {step number and name}
- **Reason**: {specific factual failure}
- **Attempts made**: {N} (budget: {configured cap})
- **Recovery options**: A. {specific recovery action} · B. {alternative approach} · C. Abort — preserve work completed so far

**After escalation**: Do not auto-select, retry, or advance until user responds.

---

## Bounded Retry Policy

**Rule**: Capped at `maxWaveRetries` / `maxSubagentRetries` from `config.json` (default: 1 each). Each retry MUST use a different approach AND state why the previous attempt failed.

**Protocol**: State failure reason → state what's different → execute if under cap → else escalate.

**Scope**: Wave retry (full re-dispatch after QA fail) · subagent retry (single task) · tool-call retry (transient network only — functional failures escalate immediately).
