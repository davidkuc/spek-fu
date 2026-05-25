#!/usr/bin/env python3
"""Spek-Fu — Parse Navigation Result: markdown-native using markdown parsing.

Default behavior: reads markdown input from --input-file or stdin
and outputs Python dicts or markdown to stdout or file.

Usage:
    # Markdown input → Python objects to stdout (default)
    python3 spek-fu/ai/scripts/python/parse-navigation-result.py --input-file spek-fu/reports/orchestration-spill/traversal-report.md

    # Markdown input → JSON output
    python3 spek-fu/ai/scripts/python/parse-navigation-result.py --input-file spek-fu/reports/orchestration-spill/traversal-report.md --as-json

    # Extract domain groups from markdown bullet list
    python3 spek-fu/ai/scripts/python/parse-navigation-result.py --input-file spek-fu/reports/orchestration-spill/traversal-report.md --extract-domains

    # Extract skill paths from markdown bullet list
    python3 spek-fu/ai/scripts/python/parse-navigation-result.py --input-file spek-fu/reports/orchestration-spill/traversal-report.md --extract-skills

Exit codes:
    0 = success
    1 = malformed/empty input
    2 = input file not found
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to import common
sys.path.insert(0, str(Path(__file__).parent))

import common


def read_input_content(input_file: str | None) -> str:
    """Read input from file or stdin.
    
    Args:
        input_file: Path to input file, or None to read from stdin.
    
    Returns:
        The input content as a string.
    
    Raises:
        FileNotFoundError: If input_file is provided but doesn't exist.
        RuntimeError: If input is empty.
    """
    if input_file:
        resolved_path = Path(input_file).resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"[skf] Input file not found: {resolved_path}")
        return resolved_path.read_text(encoding="utf-8")
    else:
        # Read from stdin
        content = sys.stdin.read()
        return content


def format_table(rows: list[dict], columns: list[str] = None) -> str:
    """Format a list of dicts as a simple text table.
    
    Args:
        rows: List of dicts where each dict maps column names to cell values.
        columns: Ordered list of column names to display. Defaults to all keys from first row.
    
    Returns:
        Formatted table string.
    """
    if not rows:
        return ""
    
    if columns is None:
        columns = list(rows[0].keys())
    
    # Compute column widths
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            cell = str(row.get(col, ""))
            if len(cell) > widths[col]:
                widths[col] = len(cell)
    
    # Build table
    separator = "  ".join("-" * widths[col] for col in columns)
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    
    lines = [header, separator]
    for row in rows:
        line = "  ".join(
            str(row.get(col, "")).ljust(widths[col]) for col in columns
        )
        lines.append(line)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for malformed input, 2 for file not found).
    """
    parser = argparse.ArgumentParser(
        description="Parse navigation result markdown and output domains/skills"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help="Path to input markdown file (reads from stdin if not provided)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Path to output file (writes to stdout if not provided)"
    )
    parser.add_argument(
        "--as-json",
        action="store_true",
        help="Output as JSON instead of text table"
    )
    parser.add_argument(
        "--extract-domains",
        action="store_true",
        help="Extract only domain values"
    )
    parser.add_argument(
        "--extract-skills",
        action="store_true",
        help="Extract only skill paths"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    
    args = parser.parse_args()
    
    # Read input
    try:
        inner_content = read_input_content(args.input_file)
    except FileNotFoundError as e:
        print(f"[skf] {e}", file=sys.stderr)
        return 2
    
    # Validate input
    if not inner_content or not inner_content.strip():
        print("[skf] Input content is empty", file=sys.stderr)
        return 1
    
    # Parse markdown sections to extract domain groups and skill paths
    domains_section = common.read_markdown_section(
        inner_content, "Domains", level=2
    )
    skills_section = common.read_markdown_section(
        inner_content, "Skills", level=2
    )
    
    domain_groups = common.parse_markdown_list(domains_section)
    skill_paths = common.parse_markdown_list(skills_section)
    
    # Create result objects
    results: list[dict[str, Any]] = []
    
    for domain in domain_groups:
        if domain:
            results.append({
                "type": "domain",
                "value": domain
            })
    
    for skill in skill_paths:
        if skill:
            results.append({
                "type": "skill",
                "value": skill
            })
    
    if not results:
        print("[skf] No domains or skills found in markdown", file=sys.stderr)
        return 1
    
    # Format output
    if args.extract_domains:
        output = "\n".join(domain_groups)
    elif args.extract_skills:
        output = "\n".join(skill_paths)
    elif args.as_json:
        if args.pretty:
            output = common.format_json_output(results)
        else:
            output = json.dumps(results, ensure_ascii=False, separators=(',', ':'))
    else:
        # Default: output as text table
        output = format_table(results, columns=["type", "value"])
    
    # Write output
    if args.output_file:
        out_path = Path(args.output_file).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"[skf] Wrote output to: {out_path}", file=sys.stderr)
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
