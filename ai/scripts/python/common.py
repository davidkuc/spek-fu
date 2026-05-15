"""Shared utilities for SKF Python automation scripts."""

import json
import re
from pathlib import Path
from typing import Any

import yaml

# Optional jsonschema import — callers should check HAS_JSONSCHEMA before use.
try:
    import jsonschema as _jsonschema

    HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    _jsonschema = None  # type: ignore[assignment]
    HAS_JSONSCHEMA = False


def parse_frontmatter(file_path: str | Path) -> dict | None:
    """Parse YAML frontmatter from a Markdown file.

    Opens the file and checks for YAML frontmatter delimited by ``---`` at
    the start of the file.  Extracts the YAML block between the first and
    second ``---`` delimiters, parses it with ``yaml.safe_load``, and returns
    the resulting dict.

    Returns ``None`` if:
    - The file does not start with ``---``.
    - There is no closing ``---`` delimiter.
    - The frontmatter block is empty or cannot be parsed as a mapping.

    Args:
        file_path: Path to the Markdown file.

    Returns:
        A dict of frontmatter fields, or ``None`` if no valid frontmatter is
        present.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return None

    # Strip the opening delimiter line and look for the closing one.
    rest = content[3:]
    # The opening --- may be followed immediately by a newline or by content.
    # Normalise: skip the newline that directly follows the opening ---.
    if rest.startswith("\n"):
        rest = rest[1:]
    elif rest.startswith("\r\n"):
        rest = rest[2:]

    # Find the closing --- delimiter.
    closing_index = rest.find("\n---")
    if closing_index == -1:
        return None

    yaml_block = rest[:closing_index]
    if not yaml_block.strip():
        return None

    parsed = yaml.safe_load(yaml_block)
    if not isinstance(parsed, dict):
        return None

    return parsed


def load_json_file(path: str | Path) -> dict | list:
    """Load a JSON file and return its contents.

    Args:
        path: Path to the JSON file.

    Returns:
        The parsed JSON contents as a dict or list.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file content is not valid JSON.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")
    try:
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {p}: {exc}") from exc


def write_json_file(path: str | Path, data: dict | list, indent: int = 2) -> None:
    """Write data as JSON to a file, creating parent directories as needed.

    Args:
        path: Destination file path.
        data: Data to serialise as JSON.
        indent: Number of spaces to use for indentation (default 2).
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)
        fh.write("\n")


def get_file_type_from_path(file_path: str | Path, schemas: dict) -> str | None:
    """Infer the SKF file-type key from a file path and the loaded schemas dict.

    Mapping rules (evaluated in order):
    - ``/skills/``    → ``"skills"``
    - ``/knowledge/`` (and not ``/lessons/``) → ``"knowledge"``
    - ``/patterns/``  → ``"patterns"``
    - ``/runbooks/``  → ``"runbooks"``
    - ``/templates/`` → ``"templates"``

    Returns ``None`` if no rule matches or the inferred type is not a key in
    ``schemas``.

    Args:
        file_path: The file path to inspect.
        schemas: The loaded frontmatter-schemas dict (keys are type names).

    Returns:
        The matching type key string, or ``None``.
    """
    normalised = Path(file_path).as_posix()

    mapping: list[tuple[str, str | None]] = [
        ("/skills/", "skills"),
        ("/patterns/", "patterns"),
        ("/runbooks/", "runbooks"),
        ("/templates/", "templates"),
    ]

    for segment, type_key in mapping:
        if segment in normalised:
            if type_key in schemas:
                return type_key
            return None

    # knowledge check: must contain /knowledge/ but not /lessons/
    if "/knowledge/" in normalised and "/lessons/" not in normalised:
        if "knowledge" in schemas:
            return "knowledge"

    return None


def print_table(rows: list[dict], columns: list[str]) -> None:
    """Print a simple aligned text table to stdout.

    Column widths are determined by the maximum of the header width and the
    widest value in that column.

    Args:
        rows: List of dicts where each dict maps column names to cell values.
        columns: Ordered list of column names to display.
    """
    # Compute column widths.
    widths: dict[str, int] = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            cell = str(row.get(col, ""))
            if len(cell) > widths[col]:
                widths[col] = len(cell)

    # Build format string.
    def _row_str(values: list[str]) -> str:
        return "  ".join(v.ljust(widths[col]) for col, v in zip(columns, values))

    header = _row_str(columns)
    separator = "  ".join("-" * widths[col] for col in columns)

    print(header)
    print(separator)
    for row in rows:
        print(_row_str([str(row.get(col, "")) for col in columns]))


def format_json_output(data: Any) -> str:
    """Return a pretty-printed JSON string.

    Args:
        data: Any JSON-serialisable value.

    Returns:
        A 2-space-indented JSON string with Unicode preserved.
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


