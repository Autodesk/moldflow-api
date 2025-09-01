# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    DoubleArray Class API Wrapper
"""

from .logger import process_log
from .helper import check_type
from .com_proxy import flag_com_method, safe_com
from .common import LogMessage


class DoubleArray:
    """
    Wrapper for DoubleArray class of Moldflow Synergy.
    """

    def __init__(self, _double_array):
        """
        Initialize the DoubleArray with a DoubleArray instance from COM.

        Args:
            _double_array: The DoubleArray instance from COM.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="DoubleArray")
        self.double_array = safe_com(_double_array)

        flag_com_method(self.double_array, "ToVBSArray")
        flag_com_method(self.double_array, "FromVBSArray")

    def val(self, index: int) -> float:
        """
        Get the value at the specified index.

        Args:
            index (int): The index of the value to get.

        Returns:
            float: The value at the specified index.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="val")
        check_type(index, int)
        return self.double_array.Val(index)

    def add_double(self, value: float) -> None:
        """
        Add a double value to the array.

        Args:
            value (float): The value to add.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_double")
        check_type(value, (int, float))
        self.double_array.AddDouble(value)

    def to_list(self) -> list[float]:
        """
        Convert the double array to a list of floats.

        Returns:
            list[float]: The list of floats.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="to_list")

        vb_array = self.double_array.ToVBSArray()
        return list(vb_array)

    def from_list(self, values: list[float]) -> None:
        """
        Convert a list of floats to a double array.

        Args:
            values (list[float]): The list of floats to convert.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="from_list")

        check_type(values, (list, tuple))
        for value in values:
            check_type(value, (int, float))

        self.double_array.FromVBSArray(list(values))

    @property
    def size(self) -> int:
        """
        Get the size of the array.

        Returns:
            int: The size of the array.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.double_array.Size
