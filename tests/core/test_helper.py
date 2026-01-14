# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test helper.py
"""

from unittest.mock import Mock
from enum import Enum
import inspect
import pytest
from moldflow.helper import (
    check_file_extension,
    check_index,
    check_is_non_negative,
    check_is_non_zero,
    check_is_positive,
    check_is_negative,
    check_min_max,
    check_type,
    check_optional_type,
    check_and_coerce_optional,
    check_range,
    check_expected_values,
    get_enum_value,
    _mf_array_to_list,
)
from moldflow import common
from tests.conftest import (
    INVALID_INT,
    INVALID_FLOAT,
    VALID_STR,
    VALID_BOOL,
    VALID_INT,
    VALID_FLOAT,
    list_intersection,
)

INVALID_VALUE_DICT = {"int": -1, "float": -1.1, "str": "invalid_string", "tuple": ()}


def _enum_test_cases_invalid_value():
    for _, enum_cls in inspect.getmembers(common, inspect.isclass):
        if issubclass(enum_cls, Enum):
            members = list(enum_cls)
            if not members:
                continue  # skip empty enums
            value_type = type(members[0].value)
            invalid = INVALID_VALUE_DICT.get(value_type.__name__)
            if not value_type == bool:
                yield invalid, enum_cls


def _enum_test_cases():
    for _, enum_cls in inspect.getmembers(common, inspect.isclass):
        if issubclass(enum_cls, Enum):
            members = list(enum_cls)
            if not members:
                continue  # skip empty enums
            value_type = type(members[0].value)
            for member in members:
                yield enum_cls, value_type, member, member.value
                yield enum_cls, value_type, member.value, member.value


@pytest.mark.core
class TestHelper:
    """
    Test suite for errors.
    """

    @pytest.mark.parametrize("enum, enum_value_type, enum_value, expected", _enum_test_cases())
    def test_get_enum_value(self, enum, enum_value_type, enum_value, expected):
        """
        Test get_enum_value function for all enums in common.py.
        """
        res = get_enum_value(enum_value, enum)
        assert isinstance(res, enum_value_type)
        assert res == expected

    @pytest.mark.parametrize("value, enum", _enum_test_cases_invalid_value())
    def test_get_enum_value_invalid_value(self, value, enum, _, caplog):
        """
        Test get_enum_value function with invalid type.
        """
        return_value = get_enum_value(value, enum)
        assert return_value == value
        assert _("this may cause function call to fail") in caplog.text

    @pytest.mark.parametrize(
        "value, types",
        [(x, (int, float)) for x in VALID_INT + VALID_FLOAT]
        + [(x, str) for x in VALID_STR]
        + [(x, bool) for x in VALID_BOOL],
    )
    def test_check_type(self, value, types, _, caplog):
        """
        Test check_type function.
        """
        check_type(value, types)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize(
        "value, types",
        [(x, (int, float)) for x in list_intersection(INVALID_FLOAT, INVALID_INT)]
        + [(x, int) for x in INVALID_INT],
    )
    def test_check_type_invalid(self, value, types, _):
        """
        Test check_type function with invalid type.
        """
        with pytest.raises(TypeError) as e:
            check_type(value, types)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "value, min_value, max_value, min_inclusive, max_inclusive",
        [
            (10, 5, 15, True, True),
            (5, 5, 15, True, True),
            (15, 5, 15, True, True),
            (5, 4, 15, False, True),
            (15, 5, 16, True, False),
            (10, 5, 15, False, False),
            (5, 4, 15, False, False),
            (15, 4, 16, False, False),
            (10, 5, 15, True, False),
            (10, 5, 15, False, True),
            (10, 5, None, True, False),
            (10, None, 15, False, True),
            (10, None, None, False, False),
            (10, None, None, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_check_range(
        self, value, min_value, max_value, min_inclusive, max_inclusive, _, caplog
    ):
        """
        Test check_range function.
        """
        check_range(value, min_value, max_value, min_inclusive, max_inclusive)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize(
        "value, min_value, max_value, min_inclusive, max_inclusive",
        [
            (4, 5, 15, True, True),
            (16, 5, 15, True, True),
            (4, 5, 15, False, True),
            (16, 5, 15, True, False),
            (4, 5, 15, False, False),
            (16, 5, 15, False, False),
            (4, 5, 15, True, False),
            (16, 5, 15, False, True),
            (4, 5, None, True, False),
            (16, None, 15, False, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_check_range_invalid(
        self, value, min_value, max_value, min_inclusive, max_inclusive, _
    ):
        """
        Test check_range function with invalid range.
        """
        with pytest.raises(ValueError) as e:
            check_range(value, min_value, max_value, min_inclusive, max_inclusive)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("value", [0, 10, 10.5])
    def test_check_is_non_negative(self, value, _, caplog):
        """
        Test check_is_non_negative function.
        """
        check_is_non_negative(value)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("value", [-10, -10.5])
    def test_check_is_non_negative_invalid(self, value, _):
        """
        Test check_is_non_negative function with invalid value.
        """
        with pytest.raises(ValueError) as e:
            check_is_non_negative(value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("value", [10, 10.5])
    def test_check_is_positive(self, value, _, caplog):
        """
        Test check_is_positive function.
        """
        check_is_positive(value)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("value", [0, -10, -10.5])
    def test_check_is_positive_invalid(self, value, _):
        """
        Test check_is_positive function with invalid value.
        """
        with pytest.raises(ValueError) as e:
            check_is_positive(value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("value", [-10, -10.5])
    def test_check_is_negative(self, value, _, caplog):
        """
        Test check_is_negative function.
        """
        check_is_negative(value)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("value", [0, 10, 10.5])
    def test_check_is_negative_invalid(self, value, _):
        """
        Test check_is_negative function with invalid value.
        """
        with pytest.raises(ValueError) as e:
            check_is_negative(value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("value", [10, 10.5, -10, -10.5])
    def test_check_is_non_zero(self, value, _, caplog):
        """
        Test check_is_non_zero function.
        """
        check_is_non_zero(value)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("value", [0])
    def test_check_is_non_zero_invalid(self, value, _):
        """
        Test check_is_non_zero function with invalid value.
        """
        with pytest.raises(ValueError) as e:
            check_is_non_zero(value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("index, min_value, max_value", [(x, 0, 10) for x in range(10)])
    def test_check_index(self, index, min_value, max_value, _, caplog):
        """
        Test check_index function.
        """
        check_index(index, min_value, max_value)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("index, min_value, max_value", [(x, 0, 10) for x in [-1, 11]])
    def test_check_index_invalid(self, index, min_value, max_value, _):
        """
        Test check_index function with invalid index.
        """
        with pytest.raises(IndexError) as e:
            check_index(index, min_value, max_value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "file_name, extensions",
        [
            ("test.txt", (".txt", ".csv")),
            ("test.txt", ".txt"),
            ("test\\test.png", (".txt", ".csv", ".png")),
        ],
    )
    def test_check_file_extension(self, file_name, extensions, _, caplog):
        """
        Test check_file_extension function.
        """
        check_file_extension(file_name, extensions)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize(
        "file_name, extensions", [("test.png", (".txt", ".csv")), ("test.txt", ".csv")]
    )
    def test_check_file_extension_invalid(self, file_name, extensions, _, caplog):
        """
        Test check_file_extension function with invalid file name.
        """
        check_file_extension(file_name, extensions)
        assert _("default") in caplog.text

    @pytest.mark.parametrize("value, expected_values", [(x, (1, 2, 3)) for x in tuple(range(1, 3))])
    def test_check_expected_values(self, value, expected_values, _, caplog):
        """
        Test check_expected_values function.
        """
        check_expected_values(value, expected_values)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("value, expected_values", [(x, (1, 2, 3)) for x in [0, 4, -1]])
    def test_check_expected_values_invalid(self, value, expected_values, _):
        """
        Test check_expected_values function with invalid value.
        """
        with pytest.raises(ValueError) as e:
            check_expected_values(value, expected_values)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("min_value, max_value", [(10, 15)])
    def test_check_min_max(self, min_value, max_value, _, caplog):
        """
        Test check_min_max function.
        """
        check_min_max(min_value, max_value)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize("min_value, max_value", [(15, 10)])
    def test_check_min_max_invalid(self, min_value, max_value, _):
        """
        Test check_min_max function with invalid min_value.
        """
        with pytest.raises(ValueError) as e:
            check_min_max(min_value, max_value)
        assert _("Invalid") in str(e.value)

    def test_mf_array_to_list(self):
        """
        Test _mf_array_to_list helper function.
        """
        # Create a mock array instance
        mock_array = Mock()
        mock_array.size = 3
        mock_array.val = Mock(side_effect=lambda i: i * 2)  # Return i * 2 for index i

        result = _mf_array_to_list(mock_array)

        assert result == [0, 2, 4]  # For indices 0, 1, 2 -> values 0, 2, 4
        assert mock_array.val.call_count == 3
        mock_array.val.assert_any_call(0)
        mock_array.val.assert_any_call(1)
        mock_array.val.assert_any_call(2)

    def test_mf_array_to_list_empty(self):
        """
        Test _mf_array_to_list helper function with empty array.
        """
        mock_array = Mock()
        mock_array.size = 0
        mock_array.val = Mock()

        result = _mf_array_to_list(mock_array)

        assert result == []
        mock_array.val.assert_not_called()

    @pytest.mark.parametrize(
        "value, types",
        [(None, (int, float))]
        + [(None, str)]
        + [(None, bool)]
        + [(x, (int, float)) for x in VALID_INT + VALID_FLOAT]
        + [(x, str) for x in VALID_STR]
        + [(x, bool) for x in VALID_BOOL],
    )
    def test_check_optional_type(self, value, types, _, caplog):
        """
        Test check_optional_type function with valid values including None.
        """
        check_optional_type(value, types)
        assert _("Valid") in caplog.text

    @pytest.mark.parametrize(
        "value, types",
        [(x, (int, float)) for x in list_intersection(INVALID_FLOAT, INVALID_INT) if x is not None]
        + [(x, int) for x in INVALID_INT if x is not None],
    )
    def test_check_optional_type_invalid(self, value, types, _):
        """
        Test check_optional_type function with invalid type (but not None).
        """
        with pytest.raises(TypeError) as e:
            check_optional_type(value, types)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("value", [None, 42, 3.14, "test"])
    def test_check_and_coerce_optional_primitives(self, value, _, caplog):
        """
        Test check_and_coerce_optional with primitive types.
        For primitives (int, float, str), the function should return the value as-is.
        """
        if value is None:
            result = check_and_coerce_optional(value, int)
            # For None, should return a VARIANT null dispatch
            assert result is not None  # Returns a VARIANT object
        elif isinstance(value, int):
            result = check_and_coerce_optional(value, int)
            assert result == value
            assert _("Valid") in caplog.text
        elif isinstance(value, float):
            result = check_and_coerce_optional(value, float)
            assert result == value
            assert _("Valid") in caplog.text
        elif isinstance(value, str):
            result = check_and_coerce_optional(value, str)
            assert result == value
            assert _("Valid") in caplog.text

    def test_check_and_coerce_optional_com_object(self, _):
        """
        Test check_and_coerce_optional with a mock COM object.
        For COM objects, the function should unwrap the internal attribute.
        """
        # Create a mock COM object that mimics EntList
        mock_ent_list = Mock()
        mock_ent_list.__class__.__name__ = 'EntList'
        mock_internal = Mock()
        mock_ent_list.ent_list = mock_internal

        # The function should validate the type and return the internal attribute
        result = check_and_coerce_optional(mock_ent_list, type(mock_ent_list))
        assert result == mock_internal

    def test_check_and_coerce_optional_none_com_object(self, _):
        """
        Test check_and_coerce_optional with None for a COM object type.
        Should return a VARIANT null dispatch.
        """
        mock_type = type('EntList', (), {})
        result = check_and_coerce_optional(None, mock_type)
        # Should return a VARIANT object, not None
        assert result is not None

    def test_check_and_coerce_optional_invalid_type(self, _):
        """
        Test check_and_coerce_optional with invalid type.
        """
        with pytest.raises(TypeError) as e:
            check_and_coerce_optional("string", int)
        assert _("Invalid") in str(e.value)
