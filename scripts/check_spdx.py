#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Script to add SPDX headers to Python source files.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List
import pathspec

SPDX_HEADER = '''# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

'''

# Files or directories to skip
SKIP_PATTERNS = {
    # Build artifacts
    'build/',
    'dist/',
    '*.egg-info/',
    # Virtual environments
    'venv/',
    '.env/',
    # Cache directories
    '__pycache__/',
    '.pytest_cache/',
    # Locale files
    'locale/',
    '*.po',
    '*.mo',
}

def get_gitignore_spec(repo_root: str) -> pathspec.PathSpec:
    """Load .gitignore patterns."""
    gitignore_file = os.path.join(repo_root, '.gitignore')
    if os.path.exists(gitignore_file):
        with open(gitignore_file, 'r') as f:
            return pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, 
                f.readlines()
            )
    return pathspec.PathSpec([])

def should_skip(path: str, gitignore_spec: pathspec.PathSpec) -> bool:
    """Check if a file should be skipped."""
    # Convert to relative path for gitignore matching
    rel_path = os.path.relpath(path, start=str(Path(__file__).parent.parent))
    
    # Check gitignore patterns
    if gitignore_spec.match_file(rel_path):
        return True
        
    # Check our custom skip patterns
    parts = Path(path).parts
    return any(
        any(part.startswith(skip.rstrip('/')) for part in parts)
        for skip in SKIP_PATTERNS
    )

def has_spdx_header(content: str) -> bool:
    """Check if file already has an SPDX header."""
    first_lines = content.split('\n')[:3]
    return any('SPDX-License-Identifier' in line for line in first_lines)

def add_spdx_header(file_path: str) -> bool:
    """Add SPDX header to a file if it doesn't have one."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if has_spdx_header(content):
            print(f"Skipping {file_path} - already has SPDX header")
            return False
            
        # If there's a shebang, preserve it
        if content.startswith('#!'):
            shebang, rest = content.split('\n', 1)
            new_content = f"{shebang}\n{SPDX_HEADER}{rest}"
        else:
            new_content = SPDX_HEADER + content
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"Added SPDX header to {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False

def find_python_files(start_dir: str, gitignore_spec: pathspec.PathSpec) -> List[str]:
    """Find all Python files in the directory tree."""
    python_files = []
    for root, _, files in os.walk(start_dir):
        if should_skip(root, gitignore_spec):
            continue
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                if not should_skip(full_path, gitignore_spec):
                    python_files.append(full_path)
    return python_files

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SPDX header checker/adder")
    parser.add_argument("--check-only", action="store_true", help="Only check, do not modify files")
    args = parser.parse_args()

    # Get repository root (assumes script is in scripts/ directory)
    repo_root = str(Path(__file__).parent.parent)

    # Load gitignore patterns
    gitignore_spec = get_gitignore_spec(repo_root)

    # Find all Python files
    python_files = find_python_files(repo_root, gitignore_spec)

    missing = []
    modified = 0

    if args.check_only:
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not has_spdx_header(content):
                    missing.append(file_path)
            except Exception as e:  # pragma: no cover
                print(f"Error reading {file_path}: {e}", file=sys.stderr)
        if missing:
            print("Files missing SPDX headers:")
            for p in missing:
                print(f"  {p}")
            print(f"\nChecked {len(python_files)} files; {len(missing)} missing headers")
            return 1
        print(f"Checked {len(python_files)} files; all have SPDX headers")
        return 0
    else:
        for file_path in python_files:
            if add_spdx_header(file_path):
                modified += 1

        print(f"\nProcessed {len(python_files)} files")
        print(f"Added SPDX headers to {modified} files")
        return 0

if __name__ == '__main__':
    main()
