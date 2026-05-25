---
id: "meta-script-manage"
recommended-tier: "fast-agent"
version: 1.0
description: "Scaffolds and validates framework scripts in `ai/scripts/`. USE FOR: authoring new scripts, auditing existing scripts against policy, fixing incomplete headers. DO NOT USE FOR: running scripts, managing skill/agent/knowledge files, or modifying files outside `ai/scripts/`."
anti-scope: "Does not run or execute scripts, manage skill/agent/knowledge files, or modify any file outside ai/scripts/ without user approval."
tags:
  - "meta"
  - "lifecycle"
  - "framework"
  - "validation"
inputs:
  - "Operation to perform: create or validate (required)"
  - "Script purpose description — required for create (optional)"
  - "Script file path — required for validate (optional)"
  - "Language override for create, python or powershell (optional)"
  - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
outputs:
  - "Execution status: ok, blocked, or fail"
  - "Path to created or modified script file"
  - "Validation report with per-check status"
  - "One-line operation summary"
dispatch-variant: "full"
---

> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: meta-script-manage

<!-- SECTION 1: Identity (primacy position) -->
Scaffolds new framework scripts (**create**) and audits existing scripts against policy (**validate**). Document operations are integrated: create always produces a complete header; validate checks header completeness and offers to fix gaps.

**Scope boundary**: Script authoring and validation only. Does NOT run scripts, manage skill/agent/knowledge files, or modify files outside `ai/scripts/` without user approval.

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER write to disk without explicit user approval — the write gate in create Step 5 and validate Step 4 is mandatory. WHY: unapproved writes to framework scripts can corrupt automation pipelines.
2. NEVER create a framework automation script in PowerShell — Python is mandatory for all cross-platform utility scripts. WHY: `constitution/constitution.md` mandates Python for utility scripting; PowerShell cannot run in GitHub Actions (Ubuntu).
3. NEVER use `run_in_terminal` — script execution is out of scope.
4. Resolve `operation` before loading any files — if absent, ask via `vscode_askQuestions`.
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>
- Verify output complies with all `<constraints>` before proceeding.
- Implement EXACTLY and ONLY the named steps — do not combine operations or silently apply fixes.
- If inputs are ambiguous or missing, call `vscode_askQuestions` rather than guessing.

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.
</behavioral_anchors>

<!-- SECTION 4: Language heuristics -->
<language_heuristics>
Apply these rules in order — stop at first match. Do NOT read the scripting guides before applying these rules.

1. **Framework automation** (sync, validation, promotion, CI pipeline work) → **Python** (mandatory; Constraint 2 overrides any user request for PowerShell).
2. **Cross-platform or runs on Linux/GitHub Actions** → **Python**.
3. **Windows admin surfaces** (AD, Exchange, registry, services, GPO, M365/Intune, IIS, Hyper-V, Azure with Az module) → **PowerShell**.
4. **Data-heavy, algorithmic, or relies on a Python/PyPI library** → **Python**.
5. **Purely cmdlet/Windows CLI orchestration and team is already in PowerShell** → **PowerShell**.
6. **Default** → **Python**.

After applying heuristics, read ONLY the guide for the determined language:
- Python → `ai/plugins/skf/knowledge/python-scripting-guide.md`
- PowerShell → `ai/plugins/skf/knowledge/powershell-scripting-guide.md`
</language_heuristics>

<!-- SECTION 5: Workflow -->
<workflow>

## Preflight

Resolve `operation` before taking any actions. For **create**: check if target path already exists — if so, present as current draft at Step 5. For **validate**: confirm `script_path` is provided; if absent, ask via `vscode_askQuestions`.

---

## Operation: create

### Step 1 — Gather purpose

If `purpose` is not provided, ask:

```json
{
  "header": "script_purpose",
  "question": "Describe the purpose of the new script — what it does, what it processes, what output it produces, and whether it must run cross-platform.",
  "allowFreeformInput": true
}
```

### Step 2 — Determine language

Apply `<language_heuristics>` in order. Present: recommended language, matched rule number, one-sentence rationale. If user provided a `language` override, acknowledge it and flag any conflict with Constraint 2.

Read the guide for the chosen language in full (multi-pass until response is shorter than page size).

### Step 3 — Determine file path

Derive filename from purpose: lowercase, hyphen-separated, descriptive.
- Python → `ai/scripts/python/`, extension `.py`
- PowerShell (Windows-specific only) → `ai/scripts/powershell/`, extension `.ps1`

Confirm no collision using `file_search`.

### Step 4 — Scaffold with header

Produce a complete, runnable scaffold. The header (Purpose, Usage, Exit codes) is part of the scaffold — not a separate step.

**Python required elements**: `#!/usr/bin/env python3` shebang, module docstring with Purpose/Usage/Exit code, `argparse` block, `main()` returning `int`, `if __name__ == "__main__":` guard. Apply best practices from the guide.

**PowerShell required elements**: `.SYNOPSIS`, `.DESCRIPTION`, `.NOTES` (document platform and PS justification), `[CmdletBinding()]`, `param()`, `Set-StrictMode -Version Latest`, `$ErrorActionPreference = 'Stop'`. Apply best practices from the guide.

### Step 5 — Write gate

⛔ **STOP — Approval required before writing.**

Present the proposed path and full scaffold. Ask:

```json
{
  "header": "script_create_review",
  "question": "Review the script scaffold above. How would you like to proceed?",
  "options": [
    { "label": "Approve — write to disk", "recommended": true },
    { "label": "Request changes" }
  ],
  "allowFreeformInput": true
}
```

