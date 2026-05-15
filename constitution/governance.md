# Governance

## Purpose

This file defines documentation governance principles for the project — specifically, the Single Source of Truth (SSOT) policy that governs how information is authored, referenced, and maintained across all project files.

---

## SSOT Principle

All project knowledge must have a **single authoritative source**. Other documents reference that source rather than duplicating content.

### Rules

The no-duplication and SSOT rules are defined authoritatively in `constitution/constitution.md` (see §No-Duplication Rule). This file does not restate them.

### What Counts as Acceptable Duplication

**Acceptable**: short (1–3 line) summaries with explicit SSOT pointers, where the pointer makes the derivation relationship visible.

**Prohibited**: full copy-paste of sections, tables reproduced without a reference marker, or content that will be silently out of sync when the SSOT changes.

**Centralized protocols**: the shared Dispatch Contract, Escalation Policy, and Bounded Retry Policy are centralized in `runbook-shared.md` and referenced (not duplicated) from each phase runbook. When those sections change, update `runbook-shared.md` and update the reference pointer in each phase runbook that links to it.

### Identifying and Designating SSOTs

- **`README.md`** (root): SSOT for quickstart guidance, orchestration entry points, and the human-readable workspace overview.
- **`constitution/`**: SSOT for constitution folder inventory and navigation.
- **`project/`**: SSOT for the project documentation inventory.
- **`ai/plugins/skf/knowledge/`**: SSOT for the knowledge inventory.
- **`ai/plugins/skf/templates/`**: SSOT for the template inventory.

---

## Deduplication Checklist

When adding content to any project file, verify:

- [ ] Is this information already documented somewhere? → Reference that location instead.
- [ ] If a summary is retained here for ergonomic reasons, is the SSOT marked explicitly with a pointer?
- [ ] If the SSOT changes, will this file's reference still be accurate (or will it break visibly)?
