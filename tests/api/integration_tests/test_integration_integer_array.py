"""
Integration tests for IntegerArray Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the IntegerArray class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import IntegerArray, Synergy
from tests.conftest import VALID_INT


@pytest.mark.integration
@pytest.mark.integer_array
class TestIntegrationIntegerArray:
    """
    Integration test suite for the IntegerArray class.
    """

    @pytest.fixture
    def integer_array(self, synergy: Synergy):
        """
        Fixture to create a real IntegerArray instance for integration testing.
        """
        return synergy.create_integer_array()

    def _check_integer_array_size(self, integer_array: IntegerArray, expected_size: int):
        """
        Verify the size of the integer array.
        """
        assert integer_array.size == expected_size

    def _check_value_at_index(self, integer_array: IntegerArray, index: int, expected_value: int):
        """
        Verify the value at a specific index in the array.
        """
        assert integer_array.val(index) == expected_value

    @pytest.mark.synergy
    def test_create_integer_array(self, synergy: Synergy):
        """
        Test that IntegerArray can be created from Synergy instance.
        """
        integer_array = synergy.create_integer_array()
        self._check_integer_array_size(integer_array, 0)

    def test_add_integer_single_value(self, integer_array: IntegerArray):
        """
        Test adding a single integer value to the array.
        """
        self._check_integer_array_size(integer_array, 0)

        integer_array.add_integer(42)
        self._check_integer_array_size(integer_array, 1)
        self._check_value_at_index(integer_array, 0, 42)

    @pytest.mark.parametrize("values", [VALID_INT])
    def test_add_integer_multiple_values(self, integer_array: IntegerArray, values: list[int]):
        """
        Test adding multiple integer values to the array.
        """
        self._check_integer_array_size(integer_array, 0)

        for i, value in enumerate(values):
            integer_array.add_integer(value)
            self._check_integer_array_size(integer_array, i + 1)
            self._check_value_at_index(integer_array, i, value)

        # Verify all values are still correct after all additions
        self._check_integer_array_size(integer_array, len(values))
        for i, value in enumerate(values):
            self._check_value_at_index(integer_array, i, value)

    def test_val_method_indexing(self, integer_array: IntegerArray):
        """
        Test accessing values by index using the val method.
        """
        test_values = VALID_INT

        # Add test values
        for value in test_values:
            integer_array.add_integer(value)

        # Test accessing each value by index
        for i, expected_value in enumerate(test_values):
            self._check_value_at_index(integer_array, i, expected_value)

    @pytest.mark.parametrize("size", [1, 5, 10])
    def test_size_property(self, integer_array: IntegerArray, size: int):
        """
        Test that the size property correctly reflects the number of values.
        """
        self._check_integer_array_size(integer_array, 0)

        for i in range(size):
            integer_array.add_integer(i)
            self._check_integer_array_size(integer_array, i + 1)

        self._check_integer_array_size(integer_array, size)

    def test_to_list_empty_array(self, integer_array: IntegerArray):
        """
        Test converting an empty integer array to a list.
        """
        result = integer_array.to_list()
        assert result == []
        assert isinstance(result, list)

    @pytest.mark.parametrize("values", [VALID_INT])
    def test_to_list_populated_array(self, integer_array: IntegerArray, values: list[int]):
        """
        Test converting a populated integer array to a list.
        """
        # Add values to array
        for value in values:
            integer_array.add_integer(value)

        # Convert to list
        result = integer_array.to_list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == len(values)
        assert result == values

    def test_from_list_empty_list(self, integer_array: IntegerArray):
        """
        Test creating a integer array from an empty list.
        """
        integer_array.from_list([])
        self._check_integer_array_size(integer_array, 0)
        assert integer_array.to_list() == []

    @pytest.mark.parametrize("values", [VALID_INT])
    def test_from_list_populated_list(self, integer_array: IntegerArray, values: list[int] | tuple):
        """
        Test creating a integer array from a populated list.
        """
        integer_array.from_list(values)

        # Verify size
        self._check_integer_array_size(integer_array, len(values))

        # Verify values
        for i, expected_value in enumerate(values):
            self._check_value_at_index(integer_array, i, expected_value)

        # Verify to_list conversion
        result = integer_array.to_list()
        assert len(result) == len(values)
        assert result == values

    def test_round_trip_conversion(self, integer_array: IntegerArray):
        """
        Test round-trip conversion: list -> IntegerArray -> list.
        """
        original_values = VALID_INT

        # Convert list to IntegerArray
        integer_array.from_list(original_values)

        # Convert back to list
        result_values = integer_array.to_list()

        # Verify round-trip conversion
        assert len(result_values) == len(original_values)
        assert result_values == original_values

    def test_round_trip_conversion2(self, synergy: Synergy):
        """
        Test round-trip conversion: list -> IntegerArray -> list.
        """
        integer_array = synergy.create_integer_array()
        integer_array2 = synergy.create_integer_array()
        original_values = VALID_INT

        for value in original_values:
            integer_array.add_integer(value)

        result_values = integer_array.to_list()

        integer_array2.from_list(result_values)

        for i, value in enumerate(original_values):
            self._check_value_at_index(integer_array, i, value)
            self._check_value_at_index(integer_array2, i, value)

    def test_reference_behavior(self, integer_array: IntegerArray):
        """
        Test reference behavior of IntegerArray.
        """
        integer_array.add_integer(1)
        integer_array_copy = integer_array
        self._check_integer_array_size(integer_array_copy, 1)
        self._check_value_at_index(integer_array_copy, 0, 1)

        integer_array_copy.add_integer(2)
        self._check_integer_array_size(integer_array_copy, 2)
        self._check_value_at_index(integer_array_copy, 0, 1)
        self._check_value_at_index(integer_array_copy, 1, 2)
        self._check_value_at_index(integer_array, 1, 2)

        integer_array_copy2 = IntegerArray(integer_array.integer_array)
        self._check_integer_array_size(integer_array_copy2, 2)
        self._check_value_at_index(integer_array_copy2, 0, 1)
        self._check_value_at_index(integer_array_copy2, 1, 2)

        integer_array_copy2.add_integer(3)
        self._check_integer_array_size(integer_array_copy2, 3)
        self._check_value_at_index(integer_array_copy2, 0, 1)
        self._check_value_at_index(integer_array_copy2, 1, 2)
        self._check_value_at_index(integer_array_copy2, 2, 3)
