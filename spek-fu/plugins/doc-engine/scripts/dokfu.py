#!/usr/bin/env python3
"""
dokfu.py - CLI entry point for the dok-fu documentation workflow system.

Subcommands:
  index     [--check]              Build spek-fu/project/code-docs/index.json; --check exits nonzero if stale
  tags      --list | --search TAG  List registry / find docs by tag
  doctor    [--json]               Validate pointers, tags, index; report problems
  changes   [--since REF]          List changed source files
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add repo root to path so 'scripts' package can be imported
_repo_root = Path(__file__).parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


def _get_config(args_root: str | None = None):
    """Load config from disk, using *args_root* as the project root."""
    from scripts.dokfu.common import load_config
    root = Path(args_root) if args_root else Path.cwd()
    return load_config(root=root), root


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _resolve_root(args: argparse.Namespace) -> Path:
    """Return the project root: --root flag if given, else cwd."""
    return Path(args.root) if args.root else Path.cwd()


def cmd_index(args: argparse.Namespace) -> int:
    from scripts.dokfu.index import build_index, is_index_stale, write_index
    from scripts.dokfu.common import load_config

    root = _resolve_root(args)
    config = load_config(root=root)

    if args.check:
        if is_index_stale(config, root=root):
            print("index: STALE — spek-fu/project/code-docs/index.json is missing or out-of-date", file=sys.stderr)
            return 1
        print("index: up-to-date")
        return 0

    entries = build_index(config, root=root)
    path = write_index(entries, config, root=root)
    print(f"index: wrote {len(entries)} entries -> {path}")
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    from scripts.dokfu.tags import list_tags, search_by_tag
    from scripts.dokfu.common import load_config

    root = _resolve_root(args)
    config = load_config(root=root)

    if args.list:
        registry = list_tags(config, root=root)
        for tag, explanation in sorted(registry.items()):
            print(f"  {tag:20s}  {explanation}")
        return 0

    if args.search:
        tag = args.search
        try:
            paths = search_by_tag(tag, config, root=root)
        except ValueError as exc:
            print(f"tags: {exc}", file=sys.stderr)
            return 1
        if not paths:
            print(f"tags: no docs found for tag '{tag}'")
            return 0
        for p in paths:
            print(p)
        return 0

    print("tags: use --list or --search TAG", file=sys.stderr)
    return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    import json
    from scripts.dokfu.doctor import run_doctor, fix_pointers
    from scripts.dokfu.index import build_index, write_index
    from scripts.dokfu.common import load_config

    root = _resolve_root(args)
    config = load_config(root=root)
    report = run_doctor(config, root=root)

    if args.json:
        # Output JSON to stdout; nothing else
        json_output = report.to_json_dict()
        print(json.dumps(json_output))
    else:
        # Default human-readable output
        for line in report.summary_lines():
            print(line)

        if args.fix_index and report.stale_index:
            entries = build_index(config, root=root)
            path = write_index(entries, config, root=root)
            print(f"doctor: rebuilt index -> {path}")

        if args.fix_pointers:
            updated = fix_pointers(report, config, root=root)
            if updated:
                print(f"doctor: fixed {len(updated)} pointer(s):")
                for p in updated:
                    print(f"  {p}")
            else:
                print("doctor: no pointers to fix")

    return 1 if report.has_problems else 0


def cmd_changes(args: argparse.Namespace) -> int:
    from scripts.dokfu.changes import get_changed_files
    from scripts.dokfu.common import load_config

    root = _resolve_root(args)
    config = load_config(root=root)
    since = args.since if args.since else "HEAD~1"

    changed, method = get_changed_files(config, root=root, since=since)
    print(f"changes ({method}, since {since}):")
    if not changed:
        print("  (none)")
    else:
        for p in changed:
            print(f"  {p}")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dokfu",
        description="Dok-Fu documentation workflow system",
    )
    parser.add_argument(
        "--root",
        default=None,
        metavar="DIR",
        help="Project root directory (default: current directory)",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # index
    p_index = sub.add_parser("index", help="Build spek-fu/project/code-docs/index.json")
    p_index.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if spek-fu/project/code-docs/index.json is stale without writing",
    )

    # tags
    p_tags = sub.add_parser("tags", help="Tag registry operations")
    tags_group = p_tags.add_mutually_exclusive_group(required=True)
    tags_group.add_argument("--list", action="store_true", help="List all registered tags")
    tags_group.add_argument("--search", metavar="TAG", help="Find docs with the given tag")

    # doctor
    p_doctor = sub.add_parser(
        "doctor",
        help="Validate pointers, tags, and index freshness",
    )
    p_doctor.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of human-readable format",
    )
    p_doctor.add_argument(
        "--fix-index",
        action="store_true",
        dest="fix_index",
        help="Rebuild index if stale",
    )
    p_doctor.add_argument(
        "--fix-pointers",
        action="store_true",
        dest="fix_pointers",
        help="Repair source file pointer comments using dokfu_id rename detection",
    )

    # changes
    p_changes = sub.add_parser("changes", help="List changed source files")
    p_changes.add_argument(
        "--since",
        default=None,
        metavar="REF",
        help="Git ref to diff against (default: HEAD)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    dispatch = {
        "index": cmd_index,
        "tags": cmd_tags,
        "doctor": cmd_doctor,
        "changes": cmd_changes,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
