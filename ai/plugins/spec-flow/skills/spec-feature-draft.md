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
  - "config_path: workspace-relative path to the config file — defaults to ai/plugins/spec-flow/skills/config.json (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Spec file written to `spec-file` path inside the numbered feature branch directory"
  - "Execution status, branch name, and spec file path"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: spec-feature-draft

<!-- SECTION 1: Identity (primacy position) -->
Generates a feature specification from a natural language feature description. The skill creates a numbered git branch, populates all required spec sections (functional requirements, user scenarios, success criteria, acceptance criteria, assumptions), and resolves critical ambiguities before reporting completion.

**Scope boundary**: This skill creates a feature specification only. It does NOT produce implementation plans, execute clarification sessions on existing specs, apply code changes, or run quality validation on the completed spec.

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
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- If the feature description is empty or ambiguous, call `vscode_askQuestions` rather than guessing.
- Detect run state before acting: if a spec file already exists at the expected path, read and update it rather than recreating; if a branch already exists for this feature number and short name, resume from the current spec content.
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve `config_path` from inputs, defaulting to `ai/plugins/spec-flow/skills/config.json` if absent. Read the config file and extract `spec-feature-draft.maxNeedsClariMarkers` (default: `10`). Apply this value wherever this skill references `maxNeedsClariMarkers`.

> **If the config file cannot be read or the `spec-feature-draft` key is absent**: apply the default value of `10` and proceed.

- Confirm the feature description is non-empty. If empty, ask via `vscode_askQuestions`:
  ```json
  {
    "header": "feature_description",
    "question": "Provide the feature description.",
    "allowFreeformInput": true
  }
  ```
- Confirm run state: if a spec file exists for this feature already, resume from existing content rather than restarting.

## Done conditions

- **Success**: `spec-file` exists on disk with all required sections populated and no `[NEEDS CLARIFICATION]` markers remain.
- **Blocked**: Clarification questions have been asked and the skill is awaiting user responses.
- **Fail**: Script execution failed, git is unavailable, or the spec template cannot be read.

## Step 1 — Generate short name

Analyze the feature description and extract the most meaningful keywords. Create a 2–4 word hyphenated short name that captures the essence of the feature. Use action-noun format when possible. Preserve technical terms and acronyms. Examples:
- "Add user authentication" → `user-auth`
- "Implement OAuth2 integration for the API" → `oauth2-api-integration`
- "Create a dashboard for analytics" → `analytics-dashboard`

## Step 2 — Find highest existing feature number

Run these commands to detect existing branches and directories for this short name:

```bash
git fetch --all --prune
git ls-remote --heads origin | grep -E "refs/heads/[0-9]+-<short-name>$"
git branch | grep -E "^[* ]*[0-9]+-<short-name>$"
```

Also check for directories matching `features/[0-9]+-<short-name>`. Extract all numbers found across remote branches, local branches, and feature directories. Use (highest number found) + 1 as the new feature number. If no entries exist for this short name, use 1.

> **If git is unavailable**: stop, report `fail`, and ask the user to resolve git access before retrying.

## Step 3 — Run create-new-feature script (once)

Run the script exactly once:

```bash
python ai/scripts/python/create-new-feature.py --feature-number <N> --feature-name "<short-name>" --output-json
```

Read the JSON output from the terminal. Extract:
- `branch-name`: the created branch name
- `spec-file`: the canonical path to write the spec
- `feature-dir`: the feature directory root

> **If the script fails or exits with a non-zero code**: stop, report `fail` with the error text, and do not proceed.
> **If `branch-name` or `spec-file` are absent from the output**: stop, report `fail`, and display the raw terminal output for diagnosis.

## Step 4 — Load spec template

Read `ai/plugins/spec-flow/templates/spec-feature-template.md` using successive `read_file` calls until the response is shorter than the page size (multi-pass). Identify all required sections and their order.

> **If the template file cannot be read**: stop, report `fail` with the path `ai/plugins/spec-flow/templates/spec-feature-template.md`, and ask the user to verify the file exists.

## Step 5 — Generate specification content

Parse the feature description and extract actors, actions, data, constraints, and success conditions. Apply these rules:

- Make informed guesses using context and industry standards for unspecified details.
- Document assumptions in the Assumptions section.
- Use `[NEEDS CLARIFICATION: <specific question>]` only when the choice significantly impacts scope or user experience, multiple reasonable interpretations exist with different implications, and no reasonable default exists.
- **Hard limit**: maximum `maxNeedsClariMarkers` (from config) `[NEEDS CLARIFICATION]` markers. Prioritize: scope > security/privacy > user experience > technical details.

**Success criteria** must be measurable (specific metrics), technology-agnostic (no frameworks or tools), user-focused (business/user outcomes), and verifiable without implementation details.

Write the specification to `spec-file` using the template structure. Preserve all section headings and order. Do NOT embed checklists inside the spec body.

## Step 6 — Resolve clarifications (if any)

If `[NEEDS CLARIFICATION]` markers remain in the spec:

1. Extract all markers. If more than `maxNeedsClariMarkers` exist, keep the `maxNeedsClariMarkers` most critical and make informed guesses for the rest.
2. Ask all clarification questions in one `vscode_askQuestions` call, one question per marker:
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
- **read_file**: Load config file (Preflight) and `ai/plugins/spec-flow/templates/spec-feature-template.md` (Step 4) using multi-pass reads; also read existing spec files when resuming.
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
Input: Feature description: "Add the ability for users to export their transaction history as a CSV file."
Expected behavior: Skill reads config (`maxNeedsClariMarkers: 10`), generates short name `export-transaction-csv`, checks remote and local branches and spec directories for existing entries — finds none — assigns number 1, runs create-new-feature script once, reads spec template, writes a complete spec with functional requirements (export trigger, column selection, file format), technology-agnostic success criteria ("Users can download a complete transaction history file within 5 seconds"), user scenarios, and documented assumptions. Reports: branch `1-export-transaction-csv`, spec at `features/001-export-transaction-csv/spec.md`, 0 clarifications.
</example>

<example>
Input: Feature description: "Users should be able to collaborate on documents in real time with other team members."
Expected behavior: Skill reads config (`maxNeedsClariMarkers: 10`), generates short name `realtime-doc-collaboration`, determines next number from branch/directory scan, runs script, writes spec. Identifies 2 critical ambiguities (conflict resolution strategy, presence/cursor visibility) and adds `[NEEDS CLARIFICATION]` markers. Presents 2 clarification questions to the user in one `vscode_askQuestions` call. After user responds, replaces both markers in the spec and reports completion with 2 clarifications resolved.
</example>

<example type="counter">
Input: Feature description: "Add OAuth2 login using Node.js and PostgreSQL."
Expected behavior: Skill writes spec with `[ASSUMPTION: authentication follows standard OAuth2 authorization code flow]` in Assumptions. Does NOT include "Node.js" or "PostgreSQL" in functional requirements or success criteria — those are implementation details. The skill produces a spec focused on user value: "Users can authenticate using their existing accounts" rather than naming the underlying protocol implementation.
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never run the create-new-feature script more than once per invocation** — WHY: duplicate runs corrupt the branch numbering sequence.
- **Never include implementation details in the spec** (languages, frameworks, databases, APIs) — WHY: specs describe user and business value; implementation belongs in technical planning artifacts.
- **Never exceed `maxNeedsClariMarkers` (from config) `[NEEDS CLARIFICATION]` markers** — WHY: more than the configured limit signals an underspecified input; make informed guesses for lower-priority gaps.
- **Always verify** output against `<constraints>` before reporting completion.

</reminders>
