#!/usr/bin/env python3
"""Spek-Fu — Classify paths as file, folder, sub-index, or missing

Usage:
    cat children.json | python3 ai/scripts/python/validate-skf-index-targets.py
    python3 ai/scripts/python/validate-skf-index-targets.py --input-file children.json
    python3 ai/scripts/python/validate-skf-index-targets.py --input-file children.json --json
    python3 ai/scripts/python/validate-skf-index-targets.py --all-plugins
    python3 ai/scripts/python/validate-skf-index-targets.py --all-plugins --json

Input: JSON array of { name, path, type?, index? } objects (from stdin or file),
       or use --all-plugins to auto-discover all targets from every plugin in
       ai/plugins/plugins-index.json (covers skf, spec-flow, and any future plugins).
Output: classified results (human-readable or JSON).
Exit code: 0 if all exist, 1 if any missing.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for common module
sys.path.insert(0, str(Path(__file__).parent))

import common


def _collect_index_items(index_rel: str, repo_root: str, plugin_name: str) -> list[dict]:
    """Recursively collect all children from an index file.

    Args:
        index_rel: Path to the index file, relative to repo root.
        repo_root: The repository root directory.
        plugin_name: Name of the owning plugin (propagated to every item).

    Returns:
        Flat list of items with name, path, plugin, and optional index fields.
    """
    items: list[dict] = []
    index_path = Path(repo_root) / index_rel

    try:
        index_content = common.load_json_file(index_path)
    except Exception as exc:
        print(f"[skf] WARN: Cannot read index {index_rel}: {exc}", file=sys.stderr)
        return items

    for child in index_content.get("children", []):
        if not isinstance(child, dict) or not child.get("path"):
            continue

        item: dict[str, Any] = {
            "name": child.get("name", ""),
            "path": child["path"],
            "plugin": plugin_name,
        }
        if "index" in child:
            item["index"] = child["index"]

        items.append(item)

        # Recurse into sub-indexes so every level is validated.
        sub_index = child.get("index", "")
        if sub_index:
            items.extend(_collect_index_items(sub_index, repo_root, plugin_name))

    return items


def collect_all_plugin_items(repo_root: str) -> list[dict]:
    """Auto-discover and collect all index targets from every plugin.

    Reads ``ai/plugins/plugins-index.json`` and recursively traverses each
    plugin's index hierarchy, so skf, spec-flow, and any future plugins are
    covered automatically.

    Args:
        repo_root: The repository root directory.

    Returns:
        Flat list of all items across all plugins.
    """
    items: list[dict] = []
    plugins_index_path = Path(repo_root) / "ai/plugins/plugins-index.json"

    try:
        plugins_index = common.load_json_file(plugins_index_path)
    except Exception as exc:
        print(f"[skf] ERROR: Cannot read plugins-index.json: {exc}", file=sys.stderr)
        return items

    for plugin in plugins_index.get("children", []):
        plugin_name = plugin.get("name", "")
        plugin_index_rel = plugin.get("index", "")
        if not plugin_name or not plugin_index_rel:
            continue

        # Include the plugin folder itself as a target.
        if plugin.get("path"):
            items.append({
                "name": plugin_name,
                "path": plugin["path"],
                "plugin": plugin_name,
            })

        # Recursively collect everything inside the plugin.
        items.extend(_collect_index_items(plugin_index_rel, repo_root, plugin_name))

    return items


def classify_path(path_str: str, repo_root: str) -> tuple[str, bool]:
    """Classify a path as file, sub-index, folder, or missing.
    
    Args:
        path_str: The path to classify.
        repo_root: The repository root directory.
    
    Returns:
        Tuple of (classification, exists) where:
        - classification: "file", "sub-index", "folder", or "missing"
        - exists: True if the path exists, False otherwise
    """
    resolved_path = common.resolve_file_path(path_str, base=repo_root)
    p = Path(resolved_path)
    
    # Check if it's a file
    if p.is_file():
        # Check if it's a sub-index (ends with -index.json or index.json)
        if path_str.endswith("-index.json") or path_str.endswith("index.json"):
            return ("sub-index", True)
        return ("file", True)
    
    # Check if it's a folder
    if p.is_dir():
        return ("folder", True)
    
    # Path doesn't exist
    return ("missing", False)


def format_human_output(items: list[dict], results: list[dict]) -> str:
    """Format results as human-readable output.
    
    Args:
        items: Original input items.
        results: Classification results.
    
    Returns:
        Formatted output string.
    """
    found_count = sum(1 for r in results if r["exists"])
    missing_count = sum(1 for r in results if not r["exists"])
    sub_index_count = sum(1 for r in results if r["classification"] == "sub-index")
    folder_count = sum(1 for r in results if r["classification"] == "folder")
    file_count = sum(1 for r in results if r["classification"] == "file")
    
    has_plugin = any("plugin" in r for r in results)
    lines = [f"[skf] Testing {len(items)} index target(s)..."]

    for result in results:
        status = "✓" if result["exists"] else "✗"
        classification = result["classification"]
        path = result["path"]
        if has_plugin and result.get("plugin"):
            plugin_tag = f"[{result['plugin']}]".ljust(12)
            lines.append(f"  {status} {plugin_tag} {classification.ljust(10)} {path}")
        else:
            lines.append(f"  {status} {classification.ljust(10)} {path} → {classification}")
    
    summary = (
        f"[skf] Results: {found_count} found "
        f"({sub_index_count} sub-index, {folder_count} folder, {file_count} file), "
        f"{missing_count} missing"
    )
    lines.append(summary)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code: 0 on success, 1 if any paths are missing.
    """
    parser = argparse.ArgumentParser(
        description="Classify paths as file, folder, sub-index, or missing"
    )
    parser.add_argument(
        "--input-file",
        help="Path to JSON input file (if not provided, reads from stdin)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of human-readable format",
    )
    parser.add_argument(
        "--all-plugins",
        action="store_true",
        help=(
            "Auto-discover and validate all targets from every plugin in "
            "ai/plugins/plugins-index.json (ignores stdin / --input-file)"
        ),
    )

    args = parser.parse_args()

    try:
        repo_root = common.get_repo_root()

        # --all-plugins: auto-discover across every plugin
        if args.all_plugins:
            items = collect_all_plugin_items(repo_root)
            if not items:
                print("[skf] ERROR: No plugin targets found", file=sys.stderr)
                return 1
        # Load input JSON
        elif args.input_file:
            input_path = Path(args.input_file)
            if not input_path.is_file():
                print(f"[skf] ERROR: Input file not found: {args.input_file}", file=sys.stderr)
                return 1
            try:
                input_json = input_path.read_text(encoding="utf-8")
            except Exception as exc:
                print(f"[skf] ERROR: Failed to read input file: {exc}", file=sys.stderr)
                return 1

            if not input_json.strip():
                print("[skf] ERROR: Input file is empty", file=sys.stderr)
                return 1

            try:
                items = json.loads(input_json)
            except json.JSONDecodeError as exc:
                print(f"[skf] ERROR: Failed to parse input JSON: {exc}", file=sys.stderr)
                return 1

            if not isinstance(items, list):
                items = [items]
        else:
            # Read from stdin
            input_json = sys.stdin.read()

            if not input_json.strip():
                print("[skf] ERROR: No input provided (stdin, --input-file, or --all-plugins)", file=sys.stderr)
                return 1

            # Parse JSON
            try:
                items = json.loads(input_json)
            except json.JSONDecodeError as exc:
                print(f"[skf] ERROR: Failed to parse input JSON: {exc}", file=sys.stderr)
                return 1

            # Ensure items is a list
            if not isinstance(items, list):
                items = [items]
        
        # Classify each path
        results = []
        missing_count = 0
        
        for item in items:
            if not isinstance(item, dict) or "path" not in item:
                continue
            
            path_str = item["path"]
            classification, exists = classify_path(path_str, repo_root)
            
            if not exists:
                missing_count += 1
            
            result: dict[str, Any] = {
                "name": item.get("name", ""),
                "path": path_str,
                "classification": classification,
                "exists": exists,
            }
            if "plugin" in item:
                result["plugin"] = item["plugin"]
            results.append(result)
        
        # Output results
        if args.json:
            output = json.dumps(results, indent=2, ensure_ascii=False)
            print(output)
        else:
            output = format_human_output(items, results)
            print(output)
        
        # Exit with 0 if all exist, 1 if any missing
        return 0 if missing_count == 0 else 1
    
    except Exception as exc:
        print(f"[skf] ERROR: Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
