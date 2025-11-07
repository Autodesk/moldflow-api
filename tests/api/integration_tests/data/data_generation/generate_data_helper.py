# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Helper functions for generating JSON test data from Synergy projects.
"""

import json
from datetime import datetime
from functools import wraps
from pathlib import Path
from moldflow import Synergy, ItemType
from tests.api.integration_tests.constants import (
    FileSet,
    ModelType,
    STUDY_FILES_DIR,
    DATA_DIR,
    METADATA_FILE,
    METADATA_FILE_NAME,
    Metadata,
    TEMP_FILE_PREFIX,
    GENERATE_DATA_FUNCTION_PREFIX,
    GENERATE_DATA_FUNCTION_SUFFIX,
    DATA_FILE_SUFFIX,
    DATA_FILE_EXTENSION,
)
from tests.api.integration_tests.data.data_generation.generate_data_logger import (
    generate_data_logger,
)
from tests.api.integration_tests.conftest import unzip_study_files


def _json_dump(json_file_name: str, result_data: dict):
    """
    Dump collected data to JSON.

    Args:
        json_file_name (str): Name of the JSON file to write the results to.
        result_data (dict): The data to dump to JSON.
    """
    output_path = Path(DATA_DIR) / json_file_name
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


def get_data_file_name(marker: str):
    """
    Get the data file name from the marker.
    The data file name must follow the pattern: <marker>_data.json
    """
    return f"{marker}{DATA_FILE_SUFFIX}{DATA_FILE_EXTENSION}"


def get_temp_file_name(marker: str):
    """
    Get the temporary file name from the marker.
    The temporary file name must follow the pattern: temp_<marker>_data.json
    """
    return f"{TEMP_FILE_PREFIX}{get_data_file_name(marker)}"


def generate_json(file_set: FileSet | None = None):
    """
    Decorator to generate JSON test data from Synergy projects or directly from Synergy.
    The function name must follow the pattern: generate_<marker>_data

    Args:
        file_set (FileSet | None): The file set to loop through (SINGLE, MESHED), or None if no project needs to be opened.
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
                    project_path = Path(STUDY_FILES_DIR) / file_set.value / f"{file_set.value}.mpi"
                    project_handle = synergy.open_project(str(project_path))
                    if not project_handle:
                        raise RuntimeError(f"Failed to open project at {project_path}")
                    project = synergy.project

                    # --- Loop through all model types ---
                    for model_type in ModelType:
                        study = project.open_item_by_name(model_type.value, ItemType.STUDY)
                        if not study:
                            continue

                        # Call the decorated function to collect data for this study
                        data = func(synergy=synergy, *args, **kwargs)
                        result_data[model_type.value] = data

                else:
                    result_data = func(synergy=synergy, *args, **kwargs)

                _json_dump(temp_file_name, result_data)
                generate_data_logger.track_generation(marker, get_data_file_name(marker))

            finally:
                # --- Teardown: close project and Synergy ---
                if project:
                    project.close(False)
                synergy.quit(False)

        return wrapper

    return decorator


def fetch_metadata(date_time: datetime):
    synergy = Synergy()
    metadata = Metadata(
        date=date_time, time=date_time, build_number=synergy.build_number, version=synergy.version
    )
    synergy.quit(False)
    return metadata.to_dict()


def clean_up_temp_files():
    for file_name in DATA_DIR.iterdir():
        if file_name.is_file() and file_name.name.startswith(TEMP_FILE_PREFIX):
            file_name.unlink()
    return 0


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
    metadata_file_data = json.load(open(METADATA_FILE))
    for marker, data in metadata.items():
        metadata_file_data[marker] = data
        generate_data_logger.track_generation(marker, METADATA_FILE_NAME)
    _json_dump(METADATA_FILE_NAME, metadata_file_data)

    # Commit temporary files to final files
    for file_name in DATA_DIR.iterdir():
        file_name_str = file_name.name

        if file_name.is_file() and file_name_str.startswith(TEMP_FILE_PREFIX):
            new_file_name = file_name_str[len(TEMP_FILE_PREFIX) :]
            data = json.load(open(file_name))
            _json_dump(new_file_name, data)
            file_name.unlink()
    # Print the beautiful summary
    generate_data_logger.print_summary(DATA_DIR)
    return 0


def get_generate_data_functions(global_namespace: dict):
    """
    Dynamically discover generate functions based on naming pattern.
    Functions should be named 'generate_<marker>_data' and will be mapped to '<marker>'.
    """
    functions = {}
    for name, obj in global_namespace.items():
        if (
            name.startswith(GENERATE_DATA_FUNCTION_PREFIX)
            and name.endswith(GENERATE_DATA_FUNCTION_SUFFIX)
            and callable(obj)
        ):
            marker = get_marker_from_generate_data_function_name(name)
            functions[marker] = obj
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
        generate_function = generate_functions.get(marker)
        metadata[marker] = metadata_data
        generate_function()
    commit_data(metadata)
    return 0


def get_available_markers(generate_functions: dict[str, callable]):
    """
    Get the available markers.
    """
    msg_str = "\n - ".join(generate_functions.keys())
    return f'Available test data markers: \n - {msg_str}'
