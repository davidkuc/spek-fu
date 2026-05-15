---
id: skf-knowledge-devcontainer-guidelines
description: "Devcontainer-specific operational guidelines (DCR-01 through DCR-09) for output verification, tool authorization, runtime detection, watcher health, toolchain probing, and Python environment setup. Consult only when the resolved environment is a devcontainer."
deprecated: false
version: 1.0
---

# devcontainer-guidelines.md

> Apply these guidelines only when the resolved environment is a devcontainer.

---

## [DCR-01] File Verification

- After dispatching a subagent that should write output, verify the expected path with `read_file`.
- Do not use `file_search` as proof that a newly written file does or does not exist.
- If the first `read_file` attempt fails, retry once. If the second attempt fails, stop and surface the error.

---

## [DCR-02] Tool Authorization

- If `create_file`, `replace_string_in_file`, or `run_in_terminal` are visible but not authorized by your role, do not use them.
- Treat extra tool visibility as a platform artifact, not as permission.

---

## [DCR-03] Terminal Hygiene

- Do not use `!` inside double-quoted bash strings.
- Do not use `<()` process substitution.
- For structural tag detection, prefer `awk` with a line-start anchor over `grep`.

---

## [DCR-04] Buffer Synchronization

- Files written by subagents through terminal commands can reach disk before VS Code refreshes its buffers.
- Use `read_file` when you need the on-disk state.

---

## [DCR-05] Environment Detection

- Read `skf-config.json` and inspect the `environment` field.
- If the value is `auto`, detect devcontainer mode by checking `/.dockerenv` or the `REMOTE_CONTAINERS` environment variable.
- If the value is `devcontainer`, confirm `.devcontainer/devcontainer.json` exists. If it does not, hard fail and surface the mismatch.

---

## [DCR-06] inotify

- If file watchers appear unreliable, inspect `/proc/sys/fs/inotify/max_user_watches`.
- Treat values below `524288` as degraded mode and warn accordingly.

---

## [DCR-07] PowerShell

- Verify `pwsh` is on `PATH` before invoking framework scripts.
- Do not assume PowerShell availability in unfamiliar environments.

---

## [DCR-08] Toolchain Probing

- Before writing any ad hoc analysis script, probe available runtimes with `command -v <tool>`.
- The base devcontainer provides `git`, `gh`, `pwsh`, and `python3`. Node is not available by default.
- Preferred fallback scripting chain: `python3` → `jq` → `perl` → `awk` → `sed`.
- To discover installed packages: `dpkg -l | grep -E "(python|node|ruby|php|perl|jq)"`.
- To list VS Code extensions inside the container: `code --list-extensions` when the CLI is available.
- VS Code tool fallback map:
  - `file_search` → `read_file` + `list_dir`
  - `grep_search` → `run_in_terminal` with `grep`
  - `semantic_search` → `grep_search` + `read_file`
- Do not assume any scripting runtime is available without an explicit probe.
- See knowledge lesson L-072 for the full context and failure history.

---

## [DCR-09] Python Environment

- `python3` and `pip3` are available on `PATH`.
- Before running any retained Python script that imports `pyyaml`, run `pip3 install -r ai/scripts/python/requirements.txt`.
- VS Code Python extensions are not installed in the devcontainer by default.
- Do not assume pip packages are pre-installed. Use `pip3 show <package>` to verify availability.