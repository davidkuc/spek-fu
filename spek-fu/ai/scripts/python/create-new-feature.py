#!/usr/bin/env python3
"""Create a new feature branch and project structure.

Purpose:
  Creates a new feature branch using the ###-branch-name naming convention,
    initializes a /spek-fu/features folder in the project root if it does not exist,
  and creates a dedicated feature folder with the same name as the branch.

Usage:
  python create-new-feature.py --feature-name "my-feature"
  python create-new-feature.py --feature-number 42 --feature-name "authentication"

Exit Codes:
  0: Success — branch and folders created
  1: Validation error (invalid input, existing branch)
  2: Git error (failed to create branch or switch)
  3: Filesystem error (permission denied, disk full)
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path


def get_next_feature_number() -> int:
    """Get the next available feature number by checking existing folders."""
    features_dir = Path("spek-fu/features")
    numbers = []
    
    if features_dir.exists():
        for folder in features_dir.iterdir():
            if folder.is_dir():
                try:
                    # Extract number from folder name (e.g., "001-my-feature" -> 1)
                    num = int(folder.name.split("-")[0])
                    numbers.append(num)
                except (ValueError, IndexError):
                    pass
    
    return max(numbers, default=0) + 1


def create_git_branch(branch_name: str) -> bool:
    """Create a new git branch."""
    try:
        subprocess.run(
            ["git", "branch", branch_name],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "checkout", branch_name],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create/checkout branch: {e.stderr}")
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new feature branch and project structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--feature-number",
        type=int,
        required=False,
        help="Feature number (auto-increment if omitted)"
    )
    parser.add_argument(
        "--feature-name",
        type=str,
        required=True,
        help="Feature name (alphanumeric, hyphens allowed)"
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get feature number (auto-increment if not provided)
    feature_num = args.feature_number
    if feature_num is None:
        feature_num = get_next_feature_number()
        if feature_num == 1 and not isinstance(feature_num, int):
            logger.error("Failed to determine next feature number")
            return 1
    
    # Create branch name with ###-feature-name convention
    branch_name = f"{feature_num:03d}-{args.feature_name}".lower()
    logger.info(f"Creating feature branch: {branch_name}")
    
    # Create git branch
    if not create_git_branch(branch_name):
        return 2
    
    # Ensure /spek-fu/features folder exists
    features_dir = Path("spek-fu/features")
    features_dir.mkdir(exist_ok=True)
    logger.info(f"Ensured /spek-fu/features directory exists: {features_dir}")
    
    # Create feature-specific folder (same name as the branch for consistency)
    feature_dir = features_dir / branch_name
    feature_dir.mkdir(exist_ok=True)
    logger.info(f"Created feature directory: {feature_dir}")
    
    # Create spec file path
    spec_file = feature_dir / "spec.md"
    
    # Output results
    if args.output_json:
        output = {
            "branch-name": branch_name,
            "spec-file": str(spec_file),
            "feature-dir": str(feature_dir),
        }
        print(json.dumps(output))
    else:
        logger.info(f"Feature setup complete: {branch_name}")
        logger.info(f"  BRANCH_NAME: {branch_name}")
        logger.info(f"  SPEC_FILE: {spec_file}")
        logger.info(f"  FEATURE_DIR: {feature_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