def validate_json_schema(
    instance: Any,
    schema: dict,
) -> tuple[bool, list[dict[str, str]]]:
    """Validate *instance* against *schema* using Draft 7.

    Collects all validation errors (does not stop at the first one).
    Requires the ``jsonschema`` package; check ``HAS_JSONSCHEMA`` before
    calling this function.

    Args:
        instance: The JSON-serialisable value to validate.
        schema: A JSON Schema dict (Draft 7).

    Returns:
        A tuple ``(is_valid, errors)`` where ``errors`` is a list of dicts
        with keys ``"path"`` (dot-notation location) and ``"message"``
        (human-readable description).  ``is_valid`` is ``True`` when
        ``errors`` is empty.

    Raises:
        RuntimeError: If the ``jsonschema`` package is not installed.
        jsonschema.SchemaError: If *schema* itself is invalid.
    """
    if not HAS_JSONSCHEMA:
        raise RuntimeError(
            "jsonschema is not installed. Run: pip install jsonschema"
        )

    errors: list[dict[str, str]] = []
    validator = _jsonschema.Draft7Validator(schema)
    for error in validator.iter_errors(instance):
        path_parts = list(error.absolute_path)
        path = ".".join(str(p) for p in path_parts) if path_parts else "$"
        errors.append({"path": path, "message": error.message})
    return (len(errors) == 0, errors)


def fill_template_placeholders(
    data: Any,
    frontmatter: dict,
    skill_id: str,
) -> Any:
    """Recursively replace ``<<FRONTMATTER: key>>`` tokens in *data*.

    Rules:
    - A string that is *exactly* ``<<FRONTMATTER: key>>`` is replaced by the
      corresponding frontmatter value (preserving its type — dict, list, etc.).
    - The special token ``<<FRONTMATTER: id>>`` is replaced by *skill_id*.
    - If the key is not present in *frontmatter*, the token becomes
      ``<<MISSING: key not defined in frontmatter>>``.
    - ``<<RUNTIME: ...>>`` tokens are left unchanged.
    - Non-string scalars (int, bool, None, …) are returned unchanged.

    Args:
        data: The value to process — may be a dict, list, string, or scalar.
        frontmatter: Parsed frontmatter dict from a skill file.
        skill_id: The skill ID used to resolve ``<<FRONTMATTER: id>>`` tokens.

    Returns:
        The processed value with frontmatter tokens replaced.
    """
    if isinstance(data, dict):
        return {k: fill_template_placeholders(v, frontmatter, skill_id) for k, v in data.items()}

    if isinstance(data, list):
        return [fill_template_placeholders(item, frontmatter, skill_id) for item in data]

    if isinstance(data, str):
        # Whole-string token → replace with native frontmatter value.
        if data.startswith("<<FRONTMATTER:") and data.endswith(">>"):
            key = data[len("<<FRONTMATTER:") : -len(">>")].strip()
            if key == "id":
                return skill_id
            return frontmatter.get(key, f"<<MISSING: {key} not defined in frontmatter>>")

        # Inline token inside a longer string (e.g., a path).
        if "<<FRONTMATTER: id>>" in data:
            return data.replace("<<FRONTMATTER: id>>", skill_id)

        return data

    return data


# ── Markdown Parsing Helpers ──────────────────────────────────────────────────

