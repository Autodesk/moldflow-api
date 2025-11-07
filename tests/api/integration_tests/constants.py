# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Constants for integration tests.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

INTEGRATION_TESTS_DIR = Path(__file__).parent
STUDY_FILES_DIR = INTEGRATION_TESTS_DIR / "study_files"
DATA_DIR = INTEGRATION_TESTS_DIR / "data"
METADATA_FILE_NAME = "metadata.json"
METADATA_FILE = Path(DATA_DIR) / METADATA_FILE_NAME
TEST_PROJECT_NAME = "test_project"
MID_DOE_MODEL_FILE = "mid_doe_model.sdy"
MID_DOE_MODEL_NAME = "mid_doe_model"

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


@dataclass
class Metadata:
    date: datetime
    time: datetime
    build_number: str
    version: str

    def to_dict(self):
        return {
            "date": self.date.strftime(METADATA_DATE_FORMAT),
            "time": self.time.strftime(METADATA_TIME_FORMAT),
            "build_number": self.build_number,
            "version": self.version,
        }


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


class ModelType(Enum):
    """
    ModelType enum defines the different types of models in each file set.
    """

    DD = "dd_model"
    MIDPLANE = "midplane_model"
    THREE_D = "3d_model"
