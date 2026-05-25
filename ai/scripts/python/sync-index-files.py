#!/usr/bin/env python3
"""Spek-Fu — Sync all *-index.json files with actual filesystem state.

For each registered *-index.json, scans the corresponding folder and:
  - Adds entries for new files/folders with deterministic fields filled in
    and description left empty ("") for AI to complete.
  - Preserves existing entries (description and all semantic fields retained).
  - Removes entries for paths no longer present on disk (with a warning).
  - Extracts deterministic data from YAML frontmatter where available
    (skills, patterns, prompts, agents).

Usage:
    python3 ai/scripts/python/sync-index-files.py
    python3 ai/scripts/python/sync-index-files.py --check
    python3 ai/scripts/python/sync-index-files.py --dry-run
    python3 ai/scripts/python/sync-index-files.py --index constitution/constitution-index.json
    python3 ai/scripts/python/sync-index-files.py --verbose

Options:
    --check       Validate index drift without writing any files.
    --dry-run     Report changes without writing any files.
    --index PATH  Sync only the specified index file (path relative to repo root).
    --verbose     Print all processed entries, not just additions and removals.

Exit codes:
    0  All synced successfully.
    1  One or more index files could not be processed.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Allow importing common.py from the same directory.
sys.path.insert(0, str(Path(__file__).parent))
import common

# Repo root is three directories above this script:
#   ai/scripts/python/sync-index-files.py -> ai/scripts/python -> ai/scripts -> ai -> root
REPO_ROOT = Path(__file__).resolve().parents[3]


# ── Index catalog ───────────────────────────────────────────────────────────────
# Each entry describes one *-index.json and how to sync it.
#
# Keys:
#   index_file   : path relative to REPO_ROOT
#   folder       : folder path relative to REPO_ROOT (empty string = repo root)
#   excluded     : basenames to skip when scanning the folder (beyond the index
#                  file itself, which is always skipped automatically)
#   builder      : child-entry builder to use
#                  "standard" | "python" | "skills" | "patterns" | "prompts" | "agents"
#   preserve_top : extra top-level JSON keys to carry through verbatim
#                  (e.g. "tag-library")

CATALOG: list[dict[str, Any]] = [
    # ── Repo root ──────────────────────────────────────────────────────────────
    {
        "index_file": "skf-root-index.json",
        "folder": "",
        "excluded": [
            ".devcontainer", ".git", ".gitattributes", ".gitignore",
            ".vscode",
            "plan.md",
            "skf-root-index.json",  # the index itself (belt-and-suspenders)
        ],
        "builder": "standard",
        "preserve_top": [],
    },


    # ── .github/ ──────────────────────────────────────────────────────────────
    {
        "index_file": ".github/github-index.json",
        "folder": ".github",
        "excluded": [],
        "builder": "standard",
        "preserve_top": [],
    },
    {
        "index_file": ".github/agents/agents-index.json",
        "folder": ".github/agents",
        "excluded": [],
        "builder": "agents",
        "preserve_top": [],
    },
    {
        "index_file": ".github/prompts/prompts-index.json",
        "folder": ".github/prompts",
        "excluded": [],
        "builder": "prompts",
        "preserve_top": [],
    },
    # ── ai/ ───────────────────────────────────────────────────────────────────
    {
        "index_file": "ai/ai-index.json",
        "folder": "ai",
        "excluded": [],
        "builder": "standard",
        "preserve_top": [],
    },
    {
        "index_file": "ai/scripts/scripts-index.json",
        "folder": "ai/scripts",
        "excluded": [],
        "builder": "standard",
        "preserve_top": [],
    },
    {
        "index_file": "ai/scripts/python/python-index.json",
        "folder": "ai/scripts/python",
        "excluded": ["__pycache__"],
        "builder": "python",
        "preserve_top": [],
    },
    # ── ai/plugins/ ───────────────────────────────────────────────────────────
    # plugins-index.json is always static; per-plugin entries are discovered
    # dynamically by _discover_plugin_catalogs() below.
    {
        "index_file": "ai/plugins/plugins-index.json",
        "folder": "ai/plugins",
        "excluded": [],
        "builder": "standard",
        "preserve_top": [],
    },
]

# Builder and excluded defaults for well-known plugin sub-folder names.
# Entries not present here default to the "standard" builder.
_FOLDER_BUILDER: dict[str, str] = {
    "skills":   "skills",
    "patterns": "patterns",
}


def _discover_plugin_catalogs(repo_root: Path) -> list[dict[str, Any]]:
    """Return CATALOG-compatible entries for every plugin in plugins-index.json.

    Reads ai/plugins/plugins-index.json, then for each plugin reads its root
    ``<name>-index.json`` to discover sub-folders.  Produces one entry for the
    plugin root index and one entry per sub-folder index found in the plugin's
    children list.

    Special handling (derived from the actual index files on disk):
    - ``skills`` sub-folders: uses the ``skills`` builder; ``config.json`` is
      excluded; ``preserve_top`` includes ``"tag-library"`` when the
      sub-index carries that field.
    - ``patterns`` sub-folders: uses the ``patterns`` builder; ``pattern-tags.md``
      is excluded when present on disk; ``preserve_top`` includes
      ``"tag-library"`` when the sub-index carries that field.
    - All other sub-folders: standard builder, no exclusions.
    """
    entries: list[dict[str, Any]] = []
    plugins_index_path = repo_root / "ai/plugins/plugins-index.json"
    try:
        plugins_index = common.load_json_file(plugins_index_path)
    except Exception as exc:
        print(f"[WARN] Cannot read plugins-index.json: {exc}", file=sys.stderr)
        return entries

    for plugin in plugins_index.get("children", []):
        plugin_name = plugin.get("name", "")
        if not plugin_name:
            continue

        plugin_folder = f"ai/plugins/{plugin_name}"
        plugin_index_rel = f"{plugin_folder}/{plugin_name}-index.json"

        # Plugin root index entry.
        entries.append({
            "index_file": plugin_index_rel,
            "folder": plugin_folder,
            "excluded": [],
            "builder": "standard",
            "preserve_top": [],
        })

        # Read the plugin's root index to discover sub-folder indexes.
        try:
            plugin_index = common.load_json_file(repo_root / plugin_index_rel)
        except Exception:
            continue

        for child in plugin_index.get("children", []):
            child_name      = child.get("name", "")
            child_index_rel = child.get("index", "")
            if not child_name or not child_index_rel:
                continue

            child_folder  = f"{plugin_folder}/{child_name}"
            builder       = _FOLDER_BUILDER.get(child_name, "standard")
            excluded: list[str] = []
            preserve_top: list[str] = []

            if child_name == "skills":
                excluded = ["config.json"]
                try:
                    sub_idx = common.load_json_file(repo_root / child_index_rel)
                    if "tag-library" in sub_idx:
                        preserve_top = ["tag-library"]
                except Exception:
                    pass

            elif child_name == "patterns":
                if (repo_root / child_folder / "pattern-tags.md").exists():
                    excluded = ["pattern-tags.md"]
                try:
                    sub_idx = common.load_json_file(repo_root / child_index_rel)
                    if "tag-library" in sub_idx:
                        preserve_top = ["tag-library"]
                except Exception:
                    pass

            entries.append({
                "index_file":   child_index_rel,
                "folder":       child_folder,
                "excluded":     excluded,
                "builder":      builder,
                "preserve_top": preserve_top,
            })

    return entries


# Extend the static catalog with dynamically discovered plugin entries at import
# time so that all code paths (including --index filtering in main()) see the
# full catalog without extra wiring.
CATALOG.extend(_discover_plugin_catalogs(REPO_ROOT))


# ── Path helpers ────────────────────────────────────────────────────────────────

def child_rel_path(folder: str, name: str, is_dir: bool) -> str:
    """Build the relative-from-root path for a child entry.

    Files:   "constitution/constitution.md"
    Folders: "constitution/"  (trailing slash convention)
    Root children: "README.md" / "constitution/"
    """
    prefix = (folder + "/") if folder else ""
    return (prefix + name + "/") if is_dir else (prefix + name)


def compute_index_pointer(folder: str, name: str) -> str | None:
    """Return the sub-index path for a folder child if the file exists on disk.

    Convention: <child_path>/<stem_without_leading_dot>-index.json
    E.g. folder="" name=".github" → ".github/github-index.json"
         folder="ai/plugins" name="skf" → "ai/plugins/skf/skf-index.json"

    Returns None when the computed path does not exist.
    """
    stem = name.lstrip(".")  # ".github" → "github"
    prefix = (folder + "/") if folder else ""
    pointer = f"{prefix}{name}/{stem}-index.json"
    return pointer if (REPO_ROOT / pointer).exists() else None


# ── Folder scanner ──────────────────────────────────────────────────────────────

def scan_folder(
    folder: str,
    excluded: list[str],
    index_filename: str,
) -> dict[str, bool]:
    """Return a dict of {basename: is_dir} for direct children of *folder*.

    Always excludes *index_filename* and every name in *excluded*.
    Hidden entries (names starting with ".") within non-root folders are
    included only when they match a name that is already tracked (i.e. the
    caller's existing entries drive visibility for hidden items).  At the repo
    root hidden items are treated the same as any other item — the CATALOG
    exclusion list governs what is visible there.
    """
    base = REPO_ROOT if not folder else REPO_ROOT / folder
    skip = set(excluded) | {index_filename}
    return {
        child.name: child.is_dir()
        for child in base.iterdir()
        if child.name not in skip
    }


# ── Frontmatter helpers ─────────────────────────────────────────────────────────

def _fm(file_rel_path: str) -> dict:
    """Load YAML frontmatter from a file; return {} on any failure."""
    try:
        result = common.parse_frontmatter(REPO_ROOT / file_rel_path)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _python_description(file_rel_path: str) -> str:
    """Extract the first line of the module docstring from a Python file."""
    try:
        content = (REPO_ROOT / file_rel_path).read_text(encoding="utf-8")
        m = re.search(r'^"""(.*?)"""', content, re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                stripped = line.strip()
                if stripped:
                    return stripped
    except Exception:
        pass
    return ""


# ── Entry builders ──────────────────────────────────────────────────────────────
# Each builder receives:
#   folder    : folder path relative to repo root
#   name      : child basename
#   is_dir    : True if the child is a directory
#   existing  : the current index entry dict (None for brand-new items)
# Returns a new entry dict.

def build_standard_entry(
    folder: str,
    name: str,
    is_dir: bool,
    existing: dict | None,
) -> dict[str, Any]:
    path = child_rel_path(folder, name, is_dir)
    entry: dict[str, Any] = {
        "name": existing["name"] if existing else name,
        "type": "folder" if is_dir else "file",
        "description": (existing or {}).get("description", ""),
        "path": path,
    }
    if is_dir:
        ptr = compute_index_pointer(folder, name)
        if ptr:
            entry["index"] = ptr
        elif existing and "index" in existing:
            # Preserve a pointer even if the sub-index does not yet exist.
            entry["index"] = existing["index"]
    return entry


def build_python_entry(
    folder: str,
    name: str,
    is_dir: bool,
    existing: dict | None,
) -> dict[str, Any]:
    """Like standard but auto-extracts description from Python docstrings."""
    path = child_rel_path(folder, name, is_dir)
    # Preserve or derive the display name (convention: strip .py for scripts).
    if existing:
        display_name = existing["name"]
    elif name.endswith(".py"):
        display_name = Path(name).stem
    else:
        display_name = name

    # Auto-fill description from docstring for new .py files only.
    desc = (existing or {}).get("description", "")
    if not desc and not is_dir and name.endswith(".py"):
        desc = _python_description(path)

    entry: dict[str, Any] = {
        "name": display_name,
        "type": "folder" if is_dir else "file",
        "description": desc,
        "path": path,
    }
    if is_dir:
        ptr = compute_index_pointer(folder, name)
        if ptr:
            entry["index"] = ptr
        elif existing and "index" in existing:
            entry["index"] = existing["index"]
    return entry


def build_skills_entry(
    folder: str,
    name: str,
    is_dir: bool,
    existing: dict | None,
) -> dict[str, Any]:
    """Extract all skill metadata from YAML frontmatter."""
    if is_dir:
        return build_standard_entry(folder, name, is_dir, existing)

    path = child_rel_path(folder, name, is_dir)
    fm = _fm(path)
    ex = existing or {}

    def _get(fm_key: str, default: Any = "") -> Any:
        """Return frontmatter value, falling back to existing entry, then default."""
        if fm_key in fm:
            return fm[fm_key]
        return ex.get(fm_key, default)

    skill_id = _get("id", Path(name).stem)

    return {
        "id": skill_id,
        "type": "file",
        "description": _get("description", ""),
        "path": path,
        "version": _get("version", ""),
        "tags": _get("tags", []),
        "inputs": _get("inputs", []),
        "outputs": _get("outputs", []),
        "dispatch-variant": _get("dispatch-variant", ""),
        "anti-scope": _get("anti-scope", ""),
        "name": skill_id,
        "recommended-tier": _get("recommended-tier", ""),
    }


def build_patterns_entry(
    folder: str,
    name: str,
    is_dir: bool,
    existing: dict | None,
) -> dict[str, Any]:
    """Extract description and recommended-tier from frontmatter; name = pattern ID."""
    if is_dir:
        return build_standard_entry(folder, name, is_dir, existing)

    path = child_rel_path(folder, name, is_dir)
    fm = _fm(path)
    ex = existing or {}

    # Pattern ID: prefer frontmatter "id", fall back to existing "name", then
    # derive from the filename prefix (e.g. "PT001-divide-and-conquer.md" → "PT001").
    if "id" in fm:
        pattern_id = str(fm["id"])
    elif "name" in ex:
        pattern_id = ex["name"]
    else:
        m = re.match(r"^([A-Z]{2}\d+)", name)
        pattern_id = m.group(1) if m else Path(name).stem

    return {
        "name": pattern_id,
        "type": "file",
        "path": path,
        "description": fm.get("description", ex.get("description", "")),
        "recommended-tier": fm.get("recommended-tier", ex.get("recommended-tier", "")),
    }


def build_prompts_entry(
    folder: str,
    name: str,
    is_dir: bool,
    existing: dict | None,
) -> dict[str, Any]:
    """Extract description from frontmatter; name = filename."""
    if is_dir:
        return build_standard_entry(folder, name, is_dir, existing)

    path = child_rel_path(folder, name, is_dir)
    fm = _fm(path)
    ex = existing or {}

    return {
        "name": ex.get("name", name),
        "type": "file",
        "description": fm.get("description", ex.get("description", "")),
        "path": path,
    }


def build_agents_entry(
    folder: str,
    name: str,
    is_dir: bool,
    existing: dict | None,
) -> dict[str, Any]:
    """Extract description from frontmatter; name = filename."""
    if is_dir:
        return build_standard_entry(folder, name, is_dir, existing)

    path = child_rel_path(folder, name, is_dir)
    fm = _fm(path)
    ex = existing or {}

    return {
        "name": ex.get("name", name),
        "type": "file",
        "description": fm.get("description", ex.get("description", "")),
        "path": path,
    }


BUILDERS: dict[str, Any] = {
    "standard": build_standard_entry,
    "python":   build_python_entry,
    "skills":   build_skills_entry,
    "patterns": build_patterns_entry,
    "prompts":  build_prompts_entry,
    "agents":   build_agents_entry,
}

SKILL_INDEX_FIELDS: tuple[str, ...] = (
    "id",
    "description",
    "path",
    "version",
    "tags",
    "inputs",
    "outputs",
    "dispatch-variant",
    "anti-scope",
    "name",
    "recommended-tier",
)


def _format_issue_value(value: Any) -> str:
    """Return a stable single-value representation for validation reports."""
    return common.format_json_output(value)


def _expected_skill_entry(folder: str, name: str, is_dir: bool) -> dict[str, Any]:
    """Return the deterministic skill entry derived from disk + frontmatter."""
    return build_skills_entry(folder, name, is_dir, None)


def validate_index(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate one index file against disk and source frontmatter."""
    index_rel = spec["index_file"]
    folder = spec["folder"]
    excluded = spec["excluded"]
    builder_name = spec["builder"]
    index_path = REPO_ROOT / index_rel

    current = common.load_json_file(index_path)
    existing_children: list[dict[str, Any]] = current.get("children", [])
    disk_items = scan_folder(folder, excluded, index_path.name)

    disk_path_to_name: dict[str, str] = {
        child_rel_path(folder, name, is_dir): name
        for name, is_dir in disk_items.items()
    }
    disk_path_to_isdir: dict[str, bool] = {
        child_rel_path(folder, name, is_dir): is_dir
        for name, is_dir in disk_items.items()
    }
    disk_paths = set(disk_path_to_name)
    indexed_paths = {entry.get("path", "") for entry in existing_children if "path" in entry}

    issues: list[dict[str, Any]] = []

    for entry in existing_children:
        path = entry.get("path", "")
        if not path:
            continue

        if path not in disk_paths:
            issues.append({
                "kind": "missing-source",
                "index": index_rel,
                "path": path,
                "message": "Indexed path is missing on disk.",
            })
            continue

        if builder_name != "skills" or entry.get("type") != "file":
            continue

        name = disk_path_to_name[path]
        is_dir = disk_path_to_isdir[path]
        expected = _expected_skill_entry(folder, name, is_dir)
        field_diffs: list[dict[str, Any]] = []

        for field in SKILL_INDEX_FIELDS:
            actual_value = entry.get(field)
            expected_value = expected.get(field)
            if actual_value != expected_value:
                field_diffs.append({
                    "field": field,
                    "index": actual_value,
                    "source": expected_value,
                })

        if field_diffs:
            issues.append({
                "kind": "frontmatter-drift",
                "index": index_rel,
                "path": path,
                "message": "Indexed skill metadata disagrees with source frontmatter.",
                "diffs": field_diffs,
            })

    for orphan_path in sorted(disk_paths - indexed_paths):
        issues.append({
            "kind": "orphan-file",
            "index": index_rel,
            "path": orphan_path,
            "message": "Filesystem entry has no index entry.",
        })

    return issues


def validate_skill_id_collisions(catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return all duplicate skill IDs found across skill indexes."""
    locations_by_id: dict[str, list[dict[str, str]]] = {}

    for spec in catalog:
        if spec["builder"] != "skills":
            continue

        index_rel = spec["index_file"]
        current = common.load_json_file(REPO_ROOT / index_rel)
        for entry in current.get("children", []):
            if entry.get("type") != "file":
                continue
            skill_id = entry.get("id")
            path = entry.get("path")
            if not skill_id or not path:
                continue
            locations_by_id.setdefault(skill_id, []).append({
                "index": index_rel,
                "path": path,
            })

    issues: list[dict[str, Any]] = []
    for skill_id, locations in sorted(locations_by_id.items()):
        if len(locations) < 2:
            continue
        issues.append({
            "kind": "skill-id-collision",
            "skill_id": skill_id,
            "message": "Skill ID is duplicated across skill indexes.",
            "locations": locations,
        })
    return issues


def validate_catalog(catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate all requested indexes and return accumulated issues."""
    issues: list[dict[str, Any]] = []

    for spec in catalog:
        try:
            issues.extend(validate_index(spec))
        except FileNotFoundError as exc:
            issues.append({
                "kind": "missing-index",
                "index": spec["index_file"],
                "message": str(exc),
            })
        except Exception as exc:
            issues.append({
                "kind": "validation-error",
                "index": spec["index_file"],
                "message": str(exc),
            })

    issues.extend(validate_skill_id_collisions(catalog))
    return issues


def print_validation_report(issues: list[dict[str, Any]]) -> None:
    """Print validation issues in a readable, diff-oriented format."""
    if not issues:
        print("\nValidation passed: no index drift detected.")
        return

    print("\nValidation failed:")
    for issue in issues:
        kind = issue["kind"]
        if kind == "frontmatter-drift":
            print(f"  [DRIFT] {issue['index']} :: {issue['path']}")
            for diff in issue["diffs"]:
                print(f"    field: {diff['field']}")
                print(f"      index : {_format_issue_value(diff['index'])}")
                print(f"      source: {_format_issue_value(diff['source'])}")
        elif kind == "skill-id-collision":
            print(f"  [COLLISION] skill id '{issue['skill_id']}'")
            for location in issue["locations"]:
                print(f"    - {location['index']} :: {location['path']}")
        else:
            label = issue.get("index", "<unknown-index>")
            path = issue.get("path")
            suffix = f" :: {path}" if path else ""
            print(f"  [{kind.upper()}] {label}{suffix}")
            print(f"    {issue['message']}")


# ── Core sync ───────────────────────────────────────────────────────────────────

def sync_index(
    spec: dict[str, Any],
    dry_run: bool,
    verbose: bool,
) -> tuple[bool, int, int, int]:
    """Sync a single index file described by *spec*.

    Returns:
        (ok, added, removed, unchanged)
    """
    index_rel = spec["index_file"]
    folder    = spec["folder"]
    excluded  = spec["excluded"]
    builder   = BUILDERS[spec["builder"]]
    preserve_top: list[str] = spec.get("preserve_top", [])

    index_path     = REPO_ROOT / index_rel
    index_filename = index_path.name

    # ── Load existing index ──────────────────────────────────────────────────
    try:
        current: dict = common.load_json_file(index_path)
    except FileNotFoundError:
        print(f"  [SKIP] {index_rel}: file not found on disk", file=sys.stderr)
        return False, 0, 0, 0
    except Exception as exc:
        print(f"  [ERROR] {index_rel}: {exc}", file=sys.stderr)
        return False, 0, 0, 0

    existing_children: list[dict] = current.get("children", [])

    # Key existing entries by their path value for O(1) lookup.
    existing_by_path: dict[str, dict] = {
        e["path"]: e for e in existing_children if "path" in e
    }

    # ── Scan disk ────────────────────────────────────────────────────────────
    disk_items: dict[str, bool] = scan_folder(folder, excluded, index_filename)

    # Compute full relative paths for everything found on disk.
    disk_path_to_name: dict[str, str] = {
        child_rel_path(folder, name, is_dir): name
        for name, is_dir in disk_items.items()
    }
    disk_path_to_isdir: dict[str, bool] = {
        child_rel_path(folder, name, is_dir): is_dir
        for name, is_dir in disk_items.items()
    }
    disk_paths = set(disk_path_to_name)

    added = removed = unchanged = 0
    new_children: list[dict] = []

    # ── Pass 1: iterate existing entries in original order ───────────────────
    # Update deterministic fields; preserve descriptions; remove stale entries.
    seen_paths: set[str] = set()

    for entry in existing_children:
        path = entry.get("path", "")
        seen_paths.add(path)

        if path not in disk_paths:
            print(f"  [REM]  {path}  (no longer on disk)")
            removed += 1
            continue

        name   = disk_path_to_name[path]
        is_dir = disk_path_to_isdir[path]
        updated = builder(folder, name, is_dir, entry)
        new_children.append(updated)

        if verbose:
            print(f"  [OK]   {path}")
        unchanged += 1

    # ── Pass 2: append new items (on disk, not yet in index) ─────────────────
    for path in sorted(disk_paths):
        if path in seen_paths:
            continue
        name   = disk_path_to_name[path]
        is_dir = disk_path_to_isdir[path]
        entry  = builder(folder, name, is_dir, None)
        new_children.append(entry)
        print(f"  [ADD]  {path}")
        added += 1

    # ── Rebuild index JSON ───────────────────────────────────────────────────
    folder_path = (folder + "/") if folder else "/"
    new_index: dict[str, Any] = {
        "name":        current.get("name", index_filename),
        "description": current.get("description", ""),
        "path":        current.get("path", folder_path),
    }
    for key in preserve_top:
        if key in current:
            new_index[key] = current[key]
    new_index["children"] = new_children

    # ── Write or report ──────────────────────────────────────────────────────
    if dry_run:
        print(f"  [DRY]  would write {index_rel}  "
              f"(+{added} added, -{removed} removed, {unchanged} unchanged)")
    else:
        common.write_json_file(index_path, new_index, indent=2)

    return True, added, removed, unchanged


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync all *-index.json files with actual filesystem state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate index drift without writing any files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing any files",
    )
    parser.add_argument(
        "--index",
        metavar="PATH",
        help="Sync only the specified index file (path relative to repo root)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print all entries, not just additions and removals",
    )
    args = parser.parse_args()

    catalog = CATALOG
    if args.index:
        catalog = [s for s in CATALOG if s["index_file"] == args.index]
        if not catalog:
            known = "\n  ".join(s["index_file"] for s in CATALOG)
            print(
                f"Error: no catalog entry for '{args.index}'.\n"
                f"Known indexes:\n  {known}",
                file=sys.stderr,
            )
            return 1

    total_added = total_removed = total_unchanged = 0
    failures = 0

    if not args.check:
        for spec in catalog:
            label = spec["index_file"]
            print(f"\nSyncing {label} ...")
            ok, added, removed, unchanged = sync_index(spec, args.dry_run, args.verbose)
            if not ok:
                failures += 1
                continue
            total_added += added
            total_removed += removed
            total_unchanged += unchanged
            action = "DRY" if args.dry_run else "DONE"
            print(f"  [{action}] +{added} added  -{removed} removed  {unchanged} unchanged")

        mode_note = " (dry-run)" if args.dry_run else ""
        print(
            f"\nTotal{mode_note}: +{total_added} added  -{total_removed} removed  "
            f"{total_unchanged} unchanged  across {len(catalog)} index(es)."
        )

    issues = validate_catalog(catalog)
    print_validation_report(issues)

    if failures:
        print(f"  {failures} index(es) failed.", file=sys.stderr)
        return 1
    if issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
