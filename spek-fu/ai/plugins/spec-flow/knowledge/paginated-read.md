---
id: "paginated-read"
description: "Canonical multi-pass read_file procedure for spec-flow skills. Use when reading any artifact that may exceed a single tool response."
---

# Paginated Read

## Purpose

Defines the canonical multi-pass `read_file` procedure for spec-flow skills. Apply this procedure whenever a required artifact, template, or knowledge file may exceed a single tool response.

## Procedure

1. Start with `read_file` from line 1 using a generous page size.
2. If the response reaches the page boundary or is otherwise truncated, advance `startLine` to the next unread line and call `read_file` again.
3. Repeat until the response is shorter than the page size and end-of-file is confirmed.
4. Treat the artifact as unread until all pages have been collected.

## Rules

- NEVER act on a partially read artifact.
- ALWAYS apply the same procedure to templates, knowledge files, and required upstream artifacts.
- Single-read access is acceptable only when the artifact is known to fit fully in one response.