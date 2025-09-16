# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for the StringArray Wrapper Class of the moldflow-api module.
"""

import pytest
from moldflow import StringArray
from tests.api.unit_tests.conftest import INVALID_MOCK_WITH_NONE
from tests.conftest import INVALID_STR


@pytest.mark.unit
@pytest.mark.string_array
class TestUnitStringArray:
    """
    Unit Test suite for the StringArray class.
    """

    @pytest.fixture
    def mock_string_array(self, mock_object) -> StringArray:
        """Fixture to initialize StringArray with the mock instance."""
        return StringArray(mock_object)

    @pytest.mark.parametrize("index, value", [(0, "Hello"), (1, "World")])
    def test_val(self, mock_string_array, mock_object, index, value):
        """Test the val method of the StringArray class."""
        mock_object.Val.return_value = value
        assert mock_string_array.val(index) == value
        mock_object.Val.assert_called_once_with(index)

    @pytest.mark.parametrize("value", ["Hello", "World", ""])
    def test_add_string(self, mock_string_array, mock_object, value):
        """Test the add_string method of the StringArray class."""
        mock_string_array.add_string(value)
        mock_object.AddString.assert_called_once_with(value)

    @pytest.mark.parametrize("value", [None, True, False, 1, 2, 0.1, 0.2])
    def test_add_string_invalid(self, mock_string_array, mock_object, value, _):
        """Test the add_string method of the StringArray class with invalid values"""
        with pytest.raises(TypeError) as e:
            mock_string_array.add_string(value)
        assert _("Invalid") in str(e.value)
        mock_object.AddString.assert_not_called()

    @pytest.mark.parametrize("size", [2, 3])
    def test_size(self, mock_string_array, mock_object, size):
        """Test the Size method of the StringArray class."""
        mock_object.Size = size
        assert mock_string_array.size == size

    @pytest.mark.parametrize(
        "size, values",
        [(3, ["hello", "world", "test"]), (2, ["foo", "bar"]), (1, ["single"]), (0, [])],
    )
    # pylint: disable=R0801
    def test_to_list(self, mock_string_array, mock_object, size, values):
        """Test the to_list method of the StringArray class."""
        mock_object.Size = size
        mock_object.Val.side_effect = lambda i: values[i] if i < len(values) else ""

        result = mock_string_array.to_list()

        assert result == values
        assert len(result) == size
        if size > 0:
            assert mock_object.Val.call_count == size
            for i in range(size):
                mock_object.Val.assert_any_call(i)

    @pytest.mark.parametrize(
        "values",
        [
            ["hello", "world", "test"],
            ["foo", "bar"],
            ["single"],
            [],
            [""],  # empty strings should work
            ("hello", "world", "test"),  # tuples should also work
        ],
    )
    # pylint: disable=R0801
    def test_from_list(self, mock_string_array, mock_object, values):
        """Test the from_list method of the StringArray class."""
        mock_object.FromVBSArray.return_value = len(values)
        result = mock_string_array.from_list(values)
        assert isinstance(result, int)
        assert result == len(values)
        mock_object.FromVBSArray.assert_called_once()

    @pytest.mark.parametrize("invalid_values", INVALID_MOCK_WITH_NONE)
    def test_from_list_invalid_type(self, mock_string_array, mock_object, invalid_values, _):
        """Test the from_list method with invalid input type."""
        with pytest.raises(TypeError) as e:
            mock_string_array.from_list(invalid_values)
        assert _("Invalid") in str(e.value)
        mock_object.FromVBSArray.assert_not_called()

    @pytest.mark.parametrize("invalid_values", INVALID_STR)
    def test_from_list_invalid_values(self, mock_string_array, mock_object, invalid_values, _):
        """StringArray.from_list should raise when non-str values present."""

        with pytest.raises(TypeError):
            mock_string_array.from_list([invalid_values])
        mock_object.FromVBSArray.assert_not_called()
