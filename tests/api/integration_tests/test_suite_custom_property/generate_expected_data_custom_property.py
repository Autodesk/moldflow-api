# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for a new property.
Returns a dict with relevant properties.
"""

from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.test_suite_custom_property.constants import (
    CUSTOM_PROPERTY_NAME,
    CUSTOM_PROPERTY_ID,
    CUSTOM_PROPERTY_TYPE,
    FIELD_PROPERTIES,
)


@generate_json(file_set=None, synergy_required=False)
def generate_custom_property_data():
    """
    Generate data for a new property.
    Returns a dict with relevant properties.
    """
    properties_data = {
        "property_name": CUSTOM_PROPERTY_NAME,
        "property_id": CUSTOM_PROPERTY_ID,
        "property_type": CUSTOM_PROPERTY_TYPE,
        "original_field_data": {
            "field_description": "",
            "field_values": [],
            "field_units": [],
            "field_writable": True,
            "field_hidden": False,
        },
        "hidden_field_data": {
            "field_description": "",
            "field_values": None,
            "field_units": [],
            "field_writable": False,
            "field_hidden": True,
        },
    }

    for index, field_properties in FIELD_PROPERTIES.items():
        properties_data[f"field_data_{index}"] = {
            "field_id": field_properties["id"],
            "field_description": field_properties["description"],
            "field_values": field_properties["values"],
            "field_units": field_properties["units"],
            "field_writable": field_properties["writable"],
            "field_hidden": field_properties["hidden"],
        }

    return properties_data


if __name__ == "__main__":
    generate_custom_property_data()
