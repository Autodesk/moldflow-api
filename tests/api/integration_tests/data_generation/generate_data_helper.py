# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Helper functions for generating JSON test data from Synergy projects.
"""

import json
import os
import subprocess
import logging
import platform
import sys
from datetime import datetime
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from moldflow import Synergy, ItemType, IntegerArray, DoubleArray, StringArray
from tests.api.integration_tests.constants import (
    FileSet,
    STUDY_FILES_DIR,
    INTEGRATION_TESTS_DIR,
    METADATA_FILE,
    METADATA_FILE_NAME,
    TEMP_FILE_PREFIX,
    GENERATE_DATA_FUNCTION_PREFIX,
    GENERATE_DATA_FUNCTION_SUFFIX,
    DATA_FILE_NAME,
    METADATA_DATE_FORMAT,
    METADATA_TIME_FORMAT,
    PROJECT_PREFIX,
    PROJECT_EXTENSION,
    TEST_SUITE_PREFIX,
    GENERATE_TEST_DATA_FILE_NAME,
    GENERATE_TEST_DATA_FUNCTION_EXTENSION,
    ROOT_DIR,
)
from tests.api.integration_tests.conftest import STUDY_FILES
from tests.api.integration_tests.data_generation.generate_data_logger import generate_data_logger


WINDOWS = platform.system() == 'Windows'


@dataclass
class Metadata:
    """
    Metadata class for storing metadata about the test data.
    """

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


def run_command(args, cwd=os.getcwd(), extra_env=None):
    """Runs native executable command, args is an array of strings"""

    logging.info(
        "Running command: '%s' in '%s'%s",
        ' '.join(args),
        cwd,
        f' with extra env: {extra_env}' if extra_env else '',
    )

    command_env = {**os.environ, **extra_env} if extra_env else os.environ

    with subprocess.Popen(args, cwd=cwd, shell=WINDOWS, env=command_env) as proc:
        proc.wait()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, ' '.join(args))


def _json_dump(json_file_name: str, result_data: dict):
    """
    Dump collected data to JSON.

    Args:
        json_file_name (str): Name of the JSON file to write the results to.
        result_data (dict): The data to dump to JSON.
    """
    output_path = Path(INTEGRATION_TESTS_DIR) / json_file_name
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)
        f.write("\n")


def get_marker_from_generate_data_function_name(function_name: str):
    """
    Get the marker from the function name.
    The function name must follow the pattern: generate_<marker>_data
    """
    if function_name.startswith(GENERATE_DATA_FUNCTION_PREFIX) and function_name.endswith(
        GENERATE_DATA_FUNCTION_SUFFIX
    ):
        return function_name[
            len(GENERATE_DATA_FUNCTION_PREFIX) : -len(GENERATE_DATA_FUNCTION_SUFFIX)
        ]
    else:
        raise ValueError(
            f"Cannot derive marker from function name '{function_name}'. "
            f"Function must follow pattern '{GENERATE_DATA_FUNCTION_PREFIX}<marker>{GENERATE_DATA_FUNCTION_SUFFIX}'."
        )


def get_test_suite_folder_name(marker: str):
    """
    Get the test suite folder name from the marker.
    The test suite folder name must follow the pattern: <TEST_SUITE_PREFIX><marker>
    """
    return f"{TEST_SUITE_PREFIX}{marker}"


def get_data_file_name(marker: str):
    """
    Get the data file name from the marker.
    The data file name must follow the pattern: <get_test_suite_folder_name(marker)>/<DATA_FILE_NAME>
    """
    return f"{get_test_suite_folder_name(marker)}/{DATA_FILE_NAME}"


def get_temp_file_name(marker: str):
    """
    Get the temporary file name from the marker.
    The temporary file name must follow the pattern: <get_test_suite_folder_name(marker)>/<TEMP_FILE_PREFIX><DATA_FILE_NAME>
    """
    return f"{get_test_suite_folder_name(marker)}/{TEMP_FILE_PREFIX}{DATA_FILE_NAME}"


def generate_json(file_set: FileSet | None = None, synergy_required: bool = True):
    """
    Decorator to generate JSON test data from Synergy projects or directly from Synergy.
    The function name must follow the pattern: generate_<marker>_data

    Args:
        file_set (FileSet | None): The file set to loop through (SINGLE, MESHED), or None if no project needed.
        synergy_required (bool): Whether Synergy instance should be passed to the function. Default: True.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Auto-derive filename if not provided
            marker = get_marker_from_generate_data_function_name(func.__name__)
            temp_file_name = get_temp_file_name(marker)
            synergy = Synergy()
            project = None

            try:
                result_data = {}
                # --- Open the project if a file set is provided ---
                if file_set is not None:
                    file_set_name = file_set.value
                    project_path = (
                        Path(STUDY_FILES_DIR)
                        / f"{PROJECT_PREFIX}{file_set_name}"
                        / f"{file_set_name}{PROJECT_EXTENSION}"
                    )
                    project_handle = synergy.open_project(str(project_path))
                    if not project_handle:
                        raise RuntimeError(f"Failed to open project at {project_path}")
                    project = synergy.project

                    # --- Loop through all study files ---
                    for study_file in STUDY_FILES[file_set_name]:
                        study = project.open_item_by_name(study_file, ItemType.STUDY)
                        if not study:
                            generate_data_logger.error(
                                f"Skipped study file '{study_file}' during data generation for file set '{file_set}': study not found."
                            )
                            continue

                        # Call the decorated function to collect data for this study
                        data = func(synergy=synergy, *args, **kwargs)
                        result_data[study_file] = data
                else:
                    if synergy_required:
                        result_data = func(synergy=synergy, *args, **kwargs)
                    else:
                        result_data = func(*args, **kwargs)

                _json_dump(temp_file_name, result_data)

            finally:
                # --- Teardown: close project and Synergy ---
                if project:
                    project.close(False)
                synergy.quit(False)

        return wrapper

    return decorator


