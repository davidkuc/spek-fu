# Project Constitution

## Purpose

This constitution governs all development activity on this project. Agents must consult the relevant sub-files before performing work that falls within their scope.

## Sub-Files

| File | Scope | When to Load |
|------|-------|-------------|
| `company-principles.md` | Organization values, culture, non-negotiable standards | Creating specs, reviewing requirements |
| `project-constraints.md` | Tech stack, architecture boundaries, dependency rules | Planning, architecture decisions |
| `coding-standards.md` | Principles-level coding standards | Writing or reviewing code |
| `testing-guidelines.md` | Test strategy, coverage, naming | Writing tests, generating checklists |
| `ai-behavior.md` | Agent constraints, gate requirements, scope limits | All AI agent operations |
| `governance.md` | Documentation governance, SSOT policy, deduplication rules | Writing or modifying any project file; reviewing for SSOT compliance |

## Conflict Resolution

If two constitution sub-files appear to conflict, apply the following ordered precedence hierarchy. The file with the lower number (**highest** position) wins:

| Precedence | File | Scope |
|------------|------|-------|
| 1 (highest) | `ai-behavior.md` | AI agent constraints, gate requirements, scope limits |
| 2 | `coding-standards.md` | Engineering principles for all authored code |
| 3 | `testing-guidelines.md` | Test strategy, coverage, and test naming |
| 4 | `governance.md` | Documentation governance and SSOT policy |
| 5 | `project-constraints.md` | Tech stack, architecture, and tooling boundaries |
| 6 (lowest) | `company-principles.md` | Organizational values and culture |

**`constitution.md` (this file) supersedes all sub-files.** Any rule stated directly here overrides an equivalent rule in any sub-file.

**Still unresolved**: surface the ambiguity to the human developer rather than picking silently.

## No-Duplication Rule

Content already stated in a higher-precedence sub-file MUST NOT be repeated in a lower-precedence sub-file. Only a brief (1–3 line) summary with an explicit pointer to the authoritative location is permitted. Full rule text exists in exactly one location.

This applies transitively: if a rule belongs in `ai-behavior.md`, neither `project-constraints.md` nor `company-principles.md` may define it — a reference with a link pointer is the only acceptable form.

