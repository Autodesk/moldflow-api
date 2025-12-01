# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for StringArray Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the StringArray class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import StringArray, Synergy
from tests.conftest import VALID_STR


@pytest.mark.integration
@pytest.mark.string_array
class TestIntegrationStringArray:
    """
    Integration test suite for the StringArray class.
    """

    @pytest.fixture
    def string_array(self, synergy: Synergy):
        """
        Fixture to create a real StringArray instance for integration testing.
        """
        return synergy.create_string_array()

    def _check_string_array_size(self, string_array: StringArray, expected_size: int):
        """
        Verify the size of the string array.
        """
        assert string_array.size == expected_size

    def _check_value_at_index(self, string_array: StringArray, index: int, expected_value: str):
        """
        Verify the value at a specific index in the array.
        """
        assert string_array.val(index) == expected_value

    @pytest.mark.synergy
    def test_create_string_array(self, synergy: Synergy):
        """
        Test that StringArray can be created from Synergy instance.
        """
        string_array = synergy.create_string_array()
        self._check_string_array_size(string_array, 0)

    def test_add_string_single_value(self, string_array: StringArray):
        """
        Test adding a single string value to the array.
        """
        self._check_string_array_size(string_array, 0)

        string_array.add_string("42.5")
        self._check_string_array_size(string_array, 1)
        self._check_value_at_index(string_array, 0, "42.5")

    @pytest.mark.parametrize("values", [VALID_STR])
    def test_add_string_multiple_values(self, string_array: StringArray, values: list[str]):
        """
        Test adding multiple string values to the array.
        """
        self._check_string_array_size(string_array, 0)

        for i, value in enumerate(values):
            string_array.add_string(value)
            self._check_string_array_size(string_array, i + 1)
            self._check_value_at_index(string_array, i, value)

        # Verify all values are still correct after all additions
        self._check_string_array_size(string_array, len(values))
        for i, value in enumerate(values):
            self._check_value_at_index(string_array, i, value)

    def test_val_method_indexing(self, string_array: StringArray):
        """
        Test accessing values by index using the val method.
        """
        test_values = VALID_STR

        # Add test values
        for value in test_values:
            string_array.add_string(value)

        # Test accessing each value by index
        for i, expected_value in enumerate(test_values):
            self._check_value_at_index(string_array, i, expected_value)

    @pytest.mark.parametrize("size", [1, 5, 10])
    def test_size_property(self, string_array: StringArray, size: int):
        """
        Test that the size property correctly reflects the number of values.
        """
        self._check_string_array_size(string_array, 0)

        for i in range(size):
            string_array.add_string(str(i))
            self._check_string_array_size(string_array, i + 1)

        self._check_string_array_size(string_array, size)

    def test_to_list_empty_array(self, string_array: StringArray):
        """
        Test converting an empty string array to a list.
        """
        result = string_array.to_list()
        assert result == []
        assert isinstance(result, list)

    @pytest.mark.parametrize("values", [VALID_STR])
    def test_to_list_populated_array(self, string_array: StringArray, values: list[str]):
        """
        Test converting a populated string array to a list.
        """
        # Add values to array
        for value in values:
            string_array.add_string(value)

        # Convert to list
        result = string_array.to_list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == len(values)
        assert result == values

    def test_from_list_empty_list(self, string_array: StringArray):
        """
        Test creating a string array from an empty list.
        """
        string_array.from_list([])
        self._check_string_array_size(string_array, 0)
        assert string_array.to_list() == []

    @pytest.mark.parametrize("values", [VALID_STR])
    def test_from_list_populated_list(
        self, string_array: StringArray, values: list[str] | tuple[str, ...]
    ):
        """
        Test creating a string array from a populated list.
        """
        string_array.from_list(values)

        # Verify size
        self._check_string_array_size(string_array, len(values))

        # Verify values
        for i, expected_value in enumerate(values):
            self._check_value_at_index(string_array, i, expected_value)

        # Verify to_list conversion
        result = string_array.to_list()
        assert len(result) == len(values)
        assert result == values

    def test_round_trip_conversion(self, string_array: StringArray):
        """
        Test round-trip conversion: list -> StringArray -> list.
        """
        original_values = VALID_STR

        # Convert list to StringArray
        string_array.from_list(original_values)

        # Convert back to list
        result_values = string_array.to_list()

        # Verify round-trip conversion
        assert len(result_values) == len(original_values)
        assert result_values == original_values

    def test_round_trip_conversion2(self, synergy: Synergy):
        """
        Test round-trip conversion: list -> StringArray -> list.
        """
        string_array = synergy.create_string_array()
        string_array2 = synergy.create_string_array()
        original_values = VALID_STR

        for value in original_values:
            string_array.add_string(value)

        result_values = string_array.to_list()

        string_array2.from_list(result_values)

        for i, value in enumerate(original_values):
            self._check_value_at_index(string_array, i, value)
            self._check_value_at_index(string_array2, i, value)

    def test_reference_behavior(self, string_array: StringArray):
        """
        Test reference behavior of StringArray.
        """
        string_array.add_string("1.1")
        string_array_copy = string_array
        self._check_string_array_size(string_array_copy, 1)
        self._check_value_at_index(string_array_copy, 0, "1.1")

        string_array_copy.add_string("2.2")
        self._check_string_array_size(string_array_copy, 2)
        self._check_value_at_index(string_array_copy, 0, "1.1")
        self._check_value_at_index(string_array_copy, 1, "2.2")
        self._check_value_at_index(string_array, 1, "2.2")

        string_array_copy2 = StringArray(string_array.string_array)
        self._check_string_array_size(string_array_copy2, 2)
        self._check_value_at_index(string_array_copy2, 0, "1.1")
        self._check_value_at_index(string_array_copy2, 1, "2.2")

        string_array_copy2.add_string("3.3")
        self._check_string_array_size(string_array_copy2, 3)
        self._check_value_at_index(string_array_copy2, 0, "1.1")
        self._check_value_at_index(string_array_copy2, 1, "2.2")
        self._check_value_at_index(string_array_copy2, 2, "3.3")
