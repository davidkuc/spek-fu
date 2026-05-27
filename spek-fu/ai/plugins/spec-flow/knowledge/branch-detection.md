---
id: "branch-detection"
description: "Canonical Branch Detection procedure for spec-flow skills. Resolves feature-dir or spec-file from the active git branch when no explicit path is supplied as input."
---

# Branch Detection

## Purpose

Determines `feature-dir` from the active git branch when it is not supplied as an explicit input to the skill.

---

## Core Procedure

1. Run `git branch --show-current` to get the active branch name.
2. A **feature branch** matches the pattern `^\d+-.+` (e.g., `001-user-auth`, `42-payment-flow`).
3. If on a feature branch: set `feature-dir = spek-fu/features/<branch-name>/`.
4. If NOT on a feature branch (e.g., `main`, `develop`, or any other non-matching branch): call `vscode_askQuestions` to ask the user for guidance — do NOT guess or assume a path:

```json
{
  "header": "feature_guidance",
  "question": "The current branch ('<branch-name>') is not a feature branch. How would you like to proceed?",
  "options": [
    { "label": "Provide the feature directory path manually" },
    { "label": "Switch to a feature branch first, then re-run" }
  ],
  "allowFreeformInput": true
}
```

- If the user provides a path: use it as `feature-dir` and proceed.
- If the user selects "Switch to a feature branch first" or declines: stop and report `status: blocked`.


## spec-file Variant

Skills that accept `spec-file` rather than `feature-dir` apply the core procedure first, then derive:

```
spec-file = {feature-dir}/spec.md
```

Use `"Provide the spec file path manually"` as the option label in the `vscode_askQuestions` call, and treat the user's freeform answer as `spec-file` directly rather than as `feature-dir`.
