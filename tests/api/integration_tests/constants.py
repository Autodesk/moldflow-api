# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Constants for integration tests.
"""

from pathlib import Path
import json
from enum import Enum

SYNERGY_VERSION = None
INTEGRATION_TESTS_DIR = Path(__file__).parent
STUDY_FILES_DIR = INTEGRATION_TESTS_DIR / "study_files"
DATA_DIR = INTEGRATION_TESTS_DIR / "data"
TEST_PROJECT_NAME = "test_project"
MID_DOE_MODEL_FILE = "mid_doe_model.sdy"
MID_DOE_MODEL_NAME = "mid_doe_model"

DEFAULT_WINDOW_SIZE_X = 2560
DEFAULT_WINDOW_SIZE_Y = 1440
DEFAULT_WINDOW_POSITION_X = 0
DEFAULT_WINDOW_POSITION_Y = 0


class DataFile(Enum):
    """
    DataFile enum defines the different types of data files.
    """

    MESH_SUMMARY = "mesh_summary_data.json"
    SYNERGY = "synergy_data.json"


with open(DATA_DIR / DataFile.SYNERGY.value, "r", encoding="utf-8") as f:
    SYNERGY_DATA = json.load(f)
SYNERGY_VERSION = SYNERGY_DATA["version"]
SYNERGY_WINDOW_TITLE = f"Autodesk Moldflow Insight {SYNERGY_VERSION}"


class FileSet(Enum):
    """
    FileSet enum defines the different categories of study files.

    SINGLE: Single Analyzed File for short tests
    RAW: Unmeshed Unanalyzed Files
    MESHED: Meshed Unanalyzed Files
    ANALYZED: Meshed Analyzed Files
    """

    SINGLE = "Single"
    # RAW = "Raw"
    MESHED = "Meshed"
    # ANALYZED = "Analyzed"


class ModelType(Enum):
    """
    ModelType enum defines the different types of models in each file set.
    """

    DD = "dd_model"
    MIDPLANE = "midplane_model"
    THREE_D = "3d_model"
