# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for a new property.
Returns a dict with relevant properties.
"""

from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet
from tests.api.integration_tests.test_suite_ent_list.constants import TEST_ENTITY_LIST_ITEMS


@generate_json(file_set=FileSet.MESHED)
def generate_ent_list_data(synergy: Synergy, study_file: str):
    """
    Generate data for a new property.
    Returns a dict with relevant properties.
    """
    entity_type = TEST_ENTITY_LIST_ITEMS[study_file]["entity_type"]
    items = TEST_ENTITY_LIST_ITEMS[study_file]["items"]

    item_string = " ".join([f"{entity_type}{item}" for item in items])
    item_predicate = f"{entity_type}{items[0]}:{items[1]}"
    converted_string = f"{item_string} "
    size = len(items)
    entity = {i: f"{entity_type}{item} " for i, item in enumerate(items)}

    return {
        "item_string": item_string,
        "item_predicate": item_predicate,
        "converted_string": converted_string,
        "size": size,
        "entity": entity,
    }


if __name__ == "__main__":
    generate_ent_list_data()