def read_markdown_section(content: str, section_header: str, level: int = 2) -> str:
    """
    Extracts the content of a named section from a markdown document.
    
    Args:
        content: The full markdown document content.
        section_header: The section header to find (e.g., "Wave 1 Summary").
        level: The heading level (2 for ##, 3 for ###). Default is 2.
    
    Returns:
        String content of the section, or empty string if not found.
    """
    prefix = '#' * level
    lines = content.split('\n')
    capturing = False
    result = []
    
    for line in lines:
        stripped = line.rstrip()
        if stripped == f"{prefix} {section_header}" or stripped.lower() == f"{prefix} {section_header}".lower():
            capturing = True
            continue
        if capturing:
            # Stop at next heading of same or higher level
            if re.match(r'^#{1,' + str(level) + r'}\s', line):
                break
            result.append(line)
    
    return '\n'.join(result).strip()


def get_markdown_field(content: str, field_name: str) -> str:
    """
    Extracts the value of a field from a markdown bullet list item.
    
    Args:
        content: The markdown content to search.
        field_name: The field name to find (e.g., "Status", "Wave", "Output path").
    
    Returns:
        String value of the field, or empty string if not found.
    """
    pattern = rf'^\s*-\s+\*\*{re.escape(field_name)}\*\*:\s*(.+)$'
    for line in content.split('\n'):
        m = re.match(pattern, line)
        if m:
            return m.group(1).strip()
    return ''


