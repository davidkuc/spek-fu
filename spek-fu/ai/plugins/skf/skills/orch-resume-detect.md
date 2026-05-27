---
id: "orch-resume-detect"
recommended-tier: "fast-agent"
version: 1.0
description: "Reports that resume is disabled under the inline-only orchestration contract. USE FOR: callers that still dispatch resume detection during migration; returning a deterministic no-resume report instead of probing temp state."
anti-scope: "It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions."
tags:
  - "utility"
  - "orchestration"
  - "resume"
  - "workflow-state"
inputs:
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "One-line summary of resume detection result"
dispatch-variant: "compact"
---

# Skill: orch-resume-detect

<!-- SECTION 1: Identity (primacy position) -->
Returns a structured report stating that resume is disabled in the inline-only contract. Always returns a structured markdown report.

**Scope boundary**: This skill reads files only. It does NOT modify any file, create missing artifacts, execute skills, or ask the user questions. Corrective action is the caller's responsibility.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. Keep this skill strictly read-and-report. Never modify any file. WHY: migration callers may still invoke it, but it must not mutate state.
2. Always return a structured report — never block the caller with an error or exception. WHY: the caller depends on a machine-readable result during migration.
3. Do NOT probe any persistence layer. WHY: resume is deliberately disabled until a non-temp persistence model is approved.
4. Recommendation must always instruct the caller to restart from Wave 1 in the current session. WHY: partial or stale persisted state is out of contract.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Before producing any output, verify your report complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — enumerate, read, report, nothing more.
- State plainly that resume is unavailable in the current contract.

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Inputs

| Field | Type | Required | Enum | Description |
|---|---|---|---|---|
| env | string | no | devcontainer \| host | Runtime environment |

## Preflight

- No filesystem preflight is required.

---

## Step 1 — Return no-resume report

Return immediately:

```markdown
## Resume State Report

- **Prior state**: false
- **Last completed wave**: none
- **Wave summaries found**: none
- **Malformed summaries**: none
- **Stale summaries**: none
- **Recommendation**: restart-current-session
- **Reason**: Resume is disabled in the inline-only orchestration contract.
```

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- No filesystem, edit, or execution tools are permitted for this skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `orch-resume-detect` |
| wave | `N` |
| step | `N.M` |
| summary | one-line summary of resume detection result |

```markdown
## Resume State Report

- **Prior state**: true | false
- **Last completed wave**: {N} | none
- **Wave summaries found**: {comma-separated filenames or none}
- **Malformed summaries**: {comma-separated filenames or none}
- **Stale summaries**: {comma-separated "filename (reason)" entries or none}
- **Recommendation**: restart-current-session
```

Rules:
- Recommendation is always `restart-current-session`.
- `Malformed summaries`, `Stale summaries`, and `Wave summaries found` remain present for schema stability and are always `none` in this contract.
</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Invocation: Current inline-only contract.
Agent: Returns: Prior state: false, Last completed wave: none, Wave summaries found: none, Malformed summaries: none, Stale summaries: none, Recommendation: restart-current-session. Does not attempt to read any files or modify anything.
</example>

<example>
Invocation: Caller still dispatches resume detection during migration.
Agent: Returns the same disabled-resume report and directs the caller to restart from Wave 1 in the current session.
</example>

<example type="counter">
Invocation: Caller expects persisted resume behavior.
Agent does NOT: inspect or accept persisted state. Instead, returns the disabled-resume report and instructs the caller to restart in the current session.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>
- NEVER inspect persisted wave state in this contract.
- ALWAYS return `restart-current-session` as the recommendation.
</reminders>
