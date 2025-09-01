# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for the IntegerArray Wrapper Class of the moldflow-api module.
"""

import pytest
from moldflow import IntegerArray
from tests.api.unit_tests.conftest import INVALID_MOCK_WITH_NONE
from tests.conftest import INVALID_INT


@pytest.mark.unit
class TestUnitIntegerArray:
    """
    Unit Test suite for the IntegerArray class.
    """

    @pytest.fixture
    def mock_integer_array(self, mock_object):
        """Fixture to initialize IntegerArray with the mock instance."""
        return IntegerArray(mock_object)

    @pytest.mark.parametrize("index, value", [(0, 1), (1, 2)])
    def test_val(self, mock_integer_array, mock_object, index, value):
        """Test the val method of the IntegerArray class."""
        mock_object.Val.return_value = value
        assert mock_integer_array.val(index) == value
        mock_object.Val.assert_called_once_with(index)

    @pytest.mark.parametrize("value", [1, 2])
    def test_add_integer(self, mock_integer_array, mock_object, value):
        """Test the add_integer method of the IntegerArray class."""
        mock_integer_array.add_integer(value)
        mock_object.AddInteger.assert_called_once_with(value)

    @pytest.mark.parametrize("value", [None, True, False, 0.1, 0.2, "ABC", "123"])
    def test_add_integer_invalid(self, mock_integer_array, mock_object, value, _):
        """Test the add_integer method of the IntegerArray class with invalid values"""
        with pytest.raises(TypeError) as e:
            mock_integer_array.add_integer(value)
        assert _("Invalid") in str(e.value)
        mock_object.AddInteger.assert_not_called()

    @pytest.mark.parametrize("size", [2, 3])
    def test_size(self, mock_integer_array, mock_object, size):
        """Test the Size method of the IntegerArray class."""
        mock_object.Size = size
        assert mock_integer_array.size == size

    @pytest.mark.parametrize("values", [[1, 2, 3], [0, 10], [42], [], [-1, 0, 1, 100]])
    def test_to_list(self, mock_integer_array, mock_object, values):
        """IntegerArray to_list should use bulk ToVBSArray."""

        mock_object.ToVBSArray.return_value = tuple(values)

        assert mock_integer_array.to_list() == values
        mock_object.ToVBSArray.assert_called_once_with()

    @pytest.mark.parametrize(
        "values",
        [[1, 2, 3], [0, 10], [42], [], [-1, 0, 1, 100], (1, 2, 3)],  # tuples should also work
    )
    # pylint: disable=R0801
    def test_from_list(self, mock_integer_array, mock_object, values):
        """Test the from_list method of the IntegerArray class."""
        mock_integer_array.from_list(values)

        mock_object.FromVBSArray.assert_called_once_with(list(values))

    @pytest.mark.parametrize("invalid_values", INVALID_MOCK_WITH_NONE)
    def test_from_list_invalid_type(self, mock_integer_array, mock_object, invalid_values, _):
        """Test the from_list method with invalid input type."""
        with pytest.raises(TypeError) as e:
            mock_integer_array.from_list(invalid_values)
        assert _("Invalid") in str(e.value)
        mock_object.FromVBSArray.assert_not_called()

    # per-element validation removed; skip invalid element tests

    @pytest.mark.parametrize("invalid_values", INVALID_INT)
    def test_from_list_invalid_values(self, mock_integer_array, mock_object, invalid_values, _):
        """IntegerArray.from_list should raise when list contains non-int values."""

        with pytest.raises(TypeError):
            mock_integer_array.from_list([invalid_values])
        mock_object.FromVBSArray.assert_not_called()
