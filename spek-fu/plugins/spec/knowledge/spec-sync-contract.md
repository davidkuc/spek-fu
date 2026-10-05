# Spec Sync Contract (D2)

Seven non-negotiable rules for syncing a remediation plan's scope back into a feature's spec artifacts, referenced by `spec-quick-planner`.

## The seven rules

1. **Additive by default; amend only on contradiction.** Never delete an FR/SC — downstream tasks and reports cite them by ID. When the remediation makes one false, rewrite that line in-place to the new truth and append `(amended by remediation <slug>)`. The ID survives.
2. **Provenance both ways.** Every new/amended FR/SC carries a trailing `— remediation/<slug>`. The plan carries a `## Spec Sync Record` table so the sync is auditable from one place.
3. **Tasks cite the requirement they satisfy.** Each injected task ends `@ref: remediation/<slug>/plan.md#<section> — FR-###`. FR/SC IDs must therefore be allocated before tasks are written.
4. **Never author a missing artifact.** If `data-model.md`, `contracts/`, or any expected artifact is absent, record the gap in the plan and move on — creating it belongs to `spec-technical-draft`.
5. **One approval covers plan, spec sync, and tasks.** Name all three before touching any. Accepting the plan while declining spec sync is allowed; record it `declined` in the Spec Sync Record.
6. **Fixed ordering: plan → sync → tasks.** Allocate FR/SC IDs during sync before injecting tasks. Any other order forces a second pass to backfill IDs.
7. **No scope invention.** Only write requirements the plan already justifies. Never allocate an FR/SC without a justifying statement in the plan.

`research.md` is NEVER touched by this sync — it is a point-in-time record; remediation reasoning belongs in the plan.

## Which artifacts sync, and how

| Artifact | Synced when | How |
|---|---|---|
| `spec.md` | always | Append new `- **FR-###**` under `### Functional Requirements`, new `- **SC-###**` under `### Measurable Outcomes`, continuing the existing sequence. Amend in-place only on contradiction. Every new/amended item carries `— remediation/<slug>`. |
| `technical-plan.md` | remediation changes the technical approach or touches unlisted source paths | Append to the affected section only — never restructure. |
| `data-model.md` | remediation adds/changes/removes an entity or field | Append or amend that entity only. |
| `contracts/*` | remediation changes a declared interface | Amend the affected contract file. |
| `quickstart.md` | remediation adds/changes a verification step | Append the command to the checklist. |
| `research.md` | never | Point-in-time record; leave untouched. |

## Spec Sync Record table (embedded in the plan)

```
## Spec Sync Record

| Artifact | Section | IDs Added/Amended | Reason |
|---|---|---|---|
| spec.md | Functional Requirements | FR-028, FR-029 | <justification from the plan> |
| spec.md | Measurable Outcomes | SC-011 | <justification from the plan> |
| spec.md | Functional Requirements (amended) | FR-023 | <contradiction and new truth> |
| technical-plan.md | [section] | [change note] | [reason] |
```

Every row traces to a statement in the remediation plan (Rule 7). A declined sync gets one row: `| all | — | none | declined by user |`.
