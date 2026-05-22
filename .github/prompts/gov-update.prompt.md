---
name: "gov-update"
description: "Applies governance file updates based on changed files or an orchestration plan. Reasons about which governance files need updating, proposes each change for per-change user approval, applies approved changes, then always runs sync-index-files.py followed by sync-index-files.py --check. USE FOR: keeping constitution, project docs, and AI framework files aligned with implemented changes."
anti-scope: "Does NOT perform analysis, modify source code, or touch iteration in-progress files."
---

Consult the skill from `ai/plugins/skf/skills/gov-update.md`. Execute its full protocol exactly as described.
