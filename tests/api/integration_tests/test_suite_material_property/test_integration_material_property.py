# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for Property Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the Property class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import Synergy, Property
from tests.api.integration_tests.common_test_utilities.property_tests_helper import (
    check_properties,
    check_property_initialization,
)
from tests.api.integration_tests.test_suite_material_property.constants import (
    MATERIAL_DB,
    MATERIAL_DB_TYPE,
)


@pytest.mark.integration
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

    def test_property_initialization(self, material_property: Property):
        """
        Test that Property instance is properly initialized.
        """
        check_property_initialization(material_property)

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
            check_properties(material_property, field_id, expected_data[f"field_{field_id}"])
            field_id = material_property.get_next_field(field_id)
