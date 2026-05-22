#!/usr/bin/env python3
"""
generate-prompt-files.py

Discovers all plugins under ai/plugins/, reads their skills-index.json files,
and generates one .prompt.md file per user-facing skill entry in .github/prompts/.
User-facing skills are all skills EXCEPT those whose id starts with a prefix
listed in EXCLUDED_PREFIXES (currently "orch-" and "impl-").

Usage: python3 ai/scripts/python/generate-prompt-files.py
Run from the workspace root: /workspaces/spek-fu/

Exit codes:
    0  All prompt files generated successfully.
    1  Error reading plugins directory or writing output files.
"""

import argparse
import json
import sys
from pathlib import Path

# Skills whose id starts with any of these prefixes are internal-dispatch-only
# and are NOT exposed as slash commands. All other skills are user-facing.
EXCLUDED_PREFIXES = ("orch-", "impl-")


def build_frontmatter(entry: dict) -> str:
    """Build YAML frontmatter for a prompt file from a skills-index entry."""
    skill_id = entry.get("id", "")
    description = entry.get("description", "")
    anti_scope = entry.get("anti-scope", "")

    lines = ["---"]
    lines.append(f'name: "{skill_id}"')

    if description:
        desc_escaped = description.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'description: "{desc_escaped}"')

    if anti_scope:
        anti_escaped = anti_scope.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'anti-scope: "{anti_escaped}"')

    lines.append("---")
    return "\n".join(lines)


def generate_prompt_file(entry: dict, output_dir: Path) -> Path:
    """Generate a single .prompt.md file for a skill entry."""
    skill_id = entry.get("id", "")
    skill_path = entry.get("path", "")
    frontmatter = build_frontmatter(entry)
    body = (
        f"\nConsult the skill from `{skill_path}`."
        " Execute its full protocol exactly as described.\n"
    )
    content = frontmatter + "\n" + body
    output_path = output_dir / f"{skill_id}.prompt.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate .prompt.md files from skills-index.json across all plugins."
    )
    parser.parse_args()

    workspace_root = Path(__file__).resolve().parent.parent.parent.parent
    plugins_dir = workspace_root / "ai" / "plugins"
    output_dir = workspace_root / ".github" / "prompts"

    if not plugins_dir.exists():
        print(
            f"ERROR: plugins directory not found at {plugins_dir}",
            file=sys.stderr,
        )
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover all plugin directories and their skills-index.json files
    all_skills = []
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        skills_index_path = plugin_dir / "skills" / "skills-index.json"
        if not skills_index_path.exists():
            continue

        try:
            data = json.loads(skills_index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(
                f"WARNING: Failed to parse {skills_index_path}: {exc}",
                file=sys.stderr,
            )
            continue

        children = data.get("children", [])
        all_skills.extend(children)

    if not all_skills:
        print("WARNING: No skills found in any plugin.")
        return 0

    # All skills are user-facing slash commands EXCEPT orch-* and impl-*.
    # See EXCLUDED_PREFIXES at the top of this file.
    count = 0
    for entry in all_skills:
        skill_id = entry.get("id", "")
        if not skill_id:
            continue
        if any(skill_id.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue
        try:
            generate_prompt_file(entry, output_dir)
            count += 1
        except OSError as exc:
            print(
                f"ERROR: Failed to write {entry.get('id')}.prompt.md: {exc}",
                file=sys.stderr,
            )
            return 1

    print(f"Generated {count} prompt files in .github/prompts/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
