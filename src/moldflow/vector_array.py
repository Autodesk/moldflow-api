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
        Resets a vector array - the size of the array is 0 subsequent to this call.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="clear")
        self.vector_array.Clear()

    def add_xyz(self, x: float | int, y: float | int, z: float | int) -> None:
        """
        Adds a vector (x, y, z) to the end of the array.

        Args:
            x [float | int]: The x component.
            y [float | int]: The y component.
            z [float | int]: The z component.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_xyz")
        check_type(x, (float, int))
        check_type(y, (float, int))
        check_type(z, (float, int))
        self.vector_array.AddXYZ(x, y, z)

    @property
    def size(self) -> int:
        """
        Returns the number of vectors in the array. [read-only]

        Returns:
            The size of the vector array.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.vector_array.Size

    def x(self, index: int) -> float:
        """
        Get the x component of the vector at the index.

        Args:
            index [int]: index between 0 and vector_array.size-1 (inclusive)

        Returns:
            The x component of the vector at offset index.
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="x", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        return self.vector_array.X(index)

    def y(self, index: int) -> float:
        """
        Get the y component of the vector at the index.

        Args:
            index [int]: index between 0 and vector_array.size-1 (inclusive)

        Returns:
            The y component of the vector at offset index.
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="y", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        return self.vector_array.Y(index)

    def z(self, index: int) -> float:
        """
        Get the z component of the vector at the index.

        Args:
            index [int]: index between 0 and vector_array.size-1 (inclusive)

        Returns:
            The z component of the vector at offset index.
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="z", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        return self.vector_array.Z(index)
