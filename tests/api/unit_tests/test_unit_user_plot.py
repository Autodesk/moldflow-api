# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for UserPlot Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import UserPlot
from moldflow.common import (
    ClampForcePlotDirection,
    ModulusPlotDirection,
    UserPlotType,
    DeflectionType,
    BirefringenceResultType,
)
from moldflow.plot import Plot
from tests.api.unit_tests.conftest import VALID_MOCK, INVALID_MOCK_WITH_NONE
from tests.conftest import (
    INVALID_BOOL,
    INVALID_INT,
    INVALID_STR,
    INVALID_FLOAT,
    VALID_BOOL,
    VALID_INT,
    VALID_STR,
    VALID_FLOAT,
    pad_and_zip,
)


@pytest.mark.unit
class TestUnitUserPlot:
    """
    Test suite for the UserPlot class.
    """

    @pytest.fixture
    def mock_user_plot(self, mock_object) -> UserPlot:
        """
        Fixture to create a mock instance of UserPlot.
        Args:
            mock_object: Mock object for the UserPlot dependency.
        Returns:
            UserPlot: An instance of UserPlot with the mock object.
        """
        return UserPlot(mock_object)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [("set_dept_name", "SetDeptName", (a,), (a,)) for a in pad_and_zip(VALID_STR)]
        + [("set_indp_name", "SetIndpName", (a,), (a,)) for a in pad_and_zip(VALID_STR)]
        + [("set_data_type", "SetDataType", (a,), (a.value,)) for a in pad_and_zip(UserPlotType)]
        + [
            ("set_data_type", "SetDataType", (a.value,), (a.value,))
            for a in pad_and_zip(UserPlotType)
        ]
        + [("set_dept_unit_name", "SetDeptUnitName", (a,), (a,)) for a in pad_and_zip(VALID_STR)]
        + [("set_indp_unit_name", "SetIndpUnitName", (a,), (a,)) for a in pad_and_zip(VALID_STR)]
        + [
            ("add_scalar_data", "AddScalarData", (a, b, c), (a, b.integer_array, c.double_array))
            for a, b, c in pad_and_zip(
                VALID_FLOAT, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "add_vector_data",
                "AddVectorData",
                (a, b, c, d, e),
                (a, b.integer_array, c.double_array, d.double_array, e.double_array),
            )
            for a, b, c, d, e in pad_and_zip(
                VALID_FLOAT,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            (
                "add_tensor_data",
                "AddTensorData",
                (a, b, c, d, e, f, g, h),
                (
                    a,
                    b.integer_array,
                    c.double_array,
                    d.double_array,
                    e.double_array,
                    f.double_array,
                    g.double_array,
                    h.double_array,
                ),
            )
            for a, b, c, d, e, f, g, h in pad_and_zip(
                VALID_FLOAT,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [("set_name", "SetName", (a,), (a,)) for a in VALID_STR]
        + [
            ("set_scalar_data", "SetScalarData", (a, b), (a.integer_array, b.double_array))
            for a, b in pad_and_zip(VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            (
                "set_vector_data",
                "SetVectorData",
                (a, b, c, d),
                (a.integer_array, b.double_array, c.double_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            (
                "set_tensor_data",
                "SetTensorData",
                (a, b, c, d, e, f, g),
                (
                    a.integer_array,
                    b.double_array,
                    c.double_array,
                    d.double_array,
                    e.double_array,
                    f.double_array,
                    g.double_array,
                ),
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("add_xy_plot_data", "AddXYPlotData", (a, b, c), (a, b.double_array, c.double_array))
            for a, b, c in pad_and_zip(
                VALID_FLOAT, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            ("set_xy_plot_data", "SetXYPlotData", (a, b), (a.double_array, b.double_array))
            for a, b in pad_and_zip(VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [("set_xy_plot_x_unit_name", "SetXYPlotXUnitName", (a,), (a,)) for a in VALID_STR]
        + [("set_xy_plot_y_unit_name", "SetXYPlotYUnitName", (a,), (a,)) for a in VALID_STR]
        + [("set_xy_plot_x_title", "SetXYPlotXTitle", (a,), (a,)) for a in VALID_STR]
        + [
            ("set_highlight_data", "SetHighlightData", (a,), (a.double_array,))
            for a in pad_and_zip(VALID_MOCK.DOUBLE_ARRAY)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_bool_return(
        self, mock_user_plot, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test the function method of UserPlot that returns a boolean.
        """
        expected = True
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_user_plot, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
        assert result == expected
        assert isinstance(result, bool)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [
            ("set_vector_as_displacement", "SetVectorAsDisplacement", (a,), (a,))
            for a in pad_and_zip(VALID_BOOL)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_no_return(
        self, mock_user_plot, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test the function method of UserPlot that returns a boolean.
        """
        getattr(mock_user_plot, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [
            ("build_weldline_plot", "BuildWeldlinePlot", (a, b, c), (a, b, c))
            for a, b, c in pad_and_zip(VALID_STR, VALID_FLOAT, VALID_BOOL)
        ]
        + [
            ("build_clamp_force_plot", "BuildClampForcePlot", (a, b, c, d), (a, b.value, c, d))
            for a, b, c, d in pad_and_zip(VALID_STR, ClampForcePlotDirection, VALID_INT, VALID_BOOL)
        ]
        + [
            (
                "build_clamp_force_plot",
                "BuildClampForcePlot",
                (a, b.value, c, d),
                (a, b.value, c, d),
            )
            for a, b, c, d in pad_and_zip(VALID_STR, ClampForcePlotDirection, VALID_INT, VALID_BOOL)
        ]
        + [
            (
                "build_birefringence_plot",
                "BuildBirefringencePlot",
                (a, b, c, d, e, f),
                (a, b.value, c, d, e, f),
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_STR,
                BirefringenceResultType,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
            )
        ]
        + [
            (
                "build_birefringence_plot",
                "BuildBirefringencePlot",
                (a, b.value, c, d, e, f),
                (a, b.value, c, d, e, f),
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_STR,
                BirefringenceResultType,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
            )
        ]
        + [
            ("build_modulus_plot", "BuildModulusPlot", (a, b, c), (a, b.value, c))
            for a, b, c in pad_and_zip(VALID_STR, ModulusPlotDirection, VALID_INT)
        ]
        + [
            ("build_modulus_plot", "BuildModulusPlot", (a, b.value, c), (a, b.value, c))
            for a, b, c in pad_and_zip(VALID_STR, ModulusPlotDirection, VALID_INT)
        ]
        + [
            ("build_deflection_plot", "BuildDeflectionPlot", (a, b, c), (a, b.value, c))
            for a, b, c in pad_and_zip(VALID_STR, DeflectionType, VALID_STR)
        ]
        + [
            ("build_deflection_plot", "BuildDeflectionPlot", (a, b.value, c), (a, b.value, c))
            for a, b, c in pad_and_zip(VALID_STR, DeflectionType, VALID_STR)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_plot_return(
        self, mock_user_plot, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test the function method of UserPlot that returns a plot.
        """
        expected = Mock(spec=Plot)
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_user_plot, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
        assert result.plot == expected
        assert isinstance(result, Plot)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [
            ("build_weldline_plot", "BuildWeldlinePlot", (a, b, c), (a, b, c))
            for a, b, c in pad_and_zip(VALID_STR, VALID_FLOAT, VALID_BOOL)
        ]
        + [
            ("build_clamp_force_plot", "BuildClampForcePlot", (a, b, c, d), (a, b.value, c, d))
            for a, b, c, d in pad_and_zip(VALID_STR, ClampForcePlotDirection, VALID_INT, VALID_BOOL)
        ]
        + [
            (
                "build_birefringence_plot",
                "BuildBirefringencePlot",
                (a, b, c, d, e, f),
                (a, b.value, c, d, e, f),
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_STR,
                BirefringenceResultType,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
            )
        ]
        + [
            ("build_modulus_plot", "BuildModulusPlot", (a, b, c), (a, b.value, c))
            for a, b, c in pad_and_zip(VALID_STR, ModulusPlotDirection, VALID_INT)
        ]
        + [
            ("build_deflection_plot", "BuildDeflectionPlot", (a, b, c), (a, b.value, c))
            for a, b, c in pad_and_zip(VALID_STR, DeflectionType, VALID_STR)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_none_return(
        self, mock_user_plot, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test the function method of UserPlot that returns a plot.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_user_plot, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
        assert result is None

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            ("set_dept_name", "SetDeptName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_indp_name", "SetIndpName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_data_type", "SetDataType", [UserPlotType.ELEMENT_DATA.value], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_dept_unit_name", "SetDeptUnitName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_indp_unit_name", "SetIndpUnitName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            (
                "add_scalar_data",
                "AddScalarData",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "add_vector_data",
                "AddVectorData",
                [
                    VALID_FLOAT[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "add_tensor_data",
                "AddVectorData",
                [
                    VALID_FLOAT[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            ("set_name", "SetName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_vector_as_displacement", "SetVectorAsDisplacement", [VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL]))
        ]
        + [
            (
                "set_scalar_data",
                "SetScalarData",
                [VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "set_vector_data",
                "SetVectorData",
                [
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "set_tensor_data",
                "SetTensorData",
                [
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "add_xy_plot_data",
                "AddXYPlotData",
                [VALID_FLOAT[0], VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "set_xy_plot_data",
                "SetXYPlotData",
                [VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            ("set_xy_plot_x_unit_name", "SetXYPlotXUnitName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_xy_plot_y_unit_name", "SetXYPlotYUnitName", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_xy_plot_x_title", "SetXYPlotXTitle", [VALID_STR[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_STR]))
        ]
        + [
            ("set_highlight_data", "SetHighlightData", [VALID_MOCK.DOUBLE_ARRAY], x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK_WITH_NONE]))
        ]
        + [
            (
                "build_weldline_plot",
                "BuildWeldlinePlot",
                [VALID_STR[0], VALID_FLOAT[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, INVALID_FLOAT, INVALID_BOOL])
            )
        ]
        + [
            (
                "build_clamp_force_plot",
                "BuildClampForcePlot",
                [VALID_STR[0], ClampForcePlotDirection.X.value, VALID_INT[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, INVALID_INT, INVALID_INT, INVALID_BOOL])
            )
        ]
        + [
            (
                "build_birefringence_plot",
                "BuildBirefringencePlot",
                [
                    VALID_STR[0],
                    BirefringenceResultType.FRINGE_PATTERN.value,
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
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
                        INVALID_INT,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                    ]
                )
            )
        ]
        + [
            (
                "build_modulus_plot",
                "BuildModulusPlot",
                [VALID_STR[0], ModulusPlotDirection.EXX.value, VALID_INT[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, INVALID_INT, INVALID_INT])
            )
        ]
        + [
            (
                "build_deflection_plot",
                "BuildDeflectionPlot",
                [VALID_STR[0], DeflectionType.DEFL.value, VALID_STR[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_STR, INVALID_STR, INVALID_STR])
            )
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_inputs(
        self, mock_user_plot, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test the function method of UserPlot with invalid inputs.
        """
        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(TypeError) as e:
                getattr(mock_user_plot, property_name)(*tuple(args))
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, pascal_name, class_name, return_value",
        [("build", "Build", Plot, VALID_MOCK.PLOT), ("build", "Build", Plot, None)],
    )
    # pylint: disable=R0913, R0917
    def test_no_args_class_return(
        self, mock_user_plot, mock_object, property_name, pascal_name, class_name, return_value
    ):
        """
        Test the function method of UserPlot with no arguments.
        """
        setattr(mock_object, pascal_name, return_value)
        result = getattr(mock_user_plot, property_name)()
        if return_value is None:
            assert result is None
        else:
            assert isinstance(result, class_name)
            assert result.plot == return_value
