# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Helper functions for generating JSON test data from Synergy projects.
"""

import json
from functools import wraps
from pathlib import Path
from moldflow import Synergy, ItemType
from tests.api.integration_tests.constants import (
    FileSet,
    ModelType,
    STUDY_FILES_DIR,
    DATA_DIR,
    DataFile,
)


def _json_dump(json_file_name: DataFile, result_data: dict):
    """
    Dump collected data to JSON.

    Args:
        json_file_name (DataFile): Name of the JSON file to write the results to.
        result_data (dict): The data to dump to JSON.
    """
    output_path = Path(DATA_DIR) / json_file_name.value
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)
        f.write("\n")
    print(f"Generated JSON data saved to {output_path}")


def generate_json(json_file_name: DataFile, file_set: FileSet | None = None):
    """
    Decorator to generate JSON test data from Synergy projects or directly from Synergy.

    Args:
        json_file_name (DataFile): Name of the JSON file to write the results to.
        file_set (FileSet | None): The file set to loop through (RAW, MESHED, ANALYZED),
                                   or None if no project needs to be opened.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            synergy = Synergy()
            project = None

            try:
                # --- Open the project if a file set is provided ---
                if file_set is not None:
                    project_path = Path(STUDY_FILES_DIR) / file_set.value / f"{file_set.value}.mpi"
                    project_handle = synergy.open_project(str(project_path))
                    if not project_handle:
                        raise RuntimeError(f"Failed to open project at {project_path}")
                    project = synergy.project

                    result_data = {}

                    # --- Loop through all model types ---
                    for model_type in ModelType:
                        print(f"Processing {model_type.value} in {file_set.value}...")
                        study = project.open_item_by_name(model_type.value, ItemType.STUDY)
                        if not study:
                            print(f"Skipping {model_type.value}, study not found.")
                            continue

                        # Call the decorated function to collect data for this study
                        data = func(synergy=synergy, *args, **kwargs)
                        result_data[model_type.value] = data

                _json_dump(json_file_name, result_data)

            finally:
                # --- Teardown: close project and Synergy ---
                if project:
                    project.close(False)
                synergy.quit(False)

        return wrapper

    return decorator
