---
id: "skill-meta-rules"
description: "Shared operational meta-rules for spec-flow skills: obey constraints, stay in scope, and avoid unrequested behavior."
---

# Skill Meta Rules

Apply these rules in addition to each skill's local constraints:

- Before producing output, verify the planned output complies with the skill's `<constraints>` section.
- Implement EXACTLY and ONLY what the skill defines.
- Do not add extra features, unrequested changes, or side effects.
- When an input path is unresolved, use the canonical branch-detection procedure rather than guessing.
- Use the canonical paginated-read procedure whenever an artifact may exceed a single `read_file` response.