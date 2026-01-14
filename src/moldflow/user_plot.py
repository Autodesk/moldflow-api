# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    UserPlot Class API Wrapper
"""

from .helper import check_type, check_and_coerce_optional, get_enum_value
from .com_proxy import safe_com
from .logger import process_log
from .common import (
    LogMessage,
    ModulusPlotDirection,
    UserPlotType,
    BirefringenceResultType,
    DeflectionType,
    ClampForcePlotDirection,
)
from .integer_array import IntegerArray
from .double_array import DoubleArray
from .plot import Plot


class UserPlot:
    """
    Wrapper for UserPlot class of Moldflow Synergy.
    """

    def __init__(self, _user_plot):
        """
        Initialize the UserPlot with a UserPlot instance from COM.

        Args:
            _user_plot: The UserPlot instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="UserPlot")
        self.user_plot = safe_com(_user_plot)

    def set_dept_name(self, name: str) -> bool:
        """
        Set the name of the user plot.

        Args:
            name (str): The name of the user plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_dept_name")
        check_type(name, str)
        return self.user_plot.SetDeptName(name)

    def set_indp_name(self, name: str) -> bool:
        """
        Set independent name of the user plot.

        Args:
            name (str): The independent variable name of the user plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_indp_name")
        check_type(name, str)
        return self.user_plot.SetIndpName(name)

    def set_data_type(self, data_type: UserPlotType | str) -> bool:
        """
        Set the data type of the user plot.

        Args:
            data_type (UserPlotType | str): The data type of the user plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_data_type")
        data_type = get_enum_value(data_type, UserPlotType)
        return self.user_plot.SetDataType(data_type)

    def set_dept_unit_name(self, unit_name: str) -> bool:
        """
        Set the unit name of the user plot.

        Args:
            unit_name (str): The unit name of the user plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_dept_unit_name")
        check_type(unit_name, str)
        return self.user_plot.SetDeptUnitName(unit_name)

    def set_indp_unit_name(self, unit_name: str) -> bool:
        """
        Set the independent unit name of the user plot.

        Args:
            unit_name (str): The independent unit name of the user plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_indp_unit_name")
        check_type(unit_name, str)
        return self.user_plot.SetIndpUnitName(unit_name)

    def add_scalar_data(
        self, indp_val: float, element_id: IntegerArray | None, data: DoubleArray | None
    ) -> bool:
        """
        Add scalar data to the user plot.

        Args:
            indp_val (float): The independent variable value.
            element_id (IntegerArray | None): The element ID.
            data (DoubleArray | None): The data to be added.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_scalar_data")
        check_type(indp_val, (int, float))

        return self.user_plot.AddScalarData(
            indp_val,
            check_and_coerce_optional(element_id, IntegerArray),
            check_and_coerce_optional(data, DoubleArray),
        )

    # pylint: disable=R0913, R0917
    def add_vector_data(
        self,
        indp_val: float,
        element_id: IntegerArray | None,
        vx: DoubleArray | None,
        vy: DoubleArray | None,
        vz: DoubleArray | None,
    ) -> bool:
        """
        Add vector data to the user plot.

        Args:
            indp_val (float): The independent variable value.
            element_id (IntegerArray | None): The element ID.
            vx (DoubleArray | None): The x-component of the vector data.
            vy (DoubleArray | None): The y-component of the vector data.
            vz (DoubleArray | None): The z-component of the vector data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_vector_data")
        check_type(indp_val, (int, float))

        return self.user_plot.AddVectorData(
            indp_val,
            check_and_coerce_optional(element_id, IntegerArray),
            check_and_coerce_optional(vx, DoubleArray),
            check_and_coerce_optional(vy, DoubleArray),
            check_and_coerce_optional(vz, DoubleArray),
        )

    # pylint: disable=R0913, R0917
    def add_tensor_data(
        self,
        indp_val: float,
        element_id: IntegerArray | None,
        t_11: DoubleArray | None,
        t_22: DoubleArray | None,
        t_33: DoubleArray | None,
        t_12: DoubleArray | None,
        t_13: DoubleArray | None,
        t_23: DoubleArray | None,
    ) -> bool:
        """
        Add tensor data to the user plot.

        Args:
            indp_val (float): The independent variable value.
            element_id (IntegerArray | None): The element ID.
            t_11 (DoubleArray | None): The xx-component of the tensor data.
            t_22 (DoubleArray | None): The yy-component of the tensor data.
            t_33 (DoubleArray | None): The zz-component of the tensor data.
            t_12 (DoubleArray | None): The xy-component of the tensor data.
            t_13 (DoubleArray | None): The xz-component of the tensor data.
            t_23 (DoubleArray | None): The yz-component of the tensor data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_tensor_data")
        check_type(indp_val, (int, float))

        return self.user_plot.AddTensorData(
            indp_val,
            check_and_coerce_optional(element_id, IntegerArray),
            check_and_coerce_optional(t_11, DoubleArray),
            check_and_coerce_optional(t_22, DoubleArray),
            check_and_coerce_optional(t_33, DoubleArray),
            check_and_coerce_optional(t_12, DoubleArray),
            check_and_coerce_optional(t_13, DoubleArray),
            check_and_coerce_optional(t_23, DoubleArray),
        )

    def build(self) -> Plot:
        """
        Build the user plot.

        Returns:
            Plot: The built user plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="build")
        result = self.user_plot.Build
        if result is None:
            return None
        return Plot(result)

    def set_name(self, name: str) -> bool:
        """
        Set the name of the user plot.

        Args:
            name (str): The name of the user plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_name")
        check_type(name, str)
        return self.user_plot.SetName(name)

    def set_vector_as_displacement(self, is_displacement: bool) -> None:
        """
        Set the vector as displacement.

        Args:
            is_displacement (bool): True if the vector is a displacement, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_vector_as_displacement")
        check_type(is_displacement, bool)
        self.user_plot.SetVectorAsDisplacement(is_displacement)

    def set_scalar_data(self, element_id: IntegerArray | None, data: DoubleArray | None) -> bool:
        """
        Set scalar data for the user plot.

        Args:
            element_id (IntegerArray | None): The element ID.
            data (DoubleArray | None): The scalar data to be set.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_scalar_data")

        return self.user_plot.SetScalarData(
            check_and_coerce_optional(element_id, IntegerArray),
            check_and_coerce_optional(data, DoubleArray),
        )

    def set_vector_data(
        self,
        element_id: IntegerArray | None,
        vx: DoubleArray | None,
        vy: DoubleArray | None,
        vz: DoubleArray | None,
    ) -> bool:
        """
        Set vector data for the user plot.

        Args:
            element_id (IntegerArray | None): The element ID.
            vx (DoubleArray | None): The x-component of the vector data.
            vy (DoubleArray | None): The y-component of the vector data.
            vz (DoubleArray | None): The z-component of the vector data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_vector_data")

        return self.user_plot.SetVectorData(
            check_and_coerce_optional(element_id, IntegerArray),
            check_and_coerce_optional(vx, DoubleArray),
            check_and_coerce_optional(vy, DoubleArray),
            check_and_coerce_optional(vz, DoubleArray),
        )

    # pylint: disable=R0913, R0917
    def set_tensor_data(
        self,
        element_id: IntegerArray | None,
        t_11: DoubleArray | None,
        t_22: DoubleArray | None,
        t_33: DoubleArray | None,
        t_12: DoubleArray | None,
        t_13: DoubleArray | None,
        t_23: DoubleArray | None,
    ) -> bool:
        """
        Set tensor data for the user plot.

        Args:
            element_id (IntegerArray | None): The element ID.
            t_11 (DoubleArray | None): The xx-component of the tensor data.
            t_22 (DoubleArray | None): The yy-component of the tensor data.
            t_33 (DoubleArray | None): The zz-component of the tensor data.
            t_12 (DoubleArray | None): The xy-component of the tensor data.
            t_13 (DoubleArray | None): The xz-component of the tensor data.
            t_23 (DoubleArray | None): The yz-component of the tensor data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_tensor_data")

        return self.user_plot.SetTensorData(
            check_and_coerce_optional(element_id, IntegerArray),
            check_and_coerce_optional(t_11, DoubleArray),
            check_and_coerce_optional(t_22, DoubleArray),
            check_and_coerce_optional(t_33, DoubleArray),
            check_and_coerce_optional(t_12, DoubleArray),
            check_and_coerce_optional(t_13, DoubleArray),
            check_and_coerce_optional(t_23, DoubleArray),
        )

    def add_xy_plot_data(
        self, indp_val: float, x_value: DoubleArray | None, y_value: DoubleArray | None
    ) -> bool:
        """
        Add XY plot data to the user plot.

        Args:
            indp_val (float): The independent variable value.
            x_value (DoubleArray | None): The x-values of the data points.
            y_value (DoubleArray | None): The y-values of the data points.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_xy_plot_data")
        check_type(indp_val, (int, float))

        return self.user_plot.AddXYPlotData(
            indp_val,
            check_and_coerce_optional(x_value, DoubleArray),
            check_and_coerce_optional(y_value, DoubleArray),
        )

    def set_xy_plot_data(self, x_value: DoubleArray | None, y_value: DoubleArray | None) -> bool:
        """
        Set XY plot data for the user plot.

        Args:
            x_value (DoubleArray | None): The x-values of the data points.
            y_value (DoubleArray | None): The y-values of the data points.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_xy_plot_data")

        return self.user_plot.SetXYPlotData(
            check_and_coerce_optional(x_value, DoubleArray),
            check_and_coerce_optional(y_value, DoubleArray),
        )

    def set_xy_plot_x_unit_name(self, unit_name: str) -> bool:
        """
        Set the x-axis unit name for the XY plot.

        Args:
            unit_name (str): The x-axis unit name.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_xy_plot_x_unit_name")
        check_type(unit_name, str)
        return self.user_plot.SetXYPlotXUnitName(unit_name)

    def set_xy_plot_y_unit_name(self, unit_name: str) -> bool:
        """
        Set the y-axis unit name for the XY plot.

        Args:
            unit_name (str): The y-axis unit name.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_xy_plot_y_unit_name")
        check_type(unit_name, str)
        return self.user_plot.SetXYPlotYUnitName(unit_name)

    def set_xy_plot_x_title(self, title: str) -> bool:
        """
        Set the x-axis title for the XY plot.

        Args:
            title (str): The x-axis title.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_xy_plot_x_title")
        check_type(title, str)
        return self.user_plot.SetXYPlotXTitle(title)

    def set_highlight_data(self, values: DoubleArray | None) -> bool:
        """
        Set the highlight data for the user plot.

        Args:
            values (DoubleArray | None): The values to be highlighted.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_highlight_data")

        return self.user_plot.SetHighlightData(check_and_coerce_optional(values, DoubleArray))

    def build_weldline_plot(self, plot_name: str, max_angle: float, for_overmolding: bool) -> Plot:
        """
        Build a weldline plot.

        Args:
            plot_name (str): The name of the weldline plot.
            max_angle (float): The maximum angle for the weldline plot.
            for_overmolding (bool): True if the plot is for overmolding, False otherwise.

        Returns:
            Plot: The weldline plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="build_weldline_plot")
        check_type(plot_name, str)
        check_type(max_angle, (int, float))
        check_type(for_overmolding, bool)
        result = self.user_plot.BuildWeldlinePlot(plot_name, max_angle, for_overmolding)
        if result is None:
            return None
        return Plot(result)

    def build_clamp_force_plot(
        self,
        plot_name: str,
        direction: ClampForcePlotDirection | int,
        lcs: int,
        for_overmolding: bool,
    ) -> Plot:
        """
        Build a clamp force plot.

        Args:
            plot_name (str): The name of the clamp force plot.
            direction (ClampForcePlotDirection | int): The direction of the clamp force plot.
            lcs (int): The local coordinate system for the clamp force plot.
            For global, set value to 0 or -1
            for_overmolding (bool): True if the plot is for overmolding, False otherwise.

        Returns:
            Plot: The clamp force plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="build_clamp_force_plot")
        check_type(plot_name, str)
        direction = get_enum_value(direction, ClampForcePlotDirection)
        check_type(lcs, int)
        check_type(for_overmolding, bool)
        result = self.user_plot.BuildClampForcePlot(plot_name, direction, lcs, for_overmolding)
        if result is None:
            return None
        return Plot(result)

    # pylint: disable=R0913, R0917
    def build_birefringence_plot(
        self,
        plot_name: str,
        result_type: BirefringenceResultType | int,
        light_wave_length: float,
        light_dir_x: float,
        light_dir_y: float,
        light_dir_z: float,
    ) -> Plot:
        """
        Build a birefringence plot.

        Args:
            plot_name (str): The name of the birefringence plot.
            result_type (BirefringenceResultType | int): The type of birefringence result.
            light_wave_length (float): The wavelength of the light.
            light_dir_x (float): The x-component of the light direction.
            light_dir_y (float): The y-component of the light direction.
            light_dir_z (float): The z-component of the light direction.

        Returns:
            Plot: The birefringence plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="build_birefringence_plot")
        check_type(plot_name, str)
        result_type = get_enum_value(result_type, BirefringenceResultType)
        check_type(light_wave_length, (int, float))
        check_type(light_dir_x, (int, float))
        check_type(light_dir_y, (int, float))
        check_type(light_dir_z, (int, float))
        result = self.user_plot.BuildBirefringencePlot(
            plot_name, result_type, light_wave_length, light_dir_x, light_dir_y, light_dir_z
        )
        if result is None:
            return None
        return Plot(result)

    def build_modulus_plot(
        self, plot_name: str, direction: ModulusPlotDirection | int, lcs: int
    ) -> Plot:
        """
        Build a modulus plot.

        Args:
            plot_name (str): The name of the modulus plot.
            direction (ModulusPlotDirection | int): The direction of the modulus plot.
            lcs (int): The local coordinate system for the modulus plot.
            For global, set value to 0 or -1

        Returns:
            Plot: The modulus plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="build_modulus_plot")
        check_type(plot_name, str)
        direction = get_enum_value(direction, ModulusPlotDirection)
        check_type(lcs, int)
        result = self.user_plot.BuildModulusPlot(plot_name, direction, lcs)
        if result is None:
            return None
        return Plot(result)

    def build_deflection_plot(self, plot_name: str, def_type: str, params: str) -> Plot:
        """
        Build a deflection plot.
        Daniela, Megan, YoonChae, Manon, Lara, Sophia
        Args:
            plot_name (str): The name of the deflection plot.
            def_type (str): The type of the deflection plot.
            params (str): The parameters for the deflection plot.

        Returns:
            Plot: The deflection plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="build_deflection_plot")
        check_type(plot_name, str)
        def_type = get_enum_value(def_type, DeflectionType)
        check_type(params, str)
        result = self.user_plot.BuildDeflectionPlot(plot_name, def_type, params)
        if result is None:
            return None
        return Plot(result)
