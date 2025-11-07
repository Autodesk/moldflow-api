# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Custom logging utility for test data generation with clean, professional output.
"""

import sys
from pathlib import Path
from typing import Dict, Set
from tests.api.integration_tests.constants import METADATA_FILE


class GenerateDataLogger:
    """A clean, professional logger for data generation scripts."""

    def __init__(self):
        self.generated_files: Dict[str, Set[str]] = {}
        self.metadata_file = METADATA_FILE

    def track_generation(self, marker: str, data_file_name: str):
        """Track a generated file for a specific marker."""
        if marker not in self.generated_files:
            self.generated_files[marker] = set()

        self.generated_files[marker].add(data_file_name)

    def error(self, message: str):
        """Log an error message."""
        print(f"❌ ERROR: {message}", file=sys.stderr)

    def info(self, message: str):
        """Log an info message."""
        print(f"ℹ️  {message}")

    def print_summary(self, data_dir: Path):
        """Print a beautiful summary of all generated files."""
        if not self.generated_files:
            return

        print("\n" + "─" * 60)
        print("📦 Test Data Generation Summary")
        print("─" * 60)

        for marker, files in self.generated_files.items():
            # Sort files to ensure consistent order
            sorted_files = sorted(files)
            files_str = ", ".join(sorted_files)

            print(f"[DATA GEN] {marker:<8} →  {files_str}")

            # Print file URLs with proper indentation
            for filename in sorted_files:
                file_path = data_dir / filename
                file_url = file_path.as_uri()
                print(f"    ↳ {file_url}")

            print()  # Empty line between markers

        print("✅ All data files generated successfully.")
        print("─" * 60)


# Global instance
generate_data_logger = GenerateDataLogger()
