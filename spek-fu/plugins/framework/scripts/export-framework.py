"""Export a fresh copy of the Spek-Fu framework.

Two modes:
- Local (no arguments): rebuilds <repo>/spek-fu-export/ from scratch.
- Path (--target <dir>): copies the framework into an existing project, which
  is also how you update the framework there.

Only the include list below is copied. Project data files ("fresh" files and
folders) are created from templates in templates/export/ and are never
overwritten if they already exist, so re-running on a project is safe.

After copying, the exported regenerate-pointer-files.py is run so the
.claude/ and .github/ pointer files exist in the destination.

Usage:
    python spek-fu/plugins/framework/scripts/export-framework.py
    python spek-fu/plugins/framework/scripts/export-framework.py --target <project-path>
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates" / "export"
LOCAL_EXPORT_DIR = ROOT / "spek-fu-export"

# Folders copied recursively (overwriting existing files).
COPY_TREES = [
    "spek-fu/constitution",
    "spek-fu/plugins/doc-engine",
    "spek-fu/plugins/framework",
    "spek-fu/plugins/project",
    "spek-fu/plugins/spec",
]

# Destination file (relative to project) -> template name in templates/export/.
FRESH_FILES = {
    "spek-fu/constitution/constitution.md": "constitution.md",
    "spek-fu/plugins/framework/knowledge/compound-knowledge.md": "compound-knowledge.md",
    "spek-fu/plugins/framework/knowledge/compound-patterns.md": "compound-patterns.md",
    "spek-fu/project/code-docs/index.json": "code-docs-index.json",
    "spek-fu/project/code-docs/root.md": "code-docs-root.md",
    "spek-fu/project/project.md": "project.md",
    "spek-fu/project/roadmap.md": "roadmap.md",
    "spek-fu/project/technical.md": "technical.md",
    ".gitignore": "python.gitignore",
}

# Folders created empty (a .gitkeep keeps them in git).
FRESH_DIRS = [
    "spek-fu/project/contracts",
    "spek-fu/project/project-docs",
    "spek-fu/project/project-features",
    "spek-fu/project/spec-features",
]

# Created only if missing.
INSTRUCTION_FILES = [".claude/CLAUDE.md", ".github/copilot-instructions.md"]
INSTRUCTION_TEXT = "Follow the constitution: `spek-fu\\constitution\\constitution.md`."

IGNORED_NAMES = shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", ".venv")
POINTER_SCRIPT = "spek-fu/plugins/framework/scripts/regenerate-pointer-files.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a fresh copy of the Spek-Fu framework.")
    parser.add_argument("--target", type=Path, help="Existing project folder to export into. Omit for local mode.")
    return parser.parse_args()


def resolve_destination(target: Path | None) -> Path:
    if target is None:
        if LOCAL_EXPORT_DIR.exists():
            shutil.rmtree(LOCAL_EXPORT_DIR)
        LOCAL_EXPORT_DIR.mkdir()
        return LOCAL_EXPORT_DIR
    target = target.resolve()
    if not target.is_dir():
        sys.exit(f"Error: target folder does not exist: {target}")
    if target == ROOT:
        sys.exit("Error: target is the framework's own repository.")
    return target


def copy_tree(rel: str, dest: Path) -> None:
    """Copy a folder over the destination, leaving out the files that have a fresh template."""
    source = ROOT / rel
    skip = {(ROOT / f).resolve() for f in FRESH_FILES}

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = set(IGNORED_NAMES(directory, names))
        ignored |= {n for n in names if (Path(directory) / n).resolve() in skip}
        return ignored

    shutil.copytree(source, dest / rel, ignore=ignore, dirs_exist_ok=True)
    print(f"  copied {rel}")


def write_if_missing(path: Path, write) -> bool:
    if path.exists():
        print(f"  kept   {path.name} (already exists)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    write(path)
    return True


def create_fresh_files(dest: Path) -> None:
    for rel, template in FRESH_FILES.items():
        target = dest / rel
        if write_if_missing(target, lambda p, t=template: shutil.copyfile(TEMPLATES_DIR / t, p)):
            print(f"  fresh  {rel}")


def create_fresh_dirs(dest: Path) -> None:
    for rel in FRESH_DIRS:
        folder = dest / rel
        if folder.exists():
            print(f"  kept   {rel} (already exists)")
            continue
        folder.mkdir(parents=True)
        (folder / ".gitkeep").touch()
        print(f"  fresh  {rel}/")


def create_instruction_files(dest: Path) -> None:
    for rel in INSTRUCTION_FILES:
        if write_if_missing(dest / rel, lambda p: p.write_text(INSTRUCTION_TEXT, encoding="utf-8")):
            print(f"  fresh  {rel}")


def regenerate_pointers(dest: Path) -> None:
    print("Pointer files:", flush=True)
    subprocess.run([sys.executable, str(dest / POINTER_SCRIPT)], check=True)


def main() -> None:
    dest = resolve_destination(parse_args().target)
    print(f"Exporting framework to {dest}")
    for rel in COPY_TREES:
        copy_tree(rel, dest)
    create_fresh_files(dest)
    create_fresh_dirs(dest)
    create_instruction_files(dest)
    regenerate_pointers(dest)
    print("Done.")


if __name__ == "__main__":
    main()
