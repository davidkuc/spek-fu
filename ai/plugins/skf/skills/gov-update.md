---
id: "gov-update"
recommended-tier: "fast-agent"
version: 1.0
description: "Applies governance file updates based on changed files or an orchestration plan. Reasons about which governance files need updating, proposes each change for per-change user approval, applies approved changes, then always runs sync-index-files.py followed by sync-index-files.py --check. USE FOR: keeping constitution, project docs, and AI framework files aligned with implemented changes."
anti-scope: "Does NOT perform analysis, modify source code, or touch iteration in-progress files."
tags:
  - "governance"
  - "constitution"
  - "approval"
  - "framework"
  - "index"
  - "sync"
inputs:
  - "Changed files list, orchestration plan, or direct user-described changes with context (required)"
  - "env: runtime environment — 'devcontainer' or 'host' (required)"
outputs:
  - "Count of changes applied/skipped"
  - "Governance update summary"
  - "Index sync and validation script output"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: gov-update

Reads a list of changed files or an orchestration plan, reasons about which governance files need updating, proposes each change for approval, applies approved changes, and always finishes by running `sync-index-files.py` followed by `sync-index-files.py --check`.

**Permitted write targets**: `constitution/`, `project/`, `ai/`, `.github/`. No writes outside these folders, ever.

<constraints>
1. Require explicit `vscode_askQuestions` approval before writing any file. Governance files are authoritative — unapproved writes corrupt the canonical record.
2. Include current text, proposed text, and rationale in every proposal. Users need full context to decide.
3. Apply changes using file-writing tools only — no analysis, no discovery.
4. Always run `sync-index-files.py` as the final step, regardless of what changed. Never sync indexes manually.
5. Read every target file before editing it.
</constraints>

<behavioral_anchors>
- Before any write, confirm the target path is inside a permitted folder.
- Do not batch unrelated changes into a single approval prompt.
- If the user skips a change, record it and continue — do not retry or argue.
- State detection: before proposing, check whether the change is already applied. Skip already-applied changes silently.

## Environment Preflight
`devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully and apply all rules before Step 1.
`host`: no additional action required.
</behavioral_anchors>

<workflow>

## Done condition
All approved changes applied, `sync-index-files.py` has run successfully, and `sync-index-files.py --check` reports no drift.

---

## Step 1: Assess

Read the input (changed files, orchestration plan, or user description). Reason about which governance files require updates:

- `constitution/` — behavioral rules, coding standards, or principles changed
- `project/` — requirements, specs or ADR content changed
- `ai/` and `.github/` — skills, agents, prompts, runbooks, knowledge, or patterns changed

Read the relevant current governance files to understand what needs to change.

> If no actionable changes are identified, inform the user and stop before running the sync script.

## Step 2: Propose

For each identified change, present:

- **Target**: file path
- **Current**: existing text (or "new file")
- **Proposed**: replacement or addition
- **Rationale**: why the change is needed

Present all proposals as a summary before soliciting any approvals.

## Step 3: Approve

Call `vscode_askQuestions` per change using this payload template:

```json
{
  "header": "governance_change_approval",
  "question": "Apply this change to {filename}?",
  "options": [
    { "label": "Apply — proceed with change", "recommended": true },
    { "label": "Skip — do not apply" },
    { "label": "Edit first — modify before applying" }
  ],
  "allowFreeformInput": true
}
```

For each selection:
- **Apply** → proceed with writing the change
- **Skip** → record and continue to next change
- **Edit first** → incorporate modifications from freeform field before writing

Use `multiSelect: true` when there are more than 5 changes.

## Step 4: Apply

For each approved change, apply it using `replace_string_in_file`, `create_file`, or `multi_replace_string_in_file`.

## Step 5: Run index sync and drift check

Run from the workspace root:

```
python3 ai/scripts/python/sync-index-files.py
```

Then immediately validate the synced result:

```
python3 ai/scripts/python/sync-index-files.py --check
```

Capture and include both script outputs in the summary. If either command exits non-zero, report the error, flag the failure in the summary, and stop — `/gov-update` must not complete successfully while index drift remains.

Always also run `generate-prompt-files.py` to regenerate `.github/prompts/` for gov-* and meta-* skills only (idempotent — safe to run unconditionally):

```
python3 ai/scripts/python/generate-prompt-files.py
```

Capture and include the script output. If the script exits non-zero, report the error and flag `prompt-gen: failed` in the summary.

</workflow>

<tools>
- **read_file**: Load governance files before editing. Always read before writing.
- **replace_string_in_file / create_file / multi_replace_string_in_file**: Use only after user approval.
- **vscode_askQuestions**: Required at every approval gate and to collect missing input.
- **run_in_terminal**: Use to execute `sync-index-files.py` in Step 5.
</tools>

<output_format>
```
## Governance Update Summary

Changes proposed: {n}
Changes applied:  {n}
Changes skipped:  {n}

### Applied
- {file}: {short description}

### Skipped
- {file}: {reason}

### Index Sync
sync:
{script stdout/stderr or error message}
index-sync: {ok | failed}

check:
{script stdout/stderr or error message}
index-check: {ok | failed}
```
</output_format>

<reminders>
- NEVER write outside `constitution/`, `project/`, `ai/`, `.github/`.
- NEVER skip the per-change approval gate.
- NEVER sync indexes manually — always use `sync-index-files.py`.
- ALWAYS run the sync script and the `--check` validation last, even if zero governance changes were applied.
</reminders>
