# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    CircuitGenerator Class API Wrapper
"""

from .logger import process_log, LogMessage
from .helper import check_type
from .com_proxy import safe_com


class CircuitGenerator:
    """
    Wrapper for CircuitGenerator class of Moldflow Synergy.
    """

    def __init__(self, _circuit_generator):
        """
        Initialize the CircuitGenerator with a CircuitGenerator instance from COM.

        Args:
            _circuit_generator: The CircuitGenerator instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="CircuitGenerator")
        self.circuit_generator = safe_com(_circuit_generator)

    def generate(self):
        """
        Automatically generates a coolant circuit.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="generate")
        return self.circuit_generator.Generate

    @property
    def diameter(self) -> float:
        """
        The cooling channel diameter.

        :getter: Get the cooling channel diameter.
        :setter: Set the cooling channel diameter.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="diameter")
        return self.circuit_generator.Diameter

    @diameter.setter
    def diameter(self, value: float) -> None:
        """
        The cooling channel diameter.

        Args:
            value: The cooling channel diameter.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="diameter", value=value)
        check_type(value, (float, int))
        self.circuit_generator.Diameter = value

    @property
    def distance(self) -> float:
        """
        The clearance for the cooling channels from the model.

        :getter: Get the clearance for the cooling channels from the model.
        :setter: Set the clearance for the cooling channels from the model.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="distance")
        return self.circuit_generator.Distance

    @distance.setter
    def distance(self, value: float) -> None:
        """
        The clearance for the cooling channels from the model.

        Args:
            value: The clearance for the cooling channels from the model.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="distance", value=value)
        check_type(value, (float, int))
        self.circuit_generator.Distance = value

    @property
    def spacing(self) -> float:
        """
        The Spacing between cooling channels.

        :getter: Get the spacing between cooling channels.
        :setter: Set the spacing between cooling channels.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="spacing")
        return self.circuit_generator.Spacing

    @spacing.setter
    def spacing(self, value: float) -> None:
        """
        The Spacing between cooling channels.

        Args:
            value: The spacing between cooling channels.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="spacing", value=value)
        check_type(value, (float, int))
        self.circuit_generator.Spacing = value

    @property
    def overhang(self) -> float:
        """
        The distance to extend beyond the part.

        :getter: Get the distance to extend beyond the part.
        :setter: Set the distance to extend beyond the part.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="overhang")
        return self.circuit_generator.Overhang

    @overhang.setter
    def overhang(self, value: float) -> None:
        """
        The distance to extend beyond the part.

        Args:
            value: The distance to extend beyond the part.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="overhang", value=value)
        check_type(value, (float, int))
        self.circuit_generator.Overhang = value

    @property
    def num_channels(self) -> int:
        """
        The Number of channels.

        :getter: Get the number of channels.
        :setter: Set the number of channels.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="num_channels")
        return self.circuit_generator.NumChannels

    @num_channels.setter
    def num_channels(self, value: int) -> None:
        """
        The Number of channels.

        Args:
            value: The number of channels.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="num_channels", value=value)
        check_type(value, int)
        self.circuit_generator.NumChannels = value

    @property
    def delete_old(self) -> bool:
        """
        Specifies whether the old layout will be deleted before generating the new one.

        :getter: Get the delete_old flag.
        :setter: Set the delete_old flag.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="delete_old")
        return self.circuit_generator.DeleteOld

    @delete_old.setter
    def delete_old(self, value: bool) -> None:
        """
        Specifies whether the old layout will be deleted before generating the new one.

        Args:
            value: The delete_old flag.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="delete_old", value=value)
        check_type(value, bool)
        self.circuit_generator.DeleteOld = value

    @property
    def use_hoses(self) -> bool:
        """
        Specifies whether hoses need to be used to connect channels.

        :getter: Get the use_hoses flag.
        :setter: Set the use_hoses flag.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_hoses")
        return self.circuit_generator.UseHoses

    @use_hoses.setter
    def use_hoses(self, value: bool) -> None:
        """
        Specifies whether hoses need to be used to connect channels.

        Args:
            value: The use_hoses flag.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="use_hoses", value=value)
        check_type(value, bool)
        self.circuit_generator.UseHoses = value

    @property
    def x_align(self) -> bool:
        """
        Specifies whether the channels are aligned along the X-axis or Y-axis.
            [True] - X-axis alignment
            [False] - Y-axis alignment

        :getter: Get the x_align flag.
        :setter: Set the x_align flag.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="x_align")
        return self.circuit_generator.XAlign

    @x_align.setter
    def x_align(self, value: bool) -> None:
        """
        Specifies whether the channels are aligned along the X-axis or Y-axis.
            [True] - X-axis alignment
            [False] - Y-axis alignment

        Args:
            value: The x_align flag.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="x_align", value=value)
        check_type(value, bool)
        self.circuit_generator.XAlign = value
