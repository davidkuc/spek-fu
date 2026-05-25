---
id: "spec-feature-draft"
recommended-tier: "standard-agent"
version: 1.0
description: "Generates a feature specification file from a natural language feature description, creating a numbered git branch and populating all required spec sections. USE FOR: drafting a new feature spec from a user description, creating spec branches, producing specification artifacts ready for planning. DO NOT USE FOR: planning implementation tasks, executing clarification sessions on existing specs, applying code changes, or running quality validation."
anti-scope: "Does not produce implementation plans, run clarification sessions on existing specs, or apply any code changes. For post-spec clarification, use spec-clarification."
tags:
  - "specification"
  - "feature"
  - "requirements"
inputs:
  - "Feature description — natural language description of the feature to specify (required)"
  - "config-path: workspace-relative path to the config file — defaults to spek-fu/ai/plugins/spec-flow/skills/config.json (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Spec file written to `spec-file` path inside the numbered feature branch directory"
  - "Execution status, branch name, and spec file path"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: spec-feature-draft

<!-- SECTION 1: Identity (primacy position) -->
Generates a feature specification from a natural language description. Creates a numbered git branch, populates all required spec sections, and resolves ambiguities before reporting completion.

**Scope boundary**: Creates feature specs only. Does NOT produce implementation plans, execute clarification sessions, apply code changes, or validate completed specs.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER begin writing the spec before the git branch and `spec-file` path have been confirmed from the script output — WHY: the script determines the canonical branch name and spec path; writing before this produces orphaned content.
2. NEVER run the create-new-feature script more than once per feature invocation — WHY: duplicate runs create duplicate branches and corrupt the numbering sequence.
3. ALWAYS cap `[NEEDS CLARIFICATION]` markers at `maxNeedsClariMarkers` (from config, default 10) — WHY: more than the configured limit signals an underspecified input, not a spec authoring problem; make informed guesses for lower-priority gaps.
4. NEVER include implementation details (languages, frameworks, APIs, database names) in the spec body — WHY: specs describe user value and business needs; implementation details belong in technical planning artifacts.
5. When the feature description is empty, stop and request it via `vscode_askQuestions` before proceeding — WHY: no meaningful spec can be generated from an empty description.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `spek-fu/ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Shared Knowledge
- Apply `spek-fu/ai/plugins/spec-flow/knowledge/skill-meta-rules.md`, `paginated-read.md`, and `needs-clarification-protocol.md` before acting.

## Operational Anchors
- Call `vscode_askQuestions` for empty or ambiguous descriptions instead of guessing.
- Detect run state: if spec or branch exists, resume from current content; otherwise proceed as new.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `config-path` from inputs, defaulting to `spek-fu/ai/plugins/spec-flow/skills/config.json` if absent. Read the config file and extract `spec-feature-draft.maxNeedsClariMarkers` (default: `10`). Apply this value wherever this skill references `maxNeedsClariMarkers`.

> **If the config file cannot be read or the `spec-feature-draft` key is absent**: apply the default value of `10` and proceed.

- Confirm the feature description is non-empty. If empty, ask via `vscode_askQuestions`:
  ```json
  {
    "header": "feature_description",
    "question": "Provide the feature description.",
    "allowFreeformInput": true
  }
  ```
  > **If `vscode_askQuestions` is unavailable (non-interactive context)**: stop, report `blocked — feature description required; re-run interactively or pass the description as an argument`.

- **Detect run state** — runs AFTER Step 2:
  - Spec with `[NEEDS CLARIFICATION]` markers → **resume**: re-run Step 6 only
  - Spec with no markers → **complete**: report ok and stop
  - No existing spec → **new**: proceed through all steps

## Done conditions

- **Success**: `spec-file` exists on disk with all required sections populated and no `[NEEDS CLARIFICATION]` markers remain.
- **Blocked**: Clarification questions have been asked and the skill is awaiting user responses.
- **Fail**: Script execution failed, git is unavailable, or the spec template cannot be read.

## Step 1 — Generate short name

Extract meaningful keywords from the feature description. Create a 2–4 word hyphenated short name using action-noun format. Preserve technical terms and acronyms.
Examples: "Add user auth" → `user-auth`, "OAuth2 API" → `oauth2-api-integration`.

## Step 2 — Find highest existing feature number

Run these commands to detect existing branches and directories for this short name:

```bash
git fetch --all --prune
git ls-remote --heads origin | grep -E "refs/heads/[0-9]+-<short-name>$"
git branch | grep -E "^[* ]*[0-9]+-<short-name>$"
```

Also check for directories matching `spek-fu/features/[0-9]+-<short-name>`. Extract all numbers found across remote branches, local branches, and feature directories. Use (highest number found) + 1 as the new feature number. If no entries exist for this short name, use 1.

> **If git is unavailable**: stop, report `fail`, and ask the user to resolve git access before retrying.

## Step 3 — Run create-new-feature script (once)

Run the script exactly once:

```bash
python spek-fu/ai/scripts/python/create-new-feature.py --feature-number <N> --feature-name "<short-name>" --output-json
```

Capture **stdout only** as the JSON source. Discard stderr (warnings and progress messages on stderr do not contaminate the JSON payload). Read the JSON output from stdout. Extract:
- **`branch-name`**: the created branch name
- **`spec-file`**: the canonical path to write the spec
- **`feature-dir`**: the feature directory root

> **If the script fails or exits with a non-zero code**: stop, report `fail` with the error text, and do not proceed.
> **If `branch-name` or `spec-file` are absent from the stdout JSON**: stop, report `fail`, and display the raw terminal output for diagnosis.

Apply the run-state detection from Preflight now that **`branch-name`**, **`spec-file`**, and **`feature-dir`** are known.

## Step 4 — Load spec template

Apply `spek-fu/ai/plugins/spec-flow/knowledge/paginated-read.md` to load `spek-fu/ai/plugins/spec-flow/templates/spec-feature-template.md` fully. Identify all required sections and their order.

> **If the template file cannot be read**: stop, report `fail` with the path `spek-fu/ai/plugins/spec-flow/templates/spec-feature-template.md`, and ask the user to verify the file exists.

## Step 5 — Generate specification content

Extract actors, actions, data, constraints, and success conditions from the feature description. Document all assumptions. Use `[NEEDS CLARIFICATION]` only when choice significantly impacts scope and no reasonable default exists. Enforce hard limit of `maxNeedsClariMarkers` markers (default: 10). Success criteria must be measurable, technology-agnostic, and user-focused. Write spec to **`spec-file`** using template structure; do NOT embed checklists.

> **If `create_file` fails** (permission error, path conflict, or disk error): stop, report `fail — could not write spec to <spec-file>: <error>`, and do not report completion.

## Step 6 — Resolve clarifications (if any)

If `[NEEDS CLARIFICATION]` markers remain, apply `needs-clarification-protocol.md`. If non-interactive, leave markers and report blocked. Extract all markers. If more than `maxNeedsClariMarkers` exist, keep critical ones and guess the rest (recording as assumptions). Ask all questions in one `vscode_askQuestions` call:
   ```json
   {
     "header": "clarification_N",
     "question": "[Question from the NEEDS CLARIFICATION marker]",
     "options": [
       { "label": "Option A — [first answer with implications]" },
       { "label": "Option B — [second answer with implications]" },
       { "label": "Option C — [third answer with implications]" }
     ],
     "allowFreeformInput": true
   }
   ```
3. After receiving responses, replace each `[NEEDS CLARIFICATION: ...]` marker in `spec-file` with the user's chosen answer.

## Step 7 — Report completion

Report using the output format defined in `<output_format>`.

The skill is complete when `spec-file` exists on disk with all required sections populated and no `[NEEDS CLARIFICATION]` markers remain.

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **run_in_terminal**: Run git commands (Step 2) and the create-new-feature script (Step 3) — run one command and read full output before proceeding to the next.
- **read_file**: Load the config file (Preflight), `spek-fu/ai/plugins/spec-flow/templates/spec-feature-template.md` (Step 4), and existing spec files when resuming. Apply `spek-fu/ai/plugins/spec-flow/knowledge/paginated-read.md` whenever the file may span multiple reads.
- **create_file**: Write `spec-file` (Step 5) — only after `branch-name` and `spec-file` are confirmed from script output.
- **replace_string_in_file**: Replace `[NEEDS CLARIFICATION]` markers (Step 6) after user responses are received.
- **vscode_askQuestions**: Collect feature description if absent (Preflight) and present clarification questions (Step 6).
- Do NOT use tools not listed here unless the skill explicitly escalates.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Completion Report**:

```
Branch:             <branch-name>
Spec file:          <spec-file>
Clarifications:     N resolved | 0 remaining
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: "Add ability to export transaction history as CSV."
Expected behavior: Generates short name, checks branches (finds none, assigns number 1), runs script, writes spec with functional requirements and success criteria. Reports: branch `1-export-transaction-csv`, spec at `spek-fu/features/001-export-transaction-csv/spec.md`, 0 clarifications.
</example>

<example>
Input: "Users collaborate on documents in real time."
Expected behavior: Generates short name, identifies 2 ambiguities (conflict resolution, cursor visibility), adds markers, asks 2 questions in one call, replaces markers after responses. Reports 2 clarifications resolved.
</example>

<example type="counter">
Input: "Add OAuth2 login using Node.js and PostgreSQL."
Expected behavior: Writes spec with `[ASSUMPTION]` for OAuth2 flow. Excludes "Node.js" and "PostgreSQL" from requirements — those are implementation details. Focuses on user value.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

- Constraint 1 — confirm `branch-name` and `spec-file` from script stdout before any write.
- Constraint 2 — run the create-new-feature script once per invocation.
- Constraint 3 — cap `[NEEDS CLARIFICATION]` markers at `maxNeedsClariMarkers`.
- Constraint 4 — keep implementation details out of the spec body.
- Constraint 5 — collect missing feature description details interactively instead of guessing.

</reminders>
