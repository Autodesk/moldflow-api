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
    STUDY_FILES_DIR,
    INTEGRATION_TESTS_DIR,
    DEFAULT_WINDOW_SIZE_X,
    DEFAULT_WINDOW_SIZE_Y,
    DEFAULT_WINDOW_POSITION_X,
    DEFAULT_WINDOW_POSITION_Y,
    PROJECT_ZIP_NAME_PATTERN,
    PROJECT_PREFIX,
    STUDY_FILE_EXTENSION,
    PROJECT_EXTENSION,
    DATA_FILE_NAME,
)


def get_study_files():
    """
    Unzip the study files and return a dictionary of project names and corresponding study files.
    Projects selected of the form project_<file_set>.
    Study files selected of the form <model_name>.sdy.
    """
    for zip_file in STUDY_FILES_DIR.glob(PROJECT_ZIP_NAME_PATTERN):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(STUDY_FILES_DIR)

    study_files = {}
    for folders in STUDY_FILES_DIR.iterdir():
        if folders.is_dir() and folders.name.startswith(PROJECT_PREFIX):
            project_name = folders.name.replace(PROJECT_PREFIX, "")
            study_files[project_name] = []
            for model in folders.iterdir():
                if model.name.endswith(STUDY_FILE_EXTENSION):
                    model_name = model.name.replace(STUDY_FILE_EXTENSION, "")
                    study_files[project_name].append(model_name)
    return study_files


STUDY_FILES = get_study_files()


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

    file_set = marker.args[0].value
    study_files = STUDY_FILES[file_set]
    params = study_files
    ids = [f"{file_set}-{model}" for model in params]
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

    file_set = marker.args[0].value

    project_path = (
        Path(STUDY_FILES_DIR) / f"{PROJECT_PREFIX}{file_set}" / f"{file_set}{PROJECT_EXTENSION}"
    )
    project_handle = synergy.open_project(str(project_path))
    if not project_handle:
        raise RuntimeError(f"Failed to open project at {project_path}")
    project = synergy.project
    yield project
    project.close(False)


@pytest.fixture(name="study_file")
def study_file_fixture(request):
    """
    Provides a single model_name string for each parametrized test.
    """
    return request.param


@pytest.fixture(name="opened_study")
def opened_study_fixture(project: Project, study_file):
    """
    Opens a study file inside an already-open project.
    """
    study = project.open_item_by_name(study_file, ItemType.STUDY)
    return study


@pytest.fixture(name="study_with_project")
def study_with_project_fixture(project, study_file, opened_study):
    """
    Provides (model_name, project, opened_study) tuple for convenience.
    """
    yield (study_file, project, opened_study)


@pytest.fixture(scope="class", name="expected_data")
def expected_data_fixture(request):
    """
    Load the expected data JSON file once per test class.

    Automatically derives the JSON filename from pytest markers.
    Looks for markers like @pytest.mark.mesh_summary or @pytest.mark.synergy
    and converts them to filenames like "mesh_summary_data.json" or "synergy_data.json".
    """
    # Try to derive filename from pytest markers first
    json_file_name = None
    marker_list = getattr(request.cls, "pytestmark", [])

    # Look for json_file_name marker first
    for marker in marker_list:
        if marker.name == 'json_file_name':
            json_file_name = marker.args[0]  # Get the first argument
            break

    # If no json_file_name marker found, look for other markers
    if json_file_name is None:
        excluded_markers = {'integration', 'file_set', 'parametrize', 'json_file_name'}
        non_excluded_markers = [m.name for m in marker_list if m.name not in excluded_markers]

        if len(non_excluded_markers) > 1:
            pytest.fail(
                f"Multiple markers found on test class '{request.cls.__name__}': {non_excluded_markers}. "
                f"Please specify which baseline data to use with "
                f"@pytest.mark.json_file_name('<marker>')."
            )
        elif len(non_excluded_markers) == 1:
            # Exactly one marker found - use it
            json_file_name = non_excluded_markers[0]
        else:
            # No markers found at all
            pytest.fail(
                f"Could not determine JSON filename for test class '{request.cls.__name__}'. "
                f"Please add a marker (e.g., @pytest.mark.my_marker) or use "
                f"@pytest.mark.json_file_name('<filename>')."
            )

    json_path = Path(INTEGRATION_TESTS_DIR) / f"test_suite_{json_file_name}" / DATA_FILE_NAME
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
    Returns expected values for the current study.

    If no matching data exists, skips the test gracefully.
    """
    expected_val = expected_data.get(study_file)
    if not expected_val:
        pytest.skip(f"No expected values found for model name: {study_file}")
    return expected_val


@pytest.fixture(scope="class")
def temp_dir():
    """Create a temporary directory for integration testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
