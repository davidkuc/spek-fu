# Feature Format

How features are written in `spek-fu/project/project-docs/<area>.md`.

Areas and their ID prefixes: `area-registry.md`. Page layout: `../templates/project-docs-template.md`.

## What counts as a feature

One thing a user can do, see, or rely on. Fine-grained: expect roughly 15-40 per area.

Internal mechanics (atomic writes, sharding, canonical sort, caching) are **not** features. They appear only under `## Technical` — inside the subsection of the feature they serve, or under `### Shared Mechanics`.

For Testing & CI, "user" means the developer running the gate: a tier verdict, an artifact path, a failure report. Internal parser shapes are not features.

## Feature ID

`<PREFIX>-<NN>` — prefix from the area registry, number padded to two digits (`ENG-07`). Three digits past 99, without re-padding older IDs.

- Next ID = the highest number ever used in that area, live **or** retired, plus one.
- Permanent: a renamed feature keeps its ID. A removed ID is never reused.
- Split: the closest survivor keeps the ID, the rest get new ones.
- Merge: the lowest ID survives, the others are retired.

## Definition line

Written only in the feature's owner area, in ID order:

- **[ENG-07] Incremental re-scan** - Re-scanning after edits only touches what changed since the last commit.

One sentence.

## Reference line

An area that depends on a feature it does not own points at it instead of describing it:

- [SRV-04] → see [server.md](server.md) — gates the toolbar's Enrich button.

The trailing text says what *this* area does with the feature; it never repeats the feature's own sentence. Reference lines come after all owned features.

Use a reference line when the area's own users meet the feature through this area. For a purely technical dependency, cite the ID inline in the technical subsection instead — adding a reference line for every rule an area relies on would bury the list.

## Owner area

The area whose `code-docs` modules implement the feature. If several do, the area where the user first meets it. Exactly one owner per feature.

## Naming

An owner area names the **capability**: "AI enrichment of graph nodes".
A surface area names the **affordance**: "`pmt enrich` command".

That split is what stops a surface feature colliding with the owner feature it cites. A surface subsection citing no owner ID is a smell.

## Retirement

The last line of `## Functional` records removed IDs, permanently:

_Retired: ENG-07, ENG-19._

`_Retired: none._` when there are none. A retired ID never appears in the live list again. This line is what keeps the high-water mark after the highest ID is removed, so an ID can never be reused.

## Technical subsection

`### [ENG-07] Incremental re-scan` — ID and name copied exactly from the definition line. Says how the feature is built and links the `code-docs` modules that implement it. Never repeats the functional sentence.

A referenced (foreign-prefix) ID gets no subsection — its detail belongs in the owner area.

Features with nothing technical to add go on the last line of `### Shared Mechanics`:

_No separate technical detail: ENG-14, ENG-22._

`### Shared Mechanics` holds only mechanics local to that area. Anything cross-area must be a feature owned somewhere. Keep it to about one screen.

## Module links

Each feature subsection links the `code-docs` modules that implement it, as bare links inside the sentence.

The "what it covers" gloss is written **only** in `### Related Modules`. Writing it in both places is duplication.

## Evidence

State a feature when `spek-fu/project/code-docs` attests it. Read source only where code-docs are vague, contradictory, or the feature spans several modules.

A missing code-docs file is itself evidence. Check the source: if the source is gone too, document nothing. Never write a behavior that no longer exists.

If neither code-docs nor source attests it, mark `[NEEDS CLARIFICATION]` and leave it out.

## Limits

From `project.md` design pillar 2, reused here rather than restated as new limits:

- One sentence per feature bullet.
- Three sentences and five bullets per technical subsection.
