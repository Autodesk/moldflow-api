# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for Property Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the Property class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import Synergy, Property, DoubleArray
from tests.api.integration_tests.constants import FileSet
from tests.api.integration_tests.common_test_utilities.property_tests_helper import (
    check_properties,
    check_property_initialization,
)
from tests.api.integration_tests.test_suite_custom_property.constants import (
    CUSTOM_PROPERTY_NAME,
    CUSTOM_PROPERTY_ID,
    CUSTOM_PROPERTY_TYPE,
    CUSTOM_PROPERTY_DEFAULTS,
    FIELD_PROPERTIES,
    FIELD_INDEX,
)


def _check_fields(
    test_property: Property,
    expected_length: int,
    fields_present: list[int],
    fields_absent: list[int],
):
    """
    Check the fields of the Property instance.
    """
    fields_list = []

    field_id = test_property.get_first_field()
    while field_id != 0:
        fields_list.append(field_id)
        field_id = test_property.get_next_field(field_id)

    assert len(fields_list) == expected_length

    assert set(fields_list) == set(fields_present)
    assert not set(fields_absent) & set(fields_list)


@pytest.mark.integration
@pytest.mark.custom_property
@pytest.mark.file_set(FileSet.SINGLE)
class TestIntegrationCustomProperty:
    """
    Integration test suite for a new custom property for Property class.
    """

    @pytest.fixture
    def custom_property(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a new property.
        """
        pe = synergy.property_editor
        prop = pe.create_property(
            CUSTOM_PROPERTY_TYPE, CUSTOM_PROPERTY_ID, CUSTOM_PROPERTY_DEFAULTS
        )
        prop.name = CUSTOM_PROPERTY_NAME
        yield prop
        pe.delete_property(CUSTOM_PROPERTY_TYPE, CUSTOM_PROPERTY_ID)

    @pytest.fixture
    def double_array(self, synergy: Synergy):
        """
        Fixture to create a double array.
        """
        return synergy.create_double_array()

    def test_property_initialization(self, custom_property: Property):
        """
        Test that Property instance is properly initialized.
        """
        check_property_initialization(custom_property)

    def test_metadata(self, custom_property: Property, expected_data: dict):
        """
        Test the name, id, and type of the new property.
        """
        assert custom_property.name == expected_data["property_name"]
        assert custom_property.id == expected_data["property_id"]
        assert custom_property.type == expected_data["property_type"]

    def test_no_fields(self, custom_property: Property):
        """
        Test the new property has no fields.
        """
        field_id = custom_property.get_first_field()
        assert field_id == 0

    def test_properties(self, custom_property: Property, expected_data: dict):
        """
        Test the properties of the new property and delete the field.
        """
        original_data = expected_data["original_field_data"]
        field_id = FIELD_PROPERTIES[FIELD_INDEX]["id"]
        check_properties(custom_property, field_id, original_data)

    def test_updating_properties(
        self, double_array: DoubleArray, custom_property: Property, expected_data: dict
    ):
        """
        Test the updating of the properties of the new property.
        """
        updated_data = expected_data[f"field_data_{FIELD_INDEX}"]
        field_id = FIELD_PROPERTIES[FIELD_INDEX]["id"]

        # Set and test the updated properties
        custom_property.set_field_description(
            field_id, FIELD_PROPERTIES[FIELD_INDEX]["description"]
        )
        double_array.from_list(FIELD_PROPERTIES[FIELD_INDEX]["values"])
        custom_property.set_field_values(field_id, double_array)

        check_properties(custom_property, field_id, updated_data)

    def test_hide_field(
        self, double_array: DoubleArray, custom_property: Property, expected_data: dict
    ):
        """
        Test the hiding of the field.
        """
        hidden_data = expected_data["hidden_field_data"]
        field_id = FIELD_PROPERTIES[FIELD_INDEX]["id"]

        # Set and test the updated properties
        custom_property.set_field_description(
            field_id, FIELD_PROPERTIES[FIELD_INDEX]["description"]
        )
        double_array.from_list(FIELD_PROPERTIES[FIELD_INDEX]["values"])
        custom_property.set_field_values(field_id, double_array)

        # Hide and test the hidden properties
        custom_property.hide_field(field_id)

        check_properties(custom_property, field_id, hidden_data)

    def test_delete_field(self, double_array: DoubleArray, custom_property: Property):
        """
        Test the deleting of the field.
        """
        field_id_to_delete = FIELD_PROPERTIES[FIELD_INDEX]["id"]

        custom_property.set_field_description(
            field_id_to_delete, FIELD_PROPERTIES[FIELD_INDEX]["description"]
        )
        double_array.from_list(FIELD_PROPERTIES[FIELD_INDEX]["values"])
        custom_property.set_field_values(field_id_to_delete, double_array)

        _check_fields(custom_property, 1, [field_id_to_delete], [])

        custom_property.delete_field(field_id_to_delete)

        _check_fields(custom_property, 0, [], [field_id_to_delete])

    def test_properties_with_two_fields(
        self, double_array: DoubleArray, custom_property: Property, expected_data: dict
    ):
        """
        Test the properties of the new property with two fields.
        """
        original_data = expected_data["original_field_data"]
        updated_data_1 = expected_data["field_data_1"]
        updated_data_2 = expected_data["field_data_2"]
        hidden_data = expected_data["hidden_field_data"]
        field_id_1 = FIELD_PROPERTIES[1]["id"]
        field_id_2 = FIELD_PROPERTIES[2]["id"]

        check_properties(custom_property, field_id_1, original_data)
        check_properties(custom_property, field_id_2, original_data)

        custom_property.set_field_description(field_id_1, FIELD_PROPERTIES[1]["description"])
        double_array.from_list(FIELD_PROPERTIES[1]["values"])
        custom_property.set_field_values(field_id_1, double_array)
        check_properties(custom_property, field_id_1, updated_data_1)
        check_properties(custom_property, field_id_2, original_data)

        custom_property.set_field_description(field_id_2, FIELD_PROPERTIES[2]["description"])
        double_array.from_list(FIELD_PROPERTIES[2]["values"])
        custom_property.set_field_values(field_id_2, double_array)

        check_properties(custom_property, field_id_1, updated_data_1)
        check_properties(custom_property, field_id_2, updated_data_2)

        custom_property.hide_field(field_id_1)
        check_properties(custom_property, field_id_1, hidden_data)
        check_properties(custom_property, field_id_2, updated_data_2)

        # Field ID 2004 is auto added when hidden fields are present
        _check_fields(custom_property, 3, [field_id_1, field_id_2, 2004], [])

        custom_property.delete_field(field_id_1)

        # Field ID 2004 is auto added when hidden fields are present
        _check_fields(custom_property, 2, [field_id_2, 2004], [field_id_1])
