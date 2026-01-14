# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Custom exceptions and messages for Moldflow API."""

from typing import NoReturn
from .i18n import get_text
from .common import ValueErrorReason, ErrorMessage
from .exceptions import SaveError, SynergyError


def raise_type_error(variable, types: tuple | str) -> NoReturn:
    """
    Raise a TypeError if the variable is not an instance of the specified type(s).

    Args:
        variable: The variable to check.
        types (tuple): A tuple of acceptable types.
        variable_name (str): The name of the variable.

    Raises:
        TypeError: If the variable is not an instance of the specified type(s).
    """
    _ = get_text()
    if isinstance(types, tuple):
        expected_types = " or ".join(type.__name__ for type in types)
    else:
        expected_types = types.__name__
    variable_type = type(variable).__name__
    err_msg = ErrorMessage.TYPE_ERROR.value
    localised_err_msg = _(err_msg).format(
        expected_types=expected_types, variable_type=variable_type
    )
    raise TypeError(localised_err_msg)


def raise_value_error(reason: ValueErrorReason | str, **kwargs) -> NoReturn:
    """
    Raise a ValueError with a custom error message.

    Args:
        reason (str): The reason for the ValueError.
        **kwargs: Additional keyword arguments to format the reason string.

    Raises:
        ValueError: With a localized custom error message.
    """
    _ = get_text()
    if isinstance(reason, ValueErrorReason):
        reason = reason.value
    localised_reason = _(reason).format(**kwargs)
    err_msg = ErrorMessage.VALUE_ERROR.value
    localised_err_msg = _(err_msg).format(reason=localised_reason)
    raise ValueError(localised_err_msg)


def raise_index_error() -> NoReturn:
    """
    Raise an IndexError if the index is out of range.

    Raises:
        IndexError: If the index is out of range.
    """
    _ = get_text()
    err_msg = ErrorMessage.INDEX_ERROR.value
    raise IndexError(_(err_msg))


def raise_save_error(saving: str, file_name: str) -> NoReturn:
    """
    Raise a SaveError if the save operation fails.

    Args:
        saving (str): The operation that failed.
        file_name (str): The name of the file that could not be saved.

    Raises:
        SaveError: If the save operation fails.
    """
    _ = get_text()
    err_msg = ErrorMessage.SAVE_ERROR.value
    localised_err_msg = _(err_msg).format(saving=saving, file_name=file_name)
    raise SaveError(localised_err_msg)


def raise_attribute_error(attribute: str) -> NoReturn:
    """Raise an AttributeError with a localised custom error message.

    Args:
        attribute (str): The attribute or method name that is missing.
    """
    _ = get_text()
    err_msg = ErrorMessage.ATTRIBUTE_ERROR.value
    localised_err_msg = _(err_msg).format(attribute=attribute)
    raise AttributeError(localised_err_msg)


def raise_synergy_error() -> NoReturn:
    """
    Raise a SynergyError with a localised custom error message.
    """
    _ = get_text()
    err_msg = ErrorMessage.SYNERGY_ERROR.value
    localised_err_msg = _(err_msg)
    raise SynergyError(localised_err_msg)
