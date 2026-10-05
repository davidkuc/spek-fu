# Pipeline Artifacts

Path table and staleness chain for spec feature artifacts, referenced by `spec-feature-analysis`.

## Artifact Paths

| Alias | Path (relative to `<spec-file-directory>` unless noted) |
|-------|-----------------------------------------------------------|
| spec-file | `spec.md` |
| spec-research-report | `spec-research/spec-research-report.md` |
| devils-advocate-report | `devils-advocate/devils-advocate-report.md` (latest, if timestamped) |
| testability-report | `test-expert/testability-assessment.md` (latest, if timestamped) |
| research-file | `research.md` |
| data-model-file | `data-model.md` |
| contracts-dir | `<contracts-root>` — inside `spek-fu/project/contracts/`, resolved from `spec-technical-draft.contractsPath` |
| quickstart-file | `quickstart.md` |
| technical-plan-file | `technical-plan.md` |
| tdd-report | `tdd-designer/tdd-report.md` (latest, if timestamped) |
| tasks-file | `tasks.md` |

## Staleness Chain

Pipeline order, per each skill's `## When to use`:

```
spec.md → spec-research-report.md
spec.md → devils-advocate-report.md
devils-advocate-report.md → testability-assessment.md
testability-assessment.md → research.md / data-model.md / contracts-dir / quickstart.md / technical-plan.md
technical-plan.md → tdd-report.md
tdd-report.md → tasks.md
```

Compare only pairs where both artifacts are present. Staleness signal: upstream last-modified timestamp newer than downstream's.
