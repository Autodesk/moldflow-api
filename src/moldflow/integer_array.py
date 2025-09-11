# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    IntegerArray Class API Wrapper
"""

from .logger import process_log
from .helper import check_type
from .com_proxy import safe_com, flag_com_method
from .common import LogMessage


class IntegerArray:
    """
    Wrapper for IntegerArray class of Moldflow Synergy.
    """

    def __init__(self, _integer_array):
        """
        Initialize the IntegerArray with a IntegerArray instance from COM.

        Args:
            _integer_array: The IntegerArray instance from COM.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="IntegerArray")
        self.integer_array = safe_com(_integer_array)

        flag_com_method(self.integer_array, "ToVBSArray")
        flag_com_method(self.integer_array, "FromVBSArray")

    def val(self, index: int) -> int:
        """
        Get the value at the specified index.

        Args:
            index (int): The index of the value to get.

        Returns:
            int: The value at the specified index.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="val")
        check_type(index, int)
        return self.integer_array.Val(index)

    def add_integer(self, value: int) -> None:
        """
        Add a integer value to the array.

        Args:
            value (int): The value to add.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_integer")
        check_type(value, int)
        self.integer_array.AddInteger(value)

    def to_list(self) -> list[int]:
        """
        Convert the integer array to a list of integers.

        Returns:
            list[int]: The list of integers.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="to_list")

        vb_array = self.integer_array.ToVBSArray()
        return list(vb_array)

    def from_list(self, values: list[int]) -> int:
        """
        Convert a list of integers to an integer array.

        Args:
            values (list[int]): The list of integers to convert.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="from_list")

        check_type(values, (list, tuple))
        for value in values:
            check_type(value, int)

        return self.integer_array.FromVBSArray(list(values))

    @property
    def size(self) -> int:
        """
        Get the size of the array.

        Returns:
            int: The size of the array.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.integer_array.Size
