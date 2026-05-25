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
