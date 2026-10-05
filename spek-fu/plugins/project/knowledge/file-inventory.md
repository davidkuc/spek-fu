# Project File Inventory

## Plugin Root

- `project-workflow.md` - glossary, skill selection guide, and command reference for the project plugin.

## skills/

- `project-owner/SKILL.md` - facade entrypoint that routes a request to the right project-plugin sub-skill(s) using `project-workflow.md`.
- `project-feature-draft/SKILL.md` - drafts a minimal project feature sketch and registers it in the roadmap.
- `project-functional-docs/SKILL.md` - syncs `project.md`, `roadmap.md`, and `project-docs/*.md` `## Functional` feature lists from a shipped spec feature.
- `project-technical-docs/SKILL.md` - syncs `technical.md` and `project-docs/*.md` `## Technical` sections, grouped under the feature IDs the functional skill minted.
- `project-user-flows/SKILL.md` - writes `user-flows/*.md` step-by-step scenarios from a shipped spec feature.
- `project-readme/SKILL.md` - maintains the repo-root `README.md` from repo scripts and config.
- `project-research/SKILL.md` - audit track; verifies the project docs against code-docs, source, and online sources and writes a research report.
- `project-devils-advocate/SKILL.md` - audit track; adversarially reviews the project docs and writes a risk-register report.
- `project-clarification/SKILL.md` - audit track; resolves ambiguity in the project docs through a budgeted multi-pass question loop.
- `project-documentation-analysis/SKILL.md` - audit track; read-only readiness check of the project docs that writes an analysis report.
- `project-maintenance/SKILL.md` - maintains the project plugin itself and audits its integrity.

## knowledge/

- `file-inventory.md` - one-sentence description of every file in the project plugin.
- `area-registry.md` - the project-doc areas with their file and permanent feature-ID prefix.
- `feature-format.md` - format spec for feature bullets, IDs, cross-area references, retirement, and technical subsections.
- `config.json` - paths and per-skill caps for the audit-track skills.
- `project-ambiguity-taxonomy.md` - ambiguity categories `project-clarification` scans the project docs against.
- `project-artifacts.md` - artifact path table and staleness chain used by `project-documentation-analysis`.

## templates/

- `project-docs-template.md` - template for a `project-docs/` area file: an ID-keyed feature list under Functional and a per-feature subsection under Technical.
- `project-feature-template.md` - template for a project feature sketch.
- `project-readme-template.md` - template for the repo-root `README.md`: required base sections plus optional ones.
- `project-research-report-template.md` - template for the `project-research` report.
- `project-devils-advocate-report-template.md` - template for the `project-devils-advocate` report.
- `documentation-analysis-report-template.md` - template for the `project-documentation-analysis` report.
- `roadmap-template.md` - template for `roadmap.md` phase/feature entries.
- `user-flow-template.md` - template for a `user-flows/*.md` scenario file.

## Outside Plugin Directory

- `spek-fu/project/project.md` - functional high-level overview of the project.
- `spek-fu/project/technical.md` - technical high-level overview of the project.
- `spek-fu/project/project-docs/` - per-area functional feature lists and per-feature technical detail.
- `spek-fu/project/roadmap.md` - roadmap of the project.
- `spek-fu/project/user-flows/` - step-by-step user scenario files.
- `README.md` (repo root) - developer command cheat sheet.
- `spek-fu/project/reports/` - audit reports written by the audit-track skills, one subfolder per skill.

<!-- Omit any folder section the plugin has no files in yet. Omit "Outside Plugin Directory" unless the plugin writes/reads files outside its own folder. -->
