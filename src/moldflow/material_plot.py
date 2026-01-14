# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    MaterialPlot Class API Wrapper
"""

from .helper import check_type
from .com_proxy import safe_com
from .logger import process_log
from .common import LogMessage


class MaterialPlot:
    """
    Wrapper for MaterialPlot class of Moldflow Synergy.
    """

    def __init__(self, _material_plot):
        """
        Initialize the MaterialPlot with a MaterialPlot instance from COM.

        Args:
            _material_plot: The MaterialPlot instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="MaterialPlot")
        self.material_plot = safe_com(_material_plot)

    def save_image(self, filename: str) -> None:
        """
        Save the image of the material plot to a file.

        Args:
            filename (str): The filename to save the image to.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_image")
        check_type(filename, str)
        self.material_plot.SaveImage(filename)

    def save_data(self, filename: str) -> None:
        """
        Save the data of the material plot to a file.

        Args:
            filename (str): The filename to save the data to.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_data")
        check_type(filename, str)
        self.material_plot.SaveData(filename)

    @property
    def default_value_range_x(self) -> bool:
        """
        The default X axis value range.

        :getter: Gets if default X axis value range is enabled.
        :setter: Sets default X axis value range enable/disable.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="default_value_range_x")
        return self.material_plot.DefaultValueRangeX

    @default_value_range_x.setter
    def default_value_range_x(self, value: bool) -> None:
        """
        The default X axis value range.

        Args:
            value (bool): True to enable, False to disable.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="default_value_range_x", value=value
        )
        check_type(value, bool)
        self.material_plot.DefaultValueRangeX = value

    @property
    def default_value_range_y(self) -> bool:
        """
        The default Y axis value range.

        :getter: Gets if default y axis value range is enabled.
        :setter: Sets default y axis value range enable/disable.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="default_value_range_y")
        return self.material_plot.DefaultValueRangeY

    @default_value_range_y.setter
    def default_value_range_y(self, value: bool) -> None:
        """
        The default Y axis value range.

        Args:
            value (bool): True to enable, False to disable.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="default_value_range_y", value=value
        )
        check_type(value, bool)
        self.material_plot.DefaultValueRangeY = value

    @property
    def value_range_min_x(self) -> float:
        """
        The minimum X axis value.

        :getter: Get the minimum value for the X axis.
        :setter: Set the minimum value for the X axis.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="value_range_min_x")
        return self.material_plot.ValueRangeMinX

    @value_range_min_x.setter
    def value_range_min_x(self, value: float) -> None:
        """
        The minimum X axis value.

        Args:
            value (float): The minimum value for the X axis.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="value_range_min_x", value=value
        )
        check_type(value, (int, float))
        self.material_plot.ValueRangeMinX = value

    @property
    def value_range_max_x(self) -> float:
        """
        The maximum X axis value.

        :getter: Get the maximum value for the X axis.
        :setter: Set the maximum value for the X axis.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="value_range_max_x")
        return self.material_plot.ValueRangeMaxX

    @value_range_max_x.setter
    def value_range_max_x(self, value: float) -> None:
        """
        The maximum X axis value.

        Args:
            value (float): The maximum value for the X axis.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="value_range_max_x", value=value
        )
        check_type(value, (int, float))
        self.material_plot.ValueRangeMaxX = value

    @property
    def value_range_min_y(self) -> float:
        """
        The minimum Y axis value.

        :getter: Get the minimum value for the Y axis.
        :setter: Set the minimum value for the Y axis.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="value_range_min_y")
        return self.material_plot.ValueRangeMinY

    @value_range_min_y.setter
    def value_range_min_y(self, value: float) -> None:
        """
        The minimum Y axis value.

        Args:
            value (float): The minimum value for the Y axis.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="value_range_min_y", value=value
        )
        check_type(value, (int, float))
        self.material_plot.ValueRangeMinY = value

    @property
    def value_range_max_y(self) -> float:
        """
        The maximum Y axis value.

        :getter: Get the maximum value for the Y axis.
        :setter: Set the maximum value for the Y axis.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="value_range_max_y")
        return self.material_plot.ValueRangeMaxY

    @value_range_max_y.setter
    def value_range_max_y(self, value: float) -> None:
        """
        The maximum Y axis value.

        Args:
            value (float): The maximum value for the Y axis.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="value_range_max_y", value=value
        )
        check_type(value, (int, float))
        self.material_plot.ValueRangeMaxY = value
