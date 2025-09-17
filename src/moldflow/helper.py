# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Helper functions for the Moldflow Wrapper Library.
"""

from enum import Enum
import os
from win32com.client import VARIANT
import pythoncom
from .errors import raise_type_error, raise_value_error, raise_index_error
from .common import ValueErrorReason, LogMessage
from .logger import process_log


def get_enum_value(value, enum: Enum):
    """
    Check if the value is part of the given enum class.
    If other_allowed is True, the function will return the value if it is in other_values.
    If other_allowed is True and other_values is None, the function will accept any value.

    Args:
        value: The value to check.
        enum (Enum): The enum class to check against.

    Returns:
        The value if it is part of the given enum class, otherwise the value.
    """
    enum_name = enum.__name__
    enum_elements = [element.value for element in enum]
    enum_value_type = type(enum_elements[0])
    process_log(__name__, LogMessage.HELPER_CHECK, locals(), value=value, name=enum_name)
    check_type(value, (enum, enum_value_type))

    if isinstance(value, enum):
        process_log(__name__, LogMessage.VALID_TYPE)
        return value.value

    if value in enum_elements:
        process_log(__name__, LogMessage.VALID_INPUT)
        return value

    process_log(__name__, LogMessage.VALUE_NOT_IN_ENUM, locals(), value=value, enum_name=enum_name)
    return value


def check_type(value, types: tuple):
    """
    Check if the value is of the specified type(s).

    Args:
        value: The value to check.
        types (tuple): A tuple of types to check against.

    Returns:
        bool: True if the value is of the specified type(s), otherwise raises a TypeError.

    Raises:
        TypeError: If the value is not of the specified type(s).

    Notes:
        - The function handles the special case where in python `bool` is a subclass of `int`.
        - If `types` is not a tuple, it is treated as a single type.
    """
    process_log(__name__, LogMessage.HELPER_CHECK, locals(), value=value, name=types)
    is_bool = isinstance(value, bool)

    if isinstance(types, tuple):
        bool_not_in_types = bool not in types
    else:
        bool_not_in_types = types != bool
    # The bool check is necessary because bool is a subclass of int: True = 1, False = 0
    if (is_bool and bool_not_in_types) or not isinstance(value, types):
        raise_type_error(value, types)
    process_log(__name__, LogMessage.VALID_INPUT)


def _compare(value1, value2, inclusive):
    """
    Compare two values

    Args:
        value1: The first value to compare.
        value2: The second value to compare.
        inclusive: Whether the comparison is inclusive.

    Returns:
        bool: True if the values are equal, otherwise False.
    """
    if value1 is None or value2 is None:
        return True
    if value2 > value1:
        return True
    return inclusive and value1 == value2


def check_range(
    value: float,
    min_value: float = None,
    max_value: float = None,
    min_inclusive: bool = False,
    max_inclusive: bool = False,
):
    """
    Check if the value is within the specified range.
    Args:
        value (float): The value to check.
        min_value (float, optional): The minimum value. Defaults to None.
        max_value (float, optional): The maximum value. Defaults to None.
        min_inclusive (bool, optional): Whether the minimum value is inclusive. (Default: False)
        max_inclusive (bool, optional): Whether the maximum value is inclusive. (Default: False)
    Returns:
        bool: True if the value is within the specified range, otherwise raises a ValueError.
    Raises:
        ValueError: If the value is not within the specified range.
    """
    if min_value is None and max_value is None:
        process_log(__name__, LogMessage.VALID_INPUT)
        return

    check_type(value, (int, float))
    if min_value is not None and max_value is not None:
        check_type(min_value, (int, float))
        check_type(max_value, (int, float))

    min_check = _compare(min_value, value, min_inclusive)
    max_check = _compare(value, max_value, max_inclusive)

    reason = None
    reason_format = None

    if min_value is not None and max_value is not None and (not min_check or not max_check):
        process_log(
            __name__,
            LogMessage.CHECK_RANGE,
            locals(),
            value=value,
            min_value=min_value,
            max_value=max_value,
        )
        reason = ValueErrorReason.NOT_IN_RANGE
        reason_format = {"value": value, "min_value": min_value, "max_value": max_value}
    elif min_value is not None and not min_check:
        process_log(__name__, LogMessage.CHECK_MIN, locals(), value=value, min_value=min_value)
        reason = ValueErrorReason.GREATER_THAN_OR_EQUAL
        reason_format = {"value": value, "min_value": min_value}
    elif max_value is not None and not max_check:
        process_log(__name__, LogMessage.CHECK_MAX, locals(), value=value, max_value=max_value)
        reason = ValueErrorReason.LESS_THAN_OR_EQUAL
        reason_format = {"value": value, "max_value": max_value}

    if reason and reason_format:
        raise_value_error(reason, **reason_format)
    process_log(__name__, LogMessage.VALID_INPUT)


def check_is_non_negative(value: float):
    """
    Check if the value is non-negative.
    Args:
        value (float): The value to check.
    Raises:
        ValueError: If the value is non-negative.
    """
    process_log(__name__, LogMessage.CHECK_NON_NEGATIVE, locals(), value=value)
    check_type(value, (int, float))
    if value < 0:
        raise_value_error(ValueErrorReason.NON_NEGATIVE, value=value)
    process_log(__name__, LogMessage.VALID_INPUT)


def check_is_positive(value: float):
    """
    Check if the value is posiive [0 not included].
    Args:
        value (float): The value to check.
    Raises:
        ValueError: If the value is negative.
    """
    process_log(__name__, LogMessage.CHECK_POSITIVE, locals(), value=value)
    check_type(value, (int, float))
    if value <= 0:
        raise_value_error(ValueErrorReason.POSITIVE, value=value)
    process_log(__name__, LogMessage.VALID_INPUT)


def check_is_negative(value: float):
    """
    Check if the value is negative.
    Args:
        value (float): The value to check.
    Raises:
        ValueError: If the value is positive.
    """
    process_log(__name__, LogMessage.CHECK_NEGATIVE, locals(), value=value)
    check_type(value, (int, float))
    if value >= 0:
        raise_value_error(ValueErrorReason.NEGATIVE, value=value)
    process_log(__name__, LogMessage.VALID_INPUT)


def check_is_non_zero(value: float):
    """
    Check if the value is non-zero.
    Args:
        value (float): The value to check.
    Raises:
        ValueError: If the value is zero.
    """
    process_log(__name__, LogMessage.CHECK_NON_ZERO, locals(), value=value)
    check_type(value, (int, float))
    if value == 0:
        raise_value_error(ValueErrorReason.NON_ZERO, value=value)
    process_log(__name__, LogMessage.VALID_INPUT)


def check_index(index: int, min_value: int, max_value: int):
    """
    Check if the index is within the specified range.
    Args:
        index (int): The index to check.
        min_value (int): The minimum index. (inclusive)
        max_value (int): The maximum index. (exclusive)
    Returns:
        bool: True if the index is within the specified range, otherwise raises an IndexError.
    Raises:
        IndexError: If the index is out of range.
    Note:
        - The minimum index is inclusive while the maximum index is exclusive.
    """
    process_log(__name__, LogMessage.CHECK_INDEX_IN_RANGE, locals(), index=index)
    if index < min_value or index >= max_value:
        raise_index_error()
    process_log(__name__, LogMessage.VALID_INPUT)


def check_file_extension(file_name: str, extensions: tuple | str):
    """
    Check if the file name has a valid extension.
    Args:
        file_name (str): The file name to check.
        extensions (list[str]): A list of valid file extensions.
    Raises:
        ValueError: If the file name does not have a valid extension.
    """
    process_log(__name__, LogMessage.CHECK_FILE_EXTENSION, locals(), file_name=file_name)
    check_type(file_name, str)
    check_type(extensions, (str, tuple))
    directory = os.path.dirname(file_name)
    if directory:
        os.makedirs(directory, exist_ok=True)
    default = extensions if isinstance(extensions, str) else extensions[0]
    if not file_name.endswith(extensions):
        process_log(
            __name__,
            LogMessage.INVALID_FILE_EXTENSION,
            locals(),
            file_name=file_name,
            default=default,
        )
        file_name = file_name + default
    return file_name


def check_expected_values(value, expected_values: tuple):
    """
    Check if the value is in the expected values.
    Args:
        value: The value to check.
        expected_values (tuple): The expected values.
    Raises:
        ValueError: If the value is not in the expected values.
    """
    process_log(__name__, LogMessage.CHECK_EXPECTED_VALUES, locals(), value=value)
    check_type(value, (int, float))
    check_type(expected_values, tuple)
    if value not in expected_values:
        raise_value_error(
            ValueErrorReason.INVALID_VALUE, value=value, expected_values=expected_values
        )


def check_min_max(min_value: float, max_value: float):
    """
    Check if the min_value is less than or equal to the max_value.
    Args:
        min_value (float): The minimum value.
        max_value (float): The maximum value.
    Raises:
        ValueError: If the min_value is greater than the max_value.
    """
    process_log(__name__, LogMessage.CHECK_MIN, locals(), min_value=min_value, value=max_value)
    check_type(min_value, (int, float))
    check_type(max_value, (int, float))
    if min_value > max_value:
        raise_value_error(
            ValueErrorReason.MIN_MORE_THAN_MAX, min_value=min_value, max_value=max_value
        )


def variant_null_idispatch():
    """Return a VARIANT representing a null IDispatch pointer (VT_DISPATCH, None)."""
    return VARIANT(pythoncom.VT_DISPATCH, None)


def coerce_optional_dispatch(value, attr_name: str | None = None):
    """
    Coerce an optional COM object argument declared as VTS_DISPATCH.

    - If value is None, return a null IDispatch VARIANT
    - If attr_name is provided, unwrap wrapper attribute (e.g., 'vector', 'ent_list', 'prop')
    - Otherwise return the value as-is

    Args:
        value: The value to coerce.
        attr_name (str | None): The attribute name to unwrap. Defaults to None.

    Returns:
        VARIANT: The coerced value.
    """
    if value is None:
        return variant_null_idispatch()
    if attr_name:
        value = getattr(value, attr_name)
    return value
