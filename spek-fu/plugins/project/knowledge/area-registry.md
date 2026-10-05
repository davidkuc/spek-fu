# Area Registry

Single source of truth for project-doc areas and their feature-ID prefixes.
Format rules: `feature-format.md`.

| Area | File | Prefix |
| --- | --- | --- |
| Projekty | `project-docs/projekty.md` | PRJ |
| Głosowanie | `project-docs/glosowanie.md` | GLS |
| Tożsamość | `project-docs/tozsamosc.md` | TOZ |
| Samorząd | `project-docs/samorzad.md` | SAM |
| Powiadomienia | `project-docs/powiadomienia.md` | PWD |
| Infrastruktura | `project-docs/infrastructure.md` | INF |
| Jakość i CI | `project-docs/jakosc-i-ci.md` | TST |

Files are relative to `spek-fu/project/`.

- A prefix is three uppercase letters, unique, and permanent — never changed, never reused after an area is retired.
- Adding or retiring an area is a plugin change: run `project-maintenance`.
- Which `code-docs` modules an area owns is **not** recorded here — each area file's `### Related Modules` list is that record.

## Area boundaries

Most areas are obvious from their name. Three need a stated rule:

- **Jakość i CI** — anything whose verdict is about the **project's own delivery machinery**: lint/orphan-code gates, the three test-pyramid runners, and the CI pipeline that blocks merges. Not the product a resident or urzędnik sees.
- **Infrastruktura** — deployment topology and cross-cutting runtime plumbing shared by all modules: the API/worker skeleton, startup/migrations/seed, background-task delivery, the OpenAPI contract and generated client, Docker Compose and Azure. `konfiguracja-azure.md` and `konfiguracja-lokalna.md` are detail pages of this same area, not separate areas — they carry no feature IDs of their own.
- **Powiadomienia** — the shared notifications module (in-app entries, badge/list, event fan-out); file is created once its first feature ships ([PF10](../project-features/PF10-powiadomienia-w-aplikacji.md)).

When the mechanism says one and the subject says the other, the subject wins.
