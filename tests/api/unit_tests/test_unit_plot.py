# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for Plot Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import (
    Plot,
    DoubleArray,
    Vector,
    EntList,
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
    SystemUnits,
    ColorScaleOptions,
)
from moldflow.exceptions import SaveError
from tests.conftest import (
    INVALID_BOOL,
    INVALID_INT,
    INVALID_FLOAT,
    INVALID_STR,
    VALID_BOOL,
    VALID_INT,
    VALID_FLOAT,
    NON_NEGATIVE_INT,
    VALID_STR,
)
from tests.api.unit_tests.conftest import VALID_COLOR_BAND_VALUES

SYSTEM_UNITS_AND_NONE = list(SystemUnits) + [None]


@pytest.mark.unit
class TestUnitPlot:
    """
    Test suite for the Plot class.
    """

    @pytest.fixture
    def mock_plot(self, mock_object) -> Plot:
        """
        Fixture to create a mock instance of Plot.
        Args:
            mock_object: Mock object for the Plot dependency.
        Returns:
            Plot: An instance of Plot with the mock object.
        """
        return Plot(mock_object)

    @pytest.fixture
    def mock_double_array(self) -> DoubleArray:
        """
        Fixture to create a mock instance of DoubleArray.
        Returns:
            DoubleArray: An instance of DoubleArray.
        """
        mock_double_array = Mock(spec=DoubleArray)
        mock_double_array.double_array = Mock()
        return mock_double_array

    @pytest.fixture
    def mock_vector(self) -> Vector:
        """
        Fixture to create a mock instance of Vector.
        Returns:
            Vector: An instance of Vector.
        """
        mock_vector = Mock(spec=Vector)
        mock_vector.vector = Mock()
        return mock_vector

    @pytest.fixture
    def mock_ent_list(self) -> EntList:
        """
        Fixture to create a mock instance of EntList.
        Returns:
            EntList: An instance of EntList.
        """
        mock_ent_list = Mock(spec=EntList)
        mock_ent_list.ent_list = Mock()
        return mock_ent_list

    def test_regenerate(self, mock_plot, mock_object):
        """
        Test the regenerate method of the Plot class.
        Args:
            mock_plot: Mock instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        mock_plot.regenerate()
        mock_object.Regenerate.assert_called_once()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("GetNumberOfFrames", "number_of_frames", x) for x in VALID_INT]
        + [("GetName", "name", x) for x in VALID_STR]
        + [("GetNumberOfContours", "number_of_contours", x) for x in VALID_INT]
        + [("GetComponent", "component", x.value) for x in DisplayComponent]
        + [("GetMeshFill", "mesh_fill", x) for x in [0.0, 1.0, 1, 0, 0.1, 0.5]]
        + [("GetNodalAveraging", "nodal_averaging", x) for x in VALID_BOOL]
        + [("GetSmoothShading", "smooth_shading", x) for x in VALID_BOOL]
        + [("GetColorScale", "color_scale", x) for x in ColorScaleOptions]
        + [("GetCapping", "capping", x) for x in VALID_BOOL]
        + [("GetScaleOption", "scale_option", x.value) for x in ScaleOptions]
        + [("GetPlotMethod", "plot_method", x.value) for x in PlotMethod]
        + [("GetAnimationType", "animation_type", x.value) for x in AnimationType]
        + [("GetNumberOfIndpVars", "number_of_indp_vars", x) for x in VALID_INT]
        + [("GetActiveIndpVar", "active_indp_var", x) for x in VALID_INT]
        + [("GetExtendedColor", "extended_color", x) for x in VALID_BOOL]
        + [("GetColorBands", "color_bands", x) for x in VALID_COLOR_BAND_VALUES]
        + [("GetColorTableId", "color_table_id", x.value) for x in ColorTableIDs]
        + [("GetXYPlotShowLegend", "xy_plot_show_legend", x) for x in VALID_BOOL]
        + [("GetXYPlotShowPoints", "xy_plot_show_points", x) for x in VALID_BOOL]
        + [("GetXYPlotOverlayWithMesh", "xy_plot_overlay_with_mesh", x) for x in VALID_BOOL]
        + [("GetXYPlotMaxNumberOfCurves", "xy_plot_max_number_of_curves", x) for x in VALID_INT]
        + [("GetXYPlotAutoRangeX", "xy_plot_auto_range_x", x) for x in VALID_BOOL]
        + [("GetXYPlotAutoRangeY", "xy_plot_auto_range_y", x) for x in VALID_BOOL]
        + [("GetXYPlotTitle", "xy_plot_title", x) for x in VALID_STR]
        + [("GetXYPlotTitleX", "xy_plot_title_x", x) for x in VALID_STR]
        + [("GetXYPlotTitleY", "xy_plot_title_y", x) for x in VALID_STR]
        + [("GetMinValue", "min_value", x) for x in VALID_FLOAT]
        + [("GetMaxValue", "max_value", x) for x in VALID_FLOAT]
        + [("GetXYPlotMinX", "xy_plot_min_x", x) for x in VALID_FLOAT]
        + [("GetXYPlotMaxX", "xy_plot_max_x", x) for x in VALID_FLOAT]
        + [("GetXYPlotMinY", "xy_plot_min_y", x) for x in VALID_FLOAT]
        + [("GetXYPlotMaxY", "xy_plot_max_y", x) for x in VALID_FLOAT]
        + [("GetXYPlotLegendRectWidth", "xy_plot_legend_rect_width", x) for x in VALID_FLOAT]
        + [("GetXYPlotLegendRectHeight", "xy_plot_legend_rect_height", x) for x in VALID_FLOAT]
        + [("GetXYPlotLegendRectLeft", "xy_plot_legend_rect_left", x) for x in VALID_FLOAT]
        + [("GetXYPlotLegendRectBottom", "xy_plot_legend_rect_bottom", x) for x in VALID_FLOAT]
        + [("GetPlotType", "plot_type", x) for x in VALID_STR]
        + [("GetNotes", "notes", x) for x in VALID_STR]
        + [("GetXYPlotNumberOfCurves", "xy_plot_number_of_curves", x) for x in VALID_INT]
        + [("GetEdgeDisplay", "edge_display", x.value) for x in EdgeDisplayOptions]
        + [("GetDataNbComponents", "data_nb_components", x) for x in VALID_INT]
        + [("GetDataID", "data_id", x) for x in VALID_INT]
        + [("GetDataType", "data_type", x) for x in VALID_STR]
        + [("GetDeflectionScaleFactor", "deflection_scale_factor", x) for x in VALID_FLOAT]
        + [("GetDeflectionScaleDirection", "deflection_scale_direction", x) for x in VALID_INT]
        + [("GetDeflectionOverlayWithMesh", "deflection_overlay_with_mesh", x) for x in VALID_BOOL]
        + [("GetDeflectionShowAnchorPlane", "deflection_show_anchor_plane", x) for x in VALID_BOOL]
        + [("GetDeflectionLCS", "deflection_lcs", x) for x in VALID_INT]
        + [
            ("GetProbePlotNumberOfProbeLines", "probe_plot_number_of_probe_lines", x)
            for x in VALID_INT
        ]
        + [("GetNumberOfAnimationFrames", "number_of_animation_frames", x) for x in VALID_INT]
        + [("GetFirstAnimationFrameIndex", "first_animation_frame_index", x) for x in VALID_INT]
        + [("GetLastAnimationFrameIndex", "last_animation_frame_index", x) for x in VALID_INT]
        + [("GetCurrentAnimationFrameIndex", "current_animation_frame_index", x) for x in VALID_INT]
        + [("GetUseSingleColor", "use_single_color", x) for x in VALID_BOOL]
        + [("GetHistogram", "histogram", x) for x in VALID_BOOL]
        + [("GetHistogramNumberOfBars", "histogram_number_of_bars", x) for x in VALID_BOOL]
        + [("GetHistogramCumulativePlot", "histogram_cumulative_plot", x) for x in VALID_BOOL]
        + [
            ("GetMinMaxSliceAtProbe", "min_max_slice_at_probe", x.value)
            for x in SliceAtProbeOptions
        ]
        + [
            ("GetPathlineNumberOfSelectedElements", "pathline_number_of_selected_elements", x)
            for x in VALID_INT
        ]
        + [("GetPathlineSelectedElements", "pathline_selected_elements", x) for x in VALID_STR]
        + [("GetMinMax", "min_max", x) for x in VALID_BOOL]
        + [("GetClipLegend", "clip_legend", x) for x in VALID_BOOL]
        + [("GetPathlineDisplayField", "pathline_display_field", x) for x in VALID_INT]
        + [("GetPathlineTraceMode", "pathline_trace_mode", x.value) for x in TraceModes]
        + [("GetPathlineTraceStyle", "pathline_trace_style", x.value) for x in TraceStyles]
        + [("GetGlyphSizeFactor", "glyph_size_factor", x) for x in VALID_FLOAT]
        + [
            ("GetTensorGlyphAxisRatio", "tensor_glyph_axis_ratio", x.value)
            for x in TensorAxisRatioOptions
        ]
        + [
            ("GetShrinkageCompensationOption", "shrinkage_compensation_option", x.value)
            for x in ShrinkageCompensationOptions
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(self, mock_plot: Plot, mock_object, pascal_name, property_name, value):
        """
        Test Get properties of Plot.

        Args:
            mock_plot: Instance of Plot.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_plot, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, expected",
        [("SetNumberOfFrames", "number_of_frames", x, x) for x in VALID_INT]
        + [("SetName", "name", x, x) for x in VALID_STR]
        + [("SetNumberOfContours", "number_of_contours", x, x) for x in VALID_INT]
        + [("SetComponent", "component", x, x.value) for x in DisplayComponent]
        + [("SetComponent", "component", x.value, x.value) for x in DisplayComponent]
        + [("SetMeshFill", "mesh_fill", x, x) for x in [0.0, 1.0, 1, 0, 0.1, 0.5]]
        + [("SetNodalAveraging", "nodal_averaging", x, x) for x in VALID_BOOL]
        + [("SetSmoothShading", "smooth_shading", x, x) for x in VALID_BOOL]
        + [("SetColorScale", "color_scale", x, x.value) for x in ColorScaleOptions]
        + [("SetColorScale", "color_scale", x.value, x.value) for x in ColorScaleOptions]
        + [("SetCapping", "capping", x, x) for x in VALID_BOOL]
        + [("SetScaleOption", "scale_option", x, x.value) for x in ScaleOptions]
        + [("SetScaleOption", "scale_option", x.value, x.value) for x in ScaleOptions]
        + [("SetPlotMethod", "plot_method", x, x.value) for x in PlotMethod]
        + [("SetPlotMethod", "plot_method", x.value, x.value) for x in PlotMethod]
        + [("SetAnimationType", "animation_type", x, x.value) for x in AnimationType]
        + [("SetAnimationType", "animation_type", x.value, x.value) for x in AnimationType]
        + [("SetExtendedColor", "extended_color", x, x) for x in VALID_BOOL]
        + [("SetColorBands", "color_bands", x, x) for x in VALID_COLOR_BAND_VALUES]
        + [("SetColorTableId", "color_table_id", x, x.value) for x in ColorTableIDs]
        + [("SetColorTableId", "color_table_id", x.value, x.value) for x in ColorTableIDs]
        + [("SetXYPlotShowLegend", "xy_plot_show_legend", x, x) for x in VALID_BOOL]
        + [("SetXYPlotShowPoints", "xy_plot_show_points", x, x) for x in VALID_BOOL]
        + [("SetXYPlotOverlayWithMesh", "xy_plot_overlay_with_mesh", x, x) for x in VALID_BOOL]
        + [("SetXYPlotMaxNumberOfCurves", "xy_plot_max_number_of_curves", x, x) for x in VALID_INT]
        + [("SetXYPlotAutoRangeX", "xy_plot_auto_range_x", x, x) for x in VALID_BOOL]
        + [("SetXYPlotAutoRangeY", "xy_plot_auto_range_y", x, x) for x in VALID_BOOL]
        + [("SetXYPlotTitle", "xy_plot_title", x, x) for x in VALID_STR]
        + [("SetXYPlotTitleX", "xy_plot_title_x", x, x) for x in VALID_STR]
        + [("SetXYPlotTitleY", "xy_plot_title_y", x, x) for x in VALID_STR]
        + [("SetMinValue", "min_value", x, x) for x in VALID_FLOAT]
        + [("SetMaxValue", "max_value", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotMinX", "xy_plot_min_x", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotMaxX", "xy_plot_max_x", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotMinY", "xy_plot_min_y", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotMaxY", "xy_plot_max_y", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotLegendRectWidth", "xy_plot_legend_rect_width", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotLegendRectHeight", "xy_plot_legend_rect_height", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotLegendRectLeft", "xy_plot_legend_rect_left", x, x) for x in VALID_FLOAT]
        + [("SetXYPlotLegendRectBottom", "xy_plot_legend_rect_bottom", x, x) for x in VALID_FLOAT]
        + [("SetNotes", "notes", x, x) for x in VALID_STR]
        + [("SetEdgeDisplay", "edge_display", x, x.value) for x in EdgeDisplayOptions]
        + [("SetEdgeDisplay", "edge_display", x.value, x.value) for x in EdgeDisplayOptions]
        + [("SetDeflectionScaleFactor", "deflection_scale_factor", x, x) for x in VALID_FLOAT]
        + [
            ("SetDeflectionScaleDirection", "deflection_scale_direction", x, x.value)
            for x in DeflectionScaleDirections
        ]
        + [
            ("SetDeflectionScaleDirection", "deflection_scale_direction", x.value, x.value)
            for x in DeflectionScaleDirections
        ]
        + [
            ("SetDeflectionOverlayWithMesh", "deflection_overlay_with_mesh", x, x)
            for x in VALID_BOOL
        ]
        + [
            ("SetDeflectionShowAnchorPlane", "deflection_show_anchor_plane", x, x)
            for x in VALID_BOOL
        ]
        + [("SetDeflectionLCS", "deflection_lcs", x, x) for x in VALID_INT]
        + [("SetNumberOfAnimationFrames", "number_of_animation_frames", x, x) for x in VALID_INT]
        + [("SetFirstAnimationFrameIndex", "first_animation_frame_index", x, x) for x in VALID_INT]
        + [("SetLastAnimationFrameIndex", "last_animation_frame_index", x, x) for x in VALID_INT]
        + [("SetUseSingleColor", "use_single_color", x, x) for x in VALID_BOOL]
        + [("SetHistogram", "histogram", x, x) for x in VALID_BOOL]
        + [("SetHistogramNumberOfBars", "histogram_number_of_bars", x, x) for x in NON_NEGATIVE_INT]
        + [("SetHistogramCumulativePlot", "histogram_cumulative_plot", x, x) for x in VALID_BOOL]
        + [
            ("SetMinMaxSliceAtProbe", "min_max_slice_at_probe", x, x.value)
            for x in SliceAtProbeOptions
        ]
        + [
            ("SetMinMaxSliceAtProbe", "min_max_slice_at_probe", x.value, x.value)
            for x in SliceAtProbeOptions
        ]
        + [
            ("SetPathlineSelectedElements", "pathline_selected_elements", x.value, x.value)
            for x in SliceAtProbeOptions
        ]
        + [("SetMinMax", "min_max", x, x) for x in VALID_BOOL]
        + [("SetClipLegend", "clip_legend", x, x) for x in VALID_BOOL]
        + [
            ("SetPathlineDisplayField", "pathline_display_field", x, x)
            for x in VALID_INT
            for y in VALID_BOOL
        ]
        + [
            ("SetPathlineTraceMode", "pathline_trace_mode", x, x.value)
            for x in TraceModes
            for y in VALID_BOOL
        ]
        + [
            ("SetPathlineTraceMode", "pathline_trace_mode", x.value, x.value)
            for x in TraceModes
            for y in VALID_BOOL
        ]
        + [
            ("SetPathlineTraceStyle", "pathline_trace_style", x, x.value)
            for x in TraceStyles
            for y in VALID_BOOL
        ]
        + [
            ("SetPathlineTraceStyle", "pathline_trace_style", x.value, x.value)
            for x in TraceStyles
            for y in VALID_BOOL
        ]
        + [("SetGlyphSizeFactor", "glyph_size_factor", x, x) for x in VALID_FLOAT]
        + [
            ("SetTensorGlyphAxisRatio", "tensor_glyph_axis_ratio", x, x.value)
            for x in TensorAxisRatioOptions
        ]
        + [
            ("SetTensorGlyphAxisRatio", "tensor_glyph_axis_ratio", x.value, x.value)
            for x in TensorAxisRatioOptions
        ]
        + [
            ("SetShrinkageCompensationOption", "shrinkage_compensation_option", x, x.value)
            for x in ShrinkageCompensationOptions
        ]
        + [
            ("SetShrinkageCompensationOption", "shrinkage_compensation_option", x.value, x.value)
            for x in ShrinkageCompensationOptions
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, value, expected
    ):
        """
        Test properties of Plot.

        Args:
            mock_plot: Instance of Plot.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_plot, property_name, value)
        getattr(mock_object, pascal_name).assert_called_once_with(expected)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("SetNumberOfFrames", "number_of_frames", x) for x in INVALID_INT]
        + [("SetName", "name", x) for x in INVALID_STR]
        + [("SetNumberOfContours", "number_of_contours", x) for x in INVALID_INT]
        + [("SetComponent", "component", x) for x in INVALID_INT]
        + [("SetMeshFill", "mesh_fill", x) for x in INVALID_FLOAT]
        + [("SetNodalAveraging", "nodal_averaging", x) for x in INVALID_BOOL]
        + [("SetSmoothShading", "smooth_shading", x) for x in INVALID_BOOL]
        + [("SetColorScale", "color_scale", x) for x in INVALID_BOOL]
        + [("SetCapping", "capping", x) for x in INVALID_BOOL]
        + [("SetScaleOption", "scale_option", x) for x in INVALID_INT]
        + [("SetPlotMethod", "plot_method", x) for x in INVALID_INT]
        + [("SetAnimationType", "animation_type", x) for x in INVALID_INT]
        + [("SetActiveIndpVar", "active_indp_var", x) for x in INVALID_INT]
        + [("SetExtendedColor", "extended_color", x) for x in INVALID_BOOL]
        + [("SetColorBands", "color_bands", x) for x in INVALID_INT]
        + [("SetColorTableId", "color_table_id", x) for x in INVALID_INT]
        + [("SetXYPlotShowLegend", "xy_plot_show_legend", x) for x in INVALID_BOOL]
        + [("SetXYPlotShowPoints", "xy_plot_show_points", x) for x in INVALID_BOOL]
        + [("SetXYPlotOverlayWithMesh", "xy_plot_overlay_with_mesh", x) for x in INVALID_BOOL]
        + [("SetXYPlotMaxNumberOfCurves", "xy_plot_max_number_of_curves", x) for x in INVALID_INT]
        + [("SetXYPlotAutoRangeX", "xy_plot_auto_range_x", x) for x in INVALID_BOOL]
        + [("SetXYPlotAutoRangeY", "xy_plot_auto_range_y", x) for x in INVALID_BOOL]
        + [("SetXYPlotTitle", "xy_plot_title", x) for x in INVALID_STR]
        + [("SetXYPlotTitleX", "xy_plot_title_x", x) for x in INVALID_STR]
        + [("SetXYPlotTitleY", "xy_plot_title_y", x) for x in INVALID_STR]
        + [("SetMinValue", "min_value", x) for x in INVALID_FLOAT]
        + [("SetMaxValue", "max_value", x) for x in INVALID_FLOAT]
        + [("SetXYPlotMinX", "xy_plot_min_x", x) for x in INVALID_FLOAT]
        + [("SetXYPlotMaxX", "xy_plot_max_x", x) for x in INVALID_FLOAT]
        + [("SetXYPlotMinY", "xy_plot_min_y", x) for x in INVALID_FLOAT]
        + [("SetXYPlotMaxY", "xy_plot_max_y", x) for x in INVALID_FLOAT]
        + [("SetXYPlotLegendRectWidth", "xy_plot_legend_rect_width", x) for x in INVALID_FLOAT]
        + [("SetXYPlotLegendRectHeight", "xy_plot_legend_rect_height", x) for x in INVALID_FLOAT]
        + [("SetXYPlotLegendRectLeft", "xy_plot_legend_rect_left", x) for x in INVALID_FLOAT]
        + [("SetXYPlotLegendRectBottom", "xy_plot_legend_rect_bottom", x) for x in INVALID_FLOAT]
        + [("SetNotes", "notes", x) for x in INVALID_STR]
        + [("SetEdgeDisplay", "edge_display", x) for x in INVALID_INT]
        + [("SetDeflectionScaleFactor", "deflection_scale_factor", x) for x in INVALID_FLOAT]
        + [("SetDeflectionScaleDirection", "deflection_scale_direction", x) for x in INVALID_INT]
        + [
            ("SetDeflectionOverlayWithMesh", "deflection_overlay_with_mesh", x)
            for x in INVALID_BOOL
        ]
        + [
            ("SetDeflectionShowAnchorPlane", "deflection_show_anchor_plane", x)
            for x in INVALID_BOOL
        ]
        + [("SetDeflectionLCS", "deflection_lcs", x) for x in INVALID_INT]
        + [("SetNumberOfAnimationFrames", "number_of_animation_frames", x) for x in INVALID_INT]
        + [("SetFirstAnimationFrameIndex", "first_animation_frame_index", x) for x in INVALID_INT]
        + [("SetLastAnimationFrameIndex", "last_animation_frame_index", x) for x in INVALID_INT]
        + [("SetUseSingleColor", "use_single_color", x) for x in INVALID_BOOL]
        + [("SetHistogram", "histogram", x) for x in INVALID_BOOL]
        + [("SetHistogramNumberOfBars", "histogram_number_of_bars", x) for x in INVALID_INT]
        + [("SetHistogramCumulativePlot", "histogram_cumulative_plot", x) for x in INVALID_BOOL]
        + [("SetMinMaxSliceAtProbe", "min_max_slice_at_probe", x) for x in INVALID_STR]
        + [("SetPathlineSelectedElements", "pathline_selected_elements", x) for x in INVALID_STR]
        + [("SetMinMax", "min_max", x) for x in INVALID_BOOL]
        + [("SetClipLegend", "clip_legend", x) for x in INVALID_BOOL]
        + [("SetPathlineDisplayField", "pathline_display_field", x) for x in INVALID_INT]
        + [("SetPathlineTraceMode", "pathline_trace_mode", x) for x in INVALID_INT]
        + [("SetPathlineTraceStyle", "pathline_trace_style", x) for x in INVALID_INT]
        + [("SetGlyphSizeFactor", "glyph_size_factor", x) for x in INVALID_FLOAT]
        + [("SetTensorGlyphAxisRatio", "tensor_glyph_axis_ratio", x) for x in INVALID_INT]
        + [
            ("SetShrinkageCompensationOption", "shrinkage_compensation_option", x)
            for x in INVALID_STR
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_properties(
        self, mock_object, mock_plot: Plot, pascal_name, property_name, value, _
    ):
        """
        Test invalid properties of Plot.
        Args:
            mock_plot: Instance of Plot.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_plot, property_name, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("SetMeshFill", "mesh_fill", x) for x in [-1.0, 2.0, 3.0]]
        + [("SetColorBands", "color_bands", x) for x in [-1, 0, 257, 300]]
        + [("SetHistogramNumberOfBars", "histogram_number_of_bars", x) for x in [-1, -2, -3, -4]],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_value_properties(
        self, mock_object, mock_plot: Plot, pascal_name, property_name, value, _
    ):
        """
        Test invalid properties of Plot.
        Args:
            mock_plot: Instance of Plot.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(ValueError) as e:
            setattr(mock_plot, property_name, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("SetComponent", "component", x) for x in [9, 10, 100]]
        + [("SetScaleOption", "scale_option", x) for x in [4, 5, 100]]
        + [("SetPlotMethod", "plot_method", x) for x in [0, 3, 5, 7, 100]]
        + [("SetAnimationType", "animation_type", x) for x in [2, 3, 100, -1]]
        + [("SetColorTableId", "color_table_id", x) for x in [1, 65, 128]]
        + [("SetEdgeDisplay", "edge_display", x) for x in [3, 4, 5, -1, 100]]
        + [
            ("SetDeflectionScaleDirection", "deflection_scale_direction", x)
            for x in [4, 5, 6, -1, 100]
        ]
        + [("SetMinMaxSliceAtProbe", "min_max_slice_at_probe", x) for x in ["", " ", "abc"]]
        + [("SetPathlineTraceMode", "pathline_trace_mode", x) for x in [2, 3, -1, 100]]
        + [("SetPathlineTraceStyle", "pathline_trace_style", x) for x in [3, 4, -1, 100]]
        + [("SetTensorGlyphAxisRatio", "tensor_glyph_axis_ratio", x) for x in [4, 5, 6, -1, 100]]
        + [
            ("SetShrinkageCompensationOption", "shrinkage_compensation_option", x)
            for x in ["", " ", "abc"]
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_enum_properties(
        self, mock_object, mock_plot: Plot, pascal_name, property_name, value, _, caplog
    ):
        """
        Test invalid properties of Plot.
        Args:
            mock_plot: Instance of Plot.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        setattr(mock_plot, property_name, value)
        assert _("this may cause function call to fail") in caplog.text
        # assert getattr(mock_plot, property_name).return_value == value
        getattr(mock_object, pascal_name).assert_called_once_with(value)

    @pytest.mark.parametrize(
        "index, value", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_FLOAT]
    )
    def test_set_fixed_indp_var_value(self, mock_plot: Plot, mock_object, index, value):
        """
        Test setting fixed independent variable value.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        mock_plot.set_fixed_indp_var_value(index, value)
        mock_object.SetFixedIndpVarValue.assert_called_once_with(index, value)

    @pytest.mark.parametrize(
        "index, value", [(x, 0.1) for x in INVALID_INT] + [(1, x) for x in INVALID_FLOAT]
    )
    def test_set_fixed_indp_var_value_invalid(self, mock_plot: Plot, mock_object, index, value, _):
        """
        Test setting fixed independent variable value.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.set_fixed_indp_var_value(index, value)
        assert _("Invalid") in str(e.value)
        mock_object.SetFixedIndpVarValue.assert_not_called()

    @pytest.mark.parametrize(
        "value, max_number, should_be", [(1, 2, 1), (2, 1, 1), (0, 1, 0), (0, 0, 0), (1, 1, 1)]
    )
    # pylint: disable-next=R0913, R0917
    def test_active_indp_var(self, mock_plot: Plot, mock_object, value, max_number, should_be):
        """
        Test ActiveIndpVar method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        mock_object.GetNumberOfIndpVars = max_number
        mock_plot.active_indp_var = value
        mock_object.SetActiveIndpVar.assert_called_once_with(should_be)

    @pytest.mark.parametrize(
        "pascal_name, property_name, expected_type, expected",
        [("WarpQueryBegin", "warp_query_begin", bool, x) for x in VALID_BOOL]
        + [("RestoreOriginalPosition", "restore_original_position", bool, x) for x in VALID_BOOL],
    )
    # pylint: disable-next=R0913, R0917
    def test_expected(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, expected_type, expected
    ):
        """

        Test WarpQueryBegin method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        setattr(mock_object, pascal_name, expected)
        result = getattr(mock_plot, property_name)()
        assert isinstance(result, expected_type)
        assert result == expected

    def test_wrap_query_end(self, mock_plot: Plot, mock_object):
        """
        Test WarpQueryEnd method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        mock_plot.warp_query_end()
        mock_object.WarpQueryEnd.assert_called_once()

    @pytest.mark.parametrize(
        "node_id, expected", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    # pylint: disable-next=R0913, R0917
    def test_warp_query_node(
        self, mock_plot: Plot, mock_object, mock_double_array, node_id, expected
    ):
        """
        Test WarpQueryNode method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            node_id: Node ID to query.
            return_value: Expected return value.
        """
        mock_object.WarpQueryNode.return_value = expected
        result = mock_plot.warp_query_node(node_id, mock_double_array)
        assert result is expected
        mock_object.WarpQueryNode.assert_called_once_with(node_id, mock_double_array.double_array)

    @pytest.mark.parametrize("node_id", INVALID_INT)
    def test_warp_query_node_invalid_type(
        self, mock_plot: Plot, mock_object, mock_double_array, node_id, _
    ):
        """
        Test WarpQueryNode method of Plot with invalid node ID.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.warp_query_node(node_id, mock_double_array)
        assert _("Invalid") in str(e.value)
        mock_object.WarpQueryNode.assert_not_called()

    @pytest.mark.parametrize("node_id", [-1, -2, -3])
    def test_warp_query_node_invalid_value(
        self, mock_plot: Plot, mock_object, mock_double_array, node_id, _
    ):
        """
        Test WarpQueryNode method of Plot with invalid value.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(ValueError) as e:
            mock_plot.warp_query_node(node_id, mock_double_array)
        assert _("Invalid") in str(e.value)
        mock_object.WarpQueryNode.assert_not_called()

    @pytest.mark.parametrize(
        "index, expected", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    # pylint: disable-next=R0913, R0917
    def test_get_probe_plot_probe_line(
        self, mock_plot: Plot, mock_object, mock_vector, index, expected
    ):
        """
        Test get_probe_plot_probe_line method of Plot.
        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            index: Index of the probe line.
            expected: Expected return value.
        """
        mock_object.GetProbePlotProbeLine.return_value = expected
        result = mock_plot.get_probe_plot_probe_line(index, mock_vector, mock_vector)
        assert result is expected
        mock_object.GetProbePlotProbeLine.assert_called_once_with(
            index, mock_vector.vector, mock_vector.vector
        )

    @pytest.mark.parametrize("index", INVALID_INT)
    def test_get_probe_plot_probe_line_invalid_type(
        self, mock_plot: Plot, mock_object, mock_vector, index, _
    ):
        """
        Test get_probe_plot_probe_line method of Plot with invalid index.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.get_probe_plot_probe_line(index, mock_vector, mock_vector)
        assert _("Invalid") in str(e.value)
        mock_object.GetProbePlotProbeLine.assert_not_called()

    @pytest.mark.parametrize("index", [-1, -2, -3])
    def test_get_probe_plot_probe_line_invalid_value(
        self, mock_plot: Plot, mock_object, mock_vector, index, _
    ):
        """
        Test get_probe_plot_probe_line method of Plot with invalid value.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(ValueError) as e:
            mock_plot.get_probe_plot_probe_line(index, mock_vector, mock_vector)
        assert _("Invalid") in str(e.value)
        mock_object.GetProbePlotProbeLine.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_add_probe_plot_probe_line(self, mock_plot: Plot, mock_object, mock_vector, expected):
        """
        Test add_probe_plot_probe_line method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            expected: Expected return value.
        """
        mock_object.AddProbePlotProbeLine.return_value = expected
        result = mock_plot.add_probe_plot_probe_line(mock_vector, mock_vector)
        assert result is expected
        mock_object.AddProbePlotProbeLine.assert_called_once_with(
            mock_vector.vector, mock_vector.vector
        )

    @pytest.mark.parametrize(
        "index, expected", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    # pylint: disable-next=R0913, R0917
    def test_set_probe_plot_probe_line(
        self, mock_plot: Plot, mock_object, mock_vector, index, expected
    ):
        """
        Test set_probe_plot_probe_line method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            index: Index of the probe line.
            expected: Expected return value.
        """
        mock_object.SetProbePlotProbeLine.return_value = expected
        result = mock_plot.set_probe_plot_probe_line(index, mock_vector, mock_vector)
        assert result is expected
        mock_object.SetProbePlotProbeLine.assert_called_once_with(
            index, mock_vector.vector, mock_vector.vector
        )

    @pytest.mark.parametrize("index", INVALID_INT)
    def test_set_probe_plot_probe_line_invalid_type(
        self, mock_plot: Plot, mock_object, mock_vector, index, _
    ):
        """
        Test set_probe_plot_probe_line method of Plot with invalid index.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.set_probe_plot_probe_line(index, mock_vector, mock_vector)
        assert _("Invalid") in str(e.value)
        mock_object.SetProbePlotProbeLine.assert_not_called()

    @pytest.mark.parametrize("index", [-1, -2, -3])
    def test_set_probe_plot_probe_line_invalid_value(
        self, mock_plot: Plot, mock_object, mock_vector, index, _
    ):
        """
        Test set_probe_plot_probe_line method of Plot with invalid value.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(ValueError) as e:
            mock_plot.set_probe_plot_probe_line(index, mock_vector, mock_vector)
        assert _("Invalid") in str(e.value)
        mock_object.SetProbePlotProbeLine.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("GetSingleColor", "single_color"),
            (
                "GetShrinkageCompensationEstimatedShrinkage",
                "shrinkage_compensation_estimated_shrinkage",
            ),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_vector_param_func(
        self, mock_plot: Plot, mock_object, mock_vector, pascal_name, property_name
    ):
        """
        Test single_color method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        setattr(mock_object, pascal_name, mock_vector.vector)
        result = getattr(mock_plot, property_name)
        assert isinstance(result, Vector)
        assert result.vector == mock_vector.vector

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("GetSingleColor", "single_color"),
            (
                "GetShrinkageCompensationEstimatedShrinkage",
                "shrinkage_compensation_estimated_shrinkage",
            ),
        ],
    )
    def test_vector_param_func_invalid(
        self, mock_plot: Plot, mock_object, pascal_name, property_name
    ):
        """
        Test single_color method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        setattr(mock_object, pascal_name, None)
        assert getattr(mock_plot, property_name) is None

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("SetSingleColor", "single_color"),
            (
                "SetShrinkageCompensationEstimatedShrinkage",
                "shrinkage_compensation_estimated_shrinkage",
            ),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_vector_param_func(
        self, mock_plot: Plot, mock_object, mock_vector, pascal_name, property_name
    ):
        """
        Test single_color method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        setattr(mock_plot, property_name, mock_vector)
        getattr(mock_object, pascal_name).assert_called_once_with(mock_vector.vector)

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("AddXYPlotCurve", "add_xy_plot_curve"),
            ("DeleteXYPlotCurve", "delete_xy_plot_curve"),
            ("SetPlotNodesFromEntList", "set_plot_nodes_from_ent_list"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_ent_list_param_func(
        self, mock_plot: Plot, mock_object, mock_ent_list, pascal_name, property_name
    ):
        """
        Test single_color method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        getattr(mock_plot, property_name)(mock_ent_list)
        getattr(mock_object, pascal_name).assert_called_once_with(mock_ent_list.ent_list)

    @pytest.mark.parametrize("expected", VALID_BOOL)
    def test_apply_best_fit(self, mock_plot: Plot, mock_object, mock_ent_list, expected):
        """
        Test single_color method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        mock_object.ApplyBestFit.return_value = expected
        result = mock_plot.apply_best_fit(mock_ent_list)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.ApplyBestFit.assert_called_once_with(mock_ent_list.ent_list)

    @pytest.mark.parametrize("nodes", VALID_STR)
    def test_set_plot_nodes_from_string(self, mock_plot: Plot, mock_object, nodes):
        """
        Test set_plot_nodes_from_string method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            nodes: Nodes to set.
        """
        mock_plot.set_plot_nodes_from_string(nodes)
        mock_object.SetPlotNodesFromString.assert_called_once_with(nodes)

    @pytest.mark.parametrize("nodes", INVALID_STR)
    def test_set_plot_nodes_from_string_invalid(self, mock_plot: Plot, mock_object, nodes, _):
        """
        Test set_plot_nodes_from_string method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            nodes: Nodes to set.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.set_plot_nodes_from_string(nodes)
        assert _("Invalid") in str(e.value)
        mock_object.SetPlotNodesFromString.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, param1, param2, expected_type, expected",
        [
            ("AddProbePlane", "add_probe_plane", x, y, bool, z)
            for x in VALID_STR
            for y in VALID_STR
            for z in VALID_BOOL
        ]
        + [
            ("SetPlotTolerance", "set_plot_tolerance", x, y, bool, z)
            for x in VALID_STR
            for y in VALID_STR
            for z in VALID_BOOL
        ]
        + [
            ("SetPathlineInjectionLocation", "set_pathline_injection_location", x, y, bool, z)
            for x in VALID_STR
            for y in VALID_BOOL
            for z in VALID_BOOL
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_two_param(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        param1,
        param2,
        expected_type,
        expected,
    ):
        """
        Test add_probe_plane method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_plot, property_name)(param1, param2)
        assert isinstance(result, expected_type)
        assert result == expected
        getattr(mock_object, pascal_name).assert_called_once_with(param1, param2)

    @pytest.mark.parametrize(
        "pascal_name, property_name, param1, param2",
        [("AddProbePlane", "add_probe_plane", x, y) for x in INVALID_STR for y in VALID_STR]
        + [("AddProbePlane", "add_probe_plane", x, y) for x in VALID_STR for y in INVALID_STR]
        + [("SetPlotTolerance", "set_plot_tolerance", x, y) for x in INVALID_STR for y in VALID_STR]
        + [("SetPlotTolerance", "set_plot_tolerance", x, y) for x in VALID_STR for y in INVALID_STR]
        + [
            ("SetPathlineInjectionLocation", "set_pathline_injection_location", x, y)
            for x in INVALID_STR
            for y in VALID_BOOL
        ]
        + [
            ("SetPathlineInjectionLocation", "set_pathline_injection_location", x, y)
            for x in VALID_STR
            for y in INVALID_BOOL
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_two_param_invalid(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, param1, param2, _
    ):
        """
        Test add_probe_plane method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(param1, param2)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "normal, point",
        [(x, y) for x in VALID_STR for y in INVALID_STR]
        + [(x, y) for x in INVALID_STR for y in VALID_STR],
    )
    def test_add_probe_plane_invalid(self, mock_plot: Plot, mock_object, normal, point, _):
        """
        Test add_probe_plane method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.add_probe_plane(normal, point)
        assert _("Invalid") in str(e.value)
        mock_object.AddProbePlane.assert_not_called()

    def test_reset_probe_plane(self, mock_plot: Plot, mock_object):
        """
        Test reset_probe_plane method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        mock_plot.reset_probe_plane()
        mock_object.ResetProbePlane.assert_called_once()

    @pytest.mark.parametrize(
        "pascal_name, property_name, trace_mode, expected_trace_mode",
        [("GetPathlineDensity", "get_pathline_density", x, x.value) for x in TraceModes]
        + [
            ("GetPathlineTraceSize", "get_pathline_trace_size", x.value, x.value)
            for x in TraceModes
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_pathline_trace_mode_param_func(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        trace_mode,
        expected_trace_mode,
    ):
        """
        Test get_pathline_density method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            trace_mode: Trace mode to set.
        """
        getattr(mock_object, pascal_name).return_value = 1
        result = getattr(mock_plot, property_name)(trace_mode)
        assert isinstance(result, int)
        assert result == 1
        getattr(mock_object, pascal_name).assert_called_once_with(expected_trace_mode)

    @pytest.mark.parametrize(
        "pascal_name, property_name, trace_mode",
        [("GetPathlineDensity", "get_pathline_density", x) for x in INVALID_INT]
        + [("GetPathlineTraceSize", "get_pathline_trace_size", x) for x in INVALID_INT],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_pathline_trace_mode_param_func_invalid_type(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, trace_mode, _
    ):
        """

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            trace_mode: Trace mode to set.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(trace_mode)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, trace_mode",
        [("GetPathlineDensity", "get_pathline_density", x) for x in [-1, -2, -3, 2, 3, 100]]
        + [("GetPathlineTraceSize", "get_pathline_trace_size", x) for x in [-1, -2, -3, 2, 3, 100]],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_pathline_trace_mode_param_func_invalid_value(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, trace_mode, _, caplog
    ):
        """
        Test get_pathline_density method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            trace_mode: Trace mode to set.
        """
        getattr(mock_plot, property_name)(trace_mode)
        assert _("this may cause function call to fail") in caplog.text
        getattr(mock_object, pascal_name).assert_called_once_with(trace_mode)

    @pytest.mark.parametrize(
        "pascal_name, property_name, trace_mode, expected_trace_mode, value, expected",
        [
            ("SetPathlineDensity", "set_pathline_density", x, x.value, y, z)
            for x in TraceModes
            for y in [0, 1, 2, 100, 30]
            for z in VALID_BOOL
        ]
        + [
            ("SetPathlineDensity", "set_pathline_density", x.value, x.value, y, z)
            for x in TraceModes
            for y in [0, 1, 2, 100, 30]
            for z in VALID_BOOL
        ]
        + [
            ("SetPathlineTraceSize", "set_pathline_trace_size", x, x.value, y, z)
            for x in TraceModes
            for y in [0, 1, 2, 10, 3]
            for z in VALID_BOOL
        ]
        + [
            ("SetPathlineTraceSize", "set_pathline_trace_size", x.value, x.value, y, z)
            for x in TraceModes
            for y in [0, 1, 2, 10, 3]
            for z in VALID_BOOL
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_trace_mode_param_func(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        trace_mode,
        expected_trace_mode,
        value,
        expected,
    ):
        """
        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            trace_mode: Trace mode to set.
            value: value to set.
        """
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_plot, property_name)(trace_mode, value)
        assert isinstance(result, bool)
        assert result is expected
        getattr(mock_object, pascal_name).assert_called_once_with(expected_trace_mode, value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, trace_mode, value",
        [
            ("SetPathlineDensity", "set_pathline_density", x, y)
            for x in [-1, -2, 2, 3, 100]
            for y in [0, 1, 2, 100, 30]
        ]
        + [
            ("SetPathlineTraceSize", "set_pathline_trace_size", x, y)
            for x in [-1, -2, 2, 3, 100]
            for y in [0, 1, 2, 10, 3]
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_trace_mode_param_func_invalid_enum(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, trace_mode, value, _, caplog
    ):
        """
        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            trace_mode: Trace mode to set.
            value: Density value to set.
        """
        getattr(mock_plot, property_name)(trace_mode, value)
        getattr(mock_object, pascal_name).assert_called_once_with(trace_mode, value)
        assert _("this may cause function call to fail") in caplog.text

    @pytest.mark.parametrize(
        "pascal_name, property_name, trace_mode, value",
        [
            ("SetPathlineDensity", "set_pathline_density", x, y)
            for x in TraceModes
            for y in [-1, -2, -3, 101, 102]
        ]
        + [
            ("SetPathlineTraceSize", "set_pathline_trace_size", x, y)
            for x in TraceModes
            for y in [-1, -2, -3, 11, 102]
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_trace_mode_param_func_invalid_value(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, trace_mode, value, _
    ):
        """
        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            trace_mode: Trace mode to set.
            value: Density value to set.
        """
        with pytest.raises(ValueError) as e:
            getattr(mock_plot, property_name)(trace_mode, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize("ds_id, expected", [(x, y) for x in VALID_INT for y in VALID_STR])
    def test_get_pathline_result_name(self, mock_plot: Plot, mock_object, ds_id, expected):
        """
        Test get_pathline_result_name method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            ds_id: Data source ID.
        """
        mock_object.GetPathlineResultName.return_value = expected
        result = mock_plot.get_pathline_result_name(ds_id)
        assert isinstance(result, str)
        assert result == expected
        mock_object.GetPathlineResultName.assert_called_once_with(ds_id)

    @pytest.mark.parametrize("ds_id", INVALID_INT)
    def test_get_pathline_result_name_invalid_type(self, mock_plot: Plot, mock_object, ds_id, _):
        """
        Test get_pathline_result_name method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            ds_id: Data source ID.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.get_pathline_result_name(ds_id)
        assert _("Invalid") in str(e.value)
        mock_object.GetPathlineResultName.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_type, expected_scale_type, result_id, expected",
        [
            ("GetPathlineResultMin", "get_pathline_result_min", x, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("GetPathlineResultMin", "get_pathline_result_min", x.value, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("GetPathlineResultMax", "get_pathline_result_max", x, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("GetPathlineResultMax", "get_pathline_result_max", x.value, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_pathline_result_min_max(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_type,
        expected_scale_type,
        result_id,
        expected,
    ):
        """
        Test get_pathline_result_min and get_pathline_result_max methods of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            type_id: Type ID.
            result_id: Result ID.
            expected: Expected return value.
        """
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_plot, property_name)(scale_type, result_id)
        assert isinstance(result, (float, int))
        assert result == expected
        getattr(mock_object, pascal_name).assert_called_once_with(expected_scale_type, result_id)

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_type, result_id",
        [
            ("GetPathlineResultMin", "get_pathline_result_min", x, y)
            for x in INVALID_INT
            for y in NON_NEGATIVE_INT
        ]
        + [
            ("GetPathlineResultMin", "get_pathline_result_min", x, y)
            for x in ScaleTypes
            for y in INVALID_INT
        ]
        + [
            ("GetPathlineResultMax", "get_pathline_result_max", x, y)
            for x in INVALID_INT
            for y in NON_NEGATIVE_INT
        ]
        + [
            ("GetPathlineResultMax", "get_pathline_result_max", x, y)
            for x in ScaleTypes
            for y in INVALID_INT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_pathline_result_min_max_invalid_type(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, scale_type, result_id, _
    ):
        """
        Test get_pathline_result_min and get_pathline_result_max methods of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            type_id: Type ID.
            result_id: Result ID.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(scale_type, result_id)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_type, result_id",
        [
            ("GetPathlineResultMin", "get_pathline_result_min", x, y)
            for x in [-1, -2, -3, 3, 100]
            for y in NON_NEGATIVE_INT
        ]
        + [
            ("GetPathlineResultMax", "get_pathline_result_max", x, y)
            for x in [-1, -2, -3, 3, 100]
            for y in NON_NEGATIVE_INT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_pathline_result_min_max_invalid_value(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_type,
        result_id,
        _,
        caplog,
    ):
        """
        Test get_pathline_result_min and get_pathline_result_max methods of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            type_id: Type ID.
            result_id: Result ID.
        """
        getattr(mock_plot, property_name)(scale_type, result_id)
        assert _("this may cause function call to fail") in caplog.text
        getattr(mock_object, pascal_name).assert_called_once_with(scale_type, result_id)

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_type, expected_scale_type, result_id, result_value",
        [
            ("SetPathlineResultMin", "set_pathline_result_min", x, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMin", "set_pathline_result_min", x.value, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMax", "set_pathline_result_max", x, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMax", "set_pathline_result_max", x.value, x.value, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_result_min_max(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_type,
        expected_scale_type,
        result_id,
        result_value,
    ):
        """
        Test set_pathline_result_min and set_pathline_result_max methods of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            type_id: Type ID.
            result_id: Result ID.
            result_value: Result value to set.
        """
        getattr(mock_plot, property_name)(scale_type, result_id, result_value)
        getattr(mock_object, pascal_name).assert_called_once_with(
            expected_scale_type, result_id, result_value
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_type, result_id, result_value",
        [
            ("SetPathlineResultMin", "set_pathline_result_min", x, y, z)
            for x in INVALID_INT
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMin", "set_pathline_result_min", x, y, z)
            for x in ScaleTypes
            for y in INVALID_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMin", "set_pathline_result_min", x, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in INVALID_FLOAT
        ]
        + [
            ("SetPathlineResultMax", "set_pathline_result_max", x, y, z)
            for x in INVALID_INT
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMax", "set_pathline_result_max", x, y, z)
            for x in ScaleTypes
            for y in INVALID_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMax", "set_pathline_result_max", x, y, z)
            for x in ScaleTypes
            for y in NON_NEGATIVE_INT
            for z in INVALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_result_min_max_invalid_type(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_type,
        result_id,
        result_value,
        _,
    ):
        """
        Test set_pathline_result_min and set_pathline_result_max methods of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            type_id: Type ID.
            result_id: Result ID.
            result_value: Result value to set.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(scale_type, result_id, result_value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_type, result_id, result_value",
        [
            ("SetPathlineResultMin", "set_pathline_result_min", x, y, z)
            for x in [-1, -2, -3, 3, 100]
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ]
        + [
            ("SetPathlineResultMax", "set_pathline_result_max", x, y, z)
            for x in [-1, -2, -3, 3, 100]
            for y in NON_NEGATIVE_INT
            for z in VALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_result_min_max_invalid_value(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_type,
        result_id,
        result_value,
        _,
        caplog,
    ):
        """
        Test set_pathline_result_min and set_pathline_result_max methods of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            type_id: Type ID.
            result_id: Result ID.
            result_value: Result value to set.
        """
        getattr(mock_plot, property_name)(scale_type, result_id, result_value)
        getattr(mock_object, pascal_name).assert_called_once_with(
            scale_type, result_id, result_value
        )
        assert _("this may cause function call to fail") in caplog.text

    @pytest.mark.parametrize(
        "result_id, expected", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    def test_get_pathline_result_use_specified_values(
        self, mock_plot: Plot, mock_object, result_id, expected
    ):
        """
        Test get_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
            expected: Expected return value.
        """
        mock_object.GetPathlineResultUseSpecifiedValues.return_value = expected
        result = mock_plot.get_pathline_result_use_specified_values(result_id)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.GetPathlineResultUseSpecifiedValues.assert_called_once_with(result_id)

    @pytest.mark.parametrize("result_id", INVALID_INT)
    def test_get_pathline_result_use_specified_values_invalid_type(
        self, mock_plot: Plot, mock_object, result_id, _
    ):
        """
        Test get_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.get_pathline_result_use_specified_values(result_id)
        assert _("Invalid") in str(e.value)
        mock_object.GetPathlineResultUseSpecifiedValues.assert_not_called()

    @pytest.mark.parametrize(
        "result_id, use_specified, expected",
        [(x, y, z) for x in NON_NEGATIVE_INT for y in VALID_BOOL for z in VALID_BOOL],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_result_use_specified(
        self, mock_plot: Plot, mock_object, result_id, use_specified, expected
    ):
        """
        Test set_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
            expected: Expected return value.
        """
        mock_object.SetPathlineResultUseSpecifiedValues.return_value = expected
        result = mock_plot.set_pathline_result_use_specified_values(result_id, use_specified)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.SetPathlineResultUseSpecifiedValues.assert_called_once_with(
            result_id, use_specified
        )

    @pytest.mark.parametrize(
        "result_id, use_specified",
        [(x, y) for x in INVALID_INT for y in VALID_BOOL]
        + [(x, y) for x in NON_NEGATIVE_INT for y in INVALID_BOOL],
    )
    def test_set_pathline_result_use_specified_invalid_type(
        self, mock_plot: Plot, mock_object, result_id, use_specified, _
    ):
        """
        Test set_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.set_pathline_result_use_specified_values(result_id, use_specified)
        assert _("Invalid") in str(e.value)
        mock_object.SetPathlineResultUseSpecifiedValues.assert_not_called()

    @pytest.mark.parametrize(
        "result_id, expected", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    def test_get_pathline_result_are_settings_valid(
        self, mock_plot: Plot, mock_object, result_id, expected
    ):
        """
        Test get_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
            expected: Expected return value.
        """
        mock_object.GetPathlineResultAreSettingsValid.return_value = expected
        result = mock_plot.get_pathline_result_are_settings_valid(result_id)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.GetPathlineResultAreSettingsValid.assert_called_once_with(result_id)

    @pytest.mark.parametrize("result_id", INVALID_INT)
    def test_get_pathline_result_are_settings_valid_invalid_type(
        self, mock_plot: Plot, mock_object, result_id, _
    ):
        """
        Test get_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.get_pathline_result_are_settings_valid(result_id)
        assert _("Invalid") in str(e.value)
        mock_object.GetPathlineResultAreSettingsValid.assert_not_called()

    @pytest.mark.parametrize(
        "result_id, expected", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    def test_get_pathline_result_use_extended_colour(
        self, mock_plot: Plot, mock_object, result_id, expected
    ):
        """
        Test get_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
            expected: Expected return value.
        """
        mock_object.GetPathlineResultUseExtendedColour.return_value = expected
        result = mock_plot.get_pathline_result_use_extended_colour(result_id)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.GetPathlineResultUseExtendedColour.assert_called_once_with(result_id)

    @pytest.mark.parametrize("result_id", INVALID_INT)
    def test_get_pathline_result_use_extended_colour_invalid_type(
        self, mock_plot: Plot, mock_object, result_id, _
    ):
        """
        Test get_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.get_pathline_result_use_extended_colour(result_id)
        assert _("Invalid") in str(e.value)
        mock_object.GetPathlineResultUseExtendedColour.assert_not_called()

    @pytest.mark.parametrize(
        "result_id, use_extended_colour", [(x, y) for x in NON_NEGATIVE_INT for y in VALID_BOOL]
    )
    # pylint: disable-next=R0913, R0917
    def test_set_pathline_result_use_extended_colour(
        self, mock_plot: Plot, mock_object, result_id, use_extended_colour
    ):
        """
        Test set_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
            expected: Expected return value.
        """
        mock_plot.set_pathline_result_use_extended_colour(result_id, use_extended_colour)
        mock_object.SetPathlineResultUseExtendedColour.assert_called_once_with(
            result_id, use_extended_colour
        )

    @pytest.mark.parametrize(
        "result_id, use_extended_colour",
        [(x, y) for x in INVALID_INT for y in VALID_BOOL]
        + [(x, y) for x in NON_NEGATIVE_INT for y in INVALID_BOOL],
    )
    def test_set_pathline_result_use_extended_colour_invalid_type(
        self, mock_plot: Plot, mock_object, result_id, use_extended_colour, _
    ):
        """
        Test set_pathline_result_use_specified method of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            result_id: Result ID.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.set_pathline_result_use_extended_colour(result_id, use_extended_colour)
        assert _("Invalid") in str(e.value)
        mock_object.SetPathlineResultUseExtendedColour.assert_not_called()

    def test_save_xy_plot_curve_data(self, mock_plot: Plot, mock_object):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
        """
        file_name = "sample.txt"
        mock_object.SaveXYPlotCurveData.return_value = True
        result = mock_plot.save_xy_plot_curve_data(file_name)
        assert isinstance(result, bool)
        assert result is True
        mock_object.SaveXYPlotCurveData.assert_called_once_with(file_name)

    @pytest.mark.parametrize("file_name", INVALID_STR)
    def test_save_xy_plot_curve_data_invalid_type(self, mock_plot: Plot, mock_object, file_name, _):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            file_name: File name to save to.
        """
        with pytest.raises(TypeError) as e:
            mock_plot.save_xy_plot_curve_data(file_name)
        assert _("Invalid") in str(e.value)
        mock_object.SaveXYPlotCurveData.assert_not_called()

    def test_save_xy_plot_curve_data_save_error(self, mock_plot: Plot, mock_object, _):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            file_name: File name to save to.
        """
        file_name = "sample.txt"
        getattr(mock_object, "SaveXYPlotCurveData").return_value = False
        with pytest.raises(SaveError) as e:
            mock_plot.save_xy_plot_curve_data(file_name)
        assert _("Save Error") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, file_name, unit_sys, unit_sys_expected",
        [("SaveResultInXML", "save_result_in_xml", "sample.xml", x, x.value) for x in SystemUnits]
        + [
            ("SaveResultInXML", "save_result_in_xml", "sample.xml", x.value, x.value)
            for x in SystemUnits
        ]
        + [("SaveResultInXML", "save_result_in_xml", "sample.xml", "", "")]
        + [
            ("SaveResultInPatran", "save_result_in_patran", "sample.ele", x, x.value)
            for x in SystemUnits
        ]
        + [
            ("SaveResultInPatran", "save_result_in_patran", "sample.ele", x.value, x.value)
            for x in SystemUnits
        ]
        + [("SaveResultInPatran", "save_result_in_patran", "sample.ele", "", "")],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        file_name,
        unit_sys,
        unit_sys_expected,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
            unit_sys: Unit system to use.
        """
        pascal_name2 = f"{pascal_name}2"
        getattr(mock_object, pascal_name).return_value = True
        getattr(mock_object, pascal_name2).return_value = True
        result = getattr(mock_plot, property_name)(file_name, unit_sys)
        getattr(mock_object, pascal_name).assert_not_called()
        getattr(mock_object, pascal_name2).assert_called_once_with(file_name, unit_sys_expected)
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.parametrize(
        "pascal_name, property_name, file_name, unit_sys",
        [
            ("SaveResultInXML", "save_result_in_xml", x, y)
            for x in INVALID_STR
            for y in SYSTEM_UNITS_AND_NONE
        ]
        + [
            ("SaveResultInXML", "save_result_in_xml", "sample.xml", x)
            for x in INVALID_STR
            if x is not None
        ]
        + [
            ("SaveResultInPatran", "save_result_in_patran", x, y)
            for x in INVALID_STR
            for y in SYSTEM_UNITS_AND_NONE
        ]
        + [
            ("SaveResultInPatran", "save_result_in_patran", "sample.ele", x)
            for x in INVALID_STR
            if x is not None
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2_invalid_type(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, file_name, unit_sys, _
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
        """
        pascal_name2 = f"{pascal_name}2"
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(file_name, unit_sys)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()
        getattr(mock_object, pascal_name2).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, file_name, unit_sys",
        [("SaveResultInXML", "save_result_in_xml", "sample.xml", x.value) for x in SystemUnits]
        + [
            ("SaveResultInPatran", "save_result_in_patran", "sample.ele", x.value)
            for x in SystemUnits
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2_save_error(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, file_name, unit_sys, _
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
        """
        pascal_name2 = f"{pascal_name}2"
        getattr(mock_object, pascal_name2).return_value = False
        with pytest.raises(SaveError) as e:
            getattr(mock_plot, property_name)(file_name, unit_sys)
        assert _("Save Error") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, inc_frames, scale_factor, binary, unit_sys, unit_sys_expected",
        [
            ("SaveResultInFBX", "save_result_in_fbx", x, y, z, u, u.value)
            for x in VALID_BOOL
            for y in VALID_FLOAT
            for z in VALID_BOOL
            for u in SystemUnits
        ]
        + [
            ("SaveResultInFBX", "save_result_in_fbx", x, y, z, u.value, u.value)
            for x in VALID_BOOL
            for y in VALID_FLOAT
            for z in VALID_BOOL
            for u in SystemUnits
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        inc_frames,
        scale_factor,
        binary,
        unit_sys,
        unit_sys_expected,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
            inc_frames: Number of incremental frames.
            scale_factor: Scale factor for the output.
            binary: Whether to save the output as binary.
            unit_sys: Unit system to use.
        """
        file_name = "sample.fbx"
        getattr(mock_object, pascal_name).return_value = True
        result = getattr(mock_plot, property_name)(
            file_name, inc_frames, scale_factor, binary, unit_sys
        )
        assert isinstance(result, bool)
        assert result is True
        getattr(mock_object, pascal_name).assert_called_once_with(
            file_name, inc_frames, scale_factor, binary, unit_sys_expected
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name, inc_frames, scale_factor, binary, unit_sys",
        [
            ("SaveResultInFBX", "save_result_in_fbx", x, y, z, w)
            for x in INVALID_BOOL
            for y in VALID_FLOAT
            for z in VALID_BOOL
            for w in SystemUnits
        ]
        + [
            ("SaveResultInFBX", "save_result_in_fbx", x, y, z, w)
            for x in VALID_BOOL
            for y in INVALID_FLOAT
            for z in VALID_BOOL
            for w in SystemUnits
        ]
        + [
            ("SaveResultInFBX", "save_result_in_fbx", x, y, z, w)
            for x in VALID_BOOL
            for y in VALID_FLOAT
            for z in INVALID_BOOL
            for w in SystemUnits
        ]
        + [
            ("SaveResultInFBX", "save_result_in_fbx", x, y, z, w)
            for x in VALID_BOOL
            for y in VALID_FLOAT
            for z in VALID_BOOL
            for w in INVALID_STR
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions_invalid_type(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        inc_frames,
        scale_factor,
        binary,
        unit_sys,
        _,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
        """
        file_name = "sample.fbx"
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(file_name, inc_frames, scale_factor, binary, unit_sys)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, inc_frames, scale_factor, binary, unit_sys",
        [
            ("SaveResultInFBX", "save_result_in_fbx", y, z, w, u)
            for y in VALID_BOOL
            for z in VALID_FLOAT
            for w in VALID_BOOL
            for u in SystemUnits
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions_save_error(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        inc_frames,
        scale_factor,
        binary,
        unit_sys,
        _,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
        """
        file_name = "sample.fbx"
        getattr(mock_object, pascal_name).return_value = False
        with pytest.raises(SaveError) as e:
            getattr(mock_plot, property_name)(file_name, inc_frames, scale_factor, binary, unit_sys)
        assert _("Save Error") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_factor, binary, unit_sys, unit_sys_expected",
        [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, z, z.value)
            for x in VALID_FLOAT
            for y in VALID_BOOL
            for z in SystemUnits
        ]
        + [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, z.value, z.value)
            for x in VALID_FLOAT
            for y in VALID_BOOL
            for z in SystemUnits
        ]
        + [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, "", "")
            for x in VALID_FLOAT
            for y in VALID_BOOL
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2_warped(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_factor,
        binary,
        unit_sys,
        unit_sys_expected,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
            unit_sys: Unit system to use.
        """
        file_name = "sample.stl"
        pascal_name2 = f"{pascal_name}2"
        getattr(mock_object, pascal_name).return_value = True
        getattr(mock_object, pascal_name2).return_value = True
        result = getattr(mock_plot, property_name)(file_name, scale_factor, binary, unit_sys)
        assert isinstance(result, bool)
        assert result is True

        if unit_sys_expected is None:
            unit_sys_expected = ""
        getattr(mock_object, pascal_name).assert_not_called()
        getattr(mock_object, pascal_name2).assert_called_once_with(
            file_name, scale_factor, binary, unit_sys_expected
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_factor, binary, unit_sys",
        [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, z)
            for x in INVALID_FLOAT
            for y in VALID_BOOL
            for z in SYSTEM_UNITS_AND_NONE
        ]
        + [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, z)
            for x in VALID_FLOAT
            for y in INVALID_BOOL
            for z in SYSTEM_UNITS_AND_NONE
        ]
        + [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, z)
            for x in VALID_FLOAT
            for y in VALID_BOOL
            for z in INVALID_STR
            if z is not None
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2_warped_invalid_type(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_factor,
        binary,
        unit_sys,
        _,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
        """
        file_name = "sample.stl"
        pascal_name2 = f"{pascal_name}2"
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(file_name, scale_factor, binary, unit_sys)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()
        getattr(mock_object, pascal_name2).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, scale_factor, binary, unit_sys",
        [
            ("SaveWarpedShapeInSTL", "save_warped_shape_in_stl", x, y, z)
            for x in VALID_FLOAT
            for y in VALID_BOOL
            for z in SystemUnits
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2_warped_save_error(
        self,
        mock_plot: Plot,
        mock_object,
        pascal_name,
        property_name,
        scale_factor,
        binary,
        unit_sys,
        _,
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
        """
        file_name = "sample.stl"
        pascal_name2 = f"{pascal_name}2"
        getattr(mock_object, pascal_name).return_value = False
        getattr(mock_object, pascal_name2).return_value = False
        with pytest.raises(SaveError) as e:
            getattr(mock_plot, property_name)(file_name, scale_factor, binary, unit_sys)
        assert _("Save Error") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, file_name, scale_factor",
        [("SaveWarpedShapeInCAD", "save_warped_shape_in_cad", "sample.cad", x) for x in VALID_FLOAT]
        + [
            ("SaveWarpedShapeInUDM", "save_warped_shape_in_udm", "sample.udm", x)
            for x in VALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions_warped(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, file_name, scale_factor
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
            unit_sys: Unit system to use.
        """
        getattr(mock_object, pascal_name).return_value = True
        result = getattr(mock_plot, property_name)(file_name, scale_factor)
        assert isinstance(result, bool)
        assert result is True
        getattr(mock_object, pascal_name).assert_called_once_with(file_name, scale_factor)

    @pytest.mark.parametrize(
        "pascal_name, property_name, file_name, scale_factor",
        [
            ("SaveWarpedShapeInCAD", "save_warped_shape_in_cad", "sample.cad", y)
            for y in INVALID_FLOAT
        ]
        + [
            ("SaveWarpedShapeInCAD", "save_warped_shape_in_cad", x, y)
            for x in INVALID_STR
            for y in VALID_FLOAT
        ]
        + [
            ("SaveWarpedShapeInUDM", "save_warped_shape_in_udm", "sample.udm", y)
            for y in INVALID_FLOAT
        ]
        + [
            ("SaveWarpedShapeInUDM", "save_warped_shape_in_udm", x, y)
            for x in INVALID_STR
            for y in VALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions_warped_invalid_type(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, file_name, scale_factor, _
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
            file_name: File name to save to.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_plot, property_name)(file_name, scale_factor)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, file_name, scale_factor",
        [("SaveWarpedShapeInCAD", "save_warped_shape_in_cad", "sample.cad", y) for y in VALID_FLOAT]
        + [
            ("SaveWarpedShapeInUDM", "save_warped_shape_in_udm", "sample.udm", y)
            for y in VALID_FLOAT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions_warped_save_error(
        self, mock_plot: Plot, mock_object, pascal_name, property_name, file_name, scale_factor, _
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
            pascal_name: Pascal case name of the property.
            property_name: Name of the property to test.
        """
        getattr(mock_object, pascal_name).return_value = False
        with pytest.raises(SaveError) as e:
            getattr(mock_plot, property_name)(file_name, scale_factor)
        assert _("Save Error") in str(e.value)
