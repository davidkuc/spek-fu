---
# id-exception: this template uses 'wave-summary-template' instead of 'skf-template-*' — intentional, matches the artifact filename convention it governs
id: wave-summary-template
title: "Wave Summary Template — Markdown Format"
category: framework
version: 1.0
---

# Wave Summary Template

This template defines the canonical markdown format for `.orchestration-temp/wave-{N}-summary.md` files produced after each execution wave.

---

## Wave {N} Summary

- **Wave**: {N}
- **Goal**: {one-sentence description of the wave's objective}
- **Status**: {ok | blocked | fail}
- **Steps completed**: {comma-separated list of step IDs, e.g. "1.1, 1.2, 1.3"}
- **Steps skipped**: {comma-separated list of step IDs, or none}
- **Steps failed**: {comma-separated list of step IDs, or none}

### Outputs Produced

| Step | File | Status |
|------|------|--------|
| {N.M} | {path/to/artifact} | {created | modified | deleted} |

### Issues

{none — or bullet list of issues encountered}

### Notes

{Optional: any relevant context for the next wave}

---

## Field Definitions

| Field | Description |
|-------|-------------|
| Wave | Integer wave number |
| Goal | One-sentence summary of what this wave accomplished |
| Status | `ok` — all steps completed; `blocked` — one or more steps blocked; `fail` — one or more steps failed |
| Steps completed | Step IDs that succeeded |
| Steps skipped | Step IDs that were intentionally skipped (with reason in Notes) |
| Steps failed | Step IDs that failed (details in Issues section) |
| Outputs Produced | Table of all files created, modified, or deleted in this wave |
| Issues | Any errors, warnings, or blockers encountered |
| Notes | Optional context for the orchestrator or next wave |

---

## Usage

Wave summaries are written to `.orchestration-temp/wave-{N}-summary.md` by the `orch-wave-verification` skill after each wave completes. The orchestrator reads these files to confirm wave success before dispatching the next wave.
