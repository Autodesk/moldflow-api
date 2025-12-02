# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for the Material Property class.
Returns a dict with relevant properties.
"""

from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import (
    generate_json,
    safe_array_to_list,
)
from tests.api.integration_tests.test_suite_material_property.constants import (
    MATERIAL_DB,
    MATERIAL_DB_TYPE,
)


@generate_json(file_set=None)
def generate_material_property_data(synergy: Synergy = None):
    """
    Generate data for the Material Property class.
    Returns a dict with relevant properties.
    """
    mf = synergy.material_finder
    mf.set_data_domain(MATERIAL_DB, MATERIAL_DB_TYPE)
    mat = mf.get_first_material()
    properties = {}

    properties["material_name"] = mat.name
    properties["material_id"] = mat.id
    properties["material_type"] = mat.type

    field_id = mat.get_first_field()
    while field_id != 0:

        field_values = safe_array_to_list(mat.get_field_values(field_id))
        field_units = safe_array_to_list(mat.field_units(field_id))

        properties[f"field_{field_id}"] = {
            "field_description": mat.get_field_description(field_id),
            "field_values": field_values,
            "field_units": field_units,
            "field_writable": mat.is_field_writable(field_id),
            "field_hidden": mat.is_field_hidden(field_id),
        }

        field_id = mat.get_next_field(field_id)

    return properties


if __name__ == "__main__":
    generate_material_property_data()
