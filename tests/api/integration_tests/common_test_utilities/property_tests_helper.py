# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Helper functions for property tests.

This module contains helper functions for property tests.
"""

from moldflow import Property


def check_properties(test_property: Property, field_id: int, expected_properties_data: dict):
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


def check_property_initialization(test_property: Property):
    """
    Test that Property instance is properly initialized.
    """
    assert test_property is not None
    assert test_property.prop is not None
    assert isinstance(test_property, Property)
