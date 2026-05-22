---
name: "meta-knowledge-distillation"
description: "Runs a single combined flow that first consolidates duplicate or near-duplicate lessons in `knowledge-database.md`, then distills the cleaned lesson set into reusable PT0xx pattern files. USE FOR: cleaning up the knowledge database and promoting general-recurring lessons to patterns in one pass. DO NOT USE FOR: recording or retrieving lessons, implementing tasks, or modifying non-pattern files outside the distillation flow."
anti-scope: "Does NOT record or retrieve lessons — use meta-knowledge-manage for that. Does NOT implement tasks. Modifies `knowledge-database.md` (merging duplicates and removing promoted lessons) and `ai/plugins/skf/patterns/` (writing new pattern files). Does not modify any other files."
---

Consult the skill from `ai/plugins/skf/skills/meta-knowledge-distillation.md`. Execute its full protocol exactly as described.
