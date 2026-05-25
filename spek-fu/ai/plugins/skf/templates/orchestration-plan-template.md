---
id: skf-template-orchestration-plan-template
title: "Orchestration Plan Template"
category: iteration
version: 1.0
---

# Orchestration Plan Template

> Use this template when formatting the output of `orch-orchestration-plan`. Replace all `{placeholder}` fields.

---

## Orchestration Plan: {Title}

**Request**: {one-line summary of what the user requested}
**Matched flow**: {workflow name | "Ad-hoc"}
**Confidence**: {≥80% exact | 50–79% partial | <50% none}

---

## TL;DR

{One-to-two sentence summary of what this orchestration accomplishes and why. Example: "Adds 13 new knowledge lessons, removes the deprecated promote-iteration-docs script, and hardens orchestrator constraints against known failure patterns."}

---

## Scope Summary

| ID | Concern | Source | Category |
|----|---------|--------|----------|
| C1 | {Short description of a problem or need this orchestration addresses} | {Origin — e.g., retrospective, governance gap, user request} | {Category — e.g., Process, SSOT, Tooling, Knowledge, Cleanup} |
| C2 | {Concern} | {Source} | {Category} |

> If this is a single-concern orchestration, write: *Single concern — see TL;DR.*

---

### Wave 1: {Wave Description}
*{Rationale — why these steps run together or in this wave}*

**1.1 {Skill Name}** (`{skill-id}`)
**Skill path**: `spek-fu/ai/plugins/skf/skills/{skill-id}.md`
**Agent tier**: {fast-agent | standard-agent | large-context-agent}
{Brief description of what this step does and what it produces.}
- Input: {source of input data}
- Output: {artifact name or state change, including path if applicable}
- Target files: {files this step will read/write — used for conflict detection}
- Rationale: {why this skill was chosen}

**1.2 {Skill Name}** (`{skill-id}`) *[parallel with 1.1]*
**Skill path**: `spek-fu/ai/plugins/skf/skills/{skill-id}.md`
**Agent tier**: {fast-agent | standard-agent | large-context-agent}
{Brief description.}
- Input: {source}
- Output: {artifact}
- Target files: {files this step will read/write — used for conflict detection}
- Rationale: {why}

**Relevant files:**
- `{path/to/file}` — {brief description of the change: create | modify | delete}
- `{path/to/file}` — {description}

---

### Wave Verification Checkpoint
*All Wave 1 outputs must be confirmed before Wave 2 begins.*
- [ ] {Expected output from Step 1.1 exists and is non-empty}
- [ ] {Expected output from Step 1.2 exists and is non-empty}

---

### Wave 2: {Wave Description}
*Depends on: Wave 1 outputs*

**2.1 {Skill Name}** (`{skill-id}`)
**Skill path**: `spek-fu/ai/plugins/skf/skills/{skill-id}.md`
**Agent tier**: {fast-agent | standard-agent | large-context-agent}
{Brief description.}
- Input: {artifact from Step 1.1}
- Output: {artifact}
- Target files: {files this step will read/write — used for conflict detection}
- Rationale: {why}

**Relevant files:**
- `{path/to/file}` — {description}

---

### Wave Verification Checkpoint
*All Wave 2 outputs must be confirmed before Governance Sync begins.*
- [ ] {Expected output from Step 2.1 exists and is non-empty}

---

### Final Wave: Governance Sync
*Depends on: all prior wave outputs. Skip if orchestration is purely read-only — record reason.*

**N.1 gov-update** (`gov`)
- Input: all modified framework files from prior waves
- Output: framework documentation updated and synced
- Rationale: mandatory — keeps framework docs consistent with changes made

**N.2 meta-knowledge-manage** (`meta`)
- Input: orchestration summary, lessons identified during execution
- Output: knowledge-database.md updated with new lessons
- Rationale: mandatory — captures lessons for future orchestrations

---

### Verification

{Numbered list of verifiable state claims — not task descriptions. Each item should describe something that can be confirmed by reading a file or running a grep.}

1. **{Claim}**: {How to verify — e.g., "Read the relevant artifact — confirm Y section exists" or "Grep for Z — expect 0 hits"}
2. **{Claim}**: {How to verify}
3. **{Claim}**: {How to verify}

---

### Decisions

- **{Decision title}**: {Rationale — what alternatives were considered and why this path was chosen}
- **{Decision title}**: {Rationale}

### Reasoning

{2–4 sentences explaining the overall approach: why these skills were selected, why this wave order, how the decomposition satisfies the requirements, and any tradeoffs made.}

### Further Considerations

{Deferred work, future improvements, or follow-up items that are out of scope for this orchestration but worth tracking.}

1. **{Consideration title}**: {What it is and why it was deferred}
2. **{Consideration title}**: {What it is and why it was deferred}

> If no further considerations exist, write: *None.*

### Gaps / Risks

- {Any required input with no declared source}
- {Any skill capability limitation relevant to the request}
- {Any dependency that could block execution}

> If no gaps exist, write: *None identified.*

---

### Relevant Files (Complete)

| File | Change |
|------|--------|
| `{path/to/file}` | {brief description — create / modify / delete} |
| `{path/to/file}` | {description} |
