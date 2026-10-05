"""Regenerate .claude/ and .github/ pointer files for every skill and agent.

Source of truth: spek-fu/plugins/<plugin>/skills/<name>/SKILL.md and
spek-fu/plugins/<plugin>/agents/<name>/AGENT.md. For each, this script
extracts the YAML frontmatter verbatim and rewrites the matching pointer
file(s), which contain that frontmatter followed by:

    This file is a pointer. Read `<source-path>` for the actual instructions.

Pointer layout:
- Skills:  .claude/skills/<name>/SKILL.md   and .github/skills/<name>/SKILL.md
- Agents:  .claude/agents/<name>/AGENT.md   and .github/agents/<name>.agent.md

Run with no arguments to rewrite every pointer file and delete stale ones
(a pointer whose source skill/agent no longer exists). A file is only
deleted if it still contains the pointer sentence, so hand-authored content
is never touched.

Usage: python spek-fu/plugins/framework/scripts/regenerate-pointer-files.py
"""
# dok-fu: spek-fu/project/code-docs/spek-fu-plugins-framework-scripts.md

from __future__ import annotations

from pathlib import Path

POINTER_SENTENCE = "This file is a pointer. Read `{source}` for the actual instructions."

ROOT = Path(__file__).resolve().parents[4]
PLUGINS_DIR = ROOT / "spek-fu" / "plugins"

# Claude Code frontmatter uses Anthropic's short model names ("haiku"/"sonnet"/"opus").
# GitHub Copilot agent frontmatter expects its own display names for the same models.
GITHUB_MODEL_NAMES = {
    "haiku": "Claude Haiku 4.5",
    "sonnet": "Claude Sonnet 5",
    "opus": "Claude Opus 5",
}


def retarget_model(frontmatter: str, model_name: str) -> str:
    """Rewrite the `model:` line in a frontmatter block to the given name."""
    lines = frontmatter.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("model:"):
            lines[i] = f'model: "{model_name}"'
            break
    return "\n".join(lines) + "\n"


def read_frontmatter_block(path: Path) -> tuple[str, str] | None:
    """Return (frontmatter_block, name) for a SKILL.md/AGENT.md file, or None if malformed."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None

    block_lines = lines[: end + 1]
    name = None
    for line in block_lines[1:end]:
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"').strip("'")
            break
    if not name:
        return None

    return "\n".join(block_lines) + "\n", name


def to_repo_path(path: Path) -> str:
    """Repo-relative path with backslashes, matching the existing pointer convention."""
    return str(path.relative_to(ROOT)).replace("/", "\\")


def write_pointer(target: Path, frontmatter: str, source: Path) -> None:
    content = f"{frontmatter}\n{POINTER_SENTENCE.format(source=to_repo_path(source))}\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_text(encoding="utf-8") != content:
        target.write_text(content, encoding="utf-8")
        print(f"  wrote {to_repo_path(target)}")


def is_stale_pointer(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return "This file is a pointer." in path.read_text(encoding="utf-8")
    except OSError:
        return False


def remove_stale(path: Path, keep_dir: Path | None = None) -> None:
    if not is_stale_pointer(path):
        return
    path.unlink()
    print(f"  removed {to_repo_path(path)}")
    parent = path.parent
    if keep_dir is not None and parent != keep_dir and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()


def regenerate_skills() -> set[str]:
    print("Skills:")
    names = set()
    for skill_md in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md")):
        parsed = read_frontmatter_block(skill_md)
        if parsed is None:
            print(f"  skip (no frontmatter): {to_repo_path(skill_md)}")
            continue
        frontmatter, name = parsed
        names.add(name)
        write_pointer(ROOT / ".claude" / "skills" / name / "SKILL.md", frontmatter, skill_md)
        write_pointer(ROOT / ".github" / "skills" / name / "SKILL.md", frontmatter, skill_md)

    for base in (ROOT / ".claude" / "skills", ROOT / ".github" / "skills"):
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and entry.name not in names:
                remove_stale(entry / "SKILL.md", keep_dir=base)
    return names


def regenerate_agents() -> set[str]:
    print("Agents:")
    names = set()
    for agent_md in sorted(PLUGINS_DIR.glob("*/agents/*/AGENT.md")):
        parsed = read_frontmatter_block(agent_md)
        if parsed is None:
            print(f"  skip (no frontmatter): {to_repo_path(agent_md)}")
            continue
        frontmatter, name = parsed
        names.add(name)
        write_pointer(ROOT / ".claude" / "agents" / name / "AGENT.md", frontmatter, agent_md)

        github_frontmatter = frontmatter
        for source_model, github_model in GITHUB_MODEL_NAMES.items():
            if f'model: "{source_model}"' in frontmatter:
                github_frontmatter = retarget_model(frontmatter, github_model)
                break
        write_pointer(ROOT / ".github" / "agents" / f"{name}.agent.md", github_frontmatter, agent_md)

    claude_agents = ROOT / ".claude" / "agents"
    if claude_agents.is_dir():
        for entry in sorted(claude_agents.iterdir()):
            if entry.is_dir() and entry.name not in names:
                remove_stale(entry / "AGENT.md", keep_dir=claude_agents)

    github_agents = ROOT / ".github" / "agents"
    if github_agents.is_dir():
        for entry in sorted(github_agents.iterdir()):
            if entry.is_file() and entry.name.endswith(".agent.md") and entry.name[: -len(".agent.md")] not in names:
                remove_stale(entry)
    return names


def main() -> None:
    regenerate_skills()
    regenerate_agents()


if __name__ == "__main__":
    main()
