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


class DataFile(Enum):
    """
    DataFile enum defines the different types of data files.
    """

    MESH_SUMMARY = "mesh_summary_data.json"


class FileSet(Enum):
    """
    FileSet enum defines the different categories of study files.

    RAW: Unmeshed Unanalyzed Files
    MESHED: Meshed Unanalyzed Files
    ANALYZED: Meshed Analyzed Files
    """

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
