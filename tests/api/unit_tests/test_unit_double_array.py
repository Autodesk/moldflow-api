# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for DoubleArray Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import DoubleArray
from tests.api.unit_tests.conftest import INVALID_MOCK_WITH_NONE
from tests.conftest import INVALID_FLOAT


@pytest.mark.unit
@pytest.mark.double_array
class TestUnitDoubleArray:
    """
    Unit Test Suite for the DoubleArray class.
    """

    @pytest.fixture
    def mock_double_array(self, mock_object):
        """Fixture to initialize DoubleArray with the mock instance."""
        return DoubleArray(mock_object)

    @pytest.mark.parametrize("index, value", [(0, 0.1), (1, 0.2)])
    def test_val(self, mock_double_array, mock_object, index, value):
        """Test the val method of the DoubleArray class."""
        mock_object.Val.return_value = value
        assert mock_double_array.val(index) == value
        mock_object.Val.assert_called_once_with(index)

    @pytest.mark.parametrize("value", [0.1, 0.2, 1, 2])
    def test_add_double(self, mock_double_array, mock_object, value):
        """Test the add_double method of the DoubleArray class."""
        mock_double_array.add_double(value)
        mock_object.AddDouble.assert_called_once_with(value)

    @pytest.mark.parametrize("value", [None, "", "ABC", "123", True, False])
    def test_add_double_invalid(self, mock_double_array, mock_object, value, _):
        """Test the add_double method of the DoubleArray class with invalid values"""
        with pytest.raises(TypeError) as e:
            mock_double_array.add_double(value)
        assert _("Invalid") in str(e.value)
        mock_object.AddDouble.assert_not_called()

    @pytest.mark.parametrize("size", [2, 3])
    def test_size(self, mock_double_array, mock_object, size):
        """Test the Size method of the DoubleArray class."""
        mock_object.Size = size
        assert mock_double_array.size == size

    @pytest.mark.parametrize("values", [[1.0, 2.5, 3.7], [0.0, 10.5], [42.42], []])
    def test_to_list(self, mock_double_array, mock_object, values):
        """to_list should use bulk ToVBSArray and return expected values."""

        mock_object.ToVBSArray.return_value = tuple(values)

        assert mock_double_array.to_list() == values
        mock_object.ToVBSArray.assert_called_once_with()

    @pytest.mark.parametrize(
        "values",
        [
            [1.0, 2.5, 3.7],
            [0.0, 10.5],
            [42.42],
            [],
            [1, 2, 3],
            (1.0, 2.5, 3.7),
        ],  # integers should also work
    )
    # pylint: disable=R0801
    def test_from_list(self, mock_double_array, mock_object, values):
        """Test the from_list method of the DoubleArray class."""
        mock_double_array.from_list(values)
        mock_object.FromVBSArray.assert_called_once_with(list(values))

    @pytest.mark.parametrize("invalid_values", INVALID_MOCK_WITH_NONE)
    def test_from_list_invalid_type(self, mock_double_array, mock_object, invalid_values, _):
        """Test the from_list method with invalid input type."""
        with pytest.raises(TypeError) as e:
            mock_double_array.from_list(invalid_values)
        assert _("Invalid") in str(e.value)
        mock_object.FromVBSArray.assert_not_called()

    @pytest.mark.parametrize("invalid_values", INVALID_FLOAT)
    def test_from_list_invalid_values(self, mock_double_array, invalid_values, _):
        """Test the from_list method with invalid values in list."""
        with pytest.raises(TypeError) as e:
            mock_double_array.from_list(invalid_values)
        assert _("Invalid") in str(e.value)
