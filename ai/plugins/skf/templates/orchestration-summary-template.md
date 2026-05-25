---
id: skf-template-orchestration-summary-template
title: "Orchestration Summary Template"
category: iteration
version: 1.0
---

# Orchestration Summary Template

> Use this template when formatting the output of Step 7 in the orchestrator workflow. Replace all `{placeholder}` fields. Write the completed summary to a file at `reports/orchestration-summary-{YYYY-MM-DD-HHmmss}.md`.

---

## Orchestration Summary

Request: {one-line summary of original request}
Workflow: {workflow name or "Ad-hoc"}
Complexity: {Simple | Standard | Complex}
Waves planned: {total waves}
Steps planned: {total}
Steps executed: {count}
Steps skipped: {count}
Steps failed: {count}

### Execution Log

| Wave | Step | Skill | Agent | Status | Output |
|------|------|-------|-------|--------|--------|
| 1 | 1 | {skill-name} | {agent} | ✅ Success | {artifact or state change} |
| 1 | 2 | {skill-name} | {agent} | ✅ Success | {artifact or state change} |
| 2 | 3 | {skill-name} | {agent} | ⏭️ Skipped | {reason} |
| 2 | 4 | {skill-name} | {agent} | ❌ Failed | {error summary} |

---

### Per-Wave Summaries

> One block per wave (copied or condensed from inline `wave-summary` state).

#### Wave 1

Steps dispatched: {count}
Artifacts produced: {list of file paths created or modified}
Outcome: {overall wave result — ok | partial | failed}
Notes: {anything unusual — conflicts serialized, skipped steps, etc.}

#### Wave 2

Steps dispatched: {count}
Artifacts produced: {list of file paths created or modified}
Outcome: {overall wave result — ok | partial | failed}
Notes: {anything unusual}

---

### Manual Intervention Points

> List every point where the orchestrator surfaced a decision to the user via `vscode_askQuestions`. If none, write "None."

| Step | Question shown to user | User decision |
|------|------------------------|---------------|
| {wave_failure_N_M} | {question text} | {chosen option or freeform answer} |

---

### Retry and Recovery Notes

> Document every retry attempt (verification retries and network retries) and how each was resolved.

| Wave | Step | Type | Reason | Resolution |
|------|------|------|--------|------------|
| {N} | {M} | Verification retry | {failure description} | {resolved / escalated to user / skipped} |
| {N} | {M} | Network retry | {transient error type} | {succeeded on retry / escalated} |

---

## Run Telemetry

| Field | Value |
|-------|-------|
| `run_id` | {YYYY-MM-DD-HHmmss} |
| `complexity_tier` | simple \| standard \| complex |
| `total_dispatches` | {integer} |
| `failed_dispatches` | {integer} |
| `retried_waves` | {list of wave numbers, or none} |
| `skills_used` | {comma-separated list of skill IDs} |
| `completion_state` | full \| partial \| failed |

---

### Knowledge Capture

> Populated after knowledge capture completes (closure Step 5). If not yet captured, leave blank.

**Blockers encountered**:
- {category}: {blocker description} → resolved by {resolution}

**Commands run manually** (flag any candidates for automation):
- {command or action} — {automatable? yes/no}

**What to do differently on restart**:
- {insight}

**Steps that took longest and why**:
- {step}: {reason} — potential improvement: {suggestion}
