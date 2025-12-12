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

    def set_xyz(self, x: float, y: float, z: float) -> None:
        """
        Set the x, y, z values of the vector.

        Args:
            x (float): The x value.
            y (float): The y value.
            z (float): The z value.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_xyz")
        check_type(x, (int, float))
        check_type(y, (int, float))
        check_type(z, (int, float))
        self.vector.SetXYZ(x, y, z)

    @property
    def x(self) -> float:
        """
        Value of x in vector

        :getter: Get the value of x property.
        :setter: Set the value of x property.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="x")
        return self.vector.X

    @x.setter
    def x(self, value: float) -> None:
        """
        Set the x value of the vector.

        Args:
            value: The x value to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="x", value=value)
        check_type(value, (int, float))
        self.vector.X = value

    @property
    def y(self) -> float:
        """
        Value of y in vector

        :getter: Get the value of y property.
        :setter: Set the value of y property.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="y")
        return self.vector.Y

    @y.setter
    def y(self, value: float) -> None:
        """
        Set the y value of the vector.

        Args:
            value: The y value to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="y", value=value)
        check_type(value, (int, float))
        self.vector.Y = value

    @property
    def z(self) -> float:
        """
        Value of z in vector

        :getter: Get the value of z property.
        :setter: Set the value of z property.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="z")
        return self.vector.Z

    @z.setter
    def z(self, value: float) -> None:
        """
        Set the z value of the vector.

        Args:
            value: The z value to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="z", value=value)
        check_type(value, (int, float))
        self.vector.Z = value
