# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Usage:
    Plot Class API Wrapper
"""

from .com_proxy import safe_com
from .logger import process_log, LogMessage
from .helper import (
    check_type,
    check_optional_type,
    get_enum_value,
    check_range,
    check_is_non_negative,
    check_expected_values,
    check_file_extension,
    coerce_optional_dispatch,
)
from .common import (
    DisplayComponent,
    ScaleOptions,
    PlotMethod,
    AnimationType,
    ColorTableIDs,
    EdgeDisplayOptions,
    DeflectionScaleDirections,
    SliceAtProbeOptions,
    TensorAxisRatioOptions,
    ShrinkageCompensationOptions,
    TraceModes,
    TraceStyles,
    ScaleTypes,
    ColorScaleOptions,
    SystemUnits,
)
from .constants import (
    COLOR_BAND_RANGE,
    TXT_FILE_EXT,
    XML_FILE_EXT,
    UDM_FILE_EXT,
    ELE_FILE_EXT,
    STL_FILE_EXT,
    FBX_FILE_EXT,
    CAD_FILE_EXT,
)
from .double_array import DoubleArray
from .vector import Vector
from .ent_list import EntList
from .errors import raise_save_error


class Plot:
    """
    Wrapper for Plot class of Moldflow Synergy.
    """

    def __init__(self, _plot):
        """
        Initialize the Plot with a Plot instance from COM.

        Args:
            _plot: The Plot instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Plot")
        self.plot = safe_com(_plot)

    def regenerate(self) -> None:
        """
        Rebuilds the plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="regenerate")
        self.plot.Regenerate()

    @property
    def number_of_frames(self) -> int:
        """
        The number of frames.

        :getter: Get the number of frames.
        :setter: Set the number of frames.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="number_of_frames")
        return self.plot.GetNumberOfFrames

    @number_of_frames.setter
    def number_of_frames(self, value: int) -> None:
        """
        The number of frames.

        Args:
            value (int): Number of frames to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="number_of_frames", value=value
        )
        check_type(value, int)
        self.plot.SetNumberOfFrames(value)

    @property
    def name(self) -> str:
        """
        The name of the plot.

        :getter: Get the name of the plot.
        :setter: Set the name of the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="name")
        return self.plot.GetName

    @name.setter
    def name(self, value: str) -> None:
        """
        The name of the plot.

        Args:
            value (str): Name to set for the plot.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="name", value=value)
        check_type(value, str)
        self.plot.SetName(value)

    @property
    def number_of_contours(self) -> int:
        """
        The number of contours.

        :getter: Get the number of contours.
        :setter: Set the number of contours.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="number_of_contours")
        return self.plot.GetNumberOfContours

    @number_of_contours.setter
    def number_of_contours(self, value: int) -> None:
        """
        The number of contours.

        Args:
            value (int): Number of contours to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="number_of_contours", value=value
        )
        check_type(value, int)
        self.plot.SetNumberOfContours(value)

    @property
    def component(self) -> int:
        """
        The displayed data component.

        :getter: Get the displayed data component.
        :setter: Set the displayed data component.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="component")
        return self.plot.GetComponent

    @component.setter
    def component(self, value: DisplayComponent | int) -> None:
        """
        The displayed data component.

        Args:
            value (int): displayed data component to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="component", value=value)
        value = get_enum_value(value, DisplayComponent)
        self.plot.SetComponent(value)

    @property
    def mesh_fill(self) -> float:
        """
        The mesh fill.

        :getter: Get the mesh fill.
        :setter: Set the mesh fill.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_fill")
        return self.plot.GetMeshFill

    @mesh_fill.setter
    def mesh_fill(self, value: float) -> None:
        """
        The mesh fill.

        Args:
            value (float): mesh fill to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mesh_fill", value=value)
        check_type(value, (float, int))
        check_range(value, 0, 1, True, True)
        self.plot.SetMeshFill(value)

    @property
    def nodal_averaging(self) -> bool:
        """
        The nodal averaging.

        :getter: Get the nodal averaging.
        :setter: Set the nodal averaging.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="nodal_averaging")
        return self.plot.GetNodalAveraging

    @nodal_averaging.setter
    def nodal_averaging(self, value: bool) -> None:
        """
        The nodal averaging.

        Args:
            value (bool): nodal averaging to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="nodal_averaging", value=value
        )
        check_type(value, bool)
        self.plot.SetNodalAveraging(value)

    @property
    def smooth_shading(self) -> bool:
        """
        The smooth shading.

        :getter: Get the smooth shading.
        :setter: Set the smooth shading.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="smooth_shading")
        return self.plot.GetSmoothShading

    @smooth_shading.setter
    def smooth_shading(self, value: bool) -> None:
        """
        The smooth shading.

        Args:
            value (bool): smooth shading to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="smooth_shading", value=value)
        check_type(value, bool)
        self.plot.SetSmoothShading(value)

    @property
    def color_scale(self) -> bool:
        """
        The color scale.
            [True if the color scale is blue-to-red, False if vice-versa]

        :getter: Get the color scale.
        :setter: Set the color scale.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="color_scale")
        return self.plot.GetColorScale

    @color_scale.setter
    def color_scale(self, value: ColorScaleOptions | bool) -> None:
        """
        The color scale.

        Args:
            value (ColorScaleOptions | bool): color scale to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="color_scale", value=value)
        value = get_enum_value(value, ColorScaleOptions)
        self.plot.SetColorScale(value)

    @property
    def capping(self) -> bool:
        """
        The capping.
        [True if the part of model behind active cutting planes is shown,
        in addition to the clipping plane]

        :getter: Get the capping.
        :setter: Set the capping.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="capping")
        return self.plot.GetCapping

    @capping.setter
    def capping(self, value: bool) -> None:
        """
        The capping.
        [True if the part of model behind active cutting planes is shown,
        in addition to the clipping plane]

        Args:
            value (bool): capping to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="capping", value=value)
        check_type(value, bool)
        self.plot.SetCapping(value)

    @property
    def scale_option(self) -> int:
        """
        The Scale Option.

        :getter: Get the Scale Option.
        :setter: Set the Scale Option.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="scale_option")
        return self.plot.GetScaleOption

    @scale_option.setter
    def scale_option(self, value: ScaleOptions | int) -> None:
        """
        The Scale Option.

        Args:
            value (ScaleOption | int): Scale Option to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="scale_option", value=value)
        value = get_enum_value(value, ScaleOptions)
        self.plot.SetScaleOption(value)

    @property
    def plot_method(self) -> int:
        """
        The Plot Method.

        :getter: Get the Plot Method.
        :setter: Set the Plot Method.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="plot_method")
        return self.plot.GetPlotMethod

    @plot_method.setter
    def plot_method(self, value: PlotMethod | int) -> None:
        """
        The Plot Method.

        Args:
            value (PlotMethod | int): Plot Method to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="plot_method", value=value)
        value = get_enum_value(value, PlotMethod)
        self.plot.SetPlotMethod(value)

    @property
    def animation_type(self) -> int:
        """
        The Animation Type.

        :getter: Get the Animation Type.
        :setter: Set the Animation Type.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="animation_type")
        return self.plot.GetAnimationType

    @animation_type.setter
    def animation_type(self, value: AnimationType | int) -> None:
        """
        The Animation Type.

        Args:
            value (AnimationType | int): Animation Type to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="animation_type", value=value)
        value = get_enum_value(value, AnimationType)
        self.plot.SetAnimationType(value)

    @property
    def number_of_indp_vars(self) -> int:
        """
        The Number of Independent Variables.

        :getter: Get the Number of Independent Variables.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="number_of_indp_vars")
        return self.plot.GetNumberOfIndpVars

    @property
    def active_indp_var(self) -> int:
        """
        The Active Independent Variable.

        :getter: Get the Active Independent Variable.
        :setter: Set the Active Independent Variable.
            [If the provided number exceeds the number of independent variables, it is capped
            to the number of independent variables.]
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="active_indp_var")
        return self.plot.GetActiveIndpVar

    @active_indp_var.setter
    def active_indp_var(self, value: int) -> None:
        """
        The Active Independent Variable.

        Args:
            value (int): Active Independent Variable to set.
            [If the provided number exceeds the number of independent variables, it is capped
            to the number of independent variables.]
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="active_indp_var", value=value
        )
        check_type(value, int)
        value = min(value, self.number_of_indp_vars)
        self.plot.SetActiveIndpVar(value)

    def set_fixed_indp_var_value(self, index: int, value: float) -> None:
        """
        Set the fixed independent variable value.

        Args:
            index (int): Index of the independent variable.
            value (float): Value to set.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_fixed_indp_var_value")
        check_type(index, int)
        check_is_non_negative(index)
        check_type(value, (float, int))
        self.plot.SetFixedIndpVarValue(index, value)

    @property
    def extended_color(self) -> bool:
        """
        The Extended Coloring Option.

        :getter: Get the Extended Coloring Option.
        :setter: Set the Extended Coloring Option.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="extended_color")
        return self.plot.GetExtendedColor

    @extended_color.setter
    def extended_color(self, value: bool) -> None:
        """
        The Extended Coloring Option.

        Args:
            value (bool): Extended Coloring Option to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="extended_color", value=value)
        check_type(value, bool)
        self.plot.SetExtendedColor(value)

    @property
    def color_bands(self) -> int:
        """
        The number of color bands.
            - values between 1 through 256: banded coloring with this number of colors

        :getter: Get the number of color bands.
        :setter: Set the number of color bands.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="color_bands")
        return self.plot.GetColorBands

    @color_bands.setter
    def color_bands(self, value: int) -> None:
        """
        The number of color bands.
            - values between 1 through 256: banded coloring with this number of colors

        Args:
            value (int): number of color bands or smooth coloring to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="color_bands", value=value)
        check_type(value, int)
        check_expected_values(value, COLOR_BAND_RANGE)
        self.plot.SetColorBands(value)

    @property
    def color_table_id(self) -> int:
        """
        The Color Table ID.

        :getter: Get the Color Table ID.
        :setter: Set the Color Table ID.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="color_table_id")
        return self.plot.GetColorTableId

    @color_table_id.setter
    def color_table_id(self, value: ColorTableIDs | int) -> None:
        """
        The Color Table ID.

        Args:
            value (ColorTableIDs | int): Color Table ID to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="color_table_id", value=value)
        value = get_enum_value(value, ColorTableIDs)
        self.plot.SetColorTableId(value)

    @property
    def xy_plot_show_legend(self) -> bool:
        """
        The XY Plot Show Legend.

        :getter: Get the XY Plot Show Legend.
        :setter: Set the XY Plot Show Legend.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_show_legend")
        return self.plot.GetXYPlotShowLegend

    @xy_plot_show_legend.setter
    def xy_plot_show_legend(self, value: bool) -> None:
        """
        The XY Plot Show Legend.

        Args:
            value (bool): XY Plot Show Legend to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_show_legend", value=value
        )
        check_type(value, bool)
        self.plot.SetXYPlotShowLegend(value)

    @property
    def xy_plot_show_points(self) -> bool:
        """
        The XY Plot Show Points.

        :getter: Get the XY Plot Show Points.
        :setter: Set the XY Plot Show Points.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_show_points")
        return self.plot.GetXYPlotShowPoints

    @xy_plot_show_points.setter
    def xy_plot_show_points(self, value: bool) -> None:
        """
        The XY Plot Show Points.

        Args:
            value (bool): XY Plot Show Points to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_show_points", value=value
        )
        check_type(value, bool)
        self.plot.SetXYPlotShowPoints(value)

    @property
    def xy_plot_overlay_with_mesh(self) -> bool:
        """
        The XY Plot Overlay With Mesh.

        :getter: Get the XY Plot Overlay With Mesh in the plot.
        :setter: Set the XY Plot Overlay With Mesh in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_overlay_with_mesh")
        return self.plot.GetXYPlotOverlayWithMesh

    @xy_plot_overlay_with_mesh.setter
    def xy_plot_overlay_with_mesh(self, value: bool) -> None:
        """
        The XY Plot Overlay With Mesh.

        Args:
            value (bool): XY Plot Overlay With Mesh to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="xy_plot_overlay_with_mesh",
            value=value,
        )
        check_type(value, bool)
        self.plot.SetXYPlotOverlayWithMesh(value)

    @property
    def xy_plot_max_number_of_curves(self) -> int:
        """
        The XY Plot Max Number of Curves.

        :getter: Get the XY Plot Max Number of Curves in the plot.
        :setter: Set the XY Plot Max Number of Curves in the plot.
        :type: int
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_max_number_of_curves"
        )
        return self.plot.GetXYPlotMaxNumberOfCurves

    @xy_plot_max_number_of_curves.setter
    def xy_plot_max_number_of_curves(self, value: int) -> None:
        """
        The XY Plot Max Number of Curves.

        Args:
            value (int): XY Plot Max Number of Curves to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="xy_plot_max_number_of_curves",
            value=value,
        )
        check_type(value, int)
        self.plot.SetXYPlotMaxNumberOfCurves(value)

    @property
    def xy_plot_auto_range_x(self) -> bool:
        """
        The XY Plot Auto Range X.

        :getter: Get the XY Plot Auto Range X in the plot.
        :setter: Set the XY Plot Auto Range X in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_auto_range_x")
        return self.plot.GetXYPlotAutoRangeX

    @xy_plot_auto_range_x.setter
    def xy_plot_auto_range_x(self, value: bool) -> None:
        """
        The XY Plot Auto Range X.

        Args:
            value (bool): XY Plot Auto Range X to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_auto_range_x", value=value
        )
        check_type(value, bool)
        self.plot.SetXYPlotAutoRangeX(value)

    @property
    def xy_plot_auto_range_y(self) -> bool:
        """
        The XY Plot Auto Range Y.

        :getter: Get the XY Plot Auto Range Y in the plot.
        :setter: Set the XY Plot Auto Range Y in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_auto_range_y")
        return self.plot.GetXYPlotAutoRangeY

    @xy_plot_auto_range_y.setter
    def xy_plot_auto_range_y(self, value: bool) -> None:
        """
        The XY Plot Auto Range Y.

        Args:
            value (bool): XY Plot Auto Range Y to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_auto_range_y", value=value
        )
        check_type(value, bool)
        self.plot.SetXYPlotAutoRangeY(value)

    @property
    def xy_plot_title(self) -> str:
        """
        The XY Plot Title.

        :getter: Get the XY Plot Title in the plot.
        :setter: Set the XY Plot Title in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_title")
        return self.plot.GetXYPlotTitle

    @xy_plot_title.setter
    def xy_plot_title(self, value: str) -> None:
        """
        The XY Plot Title.

        Args:
            value (str): XY Plot Title to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_title", value=value)
        check_type(value, str)
        self.plot.SetXYPlotTitle(value)

    @property
    def xy_plot_title_x(self) -> str:
        """
        The XY Plot Title X.

        :getter: Get the XY Plot Title X in the plot.
        :setter: Set the XY Plot Title X in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_title_x")
        return self.plot.GetXYPlotTitleX

    @xy_plot_title_x.setter
    def xy_plot_title_x(self, value: str) -> None:
        """
        The XY Plot Title X.

        Args:
            value (str): XY Plot Title X to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_title_x", value=value
        )
        check_type(value, str)
        self.plot.SetXYPlotTitleX(value)

    @property
    def xy_plot_title_y(self) -> str:
        """
        The XY Plot Title Y.

        :getter: Get the XY Plot Title Y in the plot.
        :setter: Set the XY Plot Title Y in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_title_y")
        return self.plot.GetXYPlotTitleY

    @xy_plot_title_y.setter
    def xy_plot_title_y(self, value: str) -> None:
        """
        The XY Plot Title Y.

        Args:
            value (str): XY Plot Title Y to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_title_y", value=value
        )
        check_type(value, str)
        self.plot.SetXYPlotTitleY(value)

    @property
    def min_value(self) -> float:
        """
        The min value.

        :getter: Get the min value in the plot.
        :setter: Set the min value in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="min_value")
        return self.plot.GetMinValue

    @min_value.setter
    def min_value(self, value: float) -> None:
        """
        The min value.

        Args:
            value (float): min value to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="min_value", value=value)
        check_type(value, (float, int))
        self.plot.SetMinValue(value)

    @property
    def max_value(self) -> float:
        """
        The max value.

        :getter: Get the max value in the plot.
        :setter: Set the max value in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="max_value")
        return self.plot.GetMaxValue

    @max_value.setter
    def max_value(self, value: float) -> None:
        """
        The max value.

        Args:
            value (float): max value to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="max_value", value=value)
        check_type(value, (float, int))
        self.plot.SetMaxValue(value)

    @property
    def xy_plot_min_x(self) -> float:
        """
        The XY Plot min X.

        :getter: Get the XY Plot min X in the plot.
        :setter: Set the XY Plot min X in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_min_x")
        return self.plot.GetXYPlotMinX

    @xy_plot_min_x.setter
    def xy_plot_min_x(self, value: float) -> None:
        """
        The XY Plot min X.

        Args:
            value (float): XY Plot min X to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_min_x", value=value)
        check_type(value, (float, int))
        self.plot.SetXYPlotMinX(value)

    @property
    def xy_plot_max_x(self) -> float:
        """
        The XY Plot max X.

        :getter: Get the XY Plot max X in the plot.
        :setter: Set the XY Plot max X in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_max_x")
        return self.plot.GetXYPlotMaxX

    @xy_plot_max_x.setter
    def xy_plot_max_x(self, value: float) -> None:
        """
        The XY Plot max X.

        Args:
            value (float): XY Plot max X to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_max_x", value=value)
        check_type(value, (float, int))
        self.plot.SetXYPlotMaxX(value)

    @property
    def xy_plot_min_y(self) -> float:
        """
        The XY Plot min Y.

        :getter: Get the XY Plot min Y in the plot.
        :setter: Set the XY Plot min Y in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_min_y")
        return self.plot.GetXYPlotMinY

    @xy_plot_min_y.setter
    def xy_plot_min_y(self, value: float) -> None:
        """
        The XY Plot min Y.

        Args:
            value (float): XY Plot min Y to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_min_y", value=value)
        check_type(value, (float, int))
        self.plot.SetXYPlotMinY(value)

    @property
    def xy_plot_max_y(self) -> float:
        """
        The XY Plot max Y.

        :getter: Get the XY Plot max Y in the plot.
        :setter: Set the XY Plot max Y in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_max_y")
        return self.plot.GetXYPlotMaxY

    @xy_plot_max_y.setter
    def xy_plot_max_y(self, value: float) -> None:
        """
        The XY Plot max Y.

        Args:
            value (float): XY Plot max Y to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="xy_plot_max_y", value=value)
        check_type(value, (float, int))
        self.plot.SetXYPlotMaxY(value)

    @property
    def xy_plot_legend_rect_width(self) -> float:
        """
        The XY Plot Legend Width.

        :getter: Get the XY Plot Legend Width in the plot.
        :setter: Set the XY Plot Legend Width in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_legend_rect_width")
        return self.plot.GetXYPlotLegendRectWidth

    @xy_plot_legend_rect_width.setter
    def xy_plot_legend_rect_width(self, value: float) -> None:
        """
        The XY Plot Legend Width.

        Args:
            value (float): XY Plot Legend Width to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="xy_plot_legend_rect_width",
            value=value,
        )
        check_type(value, (float, int))
        self.plot.SetXYPlotLegendRectWidth(value)

    @property
    def xy_plot_legend_rect_height(self) -> float:
        """
        The XY Plot Legend Height.

        :getter: Get the XY Plot Legend Height in the plot.
        :setter: Set the XY Plot Legend Height in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_legend_rect_height")
        return self.plot.GetXYPlotLegendRectHeight

    @xy_plot_legend_rect_height.setter
    def xy_plot_legend_rect_height(self, value: float) -> None:
        """
        The XY Plot Legend Height.

        Args:
            value (float): XY Plot Legend Height to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="xy_plot_legend_rect_height",
            value=value,
        )
        check_type(value, (float, int))
        self.plot.SetXYPlotLegendRectHeight(value)

    @property
    def xy_plot_legend_rect_left(self) -> float:
        """
        The XY Plot Legend Rect left position.

        :getter: Get the XY Plot Legend Rect left position in the plot.
        :setter: Set the XY Plot Legend Rect left position in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_legend_rect_left")
        return self.plot.GetXYPlotLegendRectLeft

    @xy_plot_legend_rect_left.setter
    def xy_plot_legend_rect_left(self, value: float) -> None:
        """
        The XY Plot Legend Rect left position.

        Args:
            value (float): XY Plot Legend Rect left position to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="xy_plot_legend_rect_left",
            value=value,
        )
        check_type(value, (float, int))
        self.plot.SetXYPlotLegendRectLeft(value)

    @property
    def xy_plot_legend_rect_bottom(self) -> float:
        """
        The XY Plot Legend Rect bottom position.

        :getter: Get the XY Plot Legend Rect bottom position in the plot.
        :setter: Set the XY Plot Legend Rect bottom position in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_legend_rect_bottom")
        return self.plot.GetXYPlotLegendRectBottom

    @xy_plot_legend_rect_bottom.setter
    def xy_plot_legend_rect_bottom(self, value: float) -> None:
        """
        The XY Plot Legend Rect bottom position.

        Args:
            value (float): XY Plot Legend Rect bottom position to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="xy_plot_legend_rect_bottom",
            value=value,
        )
        check_type(value, (float, int))
        self.plot.SetXYPlotLegendRectBottom(value)

    @property
    def plot_type(self) -> str:
        """
        The Plot Type.
        - Highlight Plot
        - XY Plot
        - Vector Plot
        - Tensor Plot
        - XYZ Plot
        - Shrink Check Plot
        - Sink Mark Plot
        - Contour Plot

        :getter: Get the Plot Type in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="plot_type")
        return self.plot.GetPlotType

    @property
    def notes(self) -> str:
        """
        The plot notes.

        :getter: Get the plot notes in the plot.
        :setter: Set the plot notes in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="notes")
        return self.plot.GetNotes

    @notes.setter
    def notes(self, value: str) -> None:
        """
        The plot notes.

        Args:
            value (str): plot notes to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="notes", value=value)
        check_type(value, str)
        self.plot.SetNotes(value)

    @property
    def xy_plot_number_of_curves(self) -> int:
        """
        The XY Plot Number of Curves.

        :getter: Get the XY Plot Number of Curves in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="xy_plot_number_of_curves")
        return self.plot.GetXYPlotNumberOfCurves

    def add_xy_plot_curve(self, curve: EntList | None) -> None:
        """
        Add curves to XY plot .

        Args:
            curve (EntList): The curve to add.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_xy_plot_curve")
        check_optional_type(curve, EntList)
        self.plot.AddXYPlotCurve(coerce_optional_dispatch(curve, "ent_list"))

    def delete_xy_plot_curve(self, curve: EntList | None) -> None:
        """
        Delete curves from XY plot.

        Args:
            curve (EntList): The curve to delete.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_xy_plot_curve")
        check_optional_type(curve, EntList)
        self.plot.DeleteXYPlotCurve(coerce_optional_dispatch(curve, "ent_list"))

    @property
    def edge_display(self) -> int:
        """
        The edge display option.

        :getter: Get the edge display option in the plot.
        :setter: Set the edge display option in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="edge_display")
        return self.plot.GetEdgeDisplay

    @edge_display.setter
    def edge_display(self, value: EdgeDisplayOptions | int) -> None:
        """
        The edge display option.

        Args:
            value (EdgeDisplayOptions | int): edge display option to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="edge_display", value=value)
        value = get_enum_value(value, EdgeDisplayOptions)
        self.plot.SetEdgeDisplay(value)

    @property
    def data_nb_components(self) -> int:
        """
        The number of components.

        :getter: Get the number of components in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="data_nb_components")
        return self.plot.GetDataNbComponents

    @property
    def data_id(self) -> int:
        """
        The data ID.

        :getter: Get the data ID in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="data_id")
        return self.plot.GetDataID

    @property
    def data_type(self) -> str:
        """
        The data type.

        :getter: Get the data type in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="data_type")
        return self.plot.GetDataType

    def restore_original_position(self) -> bool:
        """
        Restore the original position of the plot.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="restore_original_position")
        return self.plot.RestoreOriginalPosition

    def apply_best_fit(self, nodes: EntList | None) -> bool:
        """
        Apply the best fit to the plot.

        Args:
            nodes (EntList | None): The nodes to apply the best fit.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="apply_best_fit")
        check_optional_type(nodes, EntList)
        return self.plot.ApplyBestFit(coerce_optional_dispatch(nodes, "ent_list"))

    @property
    def deflection_scale_factor(self) -> float:
        """
        The deflection scale factor.

        :getter: Get the deflection scale factor in the plot.
        :setter: Set the deflection scale factor in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="deflection_scale_factor")
        return self.plot.GetDeflectionScaleFactor

    @deflection_scale_factor.setter
    def deflection_scale_factor(self, value: float) -> None:
        """
        The deflection scale factor.

        Args:
            value (float): deflection scale factor to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="deflection_scale_factor", value=value
        )
        check_type(value, (float, int))
        self.plot.SetDeflectionScaleFactor(value)

    @property
    def deflection_scale_direction(self) -> int:
        """
        The deflection scale direction.

        :getter: Get the deflection scale direction in the plot.
        :setter: Set the deflection scale direction in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="deflection_scale_direction")
        return self.plot.GetDeflectionScaleDirection

    @deflection_scale_direction.setter
    def deflection_scale_direction(self, value: DeflectionScaleDirections | int) -> None:
        """
        The deflection scale direction.

        Args:
            value (DeflectionScaleDirections | int): deflection scale direction to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="deflection_scale_direction",
            value=value,
        )
        value = get_enum_value(value, DeflectionScaleDirections)
        self.plot.SetDeflectionScaleDirection(value)

    @property
    def deflection_overlay_with_mesh(self) -> bool:
        """
        The deflection overlay with mesh.

        :getter: Get the deflection overlay with mesh in the plot.
        :setter: Set the deflection overlay with mesh in the plot.
        :type: bool
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="deflection_overlay_with_mesh"
        )
        return self.plot.GetDeflectionOverlayWithMesh

    @deflection_overlay_with_mesh.setter
    def deflection_overlay_with_mesh(self, value: bool) -> None:
        """
        The deflection overlay with mesh.

        Args:
            value (bool): deflection overlay with mesh to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="deflection_overlay_with_mesh",
            value=value,
        )
        check_type(value, bool)
        self.plot.SetDeflectionOverlayWithMesh(value)

    @property
    def deflection_show_anchor_plane(self) -> bool:
        """
        The deflection show anchor plane.

        :getter: Get the deflection show anchor plane in the plot.
        :setter: Set the deflection show anchor plane in the plot.
        :type: bool
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="deflection_show_anchor_plane"
        )
        return self.plot.GetDeflectionShowAnchorPlane

    @deflection_show_anchor_plane.setter
    def deflection_show_anchor_plane(self, value: bool) -> None:
        """
        The deflection show anchor plane.

        Args:
            value (bool): deflection show anchor plane to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="deflection_show_anchor_plane",
            value=value,
        )
        check_type(value, bool)
        self.plot.SetDeflectionShowAnchorPlane(value)

    @property
    def deflection_lcs(self) -> int:
        """
        The deflection LCS (local coordinate system).

        :getter: Get the deflection LCS (local coordinate system) in the plot.
        :setter: Set the deflection LCS (local coordinate system) in the plot.
            For global, set value to 0 or -1
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="deflection_lcs")
        return self.plot.GetDeflectionLCS

    @deflection_lcs.setter
    def deflection_lcs(self, value: int) -> None:
        """
        The deflection LCS (local coordinate system).

        Args:
            value (int): deflection LCS (local coordinate system) to set.
            For global, set value to 0 or -1
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="deflection_lcs", value=value)
        check_type(value, int)
        self.plot.SetDeflectionLCS(value)

    def warp_query_begin(self) -> bool:
        """
        Begin the warp query.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="warp_query_begin")
        return self.plot.WarpQueryBegin

    def warp_query_end(self) -> None:
        """
        End the warp query.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="warp_query_end")
        self.plot.WarpQueryEnd()

    def warp_query_node(self, node_id: int, return_values: DoubleArray | None) -> bool:
        """
        Query the warp node.

        Args:
            node_id (int): Node ID to query.
            return_values (DoubleArray): Returned query values.
            (node coordinates before and after deflection, and displacements)

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="warp_query_node")
        check_type(node_id, int)
        check_is_non_negative(node_id)
        check_optional_type(return_values, DoubleArray)
        return self.plot.WarpQueryNode(
            node_id, coerce_optional_dispatch(return_values, "double_array")
        )

    @property
    def probe_plot_number_of_probe_lines(self) -> int:
        """
        The probe plot number of probe lines.

        :getter: Get the probe plot number of probe lines in the plot.
        :type: int
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="probe_plot_number_of_probe_lines"
        )
        return self.plot.GetProbePlotNumberOfProbeLines

    def get_probe_plot_probe_line(
        self, index: int, start_pt: Vector | None, end_pt: Vector | None
    ) -> bool:
        """
        Returns the two end points of a probe line

        Args:
            index (int): Index of the probe line.
            start_pt (Vector): Start point of the probe line.
            end_pt (Vector): End point of the probe line.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_probe_plot_probe_line")
        check_type(index, int)
        check_is_non_negative(index)
        check_optional_type(start_pt, Vector)
        check_optional_type(end_pt, Vector)
        return self.plot.GetProbePlotProbeLine(
            index,
            coerce_optional_dispatch(start_pt, "vector"),
            coerce_optional_dispatch(end_pt, "vector"),
        )

    def add_probe_plot_probe_line(self, start_pt: Vector | None, end_pt: Vector | None) -> bool:
        """
        Add a probe plot probe line.

        Args:
            start_pt (Vector): Start point of the probe line.
            end_pt (Vector): End point of the probe line.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_probe_plot_probe_line")
        check_optional_type(start_pt, Vector)
        check_optional_type(end_pt, Vector)
        return self.plot.AddProbePlotProbeLine(
            coerce_optional_dispatch(start_pt, "vector"), coerce_optional_dispatch(end_pt, "vector")
        )

    def set_probe_plot_probe_line(
        self, index: int, start_pt: Vector | None, end_pt: Vector | None
    ) -> bool:
        """
        Modifies an existing probe line

        Args:
            index (int): Index of the probe line.
            start_pt (Vector): Start point of the probe line.
            end_pt (Vector): End point of the probe line.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_probe_plot_probe_line")
        check_type(index, int)
        check_is_non_negative(index)
        check_optional_type(start_pt, Vector)
        check_optional_type(end_pt, Vector)
        return self.plot.SetProbePlotProbeLine(
            index,
            coerce_optional_dispatch(start_pt, "vector"),
            coerce_optional_dispatch(end_pt, "vector"),
        )

    @property
    def number_of_animation_frames(self) -> int:
        """
        The number of animation frames.

        :getter: Get the number of animation frames in the plot.
        :setter: Set the number of animation frames in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="number_of_animation_frames")
        return self.plot.GetNumberOfAnimationFrames

    @number_of_animation_frames.setter
    def number_of_animation_frames(self, value: int) -> None:
        """
        The number of animation frames.

        Args:
            value (int): number of animation frames to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="number_of_animation_frames",
            value=value,
        )
        check_type(value, int)
        self.plot.SetNumberOfAnimationFrames(value)

    @property
    def first_animation_frame_index(self) -> int:
        """
        The first animation frame index.

        :getter: Get the first animation frame index in the plot.
        :setter: Set the first animation frame index in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="first_animation_frame_index")
        return self.plot.GetFirstAnimationFrameIndex

    @first_animation_frame_index.setter
    def first_animation_frame_index(self, value: int) -> None:
        """
        The first animation frame index.

        Args:
            value (int): first animation frame index to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="first_animation_frame_index",
            value=value,
        )
        check_type(value, int)
        self.plot.SetFirstAnimationFrameIndex(value)

    @property
    def last_animation_frame_index(self) -> int:
        """
        The last animation frame index.

        :getter: Get the last animation frame index in the plot.
        :setter: Set the last animation frame index in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="last_animation_frame_index")
        return self.plot.GetLastAnimationFrameIndex

    @last_animation_frame_index.setter
    def last_animation_frame_index(self, value: int) -> None:
        """
        The last animation frame index.

        Args:
            value (int): last animation frame index to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="last_animation_frame_index",
            value=value,
        )
        check_type(value, int)
        self.plot.SetLastAnimationFrameIndex(value)

    @property
    def current_animation_frame_index(self) -> int:
        """
        The current animation frame index.

        :getter: Get the current animation frame index in the plot.
        :type: int
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="current_animation_frame_index"
        )
        return self.plot.GetCurrentAnimationFrameIndex

    def save_result_in_xml(self, file_name: str, unit_sys: SystemUnits | str = "") -> bool:
        """
        Save the result in XML format.

        Args:
            file_name (str): The file name to save the result.
            unit_sys (SystemUnits | str): The unit system to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_result_in_xml")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, XML_FILE_EXT)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot.SaveResultInXML2(file_name, unit_sys)
        if not result:
            raise_save_error(saving="Results", file_name=file_name)
        return result

    def save_result_in_patran(self, file_name: str, unit_sys: SystemUnits | str = "") -> bool:
        """
        Save the result in Patran format.

        Args:
            file_name (str): The file name to save the result.
            unit_sys (SystemUnits | str): The unit system to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_result_in_patran")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, ELE_FILE_EXT)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot.SaveResultInPatran2(file_name, unit_sys)
        if not result:
            raise_save_error(saving="Results", file_name=file_name)
        return result

    def save_xy_plot_curve_data(self, file_name: str) -> bool:
        """
        Save the XY plot curve data.

        Args:
            file_name (str): The file_name to save the data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_xy_plot_curve_data")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, TXT_FILE_EXT)
        result = self.plot.SaveXYPlotCurveData(file_name)
        if not result:
            raise_save_error(saving="XY plot curve data", file_name=file_name)
        return result

    def save_warped_shape_in_stl(
        self,
        file_name: str,
        scale_factor: float,
        binary: bool,
        unit_sys: SystemUnits | str = SystemUnits.STANDARD,
    ) -> bool:
        """
        Save the warped shape in STL format.

        Args:
            file_name (str): The file name to save the warped shape.
            scale_factor (float): The scale factor to use.
            binary (bool): True if binary format, False if ASCII format.
            unit_sys (SystemUnits | str): The unit system to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_warped_shape_in_stl")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, STL_FILE_EXT)
        check_type(scale_factor, (float, int))
        check_type(binary, bool)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot.SaveWarpedShapeInSTL2(file_name, scale_factor, binary, unit_sys)
        if not result:
            raise_save_error(saving="Warped Shape", file_name=file_name)
        return result

    def save_warped_shape_in_udm(self, file_name: str, scale_factor: float) -> bool:
        """
        Save the warped shape in UDM format.

        Args:
            file_name (str): The file name to save the warped shape.
            scale_factor (float): The scale factor to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_warped_shape_in_udm")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, UDM_FILE_EXT)
        check_type(scale_factor, (float, int))
        result = self.plot.SaveWarpedShapeInUDM(file_name, scale_factor)
        if not result:
            raise_save_error(saving="Warped Shape", file_name=file_name)
        return result

    def save_warped_shape_in_cad(self, file_name: str, scale_factor: float) -> bool:
        """
        Save the warped shape in CAD format.

        Args:
            file_name (str): The file name to save the warped shape.
            scale_factor (float): The scale factor to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_warped_shape_in_cad")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, CAD_FILE_EXT)
        check_type(scale_factor, (float, int))
        result = self.plot.SaveWarpedShapeInCAD(file_name, scale_factor)
        if not result:
            raise_save_error(saving="Warped Shape", file_name=file_name)
        return result

    # pylint: disable-next=R0913, R0917
    def save_result_in_fbx(
        self,
        file_name: str,
        inc_frames: bool,
        scale_factor: float,
        binary: bool,
        unit_sys: SystemUnits | str = "",
    ) -> bool:
        """
        Save the result in FBX format.

        Args:
            file_name (str): The file name to save the result.
            inc_frames (bool): True if incremental frames, False otherwise.
            scale_factor (float): The scale factor to use.
            binary (bool): True if binary format, False if ASCII format.
            unit_sys (SystemUnits | str): The unit system to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_result_in_fbx")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, FBX_FILE_EXT)
        check_type(inc_frames, bool)
        check_type(scale_factor, (float, int))
        check_type(binary, bool)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot.SaveResultInFBX(file_name, inc_frames, scale_factor, binary, unit_sys)
        if not result:
            raise_save_error(saving="Results", file_name=file_name)
        return result

    @property
    def use_single_color(self) -> bool:
        """
        The use single color.

        :getter: Get the use single color in the plot.
        :setter: Set the use single color in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_single_color")
        return self.plot.GetUseSingleColor

    @use_single_color.setter
    def use_single_color(self, value: bool) -> None:
        """
        The use single color.

        Args:
            value (bool): use single color to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="use_single_color", value=value
        )
        check_type(value, bool)
        self.plot.SetUseSingleColor(value)

    @property
    def single_color(self) -> Vector | None:
        """
        The single color as RGB vector.

        :getter: Get the single color in the plot as RGB vector.
        :setter: Set the single color in the plot as RGB vector.
        :type: Vector
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="single_color")
        result = self.plot.GetSingleColor
        if result is None:
            return None
        return Vector(result)

    @single_color.setter
    def single_color(self, value: Vector | None) -> None:
        """
        The single color as RGB vector.

        Args:
            value (Vector): single color to set as RGB vector.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="single_color", value=value)
        check_optional_type(value, Vector)
        self.plot.SetSingleColor(coerce_optional_dispatch(value, "vector"))

    def set_plot_nodes_from_string(self, nodes: str) -> None:
        """
        Set the plot nodes from a string.

        Args:
            nodes (str): The nodes to set.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_plot_nodes_from_string")
        check_type(nodes, str)
        self.plot.SetPlotNodesFromString(nodes)

    def set_plot_nodes_from_ent_list(self, ent_list: EntList | None) -> None:
        """
        Set the plot nodes from an entity list.

        Args:
            ent_list (EntList): The entity list to set.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="set_plot_nodes_from_ent_list"
        )
        check_optional_type(ent_list, EntList)
        self.plot.SetPlotNodesFromEntList(coerce_optional_dispatch(ent_list, "ent_list"))

    def add_probe_plane(self, normal: str, point: str) -> bool:
        """
        Display a Probe plot.

        Args:
            normal (str): The normal vector of the probe plane.
            point (str): The point on the probe plane.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_probe_plane")
        check_type(normal, str)
        check_type(point, str)
        return self.plot.AddProbePlane(normal, point)

    def reset_probe_plane(self) -> None:
        """
        Reset the probe plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="reset_probe_plane")
        self.plot.ResetProbePlane()

    def set_plot_tolerance(self, min_value: str, max_value: str) -> bool:
        """
        Set 2 lines to be shown at certain Y positions.

        Args:
            min_value (str): The minimum value of the tolerance.
            max_value (str): The maximum value of the tolerance.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_plot_tolerance")
        check_type(min_value, str)
        check_type(max_value, str)
        return self.plot.SetPlotTolerance(min_value, max_value)

    @property
    def histogram(self) -> bool:
        """
        The visibility status of histogram.

        :getter: Get the visibility status of histogram in the plot.
        :setter: Set the visibility status of histogram in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="histogram")
        return self.plot.GetHistogram

    @histogram.setter
    def histogram(self, value: bool) -> None:
        """
        The visibility status of histogram.

        Args:
            value (bool): visibility status of histogram to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="histogram", value=value)
        check_type(value, bool)
        self.plot.SetHistogram(value)

    @property
    def histogram_number_of_bars(self) -> int:
        """
        The number of bars in histogram.

        :getter: Get the number of bars in histogram in the plot.
        :setter: Set the number of bars in histogram in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="histogram_number_of_bars")
        return self.plot.GetHistogramNumberOfBars

    @histogram_number_of_bars.setter
    def histogram_number_of_bars(self, value: int) -> None:
        """
        The number of bars in histogram.

        Args:
            value (int): number of bars in histogram to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="histogram_number_of_bars",
            value=value,
        )
        check_type(value, int)
        check_is_non_negative(value)
        self.plot.SetHistogramNumberOfBars(value)

    @property
    def histogram_cumulative_plot(self) -> bool:
        """
        The displayed volume is cumulative for the histogram plot.

        :getter: Get the displayed volume is cumulative for the histogram plot in the plot.
        :setter: Set the displayed volume is cumulative for the histogram plot in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="histogram_cumulative_plot")
        return self.plot.GetHistogramCumulativePlot

    @histogram_cumulative_plot.setter
    def histogram_cumulative_plot(self, value: bool) -> None:
        """
        The displayed volume is cumulative for the histogram plot.

        Args:
            value (bool): displayed volume is cumulative for the histogram plot to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="histogram_cumulative_plot",
            value=value,
        )
        check_type(value, bool)
        self.plot.SetHistogramCumulativePlot(value)

    @property
    def min_max_slice_at_probe(self) -> str:
        """
        The Min/Max slice plane location of a plot.

        :getter: Get the Min/Max slice plane location of a plot in the plot.
        :setter: Set the Min/Max slice plane location of a plot in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="min_max_slice_at_probe")
        return self.plot.GetMinMaxSliceAtProbe

    @min_max_slice_at_probe.setter
    def min_max_slice_at_probe(self, value: SliceAtProbeOptions | str) -> None:
        """
        The Min/Max slice plane location of a plot.

        Args:
            value (SliceAtProbeOptions | str): Min/Max slice plane location of a plot to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="min_max_slice_at_probe", value=value
        )
        value = get_enum_value(value, SliceAtProbeOptions)
        self.plot.SetMinMaxSliceAtProbe(value)

    @property
    def pathline_number_of_selected_elements(self) -> int:
        """
        The number of selected elements in the pathline plot.

        :getter: Get the number of selected elements in the pathline plot in the plot.
        :type: int
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="pathline_number_of_selected_elements"
        )
        return self.plot.GetPathlineNumberOfSelectedElements

    @property
    def pathline_selected_elements(self) -> str:
        """
        The selected elements for the pathline plot.

        :getter: Get the selected elements for the pathline plot in the plot.
        :setter: Set the selected elements for the pathline plot in the plot.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="pathline_selected_elements")
        return self.plot.GetPathlineSelectedElements

    @pathline_selected_elements.setter
    def pathline_selected_elements(self, value: str) -> None:
        """
        The selected elements for the pathline plot.

        Args:
            value (str): selected elements for the pathline plot to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="pathline_selected_elements",
            value=value,
        )
        check_type(value, str)
        self.plot.SetPathlineSelectedElements(value)

    @property
    def min_max(self) -> bool:
        """
        The Min/Max visibility status.

        :getter: Get the Min/Max visibility status in the plot.
        :setter: Set the Min/Max visibility status in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="min_max")
        return self.plot.GetMinMax

    @min_max.setter
    def min_max(self, value: bool) -> None:
        """
        The Min/Max visibility status.

        Args:
            value (bool): Min/Max visibility status to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="min_max", value=value)
        check_type(value, bool)
        self.plot.SetMinMax(value)

    @property
    def clip_legend(self) -> bool:
        """
        The status of the Clip Legend option.

        :getter: Get the status of the Clip Legend option in the plot.
        :setter: Set the status of the Clip Legend option in the plot.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="clip_legend")
        return self.plot.GetClipLegend

    @clip_legend.setter
    def clip_legend(self, value: bool) -> None:
        """
        The status of the Clip Legend option.

        Args:
            value (bool): status of the Clip Legend option to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="clip_legend", value=value)
        check_type(value, bool)
        self.plot.SetClipLegend(value)

    @property
    def pathline_display_field(self) -> int:
        """
        Get the ID of the result mapped on the pathlines.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="pathline_display_field")
        return self.plot.GetPathlineDisplayField

    @pathline_display_field.setter
    def pathline_display_field(self, value: int) -> None:
        """
        Set the current result mapped on the pathlines to the specified dataset ID.

        Args:
            value (int):  dsID to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="pathline_display_field", value=value
        )
        check_type(value, int)
        self.plot.SetPathlineDisplayField(value)

    @property
    def pathline_trace_mode(self) -> int:
        """
        Get the ID of the result mapped on the pathlines.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="pathline_trace_mode")
        return self.plot.GetPathlineTraceMode

    @pathline_trace_mode.setter
    def pathline_trace_mode(self, value: TraceModes | int) -> None:
        """
        Set the current result mapped on the pathlines to the specified dataset ID.

        Args:
            value (TraceModes | int):  dsID to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="pathline_trace_mode", value=value
        )
        value = get_enum_value(value, TraceModes)
        self.plot.SetPathlineTraceMode(value)

    @property
    def pathline_trace_style(self) -> int:
        """
        Get the current trace style.x
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="pathline_trace_style")
        return self.plot.GetPathlineTraceStyle

    @pathline_trace_style.setter
    def pathline_trace_style(self, value: TraceStyles | int) -> None:
        """
        Set the current trace style.

        Args:
            value (TraceStyles | int):  dsID to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="pathline_trace_style", value=value
        )
        value = get_enum_value(value, TraceStyles)
        self.plot.SetPathlineTraceStyle(value)

    def get_pathline_density(self, trace_mode: TraceModes | int) -> int:
        """
        Get the trace density for the given trace mode .

        Args:
            trace_mode (TraceModes | int): Trace mode to get the trace density.

        Returns:
            int: The trace density for the given trace mode .
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_pathline_density")
        trace_mode = get_enum_value(trace_mode, TraceModes)
        return self.plot.GetPathlineDensity(trace_mode)

    def set_pathline_density(self, trace_mode: TraceModes | int, value: int) -> bool:
        """
        Set the trace density for the given trace mode .

        Args:
            trace_mode (TraceModes | int): Trace mode to set the trace density.
            value (int): Trace density to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_pathline_density")
        trace_mode = get_enum_value(trace_mode, TraceModes)
        check_type(value, int)
        check_range(value, 0, 100, True, True)
        return self.plot.SetPathlineDensity(trace_mode, value)

    def set_pathline_injection_location(self, key: str, enabled: bool) -> bool:
        """
        Set the visibility of pathlines originating from specified injection location .

        Args:
            key (str): The injection location node ID.
            enabled (bool): The visibility is on.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="set_pathline_injection_location"
        )
        check_type(key, str)
        check_type(enabled, bool)
        return self.plot.SetPathlineInjectionLocation(key, enabled)

    def get_pathline_trace_size(self, trace_mode: TraceModes | int) -> int:
        """
        Get the trace size for the given trace mode .

        Args:
            trace_mode (TraceModes | int): Trace mode to get the trace density.

        Returns:
            int: The trace size for the given trace mode .
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_pathline_trace_size")
        value = get_enum_value(trace_mode, TraceModes)
        return self.plot.GetPathlineTraceSize(value)

    def set_pathline_trace_size(self, trace_mode: TraceModes | int, value: int) -> bool:
        """
        Set the trace size for the given trace mode .

        Args:
            trace_mode (TraceModes | int): Trace mode to set the trace density.
            value (int): Trace size to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_pathline_trace_size")
        trace_mode = get_enum_value(trace_mode, TraceModes)
        check_type(value, int)
        check_range(value, 0, 10, True, True)
        return self.plot.SetPathlineTraceSize(trace_mode, value)

    def get_pathline_result_name(self, ds_id: int) -> str:
        """
        Get the name of the result for the given dataset ID.

        Args:
            ds_id (int): Dataset ID to get the result name.

        Returns:
            str: The name of the result for the given dataset ID.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_PARAM_GET,
            locals(),
            name="get_pathline_result_name",
            value=ds_id,
        )
        check_type(ds_id, int)
        return self.plot.GetPathlineResultName(ds_id)

    def get_pathline_result_min(self, scale_type: ScaleTypes | int, result_id: int) -> float:
        """
        Get the minimum value of the result for the given type ID and result ID.

        Args:
            scale_type (ScaleTypes | int): Type ID to get the result minimum value.
            result_id (int): Result ID to get the result minimum value.

        Returns:
            float: The minimum value of the result for the given type ID and result ID.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_pathline_result_min")
        scale_type = get_enum_value(scale_type, ScaleTypes)
        check_type(result_id, int)
        check_is_non_negative(result_id)
        return self.plot.GetPathlineResultMin(scale_type, result_id)

    def set_pathline_result_min(
        self, scale_type: ScaleTypes | int, result_id: int, result_min: float
    ) -> None:
        """
        Set the minimum value of the result for the given type ID and result ID.

        Args:
            scale_type (ScaleTypes | int): Type ID to set the result minimum value.
            result_id (int): Result ID to set the result minimum value.
            result_min (float, int): Result minimum value to set.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_pathline_result_min")
        scale_type = get_enum_value(scale_type, ScaleTypes)
        check_type(result_id, int)
        check_is_non_negative(result_id)
        check_type(result_min, (float, int))
        self.plot.SetPathlineResultMin(scale_type, result_id, result_min)

    def get_pathline_result_max(self, scale_type: ScaleTypes | int, result_id: int) -> float:
        """
        Get the maximum value of the result for the given type ID and result ID.

        Args:
            scale_type (ScaleTypes | int): Type ID to get the result maximum value.
            result_id (int): Result ID to get the result maximum value.

        Returns:
            float: The maximum value of the result for the given type ID and result ID.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_pathline_result_max")
        scale_type = get_enum_value(scale_type, ScaleTypes)
        check_type(result_id, int)
        check_is_non_negative(result_id)
        return self.plot.GetPathlineResultMax(scale_type, result_id)

    def set_pathline_result_max(
        self, scale_type: ScaleTypes | int, result_id: int, result_max: float
    ) -> None:
        """
        Set the maximum value of the result for the given type ID and result ID.

        Args:
            scale_type (ScaleTypes | int): Type ID to set the result maximum value.
            result_id (int): Result ID to set the result maximum value.
            result_max (float, int): Result maximum value to set.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_pathline_result_max")
        scale_type = get_enum_value(scale_type, ScaleTypes)
        check_type(result_id, int)
        check_is_non_negative(result_id)
        check_type(result_max, (float, int))
        self.plot.SetPathlineResultMax(scale_type, result_id, result_max)

    def get_pathline_result_use_specified_values(self, result_id: int) -> bool:
        """
        Get the use specified values for the given result ID.

        Args:
            result_id (int): Result ID to get the use specified values.

        Returns:
            bool: The use specified values for the given result ID.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_PARAM_GET,
            locals(),
            name="get_pathline_result_use_specified_values",
            value=result_id,
        )
        check_type(result_id, int)
        check_is_non_negative(result_id)
        return self.plot.GetPathlineResultUseSpecifiedValues(result_id)

    def set_pathline_result_use_specified_values(
        self, result_id: int, use_specified_values: bool
    ) -> bool:
        """
        Set the use specified values for the given result ID.

        Args:
            result_id (int): Result ID to set the use specified values.
            use_specified_values (bool): Use specified values or not.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="set_pathline_result_use_specified_values",
        )
        check_type(result_id, int)
        check_is_non_negative(result_id)
        check_type(use_specified_values, bool)
        return self.plot.SetPathlineResultUseSpecifiedValues(result_id, use_specified_values)

    def get_pathline_result_are_settings_valid(self, result_id: int) -> bool:
        """
        Get the validity of the settings for the pathline result.

        Args:
            result_id (int): Result ID to check the validity of the settings.

        Returns:
            bool: True if settings are valid, False otherwise.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_PARAM_GET,
            locals(),
            name="get_pathline_result_are_settings_valid",
            value=result_id,
        )
        check_type(result_id, int)
        check_is_non_negative(result_id)
        return self.plot.GetPathlineResultAreSettingsValid(result_id)

    def get_pathline_result_use_extended_colour(self, result_id: int) -> bool:
        """
        Get the use extended colour for the pathline result.

        Args:
            result_id (int): Result ID to get the use extended colour.

        Returns:
            bool: The use extended colour for the pathline result.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_GET,
            locals(),
            name="get_pathline_result_use_extended_colour",
        )
        check_type(result_id, int)
        check_is_non_negative(result_id)
        return self.plot.GetPathlineResultUseExtendedColour(result_id)

    def set_pathline_result_use_extended_colour(
        self, result_id: int, use_extended_colour: bool
    ) -> None:
        """
        Set the use extended colour for the pathline result.

        Args:
            result_id (int): Result ID to set the use extended colour.
            use_extended_colour (bool): Use extended colour or not.
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="set_pathline_result_use_extended_colour",
        )
        check_type(result_id, int)
        check_is_non_negative(result_id)
        check_type(use_extended_colour, bool)
        self.plot.SetPathlineResultUseExtendedColour(result_id, use_extended_colour)

    @property
    def glyph_size_factor(self) -> float:
        """
        The glyph size factor.

        :getter: Get the glyph size factor in the plot.
        :setter: Set the glyph size factor in the plot.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="glyph_size_factor")
        return self.plot.GetGlyphSizeFactor

    @glyph_size_factor.setter
    def glyph_size_factor(self, value: float) -> None:
        """
        The glyph size factor.

        Args:
            value (float): glyph size factor to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="glyph_size_factor", value=value
        )
        check_type(value, (float, int))
        self.plot.SetGlyphSizeFactor(value)

    @property
    def tensor_glyph_axis_ratio(self) -> int:
        """
        The glyph tensor axis ratio.

        :getter: Get the glyph tensor axis ratio in the plot.
        :setter: Set the glyph tensor axis ratio in the plot.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tensor_glyph_axis_ratio")
        return self.plot.GetTensorGlyphAxisRatio

    @tensor_glyph_axis_ratio.setter
    def tensor_glyph_axis_ratio(self, value: TensorAxisRatioOptions | int) -> None:
        """
        The glyph tensor axis ratio.

        Args:
            value (TensorAxisRatioOptions | int): glyph tensor axis ratio to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="tensor_glyph_axis_ratio", value=value
        )
        value = get_enum_value(value, TensorAxisRatioOptions)
        self.plot.SetTensorGlyphAxisRatio(value)

    @property
    def shrinkage_compensation_option(self) -> str:
        """
        The shrinkage compensation option.

        :getter: Get the shrinkage compensation option in the plot.
        :setter: Set the shrinkage compensation option in the plot.
        :type: str
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="shrinkage_compensation_option"
        )
        return self.plot.GetShrinkageCompensationOption

    @shrinkage_compensation_option.setter
    def shrinkage_compensation_option(self, value: ShrinkageCompensationOptions | str) -> None:
        """
        The shrinkage compensation option.

        Args:
            value (ShrinkageCompensationOptions | str): shrinkage compensation option to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="shrinkage_compensation_option",
            value=value,
        )
        value = get_enum_value(value, ShrinkageCompensationOptions)
        self.plot.SetShrinkageCompensationOption(value)

    @property
    def shrinkage_compensation_estimated_shrinkage(self) -> Vector | None:
        """
        The shrinkage compensation estimated shrinkage.

        :getter: Get the shrinkage compensation estimated shrinkage in the plot.
        :setter: Set the shrinkage compensation estimated shrinkage in the plot.
        :type: Vector
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_GET,
            locals(),
            name="shrinkage_compensation_estimated_shrinkage",
        )
        result = self.plot.GetShrinkageCompensationEstimatedShrinkage
        if result is None:
            return None
        return Vector(result)

    @shrinkage_compensation_estimated_shrinkage.setter
    def shrinkage_compensation_estimated_shrinkage(self, value: Vector | None) -> None:
        """
        The shrinkage compensation estimated shrinkage.

        Args:
            value (Vector): shrinkage compensation estimated shrinkage to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="shrinkage_compensation_estimated_shrinkage",
            value=value,
        )
        check_optional_type(value, Vector)
        self.plot.SetShrinkageCompensationEstimatedShrinkage(
            coerce_optional_dispatch(value, "vector")
        )
