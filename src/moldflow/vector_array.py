# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    VectorArray Class API Wrapper
"""

from .helper import check_type, check_index
from .com_proxy import safe_com
from .logger import process_log, LogMessage


class VectorArray:
    """
    Wrapper for VectorArray class of Moldflow Synergy.
    """

    def __init__(self, _vector_array):
        """
        Initialize the VectorArray with a VectorArray instance from COM.

        Args:
            _vector_array: The VectorArray instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="VectorArray")
        self.vector_array = safe_com(_vector_array)

    def clear(self) -> None:
        """
        Clear the vector array.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="clear")
        self.vector_array.Clear()

    def add_xyz(self, x: float, y: float, z: float) -> None:
        """
        Add a vector to the array with x, y, z values.

        Args:
            x (float): The x value.
            y (float): The y value.
            z (float): The z value.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_xyz")
        check_type(x, (float, int))
        check_type(y, (float, int))
        check_type(z, (float, int))
        self.vector_array.AddXYZ(x, y, z)

    @property
    def size(self) -> int:
        """
        Get the size of the vector array.

        Returns:
            int: The size of the vector array.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.vector_array.Size

    def x(self, index: int) -> float:
        """
        Get the x value of the vector at the index.

        Args:
            index (int): The index of the vector.

        Returns:
            float: The x value of the vector.
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="x", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        return self.vector_array.X(index)

    def y(self, index: int) -> float:
        """
        Get the y value of the vector at the index.

        Args:
            index (int): The index of the vector.

        Returns:
            float: The y value of the vector.
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="y", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        return self.vector_array.Y(index)

    def z(self, index: int) -> float:
        """
        Get the z value of the vector at the index.

        Args:
            index (int): The index of the vector.

        Returns:
            float: The z value of the vector.
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="z", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        return self.vector_array.Z(index)
