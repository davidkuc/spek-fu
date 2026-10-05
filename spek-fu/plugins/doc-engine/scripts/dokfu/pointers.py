"""
pointers.py - Two-way pointer extraction and validation for dok-fu.

Handles:
- doc->code: reads 'code' field from doc YAML frontmatter
- code->doc: scans source file lines for the pointer comment token
- validate_pair(): confirms both pointers exist and agree
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NamedTuple

from .common import (
    load_config,
    map_doc_to_source,
    map_source_to_doc,
    parse_pointer_line,
    read_frontmatter_file,
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class SourcePointerInfo(NamedTuple):
    """Information about a pointer comment found in a source file.

    Attributes:
        pointer: The doc path string extracted from the pointer comment, or None if not found.
        line_number: The 1-based line number where the pointer was found, or None if not found.
        in_window: True if the pointer is in the first 30 lines (compliant placement),
                   False if it's past line 30 (outside window but still found),
                   None if no pointer was found.
    """
    pointer: str | None
    line_number: int | None
    in_window: bool | None


@dataclass
class ValidationResult:
    """Result of validating a doc<->code pointer pair."""

    doc_path: Path
    source_path: Path | None
    # Pointer found in doc frontmatter (code field)
    doc_has_code_field: bool = False
    # Pointer found in source file comments
    source_has_pointer: bool = False
    # Both pointers resolve to each other
    pair_agrees: bool = False
    # Human-readable list of issues
    issues: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0


# ---------------------------------------------------------------------------
# Section path extraction
# ---------------------------------------------------------------------------

def get_section_paths(doc_path: str | os.PathLike) -> list[str]:
    """Return the repo-relative file paths declared in module section bodies.

    Scans H2 section bodies for ``path: <value>`` lines.  Each H2 section
    in a module documents one source file; the first ``path:`` line after
    the H2 heading gives its repo-relative path.

    Args:
        doc_path: Absolute path to the .md doc file.

    Returns:
        List of path strings in declaration order.
    """
    import re as _re
    try:
        _, body = read_frontmatter_file(doc_path)
    except (ValueError, OSError):
        return []

    paths: list[str] = []
    in_h2 = False
    for line in body.splitlines():
        if line.startswith("## "):
            in_h2 = True
            continue
        if in_h2:
            m = _re.match(r"^path:\s+(\S+)", line.strip())
            if m:
                paths.append(m.group(1))
                in_h2 = False  # one path per section
    return paths


# ---------------------------------------------------------------------------
# doc -> code extraction
# ---------------------------------------------------------------------------

def get_doc_code_pointer(doc_path: str | os.PathLike) -> str | None:
    """Return the 'code' field from a doc's YAML frontmatter, or None.

    Args:
        doc_path: Absolute path to the .md doc file.

    Returns:
        The raw string value of the 'code' frontmatter field, or None.
    """
    try:
        fm, _ = read_frontmatter_file(doc_path)
        return fm.get("code") or None
    except (ValueError, OSError):
        return None


# ---------------------------------------------------------------------------
# code -> doc extraction
# ---------------------------------------------------------------------------

def get_source_doc_pointer(source_path: str | os.PathLike, config: dict[str, Any]) -> SourcePointerInfo:
    """Scan a source file for a dok-fu pointer comment and return detailed info.

    Scans the entire file to detect pointers. The first 30 lines define the
    "header window" — pointers found there are considered compliant (in_window=True).
    Pointers found past line 30 are still detected but flagged as outside the window
    (in_window=False). This allows distinguishing "pointer exists but misplaced"
    from "no pointer found anywhere".

    Args:
        source_path: Absolute path to the source file.
        config: Loaded dok-fu config dict.

    Returns:
        SourcePointerInfo with:
            - pointer: doc path string if found, else None
            - line_number: 1-based line number where found (or None if not found)
            - in_window: True if in first 30 lines, False if past line 30, None if not found
    """
    source_path = Path(source_path)
    try:
        lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return SourcePointerInfo(pointer=None, line_number=None, in_window=None)

    # First pass: scan the 30-line header window
    for line_idx, line in enumerate(lines[:30]):
        result = parse_pointer_line(line, config)
        if result is not None:
            return SourcePointerInfo(pointer=result, line_number=line_idx + 1, in_window=True)

    # Second pass: scan the rest of the file for pointers past the window
    for line_idx in range(30, len(lines)):
        result = parse_pointer_line(lines[line_idx], config)
        if result is not None:
            return SourcePointerInfo(pointer=result, line_number=line_idx + 1, in_window=False)

    # No pointer found anywhere
    return SourcePointerInfo(pointer=None, line_number=None, in_window=None)


# ---------------------------------------------------------------------------
# Pair validation
# ---------------------------------------------------------------------------

def validate_pair(
    doc_path: str | os.PathLike,
    config: dict[str, Any],
    root: str | os.PathLike | None = None,
) -> ValidationResult:
    """Validate the two-way pointer relationship for a doc file.

    Checks:
    1. Doc has a 'code' frontmatter field pointing to an existing source file.
    2. That source file has a pointer comment pointing back to this doc.
    3. Both pointers agree (resolve to each other).

    Args:
        doc_path: Absolute path to the .md doc file.
        config: Loaded dok-fu config dict.
        root: Project root. Falls back to config['_root'] then cwd.

    Returns:
        A :class:`ValidationResult` describing any issues found.
    """
    root = Path(root or config.get("_root") or Path.cwd())
    doc_path = Path(doc_path)
    result = ValidationResult(doc_path=doc_path, source_path=None)

    # 1. Check doc->code pointer (must reference a source folder)
    code_field = get_doc_code_pointer(doc_path)
    if not code_field:
        result.issues.append(f"Doc missing 'code' frontmatter field: {doc_path.relative_to(root).as_posix()}")
        return result

    result.doc_has_code_field = True
    folder_path = root / code_field
    result.source_path = folder_path

    if not folder_path.exists() or not folder_path.is_dir():
        result.issues.append(
            f"Doc 'code' field points to non-existent source folder: {code_field}"
        )
        return result

    # 2. Check that at least one source file in the folder points back to this doc
    expected_doc_rel = doc_path.relative_to(root).as_posix()
    found_pointer = False
    for src_file in folder_path.iterdir():
        if not src_file.is_file():
            continue
        pointer_info = get_source_doc_pointer(src_file, config)
        if pointer_info.pointer == expected_doc_rel:
            found_pointer = True
            break

    if not found_pointer:
        result.issues.append(
            f"No source file in '{code_field}' has a dok-fu pointer to this doc"
        )
        return result

    result.source_has_pointer = True
    result.pair_agrees = True
    return result


def validate_all_docs(
    config: dict[str, Any],
    root: str | os.PathLike | None = None,
) -> list[ValidationResult]:
    """Validate pointer pairs for all doc files under spek-fu/project/code-docs/.

    Args:
        config: Loaded dok-fu config dict.
        root: Project root.

    Returns:
        List of :class:`ValidationResult` objects (one per doc file found).
    """
    root = Path(root or config.get("_root") or Path.cwd())
    docs_dir = config.get("docs_dir", "docs")
    docs_root = root / docs_dir

    results: list[ValidationResult] = []
    if not docs_root.exists():
        return results

    for doc_path in sorted(docs_root.rglob("*.md")):
        # Skip hidden files and index.json-adjacent non-doc files
        if any(part.startswith(".") for part in doc_path.parts):
            continue
        results.append(validate_pair(doc_path, config, root=root))

    return results
