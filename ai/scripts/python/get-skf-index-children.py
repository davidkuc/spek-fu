#!/usr/bin/env python3
"""Spek-Fu — Parse a single index JSON file and return normalized children array

Usage:
    python3 ai/scripts/python/get-skf-index-children.py --index-path ai/ai-index.json
    python3 ai/scripts/python/get-skf-index-children.py --index-path ai/ai-index.json --json

Output: normalized children array (human-readable or JSON).
Exit code: 0 if success, 1 if file not found or malformed JSON.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for common module
sys.path.insert(0, str(Path(__file__).parent))

import common


def normalize_children(index_content: dict) -> list[dict[str, Any]]:
    """Normalize children array from index content.
    
    Each child is normalized to have:
    - name (default: "")
    - type (default: "file")
    - description (default: "")
    - path (default: "")
    - index (only if present in source)
    
    Args:
        index_content: Parsed index JSON dict.
    
    Returns:
        List of normalized child dicts.
    
    Raises:
        ValueError: If children is not a list or is missing.
    """
    if not isinstance(index_content, dict):
        raise ValueError("Index content must be a dict")
    
    if "children" not in index_content:
        raise ValueError("Index missing 'children' array")
    
    children = index_content["children"]
    if not isinstance(children, list):
        raise ValueError("'children' must be an array")
    
    normalized = []
    for child in children:
        if not isinstance(child, dict):
            continue
        
        obj = {
            "name": child.get("name", ""),
            "type": child.get("type", "file"),
            "description": child.get("description", ""),
            "path": child.get("path", ""),
        }
        
        # Add index only if it exists
        if "index" in child:
            obj["index"] = child["index"]
        
        normalized.append(obj)
    
    return normalized


def format_human_output(index_path: str, normalized: list[dict[str, Any]]) -> str:
    """Format normalized children as human-readable output.
    
    Args:
        index_path: The original index path (for header).
        normalized: List of normalized child dicts.
    
    Returns:
        Formatted output string.
    """
    lines = [f"[skf] Children of {index_path} ({len(normalized)} items):"]
    
    for child in normalized:
        icon = "📁" if child["type"] == "folder" else "📄"
        name = child["name"]
        path = child["path"]
        
        if "index" in child:
            line = f"  {icon} {name} → {path} [index: {child['index']}]"
        else:
            line = f"  {icon} {name} → {path}"
        
        lines.append(line)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code: 0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Parse a single index JSON file and return normalized children array"
    )
    parser.add_argument(
        "--index-path",
        required=True,
        help="Path to index JSON file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of human-readable format",
    )
    
    args = parser.parse_args()
    
    try:
        # Resolve index path
        resolved_path = common.resolve_file_path(args.index_path, base=common.get_repo_root())
        
        # Check if file exists
        if not Path(resolved_path).is_file():
            print(f"[skf] ERROR: Index file not found: {resolved_path}", file=sys.stderr)
            return 1
        
        # Load and parse index
        try:
            index_content = common.load_json_file(resolved_path)
        except Exception as exc:
            print(f"[skf] ERROR: Failed to parse index JSON: {exc}", file=sys.stderr)
            return 1
        
        # Normalize children
        try:
            normalized = normalize_children(index_content)
        except ValueError as exc:
            print(f"[skf] ERROR: {exc}", file=sys.stderr)
            return 1
        
        # Output
        if args.json:
            output = json.dumps(normalized, indent=2, ensure_ascii=False)
            print(output)
        else:
            output = format_human_output(args.index_path, normalized)
            print(output)
        
        return 0
    
    except Exception as exc:
        print(f"[skf] ERROR: Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
