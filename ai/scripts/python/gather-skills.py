#!/usr/bin/env python3
"""Spek-Fu — Gather all available skills from plugin indexes, pre-filtered by ignore config.

Reads all plugin skill entries by following the index chain from plugins-index.json
through each plugin's root index to its skills-index.json. Merges the entries across
all plugins, then removes any skills whose path appears in the ignoredSkills list in
ai/plugins/skf/skills/config.json.

This script is the single source of truth for the available skill catalog used by
orch-skill-resolve. Running it once avoids repeated index file reads inside the skill.

Usage:
    python3 ai/scripts/python/gather-skills.py
    python3 ai/scripts/python/gather-skills.py --format table
    python3 ai/scripts/python/gather-skills.py --format json
    python3 ai/scripts/python/gather-skills.py --config path/to/config.json
    python3 ai/scripts/python/gather-skills.py --plugins-index path/to/plugins-index.json

Options:
    --format FORMAT         Output format: json (default) or table.
    --config PATH           Path to config.json relative to repo root
                            (default: ai/plugins/skf/skills/config.json).
    --plugins-index PATH    Path to plugins-index.json relative to repo root
                            (default: ai/plugins/plugins-index.json).

JSON output shape:
    {
      "total": <int>,      # total skills found across all plugin indexes
      "ignored": <int>,    # count removed by the ignore list
      "available": <int>,  # count remaining after filtering
      "skills": [...]      # array of skill entry objects
    }

Exit codes:
    0  Success.
    1  A required file could not be read or was malformed; no skills were gathered.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common

# Repo root is three levels above this script:
#   ai/scripts/python/gather-skills.py -> ai/scripts/python -> ai/scripts -> ai -> root
REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_PLUGINS_INDEX = "ai/plugins/plugins-index.json"
DEFAULT_CONFIG = "ai/plugins/skf/skills/config.json"


def load_ignored_skills(config_path: Path) -> set[str]:
    """Return the set of skill paths to ignore from config.json.

    Returns an empty set if the file is missing, malformed, or the key is absent.
    """
    try:
        config = common.load_json_file(config_path)
    except (FileNotFoundError, ValueError):
        return set()

    if not isinstance(config, dict):
        return set()

    ignored = config.get("skillSelection", {}).get("ignoredSkills", [])
    if not isinstance(ignored, list):
        return set()

    return set(str(p) for p in ignored)


def gather_all_skills(plugins_index_path: Path) -> tuple[list[dict], list[str]]:
    """Traverse the plugin index chain and collect all skill entries.

    Follows plugins-index.json -> plugin root index -> skills-index.json for
    every registered plugin. Returns a tuple of (merged skill list, error messages).
    Errors are non-fatal per-plugin failures; a fatal error (plugins-index.json
    unreadable) returns an empty list and a single error message.
    """
    errors: list[str] = []
    all_skills: list[dict] = []

    try:
        plugins_index = common.load_json_file(plugins_index_path)
    except (FileNotFoundError, ValueError) as exc:
        return [], [f"Cannot read plugins-index.json ({plugins_index_path}): {exc}"]

    if not isinstance(plugins_index, dict):
        return [], [f"plugins-index.json is not a JSON object: {plugins_index_path}"]

    plugins = plugins_index.get("children", [])
    if not isinstance(plugins, list):
        return [], ["plugins-index.json 'children' is not an array"]

    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue

        plugin_name = plugin.get("name", "<unnamed>")
        plugin_index_rel = plugin.get("index")
        if not plugin_index_rel:
            continue

        # ── Load plugin root index ──────────────────────────────────────────
        plugin_index_path = REPO_ROOT / plugin_index_rel
        try:
            plugin_index = common.load_json_file(plugin_index_path)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(f"Plugin '{plugin_name}': cannot read root index {plugin_index_rel}: {exc}")
            continue

        if not isinstance(plugin_index, dict):
            errors.append(f"Plugin '{plugin_name}': root index {plugin_index_rel} is not a JSON object")
            continue

        # ── Locate the skills child entry ───────────────────────────────────
        children = plugin_index.get("children", [])
        if not isinstance(children, list):
            errors.append(f"Plugin '{plugin_name}': root index 'children' is not an array")
            continue

        skills_entry = next(
            (c for c in children if isinstance(c, dict) and c.get("name") == "skills"),
            None,
        )
        if skills_entry is None:
            continue  # Plugin has no skills folder; skip silently

        skills_index_rel = skills_entry.get("index")
        if not skills_index_rel:
            errors.append(f"Plugin '{plugin_name}': skills entry has no 'index' pointer")
            continue

        # ── Load skills-index.json ──────────────────────────────────────────
        skills_index_path = REPO_ROOT / skills_index_rel
        try:
            skills_index = common.load_json_file(skills_index_path)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(f"Plugin '{plugin_name}': cannot read skills index {skills_index_rel}: {exc}")
            continue

        if not isinstance(skills_index, dict):
            errors.append(f"Plugin '{plugin_name}': skills index {skills_index_rel} is not a JSON object")
            continue

        skills = skills_index.get("children", [])
        if not isinstance(skills, list):
            errors.append(f"Plugin '{plugin_name}': skills index 'children' is not an array")
            continue

        all_skills.extend(skills)

    return all_skills, errors


def format_table(skills: list[dict]) -> str:
    """Format skills as an ASCII table with four columns."""
    if not skills:
        return "(no available skills)"

    headers = ["ID", "Path", "Recommended Tier", "Dispatch Variant"]
    rows = [
        [
            str(s.get("id", "")),
            str(s.get("path", "")),
            str(s.get("recommended-tier", "")),
            str(s.get("dispatch-variant", "")),
        ]
        for s in skills
    ]

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"

    lines = [sep, header_row, sep]
    for row in rows:
        lines.append("| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |")
    lines.append(sep)

    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gather all available skills, pre-filtered by the ignore config."
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "table"],
        help="Output format: json (default) or table.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help=f"Path to config.json, relative to repo root (default: {DEFAULT_CONFIG}).",
    )
    parser.add_argument(
        "--plugins-index",
        default=DEFAULT_PLUGINS_INDEX,
        dest="plugins_index",
        help=f"Path to plugins-index.json, relative to repo root (default: {DEFAULT_PLUGINS_INDEX}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    plugins_index_path = REPO_ROOT / args.plugins_index
    config_path = REPO_ROOT / args.config

    ignored = load_ignored_skills(config_path)

    all_skills, errors = gather_all_skills(plugins_index_path)

    if errors and not all_skills:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    for err in errors:
        print(f"WARNING: {err}", file=sys.stderr)

    total = len(all_skills)
    available_skills = [s for s in all_skills if s.get("path") not in ignored]
    ignored_count = total - len(available_skills)

    if args.format == "json":
        output = {
            "total": total,
            "ignored": ignored_count,
            "available": len(available_skills),
            "skills": available_skills,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Total: {total}  Ignored: {ignored_count}  Available: {len(available_skills)}")
        print()
        print(format_table(available_skills))

    return 0


if __name__ == "__main__":
    sys.exit(main())
