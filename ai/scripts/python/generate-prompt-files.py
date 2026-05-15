#!/usr/bin/env python3
"""
generate-prompt-files.py

Reads ai/plugins/skf/skills/skills-index.json and generates one .prompt.md
file per skill entry in .github/prompts/.

Usage: python3 ai/scripts/python/generate-prompt-files.py
Run from the workspace root: /workspaces/spek-fu/

Exit codes:
    0  All prompt files generated successfully.
    1  Error reading skills-index.json or writing output files.
"""

import argparse
import json
import sys
from pathlib import Path


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
    frontmatter = build_frontmatter(entry)
    body = (
        f"\nConsult the skill from `ai/plugins/skf/skills/{skill_id}.md`."
        " Execute its full protocol exactly as described.\n"
    )
    content = frontmatter + "\n" + body
    output_path = output_dir / f"{skill_id}.prompt.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate .prompt.md files from skills-index.json."
    )
    parser.parse_args()

    workspace_root = Path(__file__).resolve().parent.parent.parent.parent
    skills_index_path = (
        workspace_root / "ai" / "plugins" / "skf" / "skills" / "skills-index.json"
    )
    output_dir = workspace_root / ".github" / "prompts"

    if not skills_index_path.exists():
        print(
            f"ERROR: skills-index.json not found at {skills_index_path}",
            file=sys.stderr,
        )
        return 1

    try:
        data = json.loads(skills_index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse skills-index.json: {exc}", file=sys.stderr)
        return 1

    children = data.get("children", [])
    if not children:
        print("WARNING: No entries found in skills-index.json children array.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)

    # Only gov-* and meta-* skills are user-facing slash commands.
    # orch-* and impl-* are internal-dispatch-only skills and are not exposed as prompts.
    count = 0
    for entry in children:
        skill_id = entry.get("id", "")
        if not skill_id:
            continue
        if not (skill_id.startswith("gov-") or skill_id.startswith("meta-")):
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
