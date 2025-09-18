# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Vector Class API Wrapper
"""

from .helper import check_type
from .com_proxy import safe_com
from .logger import process_log, LogMessage


class Vector:
    """
    Wrapper for Vector class of Moldflow Synergy.
    """

    def __init__(self, _vector):
        """
        Initialize the Vector with a Vector instance from COM.

        Args:
            _vector: The Vector instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Vector")
        self.vector = safe_com(_vector)

    def set_xyz(self, x: float | int, y: float | int, z: float | int) -> None:
        """
        Set the x, y, z components of the vector.

        Args:
            x (float | int): The x component.
            y (float | int): The y component.
            z (float | int): The z component.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_xyz")
        check_type(x, (float, int))
        check_type(y, (float, int))
        check_type(z, (float, int))
        self.vector.SetXYZ(x, y, z)

    @property
    def x(self) -> float:
        """
        The x component of the vector

        :getter: Get the x component of the vector.
        :setter: Set the x component of the vector.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="x")
        return self.vector.X

    @x.setter
    def x(self, value: float | int) -> None:
        """
        Set the x component of the vector.

        Args:
            value (float | int): The x component to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="x", value=value)
        check_type(value, (float, int))
        self.vector.X = value

    @property
    def y(self) -> float:
        """
        The y component of the vector

        :getter: Get the y component of the vector.
        :setter: Set the y component of the vector.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="y")
        return self.vector.Y

    @y.setter
    def y(self, value: float | int) -> None:
        """
        Set the y component of the vector.

        Args:
            value (float | int): The y component to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="y", value=value)
        check_type(value, (float, int))
        self.vector.Y = value

    @property
    def z(self) -> float:
        """
        The z component of the vector

        :getter: Get the z component of the vector.
        :setter: Set the z component of the vector.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="z")
        return self.vector.Z

    @z.setter
    def z(self, value: float | int) -> None:
        """
        Set the z component of the vector.

        Args:
            value (float | int): The z component to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="z", value=value)
        check_type(value, (float, int))
        self.vector.Z = value
