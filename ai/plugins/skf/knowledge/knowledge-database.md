# SKF Knowledge Database

Verified lessons captured from framework operations.


## L-001: Referenced Skill Artifacts Must Be Co-Created

*Consolidates: original L-001, L-015*

**Tags**: `framework`, `skills`, `configuration`, `files`

**Trigger**: Skills referenced co-located files that didn't exist on disk, causing hard halts or undefined behavior.

**Context**: This lesson captures the operational context for the trigger and guidance below.

**Solution**: Any artifact referenced by a skill must be created atomically with the skill. Embed content directly in skill or co-create the physical file in the same commit — documentation and filesystem must agree.

---

## L-002: Terminal & Bash Command Hygiene

*Consolidates: original L-003, L-004, L-007*

**Tags**: `framework`, `scripts`, `files`

**Trigger**: Bash commands using `!`, `<(...)` process substitution, and simple `grep` patterns caused crashes, stalls, and false positives in the VS Code terminal.

**Context**: This lesson captures the operational context for the trigger and guidance below.

**Solution**:
1. **Never use `!` inside double-quoted strings** — replace `if ! cmd; then` with `if cmd; then :; else ...; fi` to avoid history expansion.
2. **Avoid `<(...)` process substitution** — use explicit `for` loops or write complex logic to a script file and execute with `bash script.sh`.
3. **Use line-start anchored awk for structural XML tag detection** — `awk '/^<constraints>/{found=1} END{exit !found}' "$f"` is immune to inline backtick prose references.

---

## L-003: Batch Sizing & Parallel Dispatch Safety

*Consolidates: original L-005, L-014, L-038, L-039, L-063, L-077*

**Tags**: `framework`, `dispatch`, `subagents`, `waves`, `parallelism`

**Trigger**: Batch sizing, parallel dispatch conflicts, and additive bloat caused agent failures and required correction waves.

**Context**: This lesson captures the operational context for the trigger and guidance below.

**Solution**:
1. **File count limits**: ~4 files/batch for medium files (150–300 lines); 1–2 files when any file >400 lines.
2. **Large waves**: Split 20+ file waves into independent batches of 2–4 files, dispatched and verified separately.
3. **Parallel dispatch is safe** when each task targets a distinct directory or file type — no serialization needed.
4. **File conflict check before parallel waves** — serialize tasks targeting the same file or combine into a single dispatch.
5. **Heading/naming conventions before parallel dispatch** — establish canonical names in the dispatch manifest TASK section to prevent divergent output.
6. **Size gate**: Check line count before dispatch; prevent additions if file ≥285 lines (near the 300-line target).

---

## L-004: Use git status Over get_changed_files

*Consolidates: original L-069*

**Tags**: `framework`, `tools`, `git`

**Trigger**: `get_changed_files` returned empty results despite actual workspace changes.

**Context**: This lesson captures the operational context for the trigger and guidance below.

**Solution**: When `get_changed_files` looks suspicious, run `git -C <repo-root> status --short --branch` and treat the filesystem as authoritative; use `git diff --name-only HEAD` for a clean changed-file list.

---

## L-005: Split Delete and Recreate Into Separate Operations

*Consolidates: original L-070*

**Tags**: `framework`, `files`

**Trigger**: A patch tried to delete and recreate the same file path in one operation, failing with a duplicate-path error.

**Context**: This lesson captures the operational context for the trigger and guidance below.

**Solution**: Split into two sequential operations — first delete, then create. For full-file replacement, use a pure update patch or plan delete/create as separate steps.

---

## L-006: Orphaned Prompt Files Must Be Cleaned After Skill Deletion

**Tags**: `framework`, `skills`, `prompts`, `cleanup`

**Trigger**: After deleting skill files, their corresponding .prompt.md files in .github/prompts/ remained as orphans.

**Context**: The generate-prompt-files.py script only creates/overwrites — it does not delete, leaving orphaned files that were detected in final QA.

**Solution**: When deleting skills in a wave, also delete their corresponding .prompt.md files in the same wave, or update generate-prompt-files.py to delete .prompt.md files whose skill-id is not in skills-index.json.

---

## L-007: Index Updates Must Follow All Artifact Changes

**Tags**: `framework`, `index`, `configuration`, `prompts`

**Trigger**: prompts-index.json was not updated during execution waves, leaving stale entries for deleted skills and missing new entries.

**Context**: Inconsistency between .github/prompts/ directory content and the index was caught in final QA.

**Solution**: Add prompts-index.json updates to the same wave as skills-index.json update, or integrate prompts-index.json generation into generate-prompt-files.py.

---

## L-008: Cross-File Reference Validation Required Before Skill Deletion

**Tags**: `framework`, `skills`, `validation`, `references`

**Trigger**: wave-summary-template.md, skill-tags.md, and orch-skill-resolve.md referenced a deleted skill (orch-wave-summary), undetected by execution wave checks.

**Context**: Auxiliary files beyond runbooks often contain skill references that are not automatically updated.

**Solution**: Before considering a skill deletion complete, grep for its ID across ALL framework files (not just runbooks), or add a cross-file reference check to the deletion wave scope.

---

## L-009: impl-implement Hard 3-File Ceiling

**Tags**: `framework`, `dispatch`, `skills`, `impl-implement`, `batching`

**Trigger**: Dispatching impl-implement with 4 files caused a redirect/rejection with "file count > 3 threshold" gate.

**Context**: Lesson #3 previously stated "~4 files/batch for medium files (150-300 lines)", but impl-implement enforces a hard 3-file ceiling regardless of file size.

**Solution**: When using impl-implement, plan wave batches at ≤3 files per dispatch. For >3 files, split into 2-file or 3-file sub-batches dispatched in parallel.

---

## L-010: Duplicate YAML Keys After Additive Frontmatter Edits

**Tags**: `framework`, `yaml`, `frontmatter`, `skills`, `validation`

**Trigger**: Wave 3 verification caught 2 files with duplicate `inputs:` keys in YAML frontmatter after impl-implement added env.

**Context**: When appending to an existing YAML array, impl-implement may create a second identical key instead of extending—invalid YAML that silently overwrites the first block.

**Solution**: After any bulk YAML frontmatter append wave, run verification to check for duplicate YAML keys. Correction pattern: read full YAML, merge arrays into single key, remove duplicate.

---

## L-011: skills-index.json Must Be Regenerated After Bulk Skill Edits

**Tags**: `framework`, `index`, `configuration`, `skills`, `validation`

**Trigger**: Final QA flagged that skills-index.json inputs arrays were stale after adding env to all 21 skill frontmatters.

**Context**: skills-index.json caches inputs arrays from skill frontmatters. Bulk edits to skill inputs require explicit regeneration.

**Solution**: Run `gov-update` with `scope: index-sync, target: skill-index` as a mandatory wave immediately after any batch that modifies skill YAML frontmatter inputs.

---

## L-012: skf-config.json Safely Removable From Orchestrator Allowlist Post-Initialize

**Tags**: `framework`, `orchestration`, `configuration`, `security`, `allowlist`

**Trigger**: Direct `read_file` access to skf-config.json was previously needed as bootstrap step but is no longer required after orch-initialize.

**Context**: orch-initialize reads skf-config.json and returns config values in init-result.md (an allowlisted subagent output). Keeping skf-config.json in the allowlist creates unnecessary bypass potential.

**Solution**: Remove skf-config.json from orchestrator read_file allowlist once orch-initialize is verified. Config values are accessible via `.orchestration-temp/init-result.md`.

---
