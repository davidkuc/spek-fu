# Project Artifacts

Artifact map and staleness chain for the project docs, referenced by `project-documentation-analysis`.

## Artifact Paths

Paths are relative to `spek-fu/project/`.

| Alias | Path |
|-------|------|
| project-overview | `project.md` |
| technical-overview | `technical.md` |
| roadmap | `roadmap.md` |
| area-docs | `project-docs/<area>.md` — one per row of `knowledge/area-registry.md` |
| user-flows | `user-flows/*.md` |
| project-features | `project-features/PF*.md` |
| code-docs | `code-docs/*.md` |
| contracts | `contracts/*.yaml` |
| spec-features | `spec-features/<###-short-name>/spec.md` |
| research-report | `reports/project-research/project-research-report.md` |
| devils-advocate-report | `reports/project-devils-advocate/project-devils-advocate-report.md` (latest, if timestamped) |
| analysis-report | `reports/project-documentation-analysis/documentation-analysis-report.md` |

## Staleness Chain

```
spec-features/*/spec.md → project-docs/<area>.md (## Functional)
spec-features/*/spec.md → user-flows/*.md
code-docs/<module>.md   → project-docs/<area>.md (## Technical, ### Related Modules)
contracts/*.yaml        → project-docs/<area>.md (## Technical)
project-features/PF*.md → roadmap.md
project-docs/<area>.md  → project.md (Reference Map)
project-docs/<area>.md  → technical.md
```

Compare only pairs where both artifacts are present. Last-modified: `git log -1 --format=%cI -- <path>`, else `unknown`. Staleness signal: upstream newer than downstream. Map an upstream file to its downstream through the references the downstream doc already contains; record `indeterminate` when no reference links them.
