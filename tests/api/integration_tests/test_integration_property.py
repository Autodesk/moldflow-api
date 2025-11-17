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
from tests.api.integration_tests.data.set_fields import (
    MATERIAL_DB,
    MATERIAL_DB_TYPE,
    CUSTOM_PROPERTY_NAME,
    CUSTOM_PROPERTY_ID,
    CUSTOM_PROPERTY_TYPE,
    CUSTOM_PROPERTY_DEFAULTS,
    FIELD_PROPERTIES,
    FIELD_INDEX,
)


def _check_properties(test_property: Property, field_id: int, expected_properties_data: dict):
    """
    Check the properties of the Property instance.
    """

    field_description = test_property.get_field_description(field_id)

    field_values = test_property.get_field_values(field_id)
    if field_values is not None:
        field_values = field_values.to_list()

    field_units = test_property.field_units(field_id)
    if field_units is not None:
        field_units = field_units.to_list()

    field_writable = test_property.is_field_writable(field_id)
    field_hidden = test_property.is_field_hidden(field_id)

    assert field_description == expected_properties_data["field_description"]
    assert field_values == expected_properties_data["field_values"]
    assert field_units == expected_properties_data["field_units"]
    assert field_writable == expected_properties_data["field_writable"]
    assert field_hidden == expected_properties_data["field_hidden"]


def _check_property_initialization(test_property: Property):
    """
    Test that Property instance is properly initialized.
    """
    assert test_property is not None
    assert test_property.prop is not None
    assert isinstance(test_property, Property)


# Testing pre-existing materials as check
# --------------------------------------------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.prop
@pytest.mark.material_property
@pytest.mark.json_file_name("material_property")
class TestIntegrationMaterialProperty:
    """
    Integration test suite for the pre-existing materials for Property class.
    """

    @pytest.fixture
    def material_property(self, synergy: Synergy):
        """
        Fixture to create a real Property instance for integration testing.
        """
        mf = synergy.material_finder
        mf.set_data_domain(MATERIAL_DB, MATERIAL_DB_TYPE)
        mat = mf.get_first_material()
        return mat

    def test_property_initialization(self, material_property: Property, expected_data: dict):
        """
        Test that Property instance is properly initialized.
        """
        _check_property_initialization(material_property)

    def test_metadata(self, material_property: Property, expected_data: dict):
        """
        Test the name, id, and type of the Material property.
        """
        assert material_property.name == expected_data["material_name"]
        assert material_property.id == expected_data["material_id"]
        assert material_property.type == expected_data["material_type"]

    def test_properties(self, material_property: Property, expected_data: dict):
        """
        Test the properties of the Property instance.
        """
        field_id = material_property.get_first_field()
        while field_id != 0:
            _check_properties(material_property, field_id, expected_data[f"field_{field_id}"])
            field_id = material_property.get_next_field(field_id)


# --------------------------------------------------------------------------------------------------

# Testing custom property
# --------------------------------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.prop
@pytest.mark.custom_property
@pytest.mark.file_set(FileSet.SINGLE)
@pytest.mark.json_file_name("custom_property")
class TestIntegrationCustomProperty:
    """
    Integration test suite for a new custom property for Property class.
    """

    @pytest.fixture()
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
        _check_property_initialization(custom_property)

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
        _check_properties(custom_property, field_id, original_data)

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

        _check_properties(custom_property, field_id, updated_data)

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

        _check_properties(custom_property, field_id, hidden_data)

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

        fields = []
        field_id = custom_property.get_first_field()
        while field_id != 0:
            fields.append(field_id)
            field_id = custom_property.get_next_field(field_id)
        assert len(fields) == 1
        assert field_id_to_delete in fields

        custom_property.delete_field(field_id_to_delete)
        fields = []
        field_id = custom_property.get_first_field()
        while field_id != 0:
            fields.append(field_id)
            field_id = custom_property.get_next_field(field_id)
        assert len(fields) == 0

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

        _check_properties(custom_property, field_id_1, original_data)
        _check_properties(custom_property, field_id_2, original_data)

        custom_property.set_field_description(field_id_1, FIELD_PROPERTIES[1]["description"])
        double_array.from_list(FIELD_PROPERTIES[1]["values"])
        custom_property.set_field_values(field_id_1, double_array)
        _check_properties(custom_property, field_id_1, updated_data_1)
        _check_properties(custom_property, field_id_2, original_data)

        custom_property.set_field_description(field_id_2, FIELD_PROPERTIES[2]["description"])
        double_array.from_list(FIELD_PROPERTIES[2]["values"])
        custom_property.set_field_values(field_id_2, double_array)

        _check_properties(custom_property, field_id_1, updated_data_1)
        _check_properties(custom_property, field_id_2, updated_data_2)

        custom_property.hide_field(field_id_1)
        _check_properties(custom_property, field_id_1, hidden_data)
        _check_properties(custom_property, field_id_2, updated_data_2)

        fields = []
        field_id = custom_property.get_first_field()
        while field_id != 0:
            fields.append(field_id)
            field_id = custom_property.get_next_field(field_id)
        assert len(fields) == 3  # Field ID 2004 is auto added when hidden fields are present
        assert field_id_1 in fields
        assert field_id_2 in fields
        assert 2004 in fields

        custom_property.delete_field(field_id_1)
        fields = []
        field_id = custom_property.get_first_field()
        while field_id != 0:
            fields.append(field_id)
            field_id = custom_property.get_next_field(field_id)
        assert len(fields) == 2  # Field ID 2004 is auto added when hidden fields are present
        assert field_id_1 not in fields
        assert field_id_2 in fields
        assert 2004 in fields
