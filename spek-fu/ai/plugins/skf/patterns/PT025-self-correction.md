---
id: PT025
version: 1.0
name: Self-Correction
description: "When the agent detects a failure, contradiction, or conflicting signal, explicitly re-examine the current approach and verify the correction before continuing. USE FOR: Long tasks with intermediate failures, tasks where early assumptions may prove wrong, multi-step work where an incorrect early step compounds downstream. DO NOT USE FOR: Short tasks, tasks with already-verified outputs where only PT009 is needed."
category: verification
tags: [self-correction, recovery, adaptive, meta-cognition, reflection, testing, execution-verification]
signals: [long-running-session, debugging, investigation]
recommended-tier: all
prevents: "Committed-wrong-approach cascade — agents that detect a failure signal (failing test, contradictory data, unexpected result) but continue execution compound the error; each subsequent step builds on the flawed foundation until the entire output is corrupted."
---

# Self-Correction

## Reasoning

Long-running tasks are error-prone at the plan level, not just the execution level. An early incorrect assumption or a subtly wrong decision propagates silently through subsequent steps. By the time the error surfaces, fixing it requires undoing many downstream steps.

Self-correction makes the agent pause and re-examine whenever it encounters a failure or contradiction, rather than trying to paper over it. The examination is explicit: state what failed, state what the current approach assumed, state which assumption appears violated, then revise the approach.

Critically, every corrected approach must be verified by execution before continuing — write → run → read output → fix if broken. Without this verification gate, "self-correction" becomes rationalization: the agent invents a reason the failure is acceptable rather than confirming the corrected approach actually works. The corrected approach is only accepted when it passes execution verification.

Note: self-correction is for genuine failures and contradictions, not for routine uncertainty. Agents must not enter self-correction loops on every step — that pattern creates the infinite loop failure mode.

## Examples

- Mid-migration: a file fails to compile after applying the migration pattern from step 2. Rather than patching the specific error, the agent steps back and re-examines whether the migration pattern is correct for this file's module type.
- Debugging: after three hypothesis cycles with no convergence, the agent re-examines the original problem statement to verify the initial scope was correct.
- Architecture: a sub-system design is flagged as infeasible by a reviewer. The agent revisits the constraint that drove the original design rather than forcing the infeasible approach to work.
- Code-generation failure: a generated function fails its tests. The agent re-examines the requirement (self-correction), updates the implementation, then runs the tests again before proceeding (execution verification). Both behaviors are required.
