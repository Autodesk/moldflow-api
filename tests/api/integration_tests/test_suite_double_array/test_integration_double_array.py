# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for DoubleArray Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the DoubleArray class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import DoubleArray, Synergy


@pytest.mark.integration
@pytest.mark.double_array
class TestIntegrationDoubleArray:
    """
    Integration test suite for the DoubleArray class.
    """

    @pytest.fixture
    def double_array(self, synergy: Synergy):
        """
        Fixture to create a real DoubleArray instance for integration testing.
        """
        return synergy.create_double_array()

    def _check_double_array_size(self, double_array: DoubleArray, expected_size: int):
        """
        Verify the size of the double array.
        """
        assert double_array.size == expected_size

    def _check_value_at_index(self, double_array: DoubleArray, index: int, expected_value: float):
        """
        Verify the value at a specific index in the array.
        """
        assert double_array.val(index) == expected_value

    @pytest.mark.synergy
    def test_create_double_array(self, synergy: Synergy):
        """
        Test that DoubleArray can be created from Synergy instance.
        """
        double_array = synergy.create_double_array()
        self._check_double_array_size(double_array, 0)

    def test_add_double_single_value(self, double_array: DoubleArray):
        """
        Test adding a single double value to the array.
        """
        self._check_double_array_size(double_array, 0)

        double_array.add_double(42.5)
        self._check_double_array_size(double_array, 1)
        self._check_value_at_index(double_array, 0, 42.5)

    @pytest.mark.parametrize("values", [[1.0, 2.5, 3.7, 0, 1, 0.0, -1.1]])
    def test_add_double_multiple_values(self, double_array: DoubleArray, values: list[float | int]):
        """
        Test adding multiple double values to the array.
        """
        self._check_double_array_size(double_array, 0)

        for i, value in enumerate(values):
            double_array.add_double(value)
            self._check_double_array_size(double_array, i + 1)
            self._check_value_at_index(double_array, i, float(value))

        # Verify all values are still correct after all additions
        self._check_double_array_size(double_array, len(values))
        for i, value in enumerate(values):
            self._check_value_at_index(double_array, i, float(value))

    def test_val_method_indexing(self, double_array: DoubleArray):
        """
        Test accessing values by index using the val method.
        """
        test_values = [10.5, -20.25, 0.0, 100.123, -5.75]

        # Add test values
        for value in test_values:
            double_array.add_double(value)

        # Test accessing each value by index
        for i, expected_value in enumerate(test_values):
            self._check_value_at_index(double_array, i, expected_value)

    @pytest.mark.parametrize("size", [1, 5, 10])
    def test_size_property(self, double_array: DoubleArray, size: int):
        """
        Test that the size property correctly reflects the number of values.
        """
        self._check_double_array_size(double_array, 0)

        for i in range(size):
            double_array.add_double(float(i * 1.5))
            self._check_double_array_size(double_array, i + 1)

        self._check_double_array_size(double_array, size)

    def test_to_list_empty_array(self, double_array: DoubleArray):
        """
        Test converting an empty double array to a list.
        """
        result = double_array.to_list()
        assert result == []
        assert isinstance(result, list)

    @pytest.mark.parametrize("values", [[0.0, -1, 10.25, -5.75]])
    def test_to_list_populated_array(self, double_array: DoubleArray, values: list[float | int]):
        """
        Test converting a populated double array to a list.
        """
        # Add values to array
        for value in values:
            double_array.add_double(value)

        # Convert to list
        result = double_array.to_list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == len(values)
        assert result == values

    def test_from_list_empty_list(self, double_array: DoubleArray):
        """
        Test creating a double array from an empty list.
        """
        double_array.from_list([])
        self._check_double_array_size(double_array, 0)
        assert double_array.to_list() == []

    @pytest.mark.parametrize("values", [[0.0, -1, 10.25, -5.75]])
    def test_from_list_populated_list(
        self, double_array: DoubleArray, values: list[float | int] | tuple
    ):
        """
        Test creating a double array from a populated list.
        """
        double_array.from_list(values)

        # Verify size
        self._check_double_array_size(double_array, len(values))

        # Verify values
        for i, expected_value in enumerate(values):
            self._check_value_at_index(double_array, i, float(expected_value))

        # Verify to_list conversion
        result = double_array.to_list()
        assert len(result) == len(values)
        assert result == values

    def test_round_trip_conversion(self, double_array: DoubleArray):
        """
        Test round-trip conversion: list -> DoubleArray -> list.
        """
        original_values = [1.5, -2.25, 0.0, 100.123, -5.75, 42.0]

        # Convert list to DoubleArray
        double_array.from_list(original_values)

        # Convert back to list
        result_values = double_array.to_list()

        # Verify round-trip conversion
        assert len(result_values) == len(original_values)
        assert result_values == original_values

    def test_round_trip_conversion2(self, synergy: Synergy):
        """
        Test round-trip conversion: list -> DoubleArray -> list.
        """
        double_array = synergy.create_double_array()
        double_array2 = synergy.create_double_array()
        original_values = [1.5, -2.25, 0.0, 100.123, -5.75, 42.0]

        for value in original_values:
            double_array.add_double(value)

        result_values = double_array.to_list()

        double_array2.from_list(result_values)

        for i, value in enumerate(original_values):
            self._check_value_at_index(double_array, i, float(value))
            self._check_value_at_index(double_array2, i, float(value))

    def test_reference_behavior(self, double_array: DoubleArray):
        """
        Test reference behavior of DoubleArray.
        """
        double_array.add_double(1.1)
        double_array_copy = double_array
        self._check_double_array_size(double_array_copy, 1)
        self._check_value_at_index(double_array_copy, 0, 1.1)

        double_array_copy.add_double(2.2)
        self._check_double_array_size(double_array_copy, 2)
        self._check_value_at_index(double_array_copy, 0, 1.1)
        self._check_value_at_index(double_array_copy, 1, 2.2)
        self._check_value_at_index(double_array, 1, 2.2)

        double_array_copy2 = DoubleArray(double_array.double_array)
        self._check_double_array_size(double_array_copy2, 2)
        self._check_value_at_index(double_array_copy2, 0, 1.1)
        self._check_value_at_index(double_array_copy2, 1, 2.2)

        double_array_copy2.add_double(3.3)
        self._check_double_array_size(double_array_copy2, 3)
        self._check_value_at_index(double_array_copy2, 0, 1.1)
        self._check_value_at_index(double_array_copy2, 1, 2.2)
        self._check_value_at_index(double_array_copy2, 2, 3.3)
