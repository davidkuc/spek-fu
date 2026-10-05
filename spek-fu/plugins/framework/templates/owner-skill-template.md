---
name: <plugin>-owner
description: "Read <plugin>-workflow.md to route a <plugin>-plugin request to the correct sub-skill(s), invoking more than one in sequence when several apply."
---

# <Plugin Title> Owner

Facade entrypoint for the <plugin> plugin: reads `<plugin>-workflow.md`'s current skill list and routes the user's request to whichever sub-skill(s) apply.

## When to use

Use for any request touching the <plugin> plugin's domain (per its `<plugin>-workflow.md`) or the plugin itself, when the caller hasn't already named a specific sub-skill. Sub-skills remain directly invocable; this skill is the recommended default when the right one isn't obvious.

<inputs>

## Inputs

- User's free-form request

</inputs>

<outputs>

## Outputs

- Results from whichever <plugin>-plugin sub-skill(s) were invoked
- A reported gap (no changes made) if no existing sub-skill covers the request

</outputs>

<constraints>

## Constitution

Read and follow the constitutional principles in `spek-fu\constitution\constitution.md`.

## Rules

- Never hardcode the plugin's skill list or trigger conditions in this file — always read them fresh from `<plugin>-workflow.md` (single source of truth, kept current by `<plugin>-maintenance`).
- Never force-fit a request into a mismatched skill. If none of the listed skills' trigger conditions match, report the gap and stop.
- May invoke more than one sub-skill for a single request when several triggers match.
- Do not duplicate a sub-skill's own logic — dispatch to it via the `Skill` tool rather than reimplementing its steps.

</constraints>

<behavioral_anchors>

## Pillars

**SSOT routing** — the routing table lives only in `<plugin>-workflow.md`; this skill reads it, never restates or caches it.

</behavioral_anchors>

<workflow>

## Steps

### 1. Read plugin context

Read `spek-fu/plugins/<plugin>/<plugin>-workflow.md` in full, in particular its "Choosing the right skill" section for the current list of skills and their trigger conditions.

### 2. Match the request

Compare the user's request against each skill's trigger condition from Step 1. A request may match one or several skills.

### 3. Handle no match

If no skill's trigger condition fits the request, report this gap to the user and stop. Do not guess or invoke an ill-fitting skill.

### 4. Dispatch

Invoke each matched skill in turn via the `Skill` tool, passing the user's request (and any input it needs).

### 5. Report

Summarize what each invoked skill did (or skipped) back to the user.

</workflow>

<done_conditions>

## Done Conditions

- Every skill invoked was one whose trigger condition, per the current `<plugin>-workflow.md`, matched the request.
- If no skill matched, the gap was reported and nothing was invoked.
- Results of all invoked skills are reported to the user.

</done_conditions>
