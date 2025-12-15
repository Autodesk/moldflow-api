# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for the PropertyEditor class.
Returns a dict with relevant properties.
"""


from moldflow import Synergy, PropertyEditor
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet
from tests.api.integration_tests.test_suite_property_editor.constants import (
    TEST_PROPERTY_TYPE,
    TEST_PROPERTY_DEFAULTS,
    TEST_MAX_PROPERTY_COUNT,
    ENTITY_TO_SET,
    PROPERTY_TO_SET_TYPE,
    PROPERTY_TO_SET_ID,
)


def create_properties(property_editor: PropertyEditor):
    for i in range(1, TEST_MAX_PROPERTY_COUNT + 1):
        property_editor.create_property(TEST_PROPERTY_TYPE, i, TEST_PROPERTY_DEFAULTS)
    return property_editor


def get_property_dict(property_editor: PropertyEditor):
    custom_property_editor = create_properties(property_editor)
    property_dict = {}
    prop_iter = custom_property_editor.get_first_property(0)
    while prop_iter is not None:
        if prop_iter.type not in property_dict:
            property_dict[prop_iter.type] = {}
        property_dict[prop_iter.type][prop_iter.id] = custom_property_editor.get_data_description(
            prop_iter.type, prop_iter.id
        )
        prop_iter = custom_property_editor.get_next_property(prop_iter)
    return custom_property_editor, property_dict


def remove_unused_properties_count(synergy: Synergy):
    property_editor = synergy.property_editor
    return property_editor.remove_unused_properties()


def get_entity_property(property_editor: PropertyEditor):
    entity_list = property_editor.create_entity_list()
    entity_list.select_from_string(ENTITY_TO_SET)
    return property_editor.get_entity_property(entity_list)


@generate_json(file_set=FileSet.SINGLE)
def generate_property_editor_data(synergy: Synergy = None, study_file: str = None):
    """
    Generate data for the PropertyEditor class.
    Returns a dict with relevant properties.
    """
    property_editor = synergy.property_editor
    custom_property_editor, property_dict = get_property_dict(property_editor)
    first_property = custom_property_editor.get_first_property(TEST_PROPERTY_TYPE)
    entity_property = get_entity_property(custom_property_editor)
    no_of_removed_properties = remove_unused_properties_count(synergy)
    return {
        "no_of_removed_properties": no_of_removed_properties,
        "first_property_type": first_property.type,
        "first_property_id": first_property.id,
        "property_dict": property_dict,
        "original_entity_property": {
            "property_type": entity_property.type,
            "property_id": entity_property.id,
        },
        "property_to_set": {
            "property_type": PROPERTY_TO_SET_TYPE,
            "property_id": PROPERTY_TO_SET_ID,
        },
    }


if __name__ == "__main__":
    generate_property_editor_data()
