# [Area Name]

## Functional

<!-- Owned by project-functional-docs. project-technical-docs must not edit this section. -->
<!-- Format rules: ../../plugins/project/knowledge/feature-format.md -->
<!-- ID prefix for this area: ../../plugins/project/knowledge/area-registry.md -->

- **[XXX-01] [Feature name]** - [What the user can do, see, or rely on. One sentence.]
- **[XXX-02] [Feature name]** - [One sentence.]
- [YYY-05] → see [other-area.md](other-area.md) — [what this area does with it.]

[Optional short prose after the list, only if the list needs framing.]

_Retired: none._

## Technical

<!-- Owned by project-technical-docs. It must never add, remove, rename, or renumber an ID. -->

[Short preamble: this area's layering or architecture, a few lines.]

### [XXX-01] [Feature name]

[How this one feature is built, linking the code-docs modules that implement it. Never repeat
the functional sentence. At most 3 sentences and 5 bullets.]

### [XXX-02] [Feature name]

[...]

### Shared Mechanics

[Technical detail that serves no single feature, local to this area.]

_No separate technical detail: none._

### Related Modules

<!-- The code-docs modules this area owns. Every module is owned by exactly one area. -->

- [code-docs slug](../code-docs/<slug>.md) — [what it covers]

## Related User Flows

<!-- Owned by project-functional-docs. -->

- [user flow](../user-flows/<file>.md) — [what it covers]
