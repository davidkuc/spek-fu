#!/usr/bin/env python3
"""
detect-spec-context.py — Detects whether the workspace is in an active spec-flow context.

CLI: python3 detect-spec-context.py [--workspace-root <path>]

Logic:
1. Run `git -C <workspace-root> branch --show-current` to get the active branch.
2. Check if branch matches `^\\d+-.+` (spec-flow branch pattern).
3. If yes: check whether `features/<branch-name>/spec.md` exists.
4. Output JSON to stdout:
   {"spec-context": true/false, "feature-dir": "features/<branch>/", "branch": "<name>"}
   feature-dir and branch are null when spec-context is false.

Exit 0 always; non-zero only on fatal errors (subprocess cannot be executed).
"""

import argparse
import json
import os
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Detect spec-flow context from current git branch"
    )
    parser.add_argument(
        "--workspace-root",
        default=os.getcwd(),
        help="Absolute path to workspace root (default: cwd)",
    )
    args = parser.parse_args()

    workspace_root = os.path.abspath(args.workspace_root)

    # Get current branch
    try:
        result = subprocess.run(
            ["git", "-C", workspace_root, "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(
            json.dumps({"error": f"git command failed: {result.stderr.strip()}"}),
            file=sys.stderr,
        )
        sys.exit(1)

    branch = result.stdout.strip()

    # Check if branch matches the spec-flow pattern (starts with a number followed by a dash)
    if not re.match(r"^\d+-.+", branch):
        print(json.dumps({"spec-context": False, "feature-dir": None, "branch": None}))
        return

    # Check if spec.md exists in features/<branch>/
    feature_dir = f"features/{branch}/"
    spec_path = os.path.join(workspace_root, "features", branch, "spec.md")

    if os.path.isfile(spec_path):
        print(
            json.dumps(
                {"spec-context": True, "feature-dir": feature_dir, "branch": branch}
            )
        )
    else:
        print(json.dumps({"spec-context": False, "feature-dir": None, "branch": None}))


if __name__ == "__main__":
    main()
