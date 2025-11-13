# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Constants for integration tests.
"""

from pathlib import Path
from enum import Enum

INTEGRATION_TESTS_DIR = Path(__file__).parent
STUDY_FILES_DIR = INTEGRATION_TESTS_DIR / "study_files"
DATA_DIR = INTEGRATION_TESTS_DIR / "data"
ROOT_DIR = INTEGRATION_TESTS_DIR.parent.parent.parent

STUDIES_FILE_NAME = "studies.json"
STUDIES_FILE = Path(STUDY_FILES_DIR) / STUDIES_FILE_NAME

METADATA_FILE_NAME = "metadata.json"
METADATA_FILE = Path(DATA_DIR) / METADATA_FILE_NAME

CHILD_MARKERS_FILE_NAME = "child_markers.json"
CHILD_MARKERS_FILE = Path(ROOT_DIR) / CHILD_MARKERS_FILE_NAME

TEST_PROJECT_NAME = "test_project"

DEFAULT_WINDOW_SIZE_X = 2560
DEFAULT_WINDOW_SIZE_Y = 1440
DEFAULT_WINDOW_POSITION_X = 0
DEFAULT_WINDOW_POSITION_Y = 0

SYNERGY_VERSION = "2026"
SYNERGY_WINDOW_TITLE = f"Autodesk Moldflow Insight {SYNERGY_VERSION}"

METADATA_DATE_FORMAT = "%Y-%m-%d"
METADATA_TIME_FORMAT = "%H:%M:%S"

TEMP_FILE_PREFIX = "temp_"
GENERATE_DATA_FUNCTION_PREFIX = "generate_"
GENERATE_DATA_FUNCTION_SUFFIX = "_data"

DATA_FILE_SUFFIX = "_data"
DATA_FILE_EXTENSION = ".json"

PROJECT_PREFIX = "project_"
PROJECT_ZIP_NAME_PATTERN = f"{PROJECT_PREFIX}*.zip"
PROJECT_EXTENSION = ".mpi"

STUDY_FILE_EXTENSION = ".sdy"


class FileSet(Enum):
    """
    FileSet enum defines the different categories of study files.

    SINGLE: Single Analyzed File for short tests
    # RAW: Unmeshed Unanalyzed Files
    MESHED: Meshed Unanalyzed Files
    # ANALYZED: Meshed Analyzed Files
    """

    SINGLE = "single_study"
    # RAW = "raw_studies"
    MESHED = "meshed_studies"
    # ANALYZED = "analyzed_studies"
