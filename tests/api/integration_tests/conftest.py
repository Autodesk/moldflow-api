# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Configuration and fixtures for integration tests.
"""

import json
from pathlib import Path
import pytest
import tempfile
import zipfile
from moldflow import Synergy, Project, ItemType
from tests.api.integration_tests.constants import (
    FileSet,
    ModelType,
    STUDY_FILES_DIR,
    DATA_DIR,
    MID_DOE_MODEL_FILE,
    MID_DOE_MODEL_NAME,
    DataFile,
    DEFAULT_WINDOW_SIZE_X,
    DEFAULT_WINDOW_SIZE_Y,
    DEFAULT_WINDOW_POSITION_X,
    DEFAULT_WINDOW_POSITION_Y,
)


def unzip_study_files():
    """
    Unzip the study files.
    """
    for zip_file in STUDY_FILES_DIR.glob("*.zip"):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(STUDY_FILES_DIR)


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
        if file_set == FileSet.SINGLE:
            file_map[file_set.name] = {MID_DOE_MODEL_NAME: str(set_dir / MID_DOE_MODEL_FILE)}
            continue

        file_map[file_set.name] = {
            model_type: str(set_dir / f"{model_type.value}.sdy") for model_type in ModelType
        }
    return file_map


unzip_study_files()
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
    if file_set == FileSet.SINGLE:
        metafunc.parametrize(
            "study_file",
            [(MID_DOE_MODEL_NAME, FILE_SETS[file_set.name][MID_DOE_MODEL_NAME])],
            ids=["Single"],
            scope="class",
        )
        return

    file_set_name = file_set.name
    params = list(FILE_SETS[file_set_name].items())
    ids = [f"{file_set}-{model_type.value}" for model_type, _ in params]

    metafunc.parametrize("study_file", params, ids=ids, scope="class")


@pytest.fixture(scope="class", name="synergy")
def synergy_fixture():
    """
    Fixture to create a real Synergy instance for integration testing.
    """
    synergy_instance = Synergy(logging=False)
    synergy_instance.silence(True)
    synergy_instance.set_application_window_pos(
        DEFAULT_WINDOW_POSITION_X,
        DEFAULT_WINDOW_POSITION_Y,
        DEFAULT_WINDOW_SIZE_X,
        DEFAULT_WINDOW_SIZE_Y,
    )
    yield synergy_instance
    if synergy_instance.synergy is not None:
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

    project_path = Path(STUDY_FILES_DIR) / file_set.value / f"{file_set.value}.mpi"
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
    if model_type == MID_DOE_MODEL_NAME:
        study = project.open_item_by_name(model_type, ItemType.STUDY)
    else:
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
    `json_file_name = DataFile.MESH_SUMMARY` (for example)
    """
    json_file_name = getattr(request.cls, "json_file_name", None)
    if not json_file_name:
        pytest.skip("Test class missing `json_file_name` attribute.")

    json_file = json_file_name.value if isinstance(json_file_name, DataFile) else json_file_name
    json_path = Path(DATA_DIR) / json_file
    if not json_path.exists():
        pytest.skip(f"Expected data file not found: {json_path}")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        pytest.skip(
            f"Expected data file is not valid JSON: {json_path}. "
            "Please run the data generation script to create/update the file."
        )


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


@pytest.fixture(name="expected_values_general")
def expected_values_general_fixture(expected_data):
    """
    Returns expected values for the general case.
    """
    return expected_data


@pytest.fixture(scope="class")
def temp_dir():
    """Create a temporary directory for integration testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