Incorporate feedback, re-present, repeat until approved or cancelled. On approval: write file using `create_file`.

---

## Operation: validate

### Step 1 — Load script

Read the target script in full. Determine language from extension (`.py` → Python, `.ps1` → PowerShell).

> If the path does not exist: stop and report — do not proceed.

Apply `<language_heuristics>` to the script's inferred purpose to detect SCR-030 violations.

### Step 2 — Read the relevant guide

Read ONLY the guide for the detected language (multi-pass until page ends).

### Step 3 — Apply checks

Mark each ✅ / ⚠️ / ❌ / N/A.

**All scripts** (SCR-001–006):
- SCR-001: File is in the correct location (`ai/scripts/python/` or `ai/scripts/powershell/`)
- SCR-002: Filename is lowercase, hyphen-separated, descriptive
- SCR-003: Module-level header block present
- SCR-004: Header contains Purpose
- SCR-005: Header contains Usage example
- SCR-006: Header contains Exit code declaration

**Python only** (SCR-010–015):
- SCR-010: `#!/usr/bin/env python3` shebang on line 1
- SCR-011: `main()` function present
- SCR-012: `if __name__ == "__main__":` guard present
- SCR-013: `argparse` for argument parsing
- SCR-014: `main()` returns `int`
- SCR-015: stdlib imports precede third-party imports

**PowerShell only** (SCR-020–023):
- SCR-020: `[CmdletBinding()]` present
- SCR-021: `Set-StrictMode -Version Latest` present
- SCR-022: `$ErrorActionPreference = 'Stop'` present
- SCR-023: `.NOTES` documents platform and PowerShell justification

**Policy** (SCR-030):
- SCR-030: Framework automation script in PowerShell → ❌ CRITICAL

If SCR-030 is violated, prepend `⛔ CRITICAL VIOLATION: Framework automation script in PowerShell — rewrite as Python per constitution/constitution.md.` and stop.

### Step 4 — Report and optional header fix

Output the validation report (see `<output_format>`).

If any header checks (SCR-003–006) are ❌ or ⚠️, ask:

```json
{
  "header": "header_fix",
  "question": "Header checks have violations. Would you like to generate and apply a corrected header block?",
  "options": [
    { "label": "Yes — generate and apply header fix", "recommended": true },
    { "label": "No — report only" }
  ],
  "allowFreeformInput": true
}
```

If fix requested: infer Purpose/Usage/Exit code from script content, present proposed header, then apply via `replace_string_in_file` only after a second approval confirmation.

</workflow>

<!-- SECTION 6: Tools -->
<tools>
- **read_file**: Load the relevant guide (multi-pass) and target scripts.
- **file_search**: Check for name collisions (create Step 3); locate scripts (validate Step 1).
- **vscode_askQuestions**: All user input and approval gates.
- **create_file**: Write approved scripts — create Step 5 only.
- **replace_string_in_file**: Apply header fixes — validate Step 4 only, after approval.
- Do NOT use `run_in_terminal` or any unlisted tool.
</tools>

<!-- SECTION 7: Output format -->
<output_format>
| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `meta-script-manage` |
| output_path | `path/to/artifact or null` |
| summary | one-line summary |

**create** (after approval):
```
Script `{name}` created at `{path}`.
Language: Python | PowerShell
Decision basis: Rule {N} — {rationale}
```

**validate**:
```
## Validation Report: {script-name}
Language: Python | PowerShell
Overall: ✅ Pass | ⚠️ Warnings | ❌ Violations

| ID | Rule | Status | Finding |
|----|------|--------|---------|

Errors (❌): N | Warnings (⚠️): N | Passed (✅): N | N/A: N

### Findings
{Each ❌ and ⚠️ with ID, rule, and script location}
```
</output_format>

<!-- SECTION 8: Examples -->
<examples>
<example>
Input: operation=create, purpose="Parse all skill markdown files and output a JSON summary."
Expected behavior: Heuristics rule 2 → Python (cross-platform on GitHub Actions). Derives a Python summary script in `ai/scripts/python/`. Reads Python guide. Scaffolds with shebang, docstring (Purpose/Usage/Exit code), argparse, `main()` returning int, `__name__` guard. Presents via write gate. On approval: writes file. Reports status=ok, decision-basis=Rule 2.
</example>

<example>
Input: operation=create, purpose="Set Windows Registry keys for CI agent configuration on Windows build machines."
Expected behavior: Heuristics rule 3 → PowerShell (Windows registry). Reads PowerShell guide. Scaffolds `set-ci-agent-registry-keys.ps1` in `ai/scripts/powershell/` with required PS elements. Presents via write gate. On approval: writes file.
</example>

<example type="counter">
Input: operation=create, purpose="Validate all skill index JSON files." User then requests PowerShell.
Expected behavior: Heuristics rule 1 → Python (framework automation/validation). Constraint 2 overrides user request. Reports: "Framework automation scripts must be Python per constitution/constitution.md — overriding to Python." Scaffolds Python only.
</example>
</examples>

<!-- SECTION 9: Critical reminders (recency position) -->
<reminders>
- **NEVER create a framework automation script in PowerShell** — Python mandatory per `constitution/constitution.md`.
- **NEVER write to disk without explicit user approval** — write gate in create Step 5 and validate Step 4 is mandatory.
- **Read ONLY the relevant guide** after determining language — do not pre-load both guides.
</reminders>