def fetch_metadata(date_time: datetime):
    """
    Fetch the metadata from the Synergy instance.
    """
    synergy = Synergy()
    metadata = Metadata(
        date=date_time, time=date_time, build_number=synergy.build_number, version=synergy.version
    )
    synergy.quit(False)
    return metadata.to_dict()


def clean_up_temp_files():
    """
    Clean up the temporary files.
    """
    for file_name in INTEGRATION_TESTS_DIR.iterdir():
        if file_name.is_dir() and file_name.name.startswith(TEST_SUITE_PREFIX):
            for temp_file_name in file_name.iterdir():
                if temp_file_name.is_file() and temp_file_name.name.startswith(TEMP_FILE_PREFIX):
                    temp_file_name.unlink()
    return 0


def read_json_file(file_path: Path):
    """
    Read and parse a JSON file, returning its contents as a dictionary.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        generate_data_logger.error(f"File '{file_path}' not found.")
        return
    except json.JSONDecodeError:
        generate_data_logger.error(f"File '{file_path}' is not valid JSON.")
        return


def commit_data(metadata: dict):
    """
    Commit the data to the data directory.
    The data is committed to the data directory in the following way:
    - The metadata is committed to the metadata file.
    - The temporary files are committed to the data directory.
    Args:
        metadata (dict): The metadata to commit.
    """
    # Update metadata file
    metadata_file_data = read_json_file(METADATA_FILE)
    for marker, data in metadata.items():
        metadata_file_data[marker] = data
        generate_data_logger.track_generation(marker, METADATA_FILE_NAME)
    _json_dump(METADATA_FILE_NAME, metadata_file_data)

    # Commit temporary files to final files
    for item in INTEGRATION_TESTS_DIR.iterdir():
        if item.is_dir() and item.name.startswith(TEST_SUITE_PREFIX):
            for file in item.iterdir():
                if file.is_file() and file.name.startswith(TEMP_FILE_PREFIX):
                    new_file_name = file.name[len(TEMP_FILE_PREFIX) :]
                    generate_data_logger.track_generation(
                        item.name[len(TEST_SUITE_PREFIX) :], f"{item.name}/{new_file_name}"
                    )
                    data = read_json_file(file)
                    if data:
                        _json_dump(f"{item.name}/{new_file_name}", data)
                    file.unlink()
    # Print the beautiful summary
    generate_data_logger.print_summary(INTEGRATION_TESTS_DIR)
    return 0


def get_generate_data_functions():
    """
    Dynamically discover generate functions based on naming pattern.
    Functions should be named 'generate_<marker>_data' and will be mapped to '<marker>'.
    """
    functions = {}
    for item in INTEGRATION_TESTS_DIR.iterdir():
        if item.is_dir() and item.name.startswith(TEST_SUITE_PREFIX):
            for file in item.iterdir():
                if file.is_file() and file.name.startswith(GENERATE_TEST_DATA_FILE_NAME):
                    functions[
                        file.name[
                            len(GENERATE_TEST_DATA_FILE_NAME) : -len(
                                GENERATE_TEST_DATA_FUNCTION_EXTENSION
                            )
                        ]
                    ] = file
    return functions


def fetch_data_on_markers(
    markers: list[str], generate_functions: dict[str, callable], date_time: datetime
):
    """
    Run the markers.
    """
    metadata = {}
    metadata_data = fetch_metadata(date_time)

    for marker in markers:
        generate_function_file = generate_functions.get(marker)
        if not generate_function_file:
            generate_data_logger.error(
                f"Generator function for marker '{marker}' not found. Please check if the function exists."
            )
            continue
        metadata[marker] = metadata_data

        # Convert file path to module path
        # e.g., D:\...\tests\api\integration_tests\test_suite_custom_property\generate_test_data_custom_property.py
        # becomes: tests.api.integration_tests.test_suite_custom_property.generate_test_data_custom_property
        relative_path = generate_function_file.relative_to(ROOT_DIR)
        module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')

        run_command([sys.executable, '-m', module_path], ROOT_DIR)
    commit_data(metadata)
    return 0


def get_available_markers(generate_functions: dict[str, callable]):
    """
    Get the available markers.
    """
    msg_str = "\n - ".join(generate_functions.keys())
    return f'Available test data markers: \n - {msg_str}'


def safe_array_to_list(array: IntegerArray | DoubleArray | StringArray):
    """
    Convert an array to a list.
    """
    try:
        return array.to_list()
    except AttributeError:
        return None
