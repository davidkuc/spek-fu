---
id: "needs-clarification-protocol"
description: "Canonical [NEEDS CLARIFICATION] marker syntax, placement, and propagation rules for spec-flow skills."
---

# NEEDS CLARIFICATION Protocol

## Purpose

Defines the single-source-of-truth protocol for creating, carrying, and reporting `[NEEDS CLARIFICATION]` markers across spec-flow artifacts.

## Marker Syntax

Use this exact inline form:

`[NEEDS CLARIFICATION: <specific question>]`

Rules:
- The question MUST be specific and actionable.
- Place the marker at the exact point of uncertainty in the artifact.
- Do not abbreviate or paraphrase the marker format.

## Origination Rules

- Any skill may create a marker when required context is ambiguous and cannot be resolved from the available artifacts.
- Skills MUST prefer an explicit marker over an invented decision.
- Skills that are explicitly interactive may resolve their own newly created markers before completion.

## Propagation Rules

When a downstream skill encounters markers already present in upstream artifacts, it MUST NOT silently resolve, delete, or ignore them.

The downstream skill MUST:
1. Record each carried marker in a `## Carried Clarifications` section of its own output artifact when that artifact is report-shaped.
2. If the skill does not write a report-shaped artifact, surface the carried markers in its completion or blocked report.
3. Proceed on a best-effort basis using only grounded context, unless the missing artifact itself is required.
4. Surface the carried-clarification count in its completion or blocked report.

## Required vs Optional Context

- A missing required artifact is a `blocked` condition.
- A present artifact that contains `[NEEDS CLARIFICATION]` markers is not, by itself, grounds to halt. Carry and report the ambiguity instead.