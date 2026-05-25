#!/usr/bin/env python3
"""Spek-Fu — Scaffold a new plugin folder under spek-fu/ai/plugins/.

Creates the standard plugin directory structure (knowledge/, skills/,
templates/) with empty index files and registers the new plugin in
plugins-index.json.

Usage:
    python3 spek-fu/ai/scripts/python/create-plugin.py --name <plugin-name>
    python3 spek-fu/ai/scripts/python/create-plugin.py --name <plugin-name> --dry-run

Options:
    --name NAME   Plugin slug (required) — lowercase alphanumeric + hyphens.
    --dry-run     Preview created paths without writing any files.

Exit codes:
    0  Plugin scaffolded (or dry-run previewed) successfully.
    1  Usage error or fatal failure.
"""

import argparse
import re
import sys
from pathlib import Path

# Allow importing common.py from the same directory.
sys.path.insert(0, str(Path(__file__).parent))
import common

REPO_ROOT = Path(common.get_repo_root())

PLUGINS_INDEX = "spek-fu/ai/plugins/plugins-index.json"


# ── Index content builders ──────────────────────────────────────────────────────

def _build_plugin_index(name: str) -> dict:
    return {
        "name": f"{name}-index.json",
        "description": f"Index of spek-fu/ai/plugins/{name} — {name} plugin",
        "path": f"spek-fu/ai/plugins/{name}/",
        "children": [
            {
                "name": "knowledge",
                "type": "folder",
                "description": f"Knowledge resources for the {name} plugin",
                "path": f"spek-fu/ai/plugins/{name}/knowledge/",
                "index": f"spek-fu/ai/plugins/{name}/knowledge/knowledge-index.json",
            },
            {
                "name": "skills",
                "type": "folder",
                "description": f"Skill definitions for the {name} plugin",
                "path": f"spek-fu/ai/plugins/{name}/skills/",
                "index": f"spek-fu/ai/plugins/{name}/skills/skills-index.json",
            },
            {
                "name": "templates",
                "type": "folder",
                "description": f"Scaffolding templates for the {name} plugin",
                "path": f"spek-fu/ai/plugins/{name}/templates/",
                "index": f"spek-fu/ai/plugins/{name}/templates/templates-index.json",
            },
        ],
    }


def _build_knowledge_index(name: str) -> dict:
    return {
        "name": "knowledge-index.json",
        "description": f"Index of spek-fu/ai/plugins/{name}/knowledge",
        "path": f"spek-fu/ai/plugins/{name}/knowledge/",
        "children": [],
    }


def _build_skills_index(name: str) -> dict:
    return {
        "name": "skills-index.json",
        "description": f"Index of spek-fu/ai/plugins/{name}/skills — skill metadata for routing and discovery",
        "path": f"spek-fu/ai/plugins/{name}/skills/",
        "children": [],
    }


def _build_templates_index(name: str) -> dict:
    return {
        "name": "templates-index.json",
        "description": f"Index of spek-fu/ai/plugins/{name}/templates — scaffolding templates",
        "path": f"spek-fu/ai/plugins/{name}/templates/",
        "children": [],
    }


# ── Validation ──────────────────────────────────────────────────────────────────

def _validate_name(name: str) -> str | None:
    """Return an error message if name is invalid, otherwise None."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        return (
            "Name must start with a lowercase letter or digit and contain only "
            "lowercase alphanumeric characters and hyphens."
        )
    return None


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new plugin folder under spek-fu/ai/plugins/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--name",
        required=True,
        metavar="NAME",
        help="Plugin slug (lowercase alphanumeric + hyphens only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview created paths without writing any files",
    )
    args = parser.parse_args()

    name: str = args.name.lower()
    dry_run: bool = args.dry_run

    # Validate name format.
    err = _validate_name(name)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    # Check plugin directory does not already exist.
    plugin_dir = REPO_ROOT / "spek-fu/ai/plugins" / name
    if plugin_dir.exists():
        print(
            f"Error: Plugin '{name}' already exists at "
            f"{plugin_dir.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 1

    # Load and validate plugins-index.json.
    plugins_index_path = REPO_ROOT / PLUGINS_INDEX
    try:
        plugins_index = common.load_json_file(plugins_index_path)
    except Exception as exc:
        print(f"Error: Cannot read {PLUGINS_INDEX}: {exc}", file=sys.stderr)
        return 1

    # Check name is not already registered in the index.
    existing_names = {c.get("name", "") for c in plugins_index.get("children", [])}
    if name in existing_names:
        print(
            f"Error: Plugin '{name}' is already registered in {PLUGINS_INDEX}",
            file=sys.stderr,
        )
        return 1

    # Define directories and files to create.
    dirs_to_create: list[str] = [
        f"spek-fu/ai/plugins/{name}/",
        f"spek-fu/ai/plugins/{name}/knowledge/",
        f"spek-fu/ai/plugins/{name}/skills/",
        f"spek-fu/ai/plugins/{name}/templates/",
    ]
    files_to_create: list[tuple[str, dict]] = [
        (f"spek-fu/ai/plugins/{name}/{name}-index.json",              _build_plugin_index(name)),
        (f"spek-fu/ai/plugins/{name}/knowledge/knowledge-index.json", _build_knowledge_index(name)),
        (f"spek-fu/ai/plugins/{name}/skills/skills-index.json",       _build_skills_index(name)),
        (f"spek-fu/ai/plugins/{name}/templates/templates-index.json", _build_templates_index(name)),
    ]

    mode = "[DRY]" if dry_run else "[CREATE]"

    # Report / create directories.
    for d in dirs_to_create:
        print(f"  {mode} dir   {d}")

    # Report / write index files.
    for rel_path, content in files_to_create:
        print(f"  {mode} file  {rel_path}")
        if not dry_run:
            common.write_json_file(REPO_ROOT / rel_path, content, indent=2)

    # Update plugins-index.json.
    new_entry = {
        "name": name,
        "type": "folder",
        "description": "",
        "path": f"spek-fu/ai/plugins/{name}/",
        "index": f"spek-fu/ai/plugins/{name}/{name}-index.json",
    }
    print(f"  {mode} entry {PLUGINS_INDEX} ← {name}")
    if not dry_run:
        plugins_index.setdefault("children", []).append(new_entry)
        common.write_json_file(plugins_index_path, plugins_index, indent=2)

    action = "Dry-run complete" if dry_run else "Plugin scaffolded"
    print(f"\n{action}: {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
