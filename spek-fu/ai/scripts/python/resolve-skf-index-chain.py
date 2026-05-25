#!/usr/bin/env python3
"""Spek-Fu — Resolve index chain: follow index pointer fields from root through nested indexes.

Usage:
    python resolve-skf-index-chain.py --root-index skf-root-index.json
    python resolve-skf-index-chain.py --root-index skf-root-index.json --branches ai constitution
    python resolve-skf-index-chain.py --root-index skf-root-index.json --json

Output: human-readable list of index chain traversed + terminal items reached, or JSON.
Exit code: 0 if success, 1 if root index not found or parse error.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for common module
sys.path.insert(0, str(Path(__file__).parent))

import common


def resolve_index_chain(
    root_index_path: str,
    branches: Optional[list[str]] = None,
    json_output: bool = False,
) -> tuple[list[str], list[dict[str, Any]], int]:
    """
    Resolve the complete index chain starting from a root index file.

    Recursively follows index pointer fields from the root through nested
    indexes, collecting all index files visited and terminal items reached.
    Implements circular reference detection and max depth protection.

    Args:
        root_index_path: Path to the root index JSON file.
        branches: Optional list of branch name prefixes to filter at root level.
        json_output: If True, return data structures; if False, print human output.

    Returns:
        Tuple of (index_chain, terminal_items, exit_code).
        exit_code: 0 on success, 1 on error.
    """
    # Resolve root index path
    try:
        resolved_root = common.resolve_file_path(root_index_path)
    except Exception as e:
        print(f"[skf] ERROR: Failed to resolve root index path: {e}", file=sys.stderr)
        return [], [], 1

    # Check if root index exists
    root_path = Path(resolved_root)
    if not root_path.is_file():
        print(
            f"[skf] ERROR: Root index not found: {resolved_root}",
            file=sys.stderr,
        )
        return [], [], 1

    # Load root index
    try:
        root_content = common.load_json_file(resolved_root)
    except Exception as e:
        print(
            f"[skf] ERROR: Failed to parse root index: {e}",
            file=sys.stderr,
        )
        return [], [], 1

    # Validate root has children array
    if not isinstance(root_content, dict) or "children" not in root_content:
        print(
            "[skf] ERROR: Root index missing 'children' array",
            file=sys.stderr,
        )
        return [], [], 1

    # Initialize traversal state
    index_chain: list[str] = []
    terminal_items: list[dict[str, Any]] = []
    max_depth = 10
    visited_paths: set[str] = set()

    def traverse_index(
        index_path: str,
        index_obj: dict[str, Any],
        depth: int = 0,
        apply_branch_filter: bool = False,
    ) -> None:
        """Recursively traverse index chain.

        Args:
            index_path: The path to the current index file.
            index_obj: The parsed JSON content of the index.
            depth: Current recursion depth.
            apply_branch_filter: Whether to apply branch filtering to children.
        """
        # Guard against max depth
        if depth >= max_depth:
            print(
                f"[skf] WARNING: Max recursion depth reached at: {index_path}",
                file=sys.stderr,
            )
            return

        # Resolve the index path to check for cycles
        try:
            resolved_path = common.resolve_file_path(index_path)
        except Exception:
            resolved_path = index_path

        # Guard against cycles
        if resolved_path in visited_paths:
            return
        visited_paths.add(resolved_path)

        # Add to chain
        index_chain.append(resolved_path)

        # Process children
        if not isinstance(index_obj, dict) or "children" not in index_obj:
            return

        children = index_obj.get("children", [])
        if not isinstance(children, list):
            return

        for child in children:
            if not isinstance(child, dict):
                continue

            # Apply branch filter at root level if enabled
            if apply_branch_filter and branches and len(branches) > 0:
                child_name = child.get("name", "")
                matches = any(
                    child_name.startswith(branch) for branch in branches
                )
                if not matches:
                    continue

            # Check if child has an index and is a folder
            child_index = child.get("index")
            child_type = child.get("type")

            if child_index and child_type == "folder":
                # Try to recursively load sub-index
                try:
                    sub_index_resolved = common.resolve_file_path(child_index)
                    sub_index_path = Path(sub_index_resolved)

                    if sub_index_path.is_file():
                        try:
                            sub_index = common.load_json_file(sub_index_resolved)
                            traverse_index(
                                child_index,
                                sub_index,
                                depth + 1,
                                apply_branch_filter=False,
                            )
                        except Exception as err:
                            print(
                                f"[skf] WARNING: Failed to parse sub-index at {child_index}: {err}",
                                file=sys.stderr,
                            )
                except Exception as err:
                    print(
                        f"[skf] WARNING: Failed to resolve sub-index at {child_index}: {err}",
                        file=sys.stderr,
                    )
            else:
                # Terminal item (file or folder without index)
                terminal_items.append(child)

    # Start traversal
    traverse_index(
        root_index_path,
        root_content,
        depth=0,
        apply_branch_filter=True,
    )

    return index_chain, terminal_items, 0


def format_human_output(
    root_index_path: str,
    index_chain: list[str],
    terminal_items: list[dict[str, Any]],
) -> str:
    """Format index chain and terminal items as human-readable output.

    Args:
        root_index_path: The original root index path.
        index_chain: List of resolved index file paths.
        terminal_items: List of terminal item dicts.

    Returns:
        Formatted string ready to print.
    """
    lines = []
    lines.append(f"[skf] Resolving index chain from: {root_index_path}")
    lines.append(
        f"[skf] Chain traversed ({len(index_chain)} indexes):"
    )
    for idx in index_chain:
        lines.append(f"  → {idx}")

    lines.append(f"[skf] Terminal items ({len(terminal_items)}):")
    for item in terminal_items:
        item_type = item.get("type", "unknown")
        item_name = item.get("name", "unnamed")
        item_path = item.get("path", "unknown")
        
        icon = "📁" if item_type == "folder" else "📄"
        lines.append(f"  {icon} {item_name} → {item_path}")

    lines.append(
        f"[skf] Done. {len(index_chain)} index files, {len(terminal_items)} terminal items."
    )

    return "\n".join(lines)


def main() -> int:
    """Parse arguments, resolve index chain, and output results."""
    parser = argparse.ArgumentParser(
        description="Resolve index chain: follow index pointer fields from root through nested indexes.",
        prog="resolve-skf-index-chain",
    )
    parser.add_argument(
        "--root-index",
        "-r",
        default="skf-root-index.json",
        help="Path to the root index JSON file (default: skf-root-index.json)",
    )
    parser.add_argument(
        "--branches",
        "-b",
        nargs="*",
        default=None,
        help="Optional branch name prefixes to filter at root level",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON instead of human-readable format",
    )

    args = parser.parse_args()

    # Resolve index chain
    index_chain, terminal_items, exit_code = resolve_index_chain(
        args.root_index,
        branches=args.branches,
        json_output=args.json,
    )

    if exit_code != 0:
        return exit_code

    # Output results
    if args.json:
        result = {
            "indexChain": index_chain,
            "terminalItems": terminal_items,
        }
        print(common.format_json_output(result))
    else:
        output = format_human_output(
            args.root_index,
            index_chain,
            terminal_items,
        )
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
