# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    StringArray Class API Wrapper
"""

from .logger import process_log
from .helper import check_type, _mf_array_to_list
from .com_proxy import safe_com, flag_com_method
from .common import LogMessage


class StringArray:
    """
    Wrapper for StringArray class of Moldflow Synergy.
    """

    def __init__(self, _string_array):
        """
        Initialize the StringArray with a Synergy instance from COM.

        Args:
            _string_array: The StringArray instance from COM.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="StringArray")
        self.string_array = safe_com(_string_array)

        flag_com_method(self.string_array, "FromVBSArray")

    def val(self, index: int) -> str:
        """
        Get the value at the specified index.

        Args:
            index (int): The index of the value to get.

        Returns:
            str: The value at the specified index.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="val")
        check_type(index, int)
        return self.string_array.Val(index)

    def add_string(self, value: str) -> None:
        """
        Add a string value to the array.

        Args:
            value (str): The value to add.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_string")
        check_type(value, str)
        self.string_array.AddString(value)

    def to_list(self) -> list[str]:
        """
        Convert the string array to a list of strings.
        Returns:
            list[str]: The list of strings.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="to_list")
        return _mf_array_to_list(self)

    def from_list(self, values: list[str]) -> int:
        """
        Convert a list of strings to a string array.

        Args:
            values (list[str]): The list of strings to convert.
        
        Returns:
            int: The number of elements added to the array.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="from_list")
        check_type(values, (list, tuple))

        for value in values:
            check_type(value, str)

        return self.string_array.FromVBSArray(list(values))

    @property
    def size(self) -> int:
        """
        Get the size of the array.

        Returns:
            int: The size of the array.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.string_array.Size
