# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Configuration and fixtures for integration tests.
"""

from enum import Enum
import json
from pathlib import Path
import pytest
from moldflow import Synergy, Project, ItemType

INTEGRATION_TESTS_DIR = Path(__file__).parent
STUDY_FILES_DIR = INTEGRATION_TESTS_DIR / "study_files"
DATA_DIR = INTEGRATION_TESTS_DIR / "data"


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


def generate_file_map(
    study_files_dir: str = STUDY_FILES_DIR,
) -> dict[FileSet, dict[ModelType, str]]:
    """
    Dynamically generate the global file map for all file sets and model types.
    Path pattern: {study_files_dir}/{fileset.value}/{modeltype.value}.sdy
    """
    file_map = {}
    for file_set in FileSet:
        set_dir = Path(study_files_dir) / file_set.value
        file_map[file_set.name] = {
            model_type: str(set_dir / f"{model_type.value}.sdy") for model_type in ModelType
        }
    return file_map


FILE_SETS = generate_file_map()


def pytest_generate_tests(metafunc):
    """
    Parametrize tests based on @pytest.mark.file_set(FileSet.<SET>).

    Class-level parameterization ensures all tests for a model type
    run together before switching models.
    """
    if "study_file" not in metafunc.fixturenames or not metafunc.cls:
        return

    # Find marker on class
    marker = None
    marker_list = getattr(metafunc.cls, "pytestmark", [])
    for m in marker_list:
        if m.name == "file_set":
            marker = m
            break

    if not marker:
        metafunc_name = metafunc.function.__name__
        raise ValueError(
            f"Test class '{metafunc_name}' requires a @pytest.mark.file_set(FileSet.<SET>) marker."
        )

    file_set = marker.args[0]
    file_set_name = file_set.name
    params = list(FILE_SETS[file_set_name].items())
    ids = [f"{file_set}-{model_type.value}" for model_type, _ in params]

    metafunc.parametrize("study_file", params, ids=ids, scope="class")


@pytest.fixture(scope="class", name="synergy")
def synergy_fixture():
    """
    Fixture to create a real Synergy instance for integration testing.
    """
    synergy_instance = Synergy()
    yield synergy_instance
    synergy_instance.quit(False)


@pytest.fixture(scope="class", name="project")
def project_fixture(synergy: Synergy, request):
    """
    Opens the project corresponding to the test's file set.
    """
    marker = request.node.get_closest_marker("file_set")
    if not marker:
        raise ValueError(
            f"Test '{request.node.name}' requires a @pytest.mark.file_set(FileSet.<SET>) marker."
        )

    file_set = marker.args[0]

    project_path = (
        Path(STUDY_FILES_DIR) / file_set.value / f"{file_set.value}.mpi"
    )  # adjust naming pattern if needed
    project_handle = synergy.open_project(str(project_path))
    if not project_handle:
        raise RuntimeError(f"Failed to open project at {project_path}")
    project = synergy.project
    yield project
    project.close(False)


@pytest.fixture(name="study_file")
def study_file_fixture(request):
    """
    Provides a single (ModelType, file_path) tuple for each parametrized test.
    """
    return request.param


@pytest.fixture(name="opened_study")
def opened_study_fixture(project: Project, study_file):
    """
    Opens a study file inside an already-open project.
    """
    model_type, _ = study_file
    study = project.open_item_by_name(model_type.value, ItemType.STUDY)
    return study


@pytest.fixture(name="study_with_project")
def study_with_project_fixture(project, study_file, opened_study):
    """
    Provides (ModelType, file_path, project, opened_study) tuple for convenience.
    """
    model_type, file_path = study_file
    yield (model_type, file_path, project, opened_study)


@pytest.fixture(scope="class", name="expected_data")
def expected_data_fixture(request):
    """
    Load the expected data JSON file once per test class.

    Expects the test class to define a class attribute:
    `json_file_name = "mesh_summary_data.json"` (for example)
    """
    json_file_name = getattr(request.cls, "json_file_name", None)
    if not json_file_name:
        pytest.skip("Test class missing `json_file_name` attribute.")

    json_path = Path(DATA_DIR) / json_file_name
    if not json_path.exists():
        pytest.skip(f"Expected data file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(name="expected_values")
def expected_values_fixture(expected_data, study_file):
    """
    Returns expected values for the current study's model type.

    If no matching data exists, skips the test gracefully.
    """
    model_type, _ = study_file
    model_data = expected_data.get(model_type.value)
    if not model_data:
        pytest.skip(f"No expected values found for model type: {model_type.value}")
    return model_data
