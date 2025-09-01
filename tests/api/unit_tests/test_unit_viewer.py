# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for Viewer Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import Viewer, Plot
from moldflow.common import ViewModes, StandardViews, AnimationSpeed
from moldflow.constants import (
    MP4_FILE_EXT,
    JPG_FILE_EXT,
    JPEG_FILE_EXT,
    PNG_FILE_EXT,
    BMP_FILE_EXT,
    TIF_FILE_EXT,
)
from moldflow.double_array import DoubleArray
from moldflow.ent_list import EntList
from moldflow.vector import Vector
from tests.api.unit_tests.conftest import VALID_MOCK, INVALID_MOCK
from tests.conftest import (
    INVALID_BOOL,
    INVALID_INT,
    INVALID_FLOAT,
    INVALID_STR,
    VALID_BOOL,
    VALID_INT,
    VALID_FLOAT,
    NON_NEGATIVE_INT,
    POSITIVE_INT,
    VALID_STR,
    pad_and_zip,
)

CENTER_RANGE = [0, 1.0, 0.5, 1]
NOT_CENTER_RANGE = [-1, 1.1, -0.1]
VALID_MIN = [0.02, 0.5, 1.0]
VALID_MAX = [0.1, 0.6, 1.5]


@pytest.mark.unit
class TestUnitViewer:
    """
    Test suite for the Viewer class.
    """

    @pytest.fixture
    def mock_viewer(self, mock_object) -> Viewer:
        """
        Fixture to create a mock instance of Viewer.
        Args:
            mock_object: Mock object for the Viewer dependency.
        Returns:
            Viewer: An instance of Viewer with the mock object.
        """
        return Viewer(mock_object)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args, return_type, class_return, expected",
        [("reset", "Reset", (), (), None, None, None)]
        + [("reset_legend", "ResetLegend", (), (), None, None, None)]
        + [
            ("reset_view", "ResetView", (a, b), (a.vector, b.vector), None, None, None)
            for a, b in pad_and_zip(VALID_MOCK.VECTOR, VALID_MOCK.VECTOR)
        ]
        + [
            ("rotate", "Rotate", (a, b, c), (a, b, c), None, None, None)
            for a, b, c in pad_and_zip(VALID_FLOAT, VALID_FLOAT, VALID_FLOAT)
        ]
        + [("rotate_x", "RotateX", (a,), (a,), None, None, None) for a in pad_and_zip(VALID_FLOAT)]
        + [("rotate_y", "RotateY", (a,), (a,), None, None, None) for a in pad_and_zip(VALID_FLOAT)]
        + [("rotate_z", "RotateZ", (a,), (a,), None, None, None) for a in pad_and_zip(VALID_FLOAT)]
        + [
            ("rotate_by", "RotateBy", (a, b, c), (a, b, c), None, None, None)
            for a, b, c in pad_and_zip(VALID_FLOAT, VALID_FLOAT, VALID_FLOAT)
        ]
        + [
            ("rotate_x_by", "RotateXBy", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_FLOAT)
        ]
        + [
            ("rotate_y_by", "RotateYBy", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_FLOAT)
        ]
        + [
            ("rotate_z_by", "RotateZBy", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_FLOAT)
        ]
        + [
            ("set_view_mode", "SetViewMode", (a,), (a.value,), None, None, None)
            for a in pad_and_zip(ViewModes)
        ]
        + [("fit", "Fit", (), (), None, None, None)]
        + [
            ("pan", "Pan", (a, b), (a, b), None, None, None)
            for a, b in pad_and_zip(VALID_FLOAT, VALID_FLOAT)
        ]
        + [("zoom", "Zoom", (a,), (a,), None, None, None) for a in pad_and_zip(VALID_FLOAT)]
        + [
            ("go_to_standard_view", "GoToStandardView", (a,), (a.value,), None, None, None)
            for a in pad_and_zip(StandardViews)
        ]
        + [
            ("create_bookmark", "CreateBookmark", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_STR)
        ]
        + [
            ("delete_bookmark", "DeleteBookmark", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_STR)
        ]
        + [
            ("go_to_bookmark", "GoToBookmark", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_STR)
        ]
        + [("print", "Print", (), (), None, None, None)]
        + [
            (
                "enable_clipping_plane_by_id",
                "EnableClippingPlaneByID",
                (a, b),
                (a, b),
                None,
                None,
                None,
            )
            for a, b in pad_and_zip(VALID_INT, VALID_BOOL)
        ]
        + [
            ("delete_clipping_plane_by_id", "DeleteClippingPlaneByID", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_INT)
        ]
        + [
            (
                "add_bookmark",
                "AddBookmark",
                (a, b, c, d, e, f, g, h, i),
                (a, b.vector, c.vector, d.vector, e.vector, f, g, h, i),
                None,
                None,
                None,
            )
            for a, b, c, d, e, f, g, h, i in pad_and_zip(
                VALID_STR,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_MIN,
                VALID_MAX,
                VALID_FLOAT,
                VALID_FLOAT,
            )
        ]
        + [
            ("show_plot", "ShowPlot", (a,), (a.plot,), None, None, None)
            for a in pad_and_zip(VALID_MOCK.PLOT)
        ]
        + [
            ("hide_plot", "HidePlot", (a,), (a.plot,), None, None, None)
            for a in pad_and_zip(VALID_MOCK.PLOT)
        ]
        + [
            ("overlay_plot", "OverlayPlot", (a,), (a.plot,), None, None, None)
            for a in pad_and_zip(VALID_MOCK.PLOT)
        ]
        + [
            ("center", "Center", (a, b), (a, b), None, None, None)
            for a, b in pad_and_zip(CENTER_RANGE, CENTER_RANGE)
        ]
        + [
            (
                "modify_clipping_plane",
                "ModifyClippingPlane",
                (a, b, c),
                (a.ent_list, b.vector, c),
                None,
                None,
                None,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_FLOAT)
        ]
        + [
            (
                "modify_clipping_plane_by_id",
                "ModifyClippingPlaneByID",
                (a, b, c),
                (a, b.vector, c),
                None,
                None,
                None,
            )
            for a, b, c in pad_and_zip(VALID_INT, VALID_MOCK.VECTOR, VALID_FLOAT)
        ]
        + [
            ("delete_clipping_plane", "DeleteClippingPlane", (a,), (a.ent_list,), None, None, None)
            for a in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [
            (
                "enable_clipping_plane",
                "EnableClippingPlane",
                (a, b),
                (a.ent_list, b),
                None,
                None,
                None,
            )
            for a, b in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            ("show_plot_frame", "ShowPlotFrame", (a, b), (a.plot, b), None, None, None)
            for a, b in pad_and_zip(VALID_MOCK.PLOT, NON_NEGATIVE_INT)
        ]
        + [
            (
                "set_min_max_minimum_label_location",
                "SetMinMaxMinimumLabelLocation",
                (a, b, c, d),
                (a, b, c, d),
                None,
                None,
                None,
            )
            for a, b, c, d in pad_and_zip(VALID_FLOAT, VALID_FLOAT, VALID_FLOAT, VALID_FLOAT)
        ]
        + [
            (
                "set_min_max_maximum_label_location",
                "SetMinMaxMaximumLabelLocation",
                (a, b, c, d),
                (a, b, c, d),
                None,
                None,
                None,
            )
            for a, b, c, d in pad_and_zip(VALID_FLOAT, VALID_FLOAT, VALID_FLOAT, VALID_FLOAT)
        ]
        + [
            (
                "set_histogram_location",
                "SetHistogramLocation",
                (a, b, c, d),
                (a, b, c, d),
                None,
                None,
                None,
            )
            for a, b, c, d in pad_and_zip(VALID_FLOAT, VALID_FLOAT, VALID_FLOAT, VALID_FLOAT)
        ]
        + [
            ("get_plot", "GetPlot", (a,), (a,), Plot, "plot", b)
            for a, b in pad_and_zip(VALID_INT, VALID_MOCK.PLOT)
        ]
        + [("get_plot", "GetPlot", (a,), (a,), None, None, None) for a in pad_and_zip(VALID_INT)]
        + [
            ("world_to_display", "WorldToDisplay", (a,), (a.vector,), Vector, "vector", b)
            for a, b in pad_and_zip(VALID_MOCK.VECTOR, VALID_MOCK.VECTOR)
        ]
        + [
            ("world_to_display", "WorldToDisplay", (a,), (a.vector,), None, None, None)
            for a in pad_and_zip(VALID_MOCK.VECTOR)
        ]
        + [
            (
                "create_clipping_plane",
                "CreateClippingPlane",
                (a, b),
                (a.vector, b),
                EntList,
                "ent_list",
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.VECTOR, VALID_FLOAT, VALID_MOCK.ENT_LIST)
        ]
        + [
            (
                "create_clipping_plane",
                "CreateClippingPlane",
                (a, b),
                (a.vector, b),
                None,
                None,
                None,
            )
            for a, b in pad_and_zip(VALID_MOCK.VECTOR, VALID_FLOAT)
        ]
        + [
            (
                "get_next_clipping_plane",
                "GetNextClippingPlane",
                (a,),
                (a.ent_list,),
                EntList,
                "ent_list",
                b,
            )
            for a, b in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST)
        ]
        + [
            (
                "get_next_clipping_plane",
                "GetNextClippingPlane",
                (a,),
                (a.ent_list,),
                None,
                None,
                None,
            )
            for a in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("play_animation", "PlayAnimation", (), (), None, None, None)],
    )
    # pylint: disable=R0913,R0917
    def test_function_no_return(
        self,
        mock_viewer,
        mock_object,
        property_name,
        pascal_name,
        args,
        passed_args,
        return_type,
        class_return,
        expected,
    ):
        """
        Test Viewer functions methods without return.
        """
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_viewer, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
        if class_return is not None:
            assert isinstance(result, return_type)
            assert getattr(result, class_return) == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, return_type, class_return, expected",
        [
            ("create_default_clipping_plane", "CreateDefaultClippingPlane", EntList, "ent_list", x)
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("create_default_clipping_plane", "CreateDefaultClippingPlane", None, None, None)]
        + [
            ("get_first_clipping_plane", "GetFirstClippingPlane", EntList, "ent_list", x)
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("get_first_clipping_plane", "GetFirstClippingPlane", None, None, None)]
        + [
            (
                "get_min_max_minimum_label_location",
                "GetMinMaxMinimumLabelLocation",
                DoubleArray,
                "double_array",
                x,
            )
            for x in pad_and_zip(VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            (
                "get_min_max_minimum_label_location",
                "GetMinMaxMinimumLabelLocation",
                None,
                None,
                None,
            )
        ]
        + [
            (
                "get_min_max_maximum_label_location",
                "GetMinMaxMaximumLabelLocation",
                DoubleArray,
                "double_array",
                x,
            )
            for x in pad_and_zip(VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            (
                "get_min_max_maximum_label_location",
                "GetMinMaxMaximumLabelLocation",
                None,
                None,
                None,
            )
        ]
        + [
            ("get_histogram_location", "GetHistogramLocation", DoubleArray, "double_array", x)
            for x in pad_and_zip(VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [("get_histogram_location", "GetHistogramLocation", None, None, None)]
        + [
            ("is_play_animation", "IsPlayAnimation", bool, None, x) for x in pad_and_zip(VALID_BOOL)
        ],
    )
    # pylint: disable=R0913,R0917
    def test_function_no_args(
        self,
        mock_viewer,
        mock_object,
        property_name,
        pascal_name,
        return_type,
        class_return,
        expected,
    ):
        """
        Test viewer functions methods with bool return.
        """
        setattr(mock_object, pascal_name, expected)
        result = getattr(mock_viewer, property_name)()
        # pylint: disable=R0801
        if return_type is not None:
            assert isinstance(result, return_type)
        if class_return:
            assert getattr(result, class_return) == expected
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args, return_type, class_return, expected",
        [
            ("save_animation", "SaveAnimation3", (a, b, c), (a, b.value, c), bool, None, d)
            for a, b, c, d in pad_and_zip(
                [x + MP4_FILE_EXT for x in VALID_STR], AnimationSpeed, VALID_BOOL, VALID_BOOL
            )
        ]
        + [
            ("save_animation", "SaveAnimation3", (a, b.value, c), (a, b.value, c), bool, None, d)
            for a, b, c, d in pad_and_zip(
                [x + MP4_FILE_EXT for x in VALID_STR], AnimationSpeed, VALID_BOOL, VALID_BOOL
            )
        ]
        + [
            ("save_plot_scale_image", "SavePlotScaleImage", (a,), (a,), bool, None, b)
            for a, b in pad_and_zip(VALID_STR, VALID_BOOL)
        ]
        + [
            ("save_axis_image", "SaveAxisImage", (a,), (a,), bool, None, b)
            for a, b in pad_and_zip(VALID_STR, VALID_BOOL)
        ]
        + [
            (
                "save_image",
                "SaveImage4",
                (a, b, c, d, e, f, g, h, i, j, k, l, m, n),
                (a, b, c, d, e, f, g, h, i, j, k, l, m, n),
                bool,
                None,
                o,
            )
            for a, b, c, d, e, f, g, h, i, j, k, l, m, n, o in pad_and_zip(
                [
                    x + y
                    for x, y in pad_and_zip(
                        VALID_STR,
                        [JPG_FILE_EXT, JPEG_FILE_EXT, PNG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT],
                    )
                ],
                VALID_INT,
                VALID_INT,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("save_image_legacy", "SaveImage", (a,), (a,), bool, None, True)
            for a in [
                x + y
                for x, y in pad_and_zip(
                    VALID_STR,
                    [JPG_FILE_EXT, JPEG_FILE_EXT, PNG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT],
                )
            ]
        ]
        + [
            ("save_image_legacy", "SaveImage2", (a, b, c), (a, b, c), bool, None, d)
            for a, b, c, d in pad_and_zip(
                [
                    x + y
                    for x, y in pad_and_zip(
                        VALID_STR,
                        [JPG_FILE_EXT, JPEG_FILE_EXT, PNG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT],
                    )
                ],
                POSITIVE_INT,
                POSITIVE_INT,
                VALID_BOOL,
            )
        ]
        + [
            ("set_view_size", "SetViewSize", (a, b), (a, b), bool, None, c)
            for a, b, c in pad_and_zip(NON_NEGATIVE_INT, NON_NEGATIVE_INT, VALID_BOOL)
        ]
        + [
            ("world_to_display", "WorldToDisplay", (a,), (a.vector,), Vector, "vector", b)
            for a, b in pad_and_zip(VALID_MOCK.VECTOR, VALID_MOCK.VECTOR)
        ]
        + [
            (
                "create_clipping_plane",
                "CreateClippingPlane",
                (a, b),
                (a.vector, b),
                EntList,
                "ent_list",
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.VECTOR, VALID_FLOAT, VALID_MOCK.ENT_LIST)
        ]
        + [
            (
                "get_next_clipping_plane",
                "GetNextClippingPlane",
                (a,),
                (a.ent_list,),
                EntList,
                "ent_list",
                b,
            )
            for a, b in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST)
        ]
        + [
            ("get_plot", "GetPlot", (a,), (a,), Plot, "plot", b)
            for a, b in pad_and_zip(VALID_INT, VALID_MOCK.PLOT)
        ]
        + [
            ("set_banded_contours", "SetBandedContours", (a, b, c), (a, b, c), None, None, None)
            for a, b, c in pad_and_zip(VALID_STR, VALID_BOOL, POSITIVE_INT)
        ]
        + [
            ("show_plot_by_name", "ShowPlotByName", (a,), (a,), None, None, None)
            for a in pad_and_zip(VALID_STR)
        ]
        + [
            ("show_plot_frame_by_name", "ShowPlotFrameByName", (a, b), (a, b), None, None, None)
            for a, b in pad_and_zip(VALID_STR, NON_NEGATIVE_INT)
        ],
    )
    # pylint: disable=R0913,R0917
    def test_function(
        self,
        mock_viewer,
        mock_object,
        property_name,
        pascal_name,
        args,
        passed_args,
        return_type,
        class_return,
        expected,
    ):
        """
        Test viewer functions methods with return.
        """
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_viewer, property_name)(*args)

        # pylint: disable=R0801
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
        if return_type is not None:
            assert isinstance(result, return_type)
        if class_return:
            assert getattr(result, class_return) == expected
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, return_type, class_name, expected",
        [("view_size_x", "GetViewSizeX", int, None, x) for x in pad_and_zip(VALID_INT)]
        + [("view_size_y", "GetViewSizeY", int, None, x) for x in pad_and_zip(VALID_INT)]
        + [("rotation_x", "GetRotationX", (int, float), None, x) for x in pad_and_zip(VALID_FLOAT)]
        + [("rotation_y", "GetRotationY", (int, float), None, x) for x in pad_and_zip(VALID_FLOAT)]
        + [("rotation_z", "GetRotationZ", (int, float), None, x) for x in pad_and_zip(VALID_FLOAT)]
        + [
            ("active_clipping_plane", "GetActiveClippingPlane", EntList, "ent_list", x)
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("active_clipping_plane", "GetActiveClippingPlane", None, None, None)]
        + [("active_plot", "ActivePlot", Plot, "plot", x) for x in pad_and_zip(VALID_MOCK.PLOT)]
        + [("active_plot", "ActivePlot", None, None, None)],
    )
    # pylint: disable=R0913,R0917
    def test_property(
        self,
        mock_viewer,
        mock_object,
        property_name,
        pascal_name,
        return_type,
        class_name,
        expected,
    ):
        """
        Test viewer properties methods with int return.
        """
        setattr(mock_object, pascal_name, expected)
        # pylint: disable=R0801
        result = getattr(mock_viewer, property_name)
        if return_type is not None:
            assert isinstance(result, return_type)
        if class_name:
            assert getattr(result, class_name) == expected
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [
            ("active_clipping_plane", "SetActiveClippingPlane", a, a.ent_list)
            for a in pad_and_zip(VALID_MOCK.ENT_LIST)
        ],
    )
    # pylint: disable=R0913,R0917
    def test_property_set(
        self, mock_viewer, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test Viewer functions methods without return.
        """
        setattr(mock_viewer, property_name, args)
        getattr(mock_object, pascal_name).assert_called_once_with(passed_args)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            ("reset_view", "ResetView", [VALID_MOCK.VECTOR, VALID_MOCK.VECTOR], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK, INVALID_MOCK]))
        ]
        + [
            ("rotate", "Rotate", [VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0]], x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT])
            )
        ]
        + [
            ("rotate_x", "RotateX", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("rotate_y", "RotateY", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("rotate_z", "RotateZ", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("rotate_by", "RotateBy", [VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0]], x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT])
            )
        ]
        + [
            ("rotate_x_by", "RotateXBy", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("rotate_y_by", "RotateYBy", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("rotate_z_by", "RotateZBy", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("set_view_mode", "SetViewMode", [ViewModes.PARALLEL_PROJECTION.value], x)
            for x in ((index, value) for index, value in enumerate([INVALID_INT]))
        ]
        + [
            ("pan", "Pan", [VALID_FLOAT[0], VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT, INVALID_FLOAT]))
        ]
        + [
            ("zoom", "Zoom", [VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT]))
        ]
        + [
            ("go_to_standard_view", "GoToStandardView", [StandardViews.FRONT.value], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("create_bookmark", "CreateBookmark", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("delete_bookmark", "DeleteBookmark", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("go_to_bookmark", "GoToBookmark", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("save_image_legacy", "SaveImage", [VALID_STR[0] + JPG_FILE_EXT], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            (
                "save_image_legacy",
                "SaveImage2",
                [VALID_STR[0] + JPG_FILE_EXT, VALID_INT[0], VALID_INT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, [INVALID_STR], [INVALID_STR]])
            )
        ]
        + [
            (
                "save_image",
                "SaveImage4",
                [
                    VALID_STR[0] + JPG_FILE_EXT,
                    VALID_INT[0],
                    VALID_INT[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_STR,
                        INVALID_INT,
                        INVALID_INT,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "save_animation",
                "SaveAnimation3",
                [VALID_STR[0] + MP4_FILE_EXT, AnimationSpeed.FAST.value, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, INVALID_STR, INVALID_BOOL])
            )
        ]
        + [
            (
                "enable_clipping_plane_by_id",
                "EnableClippingPlaneByID",
                [VALID_INT[0], VALID_BOOL[0]],
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_INT, INVALID_BOOL]))
        ]
        + [
            ("delete_clipping_plane_by_id", "DeleteClippingPlaneByID", [VALID_INT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_INT]))
        ]
        + [
            (
                "add_bookmark",
                "AddBookmark",
                [
                    VALID_STR[0],
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MIN[0],
                    VALID_MAX[0],
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_STR,
                        INVALID_MOCK,
                        INVALID_MOCK,
                        INVALID_MOCK,
                        INVALID_MOCK,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                    ]
                )
            )
        ]
        + [
            ("show_plot", "ShowPlot", [VALID_MOCK.PLOT], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ]
        + [
            ("hide_plot", "HidePlot", [VALID_MOCK.PLOT], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ]
        + [
            ("overlay_plot", "OverlayPlot", [VALID_MOCK.PLOT], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ]
        + [
            ("get_plot", "GetPlot", [VALID_INT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_INT]))
        ]
        + [
            ("center", "Center", [CENTER_RANGE[0], CENTER_RANGE[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT, INVALID_FLOAT]))
        ]
        + [
            ("world_to_display", "WorldToDisplay", [VALID_MOCK.VECTOR], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ]
        + [
            ("create_clipping_plane", "CreateClippingPlane", [VALID_MOCK.VECTOR, VALID_FLOAT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK, INVALID_FLOAT]))
        ]
        + [
            (
                "modify_clipping_plane",
                "ModifyClippingPlane",
                [VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_FLOAT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK, INVALID_MOCK, INVALID_FLOAT])
            )
        ]
        + [
            (
                "modify_clipping_plane_by_id",
                "ModifyClippingPlaneByID",
                [VALID_INT[0], VALID_MOCK.VECTOR, VALID_FLOAT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_INT, INVALID_MOCK, INVALID_FLOAT])
            )
        ]
        + [
            ("delete_clipping_plane", "DeleteClippingPlane", [VALID_MOCK.ENT_LIST], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ]
        + [
            ("get_next_clipping_plane", "GetNextClippingPlane", [VALID_MOCK.ENT_LIST], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ]
        + [
            (
                "enable_clipping_plane",
                "EnableClippingPlane",
                [VALID_MOCK.ENT_LIST, VALID_BOOL[0]],
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK, INVALID_BOOL]))
        ]
        + [
            ("show_plot_frame", "ShowPlotFrame", [VALID_MOCK.PLOT, VALID_INT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK, INVALID_INT]))
        ]
        + [
            ("save_plot_scale_image", "SavePlotScaleImage", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("save_axis_image", "SaveAxisImage", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            (
                "set_min_max_minimum_label_location",
                "SetMinMaxMinimumLabelLocation",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT]
                )
            )
        ]
        + [
            (
                "set_min_max_maximum_label_location",
                "SetMinMaxMaximumLabelLocation",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT]
                )
            )
        ]
        + [
            (
                "set_histogram_location",
                "SetHistogramLocation",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0], VALID_FLOAT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT, INVALID_FLOAT]
                )
            )
        ]
        + [
            (
                "set_banded_contours",
                "SetBandedContours",
                [VALID_STR[0], VALID_BOOL[0], VALID_INT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, INVALID_BOOL, INVALID_INT])
            )
        ]
        + [
            ("show_plot_by_name", "ShowPlotByName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("show_plot_frame_by_name", "ShowPlotFrameByName", [VALID_STR[0], VALID_INT[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR, INVALID_INT]))
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_inputs(
        self, mock_viewer, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test viewer functions methods with invalid inputs.
        """
        args = list(args)
        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(TypeError) as e:
                getattr(mock_viewer, property_name)(*args)
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            ("active_clipping_plane", "SetActiveClippingPlane", VALID_MOCK.ENT_LIST, x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK]))
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_inputs_property(
        self, mock_viewer, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test viewer functions methods with invalid inputs.
        """
        for i in invalid_val[1]:
            args = i
            with pytest.raises(TypeError) as e:
                setattr(mock_viewer, property_name, args)
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            (
                "add_bookmark",
                "AddBookmark",
                [
                    VALID_STR[0],
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                ],
                x,
            )
            for x in ((index, value) for index, value in [(5, [-1.5, 0, -1]), (6, [-1, 0.9, 0])])
        ]
        + [
            ("show_plot_frame", "ShowPlotFrame", [VALID_MOCK.PLOT, VALID_INT[0]], x)
            for x in ((index, value) for index, value in [(1, [-1, -10])])
        ]
        + [
            ("set_view_size", "SetViewSize", [VALID_INT[0], VALID_INT[0]], x)
            for x in ((index, value) for index, value in [(0, [-1, -10]), (1, [-1, -5])])
        ]
        + [
            ("center", "Center", [NOT_CENTER_RANGE[0], NOT_CENTER_RANGE[0]], x)
            for x in (
                (index, value) for index, value in [(0, [-1, -0.1, 1.1]), (1, [-1, -0.1, 1.1])]
            )
        ]
        + [
            (
                "save_image_legacy",
                "SaveImage2",
                [VALID_STR[0] + JPG_FILE_EXT, POSITIVE_INT[0], None],
                x,
            )
            for x in ((index, value) for index, value in [(2, [None])])
        ]
        + [
            (
                "save_image_legacy",
                "SaveImage2",
                [VALID_STR[0] + JPG_FILE_EXT, None, POSITIVE_INT[0]],
                x,
            )
            for x in ((index, value) for index, value in [(1, [None])])
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_values(
        self, mock_viewer, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test viewer functions methods with invalid values.
        """

        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(ValueError) as e:
                getattr(mock_viewer, property_name)(*args)
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()

    def test_get_number_frames_by_name(self, mock_viewer, mock_object):
        """
        Test getting the number of frames by name using the viewer.
        """

        def fake_get_number_frames_by_name(plot_name, out_val):  # pylint: disable=W0613
            out_val.value = 5

        mock_object.GetNumberFramesByName.side_effect = fake_get_number_frames_by_name

        result = mock_viewer.get_number_frames_by_name("TestPlot")
        assert result == 5
        mock_object.GetNumberFramesByName.assert_called_once()
