"""Search .md files in the framework by YAML frontmatter fields.

CLI usage:
    python3 search-by-frontmatter.py --root <directory> [--tags t1,t2]
        [--group util] [--tier fast-agent] [--type reference]
        [--text "query"] [--format json|table] [--min-score N]
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import format_json_output, parse_frontmatter, print_table


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search .md files by YAML frontmatter fields."
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Root directory to search recursively.",
    )
    parser.add_argument(
        "--tags",
        default=None,
        help="Comma-separated tag list. Matches if ANY tag appears in frontmatter tags.",
    )
    parser.add_argument(
        "--group",
        default=None,
        help="Match files where frontmatter group equals this value (case-insensitive).",
    )
    parser.add_argument(
        "--tier",
        default=None,
        help="Match files where frontmatter tier equals this value (case-insensitive).",
    )
    parser.add_argument(
        "--type",
        default=None,
        dest="file_type",
        help="Match files where frontmatter type equals this value (case-insensitive).",
    )
    parser.add_argument(
        "--text",
        default=None,
        help="Free-text search against frontmatter title, description, id, name, and tags.",
    )
    parser.add_argument(
        "--format",
        default="table",
        choices=["table", "json"],
        help="Output format: table (default) or json.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=1,
        dest="min_score",
        help="Minimum relevance score to include in results (default: 1).",
    )
    return parser.parse_args(argv)


def collect_md_files(root: Path) -> list[Path]:
    """Recursively collect all .md files under root, skipping README.md."""
    files: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".md") and filename != "README.md":
                files.append(Path(dirpath) / filename)
    return sorted(files)


def score_file(
    frontmatter: dict,
    tags_filter: list[str] | None,
    group_filter: str | None,
    tier_filter: str | None,
    type_filter: str | None,
    text_filter: str | None,
) -> int:
    """Compute a relevance score for a file given the active filters."""
    score = 0

    fm_tags: list[str] = [str(t).lower() for t in (frontmatter.get("tags") or [])]
    fm_group: str = str(frontmatter.get("group", "")).lower()
    fm_tier: str = str(frontmatter.get("recommended-tier", "")).lower()
    fm_type: str = str(frontmatter.get("type", "")).lower()
    fm_title: str = str(frontmatter.get("title", "")).lower()
    fm_name: str = str((frontmatter.get("name") or frontmatter.get("id") or "")).lower()
    fm_description: str = str(frontmatter.get("description", "")).lower()
    fm_id: str = str(frontmatter.get("id", "")).lower()

    if tags_filter is not None:
        for tag in tags_filter:
            if tag.lower() in fm_tags:
                score += 2

    if group_filter is not None and fm_group == group_filter.lower():
        score += 3

    if tier_filter is not None and fm_tier == tier_filter.lower():
        score += 2

    if type_filter is not None and fm_type == type_filter.lower():
        score += 2

    if text_filter is not None:
        needle = text_filter.lower()
        if needle in fm_title or needle in fm_name:
            score += 3
        if needle in fm_description:
            score += 2
        if needle in fm_id:
            score += 1
        for tag in fm_tags:
            if needle in tag:
                score += 1

    return score


def build_results(
    root: Path,
    md_files: list[Path],
    tags_filter: list[str] | None,
    group_filter: str | None,
    tier_filter: str | None,
    type_filter: str | None,
    text_filter: str | None,
    min_score: int,
    has_filters: bool,
) -> list[dict]:
    """Parse frontmatter and score each file; return filtered, sorted results."""
    results: list[dict] = []

    for file_path in md_files:
        try:
            fm = parse_frontmatter(file_path)
        except Exception:
            continue

        if fm is None:
            continue

        score = score_file(
            fm,
            tags_filter,
            group_filter,
            tier_filter,
            type_filter,
            text_filter,
        )

        if has_filters and score < min_score:
            continue

        try:
            rel_path = file_path.relative_to(root.parent)
        except ValueError:
            rel_path = file_path

        results.append(
            {
                "path": str(rel_path),
                "score": score,
                "frontmatter": fm,
            }
        )

    if has_filters:
        results.sort(key=lambda r: r["score"], reverse=True)
    else:
        results.sort(key=lambda r: r["path"])

    return results


def output_table(results: list[dict], query_parts: dict) -> None:
    """Print results in aligned table format."""
    query_str = "  ".join(f"{k}={v}" for k, v in query_parts.items())
    print(f"Search: {query_str}")
    print(f"Results: {len(results)} matches")
    print()

    if not results:
        return

    rows = []
    for r in results:
        fm = r["frontmatter"]
        rows.append(
            {
                "Path": r["path"],
                "Name": str(fm.get("name") or fm.get("id") or fm.get("title") or ""),
                "Group": str(fm.get("group", "")),
                "Tier": str(fm.get("recommended-tier", "")),
                "Score": str(r["score"]),
            }
        )

    print_table(rows, ["Path", "Name", "Group", "Tier", "Score"])


def output_json(results: list[dict], query_parts: dict) -> None:
    """Print results as JSON."""
    payload = {
        "query": query_parts,
        "total": len(results),
        "results": results,
    }
    print(format_json_output(payload))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: --root is not a readable directory: {args.root}", file=sys.stderr)
        return 1

    tags_filter: list[str] | None = None
    if args.tags:
        tags_filter = [t.strip() for t in args.tags.split(",") if t.strip()]

    group_filter: str | None = args.group
    tier_filter: str | None = args.tier
    type_filter: str | None = args.file_type
    text_filter: str | None = args.text

    has_filters = any(
        f is not None
        for f in (tags_filter, group_filter, tier_filter, type_filter, text_filter)
    )

    md_files = collect_md_files(root)

    results = build_results(
        root=root,
        md_files=md_files,
        tags_filter=tags_filter,
        group_filter=group_filter,
        tier_filter=tier_filter,
        type_filter=type_filter,
        text_filter=text_filter,
        min_score=args.min_score,
        has_filters=has_filters,
    )

    query_parts: dict = {"root": args.root}
    if tags_filter is not None:
        query_parts["tags"] = args.tags
    if group_filter is not None:
        query_parts["group"] = group_filter
    if tier_filter is not None:
        query_parts["tier"] = tier_filter
    if type_filter is not None:
        query_parts["type"] = type_filter
    if text_filter is not None:
        query_parts["text"] = text_filter

    if args.format == "json":
        output_json(results, query_parts)
    else:
        output_table(results, query_parts)

    return 0


if __name__ == "__main__":
    sys.exit(main())
