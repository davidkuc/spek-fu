---
id: "branch-detection"
description: "Canonical Branch Detection procedure for spec-flow skills. Resolves the active feature directory from the current git branch when no explicit path is supplied as input."
---

# Branch Detection

## Purpose

Determines `FEATURE_DIR` (the feature directory path) from the active git branch when it is not supplied as an explicit input to the skill. Skills that use a different variable name follow the same procedure with their variable substituted for `FEATURE_DIR`.

---

## Core Procedure

1. Run `git branch --show-current` to get the active branch name.
2. A **feature branch** matches the pattern `^\d+-.+` (e.g., `001-user-auth`, `42-payment-flow`).
3. If on a feature branch: set `FEATURE_DIR = features/<branch-name>/`.
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

- If the user provides a path: use it as `FEATURE_DIR` and proceed.
- If the user selects "Switch to a feature branch first" or declines: stop and report `status: blocked`.

---

## Skill-Specific Variants

### `spec_path` resolution — spec-clarification, spec-devils-advocate

These skills work with a `spec_path` variable rather than `FEATURE_DIR` directly. After applying the core procedure to resolve `FEATURE_DIR`, additionally set:

```
spec_path = FEATURE_DIR/spec.md
```

Use `"Provide the spec file path manually"` as the option label in the `vscode_askQuestions` call (not "Provide the feature directory path manually"), and treat the user's freeform answer as `spec_path` directly rather than as `FEATURE_DIR`.

### `SPECS_DIR` alias — spec-technical-draft

This skill uses `SPECS_DIR` as its directory variable. Apply the core procedure with `SPECS_DIR` substituted for `FEATURE_DIR` everywhere, including the `vscode_askQuestions` option label (`"Provide the SPECS_DIR path manually"`).