def parse_knowledge_markdown(path: str | Path) -> list[dict]:
    """Parse lessons from a knowledge database markdown file.

    Each lesson is delimited by a ``## L-{id}: {title}`` heading and contains
    ``**Tags**``, ``**Trigger**``, ``**Context**``, and ``**Solution**`` fields.

    Args:
        path: Path to the markdown file.

    Returns:
        A list of lesson dicts with keys: id, title, tags, trigger, context,
        solution.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Markdown file not found: {p}")

    content = p.read_text(encoding="utf-8")

    # Split on lesson heading boundaries; first element is the file intro.
    raw_blocks = content.split("\n## L-")

    lessons: list[dict] = []
    for block in raw_blocks[1:]:
        lines = block.split("\n")
        heading_line = lines[0]
        # heading_line format: "{id}: {title}"  (the '## L-' prefix was consumed)
        colon_idx = heading_line.find(":")
        if colon_idx == -1:
            continue
        id_str = heading_line[:colon_idx].strip()
        title = heading_line[colon_idx + 1:].strip()
        try:
            lesson_id = int(id_str)
        except ValueError:
            continue

        block_text = "\n".join(lines[1:])

        def _extract_field(field: str) -> str:
            m = re.search(
                rf"\*\*{field}\*\*:\s*(.*?)(?=\n\*\*|\n---|\Z)",
                block_text,
                re.DOTALL,
            )
            return m.group(1).strip() if m else ""

        tags_raw = _extract_field("Tags")
        tags = re.findall(r"`([^`]+)`", tags_raw)

        lessons.append({
            "id": lesson_id,
            "title": title,
            "tags": tags,
            "trigger": _extract_field("Trigger"),
            "context": _extract_field("Context"),
            "solution": _extract_field("Solution"),
        })

    return lessons


def parse_markdown_list(content: str) -> list:
    """
    Parses a markdown bullet list into a Python list of strings.
    
    Args:
        content: The markdown content containing the list.
    
    Returns:
        List of strings (without leading "- " markers).
    """
    items = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('- '):
            items.append(stripped[2:].strip())
    return items


def read_wave_summary_md(path: str) -> dict:
    """
    Parses a wave-{N}-summary.md file into a dictionary.
    
    Args:
        path: Path to the wave summary markdown file.
    
    Returns:
        Dict with wave, goal, status, steps_completed, steps_skipped, steps_failed, issues, notes keys.
        Returns None if file not found.
    """
    import os
    if not os.path.exists(path):
        return None
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        'wave': get_markdown_field(content, 'Wave'),
        'goal': get_markdown_field(content, 'Goal'),
        'status': get_markdown_field(content, 'Status'),
        'steps_completed': get_markdown_field(content, 'Steps completed'),
        'steps_skipped': get_markdown_field(content, 'Steps skipped'),
        'steps_failed': get_markdown_field(content, 'Steps failed'),
        'issues': read_markdown_section(content, 'Issues', level=3),
        'notes': read_markdown_section(content, 'Notes', level=3),
    }


def validate_dispatch_manifest_md(content: str, variant: str = 'full') -> tuple:
    """
    Validates a markdown dispatch manifest for required sections.
    
    Args:
        content: The markdown content of the dispatch manifest.
        variant: 'full' or 'compact'. Full requires Identity, Advisory, Output Format.
    
    Returns:
        Tuple of (is_valid: bool, errors: list of str).
    """
    errors = []
    required_sections = ['Skill', 'Task', 'Context', 'Constraints', 'Tier']
    
    if variant == 'full':
        required_sections = ['Identity', 'Skill', 'Task', 'Context', 'Constraints', 'Advisory', 'Output Format', 'Tier']
    
    # Check for Dispatch Manifest header
    if '## Dispatch Manifest' not in content:
        errors.append("Missing '## Dispatch Manifest' header")
    
    for section in required_sections:
        if f'### {section}' not in content:
            errors.append(f"Missing required section: ### {section}")
    
    # Check required fields in Identity (full only)
    if variant == 'full' and '### Identity' in content:
        identity_content = read_markdown_section(content, 'Identity', level=3)
        for field in ['Skill', 'Function', 'Anti-scope']:
            if get_markdown_field(identity_content, field) == '':
                errors.append(f"Missing or empty field in Identity: {field}")
    
    # Check Tier is valid
    tier_section = read_markdown_section(content, 'Tier', level=3)
    valid_tiers = ['fast-agent', 'standard-agent', 'large-context-agent']
    if tier_section.strip() not in valid_tiers:
        errors.append(f"Invalid Tier value: '{tier_section.strip()}'. Must be one of: {', '.join(valid_tiers)}")
    
    return (len(errors) == 0, errors)


# ── Markdown Table Parsing ─────────────────────────────────────────────────────

def parse_markdown_table(text: str) -> list[dict[str, str]]:
    """Parse a markdown table into a list of dictionaries.
    
    Parses markdown tables with pipe-delimited columns and a separator row.
    Each row becomes a dict mapping header names to cell values.
    
    Args:
        text: Markdown text containing a table (may have leading/trailing whitespace).
    
    Returns:
        List of dicts where each dict maps column names to cell values.
        Returns empty list if:
        - Text is empty or None.
        - No table structure is found (header, separator, data rows).
    """
    if not text or not isinstance(text, str):
        return []
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if len(lines) < 2:
        return []
    
    # Find the header row (first line containing '|')
    header_idx = -1
    for i, line in enumerate(lines):
        if '|' in line:
            header_idx = i
            break
    
    if header_idx == -1:
        return []
    
    # Parse header row
    header_line = lines[header_idx]
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    if not headers:
        return []
    
    # Find separator row (contains dashes and pipes, e.g., "| --- | --- |")
    sep_idx = -1
    for i in range(header_idx + 1, len(lines)):
        line = lines[i]
        # Check if line matches separator pattern: only pipes, dashes, spaces, and colons
        if re.match(r'^[\|\s\-:]+$', line):
            sep_idx = i
            break
    
    # If no separator found, assume next line is separator
    if sep_idx == -1:
        sep_idx = header_idx + 1
    
    # Parse data rows (all lines after separator)
    result: list[dict[str, str]] = []
    for i in range(sep_idx + 1, len(lines)):
        line = lines[i]
        if not line or '|' not in line:
            continue
        
        values = [v.strip() for v in line.split('|') if v.strip()]
        
        # Only include rows with matching column count
        if len(values) == len(headers):
            row_dict = dict(zip(headers, values))
            result.append(row_dict)
    
    return result


def read_dispatch_manifest_md(content: str) -> dict[str, str]:
    """Parse a dispatch manifest markdown block into a dictionary.
    
    Extracts fields like Skill, Task, Status, Wave, Step, OutputPath, Summary.
    
    Args:
        content: The markdown content of the dispatch manifest.
    
    Returns:
        Dict with extracted field values. Missing fields default to empty string.
    """
    return {
        'Skill': get_markdown_field(content, 'Skill'),
        'Task': read_markdown_section(content, 'Task', level=3),
        'Status': get_markdown_field(content, 'Status'),
        'Wave': get_markdown_field(content, 'Wave'),
        'Step': get_markdown_field(content, 'Step'),
        'OutputPath': get_markdown_field(content, 'Output path'),
        'Summary': get_markdown_field(content, 'Summary'),
    }


# ── File System Operations ──────────────────────────────────────────────────────

def resolve_file_path(path: str | Path, base: str | Path | None = None) -> str:
    """Resolve a file path to an absolute path.
    
    If the path is already absolute, return it as-is.
    Otherwise, resolve it relative to `base` (or current working directory if base is None).
    
    Args:
        path: The file path to resolve.
        base: Base directory for relative paths. If None, uses current working directory.
    
    Returns:
        Absolute file path as a string.
    """
    p = Path(path)
    if p.is_absolute():
        return str(p)
    
    if base is None:
        return str(Path.cwd() / p)
    
    base_path = Path(base)
    return str(base_path / p)


def check_file_exists(path: str | Path, description: str = "") -> bool:
    """Check if a file exists and optionally print a status message.
    
    Args:
        path: Path to the file to check.
        description: Optional description to print (if provided, prints "✓ description" or "✗ description").
    
    Returns:
        True if file exists, False otherwise.
    """
    exists = Path(path).is_file()
    if description:
        status = "✓" if exists else "✗"
        print(f"  {status} {description}")
    return exists


def check_path_exists(path: str | Path, is_dir: bool = False, description: str = "") -> bool:
    """Check if a path exists (file or directory).
    
    Args:
        path: Path to check.
        is_dir: If True, check for directory; if False, check for file.
        description: Optional description to print with status icon.
    
    Returns:
        True if path exists with the specified type, False otherwise.
    """
    p = Path(path)
    if is_dir:
        exists = p.is_dir()
    else:
        exists = p.is_file()
    
    if description:
        status = "✓" if exists else "✗"
        print(f"  {status} {description}")
    return exists


# ── Markdown Heading Parsing ───────────────────────────────────────────────────

def get_markdown_heading(line: str) -> dict[str, Any]:
    """Parse a markdown heading line and extract heading type and content.
    
    Recognizes:
    - Wave headings: "## Wave N" or "**Wave N**" with optional title
    - Step headings: "### Step N.M" or "**Step N.M**" with optional title
    - Generic ATX headings: "# text", "## text", etc.
    
    Args:
        line: A single line of markdown.
    
    Returns:
        Dict with:
        - For wave: {'type': 'wave', 'number': 'N', 'title': 'optional title'}
        - For step: {'type': 'step', 'id': 'N.M', 'title': 'optional title'}
        - For section: {'type': 'section', 'level': N, 'title': 'text'}
        - If not a heading: {'type': 'none'}
    """
    # Wave heading: ## Wave N or **Wave N**
    wave_match = re.search(r'(?i)^(#{2,4})\s+Wave\s+(\d+)\s*(?:[—\-]\s*(.+))?$', line)
    if wave_match:
        number = wave_match.group(2)
        title = (wave_match.group(3) or "").strip()
        return {'type': 'wave', 'number': number, 'title': title}
    
    wave_match2 = re.search(r'(?i)^\*\*Wave\s+(\d+)\*\*\s*(?:[—\-]\s*(.+))?$', line)
    if wave_match2:
        number = wave_match2.group(1)
        title = (wave_match2.group(2) or "").strip()
        return {'type': 'wave', 'number': number, 'title': title}
    
    # Step heading: ### Step N.M or **Step N.M**
    step_match = re.search(r'(?i)^#{3,5}\s+Step\s+([\d\.]+)(?:\s*[—\-]\s*(.+))?$', line)
    if step_match:
        step_id = step_match.group(1)
        title = (step_match.group(2) or "").strip()
        return {'type': 'step', 'id': step_id, 'title': title}
    
    step_match2 = re.search(r'(?i)^\*\*Step\s+([\d\.]+)\*\*(?:\s*[—\-]\s*(.+))?$', line)
    if step_match2:
        step_id = step_match2.group(1)
        title = (step_match2.group(2) or "").strip()
        return {'type': 'step', 'id': step_id, 'title': title}
    
    # Generic ATX heading (any level)
    atx_match = re.match(r'^(#{1,6})\s+(.+)$', line)
    if atx_match:
        level = len(atx_match.group(1))
        title = atx_match.group(2).strip()
        return {'type': 'section', 'level': level, 'title': title}
    
    return {'type': 'none'}


# ── Status Output ───────────────────────────────────────────────────────────────

def write_status_message(
    message: str,
    status: str = 'info',
) -> None:
    """Write a status message to stdout with a colored icon.
    
    Args:
        message: The message text.
        status: Status type ('ok', 'fail', 'warn', 'info', 'header').
                Determines icon and formatting.
    """
    icons = {
        'ok': '✓',
        'fail': '✗',
        'warn': '⚠',
        'info': ' ',
        'header': ' ',
    }
    icon = icons.get(status, ' ')
    print(f"  {icon} {message}")


# ── String Utilities ────────────────────────────────────────────────────────────

def get_levenshtein_distance(a: str, b: str) -> int:
    """Calculate the Levenshtein distance between two strings.
    
    The Levenshtein distance is the minimum number of single-character edits
    (insertions, deletions, substitutions) required to transform one string
    into another.
    
    Args:
        a: First string.
        b: Second string.
    
    Returns:
        The Levenshtein distance as an integer.
    """
    m, n = len(a), len(b)
    
    # Create a (m+1) x (n+1) matrix
    d = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize first column and row
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j
    
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,      # deletion
                d[i][j - 1] + 1,      # insertion
                d[i - 1][j - 1] + cost  # substitution
            )
    
    return d[m][n]


def convert_to_normalized_array(value: Any) -> list[str]:
    """Convert a value to a normalized array of strings.
    
    Handles:
    - None/empty: returns []
    - Lists/iterables: flattens and splits by comma
    - Strings: splits by comma
    
    Each item is trimmed and empty items are filtered out.
    
    Args:
        value: Any value to convert.
    
    Returns:
        List of non-empty strings.
    """
    if value is None:
        return []
    
    # If it's an iterable (but not a string), flatten it
    if hasattr(value, '__iter__') and not isinstance(value, str):
        result = []
        for item in value:
            item_str = str(item).strip()
            if item_str:
                # Also split by comma in case items contain comma-separated values
                result.extend([x.strip() for x in item_str.split(',') if x.strip()])
        return result
    
    # If it's a string, split by comma
    value_str = str(value).strip()
    if not value_str:
        return []
    
    return [x.strip() for x in value_str.split(',') if x.strip()]


def convert_to_markdown_list(items: list[str]) -> str:
    """Convert a list of strings to a markdown bullet list.
    
    Args:
        items: List of strings.
    
    Returns:
        Markdown bullet list as a string, with each item on a new line.
    """
    return '\n'.join(f"- {item}" for item in items)


# ── Git & Repository Operations ─────────────────────────────────────────────────

def find_skf_root(start_dir: str | Path | None = None) -> str | None:
    """Find the SKF project root by looking for the 'ai' directory.
    
    Searches upward from start_dir (or current directory) until it finds
    a directory containing an 'ai' subdirectory.
    
    Args:
        start_dir: Starting directory. If None, uses current working directory.
    
    Returns:
        Absolute path to SKF root, or None if not found.
    """
    if start_dir is None:
        current = Path.cwd()
    else:
        current = Path(start_dir).resolve()
    
    while True:
        ai_dir = current / 'ai'
        if ai_dir.is_dir():
            return str(current)
        
        parent = current.parent
        if parent == current:  # reached root
            return None
        
        current = parent


def get_repo_root() -> str:
    """Get the repository root directory.
    
    Tries in order:
    1. find_skf_root()
    2. git rev-parse --show-toplevel
    3. Resolved path relative to this file's location
    
    Returns:
        Absolute path to repository root as a string.
    """
    import subprocess
    
    skf_root = find_skf_root()
    if skf_root:
        return skf_root
    
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback: resolve relative to this file
    script_dir = Path(__file__).parent
    # Navigate from ai/scripts/python to repository root
    return str(script_dir.parent.parent.parent)


def has_git() -> bool:
    """Check if git is available and we're in a git repository.
    
    Returns:
        True if git command exists and we're in a git repository, False otherwise.
    """
    import subprocess
    
    try:
        # Check if git command exists
        subprocess.run(['git', '--version'], capture_output=True, timeout=2, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
    
    try:
        repo_root = get_repo_root()
        result = subprocess.run(
            ['git', '-C', repo_root, 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_current_branch() -> str:
    """Get the current git branch or iteration directory name.
    
    Tries in order:
    1. SKF_FEATURE environment variable
    2. git rev-parse --abbrev-ref HEAD
    3. Latest iteration directory (highest ###-name)
    4. Falls back to 'main'
    
    Returns:
        Branch name or iteration directory name as a string.
    """
    import os
    import subprocess
    
    # Check environment variable
    if 'SKF_FEATURE' in os.environ:
        return os.environ['SKF_FEATURE']
    
    repo_root = get_repo_root()
    
    # Try git
    if has_git():
        try:
            result = subprocess.run(
                ['git', '-C', repo_root, 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Check iterations directory
    iter_dir = Path(repo_root) / 'iterations'
    if iter_dir.is_dir():
        highest = 0
        latest_feature = ""
        for item in iter_dir.iterdir():
            if item.is_dir():
                match = re.match(r'^(\d{3})-', item.name)
                if match:
                    num = int(match.group(1))
                    if num > highest:
                        highest = num
                        latest_feature = item.name
        if latest_feature:
            return latest_feature
    
    return "main"


def is_feature_branch(branch: str, has_git: bool = True) -> bool:
    """Check if a branch name follows the feature branch convention (###-name).
    
    Args:
        branch: Branch name to check.
        has_git: If False, returns True without validation (prints warning).
    
    Returns:
        True if branch matches feature naming (###-*), False otherwise.
    """
    if not has_git:
        print("[skf] Warning: Git repository not detected; skipped branch validation")
        return True
    
    if not re.match(r'^\d{3}-', branch):
        print(f"ERROR: Not on a feature branch. Current branch: {branch}")
        print("Feature branches should be named like: 001-feature-name")
        return False
    
    return True


def get_iteration_dir(repo_root: str | Path, branch: str) -> str:
    """Get the iteration directory path for a given branch.
    
    Args:
        repo_root: Repository root path.
        branch: Branch name (e.g., "001-feature-name").
    
    Returns:
        Path to iteration directory.
    """
    return str(Path(repo_root) / "iterations" / branch)


def get_next_iteration_number(repo_root: str | Path) -> int:
    """Get the next iteration number based on existing iteration directories.
    
    Scans the iterations directory and returns the highest three-digit number + 1.
    
    Args:
        repo_root: Repository root path.
    
    Returns:
        Next iteration number (int), or 1 if no iterations exist.
    """
    iter_dir = Path(repo_root) / "iterations"
    if not iter_dir.is_dir():
        return 1
    
    highest = 0
    for item in iter_dir.iterdir():
        if item.is_dir():
            match = re.match(r'^(\d{3})-', item.name)
            if match:
                num = int(match.group(1))
                if num > highest:
                    highest = num
    
    return highest + 1


def get_iteration_paths(repo_root: str | Path | None = None, branch: str | None = None) -> dict[str, str]:
    """Get all iteration-related file paths for the current feature branch.
    
    Args:
        repo_root: Repository root path. If None, uses get_repo_root().
        branch: Branch/iteration name. If None, uses get_current_branch().
    
    Returns:
        Dict with keys: REPO_ROOT, CURRENT_BRANCH, HAS_GIT, ITERATION_DIR, SPEC, PLAN,
        TASKS, CHECKLIST, DOC_UPDATE, CONTRACTS_DIR.
    """
    if repo_root is None:
        repo_root = get_repo_root()
    else:
        repo_root = str(repo_root)
    
    if branch is None:
        branch = get_current_branch()
    
    git_available = has_git()
    iter_dir = get_iteration_dir(repo_root, branch)
    
    return {
        'REPO_ROOT': repo_root,
        'CURRENT_BRANCH': branch,
        'HAS_GIT': str(git_available),
        'ITERATION_DIR': iter_dir,
        'SPEC': str(Path(iter_dir) / 'spec.md'),
        'PLAN': str(Path(iter_dir) / 'plan.md'),
        'TASKS': str(Path(iter_dir) / 'tasks.md'),
        'CHECKLIST': str(Path(iter_dir) / 'checklist.md'),
        'CONTRACTS_DIR': str(Path(iter_dir) / 'contracts'),
    }
