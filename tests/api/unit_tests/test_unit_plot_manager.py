# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for PlotManager Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import (
    MaterialDatabase,
    MaterialIndex,
    SystemUnits,
    MaterialPlot,
    PlotManager,
    Plot,
    PlotType,
    UserPlot,
)
from moldflow.exceptions import SaveError
from tests.conftest import (
    VALID_BOOL,
    VALID_INT,
    VALID_STR,
    VALID_FLOAT,
    INVALID_INT,
    INVALID_STR,
    INVALID_BOOL,
    INVALID_FLOAT,
    pad_and_zip,
)
from tests.api.unit_tests.conftest import VALID_MOCK, INVALID_MOCK

SYSTEM_UNITS_AND_NONE = list(SystemUnits) + [""]


@pytest.mark.unit
class TestUnitPlotManager:
    """
    Test suite for the PlotManager class.
    """

    @pytest.fixture
    def mock_plot_manager(self, mock_object) -> PlotManager:
        """
        Fixture to create a mock instance of PlotManager.
        Args:
            mock_object: Mock object for the PlotManager dependency.
        Returns:
            PlotManager: An instance of PlotManager with the mock object.
        """
        return PlotManager(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, mock_plot",
        [("GetFirstPlot", "get_first_plot", VALID_MOCK.PLOT)],
    )
    # pylint: disable-next=R0913, R0917
    def test_attribute_return_plot(
        self, mock_plot_manager: PlotManager, mock_object, mock_plot, pascal_name, property_name
    ):
        """
        Test the get_first_plot method.
        """
        setattr(mock_object, pascal_name, mock_plot.plot)
        result = getattr(mock_plot_manager, property_name)()
        assert isinstance(result, Plot)
        assert result.plot == mock_plot.plot

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [("GetNextPlot", "get_next_plot", (x,), (x.plot,)) for x in pad_and_zip(VALID_MOCK.PLOT)]
        + [
            ("CreatePlotByDsID2", "create_plot_by_ds_id", (x, y), (x, y.value))
            for x in VALID_INT
            for y in PlotType
        ]
        + [
            ("CreatePlotByDsID2", "create_plot_by_ds_id", (x, y.value), (x, y.value))
            for x in VALID_INT
            for y in PlotType
        ]
        + [
            ("CreatePlotByName", "create_plot_by_name", (x, y), (x, y))
            for x in VALID_STR
            for y in VALID_BOOL
        ]
        + [("CreateXYPlotByName", "create_xy_plot_by_name", (x,), (x,)) for x in VALID_STR],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_return_plot(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the functions that return a Plot object.
        """
        expected_mock_plot = VALID_MOCK.PLOT
        getattr(mock_object, pascal_name).return_value = expected_mock_plot.plot
        result = getattr(mock_plot_manager, property_name)(*args)
        assert isinstance(result, Plot)
        assert result.plot == expected_mock_plot.plot
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [("DeletePlotByName", "delete_plot_by_name", (x,), (x,)) for x in VALID_STR]
        + [("DeletePlotByDsID", "delete_plot_by_ds_id", (x,), (x,)) for x in VALID_INT]
        + [("WarpQueryEnd", "warp_query_end", (), ())],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_return_none(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the functions that return None.
        """
        getattr(mock_plot_manager, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    def test_delete_plot(self, mock_plot_manager: PlotManager, mock_object):
        """
        Test the delete_plot method.
        """
        expected_mock_plot = VALID_MOCK.PLOT
        mock_plot_manager.delete_plot(expected_mock_plot)
        mock_object.DeletePlot.assert_called_once_with(expected_mock_plot.plot)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            ("DataHasXYPlotByDsID", "data_has_xy_plot_by_ds_id", (x,), (x,), bool, y)
            for x in VALID_INT
            for y in VALID_BOOL
        ]
        + [
            ("DataHasXYPlotByName", "data_has_xy_plot_by_name", (x,), (x,), bool, y)
            for x in VALID_STR
            for y in VALID_BOOL
        ]
        + [
            (
                "GetScalarData",
                "get_scalar_data",
                (x, y, z, u),
                (x, y.double_array, z.integer_array, u.double_array),
                bool,
                v,
            )
            for x, y, z, u, v in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_BOOL,
            )
        ]
        + [
            (
                "GetVectorData",
                "get_vector_data",
                (x, y, z, u, v, w),
                (
                    x,
                    y.double_array,
                    z.integer_array,
                    u.double_array,
                    v.double_array,
                    w.double_array,
                ),
                bool,
                a,
            )
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_BOOL,
            )
        ]
        + [
            (
                "GetTensorData",
                "get_tensor_data",
                (x, y, z, t11, t22, t33, t12, t13, t23),
                (
                    x,
                    y.double_array,
                    z.integer_array,
                    t11.double_array,
                    t22.double_array,
                    t33.double_array,
                    t12.double_array,
                    t13.double_array,
                    t23.double_array,
                ),
                bool,
                v,
            )
            for x, y, z, t11, t22, t33, t12, t13, t23, v in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_BOOL,
            )
        ]
        + [
            (
                "GetNonmeshData",
                "get_non_mesh_data",
                (x, y, z),
                (x, y.double_array, z.double_array),
                bool,
                v,
            )
            for x, y, z, v in pad_and_zip(
                VALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL
            )
        ]
        + [
            (
                "GetHighlightData",
                "get_highlight_data",
                (x, y, z),
                (x, y.double_array, z.double_array),
                bool,
                u,
            )
            for x, y, z, u in pad_and_zip(
                VALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL
            )
        ]
        + [
            ("FindDatasetIdByName", "find_dataset_id_by_name", (x,), (x,), int, y)
            for x in VALID_STR
            for y in VALID_INT
        ]
        + [
            ("GetIndpVarCount", "get_indp_var_count", (x,), (x,), int, y)
            for x in VALID_INT
            for y in VALID_INT
        ]
        + [
            ("GetIndpValues", "get_indp_values", (x, y), (x, y.double_array), bool, z)
            for x, y, z in pad_and_zip(VALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL)
        ]
        + [
            ("GetDataNbComponents", "get_data_nb_components", (x,), (x,), int, y)
            for x in VALID_INT
            for y in VALID_INT
        ]
        + [
            ("GetDataType", "get_data_type", (x,), (x,), str, y)
            for x in VALID_INT
            for y in VALID_STR
        ]
        + [
            (
                "FindDatasetIdsByName",
                "find_dataset_ids_by_name",
                (x, y),
                (x, y.integer_array),
                int,
                z,
            )
            for x, y, z in pad_and_zip(VALID_STR, VALID_MOCK.INTEGER_ARRAY, VALID_INT)
        ]
        + [
            ("CreateAnchorPlane", "create_anchor_plane", (x, y, z, u), (x, y, z, u), int, v)
            for x in VALID_INT
            for y in VALID_INT
            for z in VALID_INT
            for u in VALID_STR
            for v in VALID_INT
        ]
        + [
            ("ApplyAnchorPlane", "apply_anchor_plane", (x, y), (x, y.plot), bool, z)
            for x, y, z in pad_and_zip(VALID_INT, VALID_MOCK.PLOT, VALID_BOOL)
        ]
        + [
            ("SetAnchorPlaneNodes", "set_anchor_plane_nodes", (x, y, z, u), (x, y, z, u), bool, v)
            for x in VALID_INT
            for y in VALID_INT
            for z in VALID_INT
            for u in VALID_INT
            for v in VALID_BOOL
        ]
        + [
            ("GetAnchorPlaneNode", "get_anchor_plane_node", (x, y), (x, y), int, z)
            for x in VALID_INT
            for y in VALID_INT
            for z in VALID_INT
        ]
        + [
            ("SetAnchorPlaneName", "set_anchor_plane_name", (x, y), (x, y), bool, z)
            for x in VALID_INT
            for y in VALID_STR
            for z in VALID_BOOL
        ]
        + [
            ("DeleteAnchorPlaneByIndex", "delete_anchor_plane_by_index", (x,), (x,), bool, y)
            for x in VALID_INT
            for y in VALID_BOOL
        ]
        + [
            ("DeleteAnchorPlaneByName", "delete_anchor_plane_by_name", (x,), (x,), bool, y)
            for x in VALID_STR
            for y in VALID_BOOL
        ]
        + [
            ("GetDataDisplayFormat", "get_data_display_format", (x,), (x,), str, y)
            for x in VALID_INT
            for y in VALID_STR
        ]
        + [
            ("SetDataDisplayFormat", "set_data_display_format", (x, y), (x, y), bool, z)
            for x in VALID_INT
            for y in VALID_STR
            for z in VALID_BOOL
        ]
        + [
            ("WarpQueryNode", "warp_query_node", (x, y, z), (x, y, z.double_array), bool, u)
            for x, y, z, u in pad_and_zip(VALID_INT, VALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL)
        ]
        + [
            ("WarpQueryBegin", "warp_query_begin", (x, y), (x, y.double_array), bool, z)
            for x, y, z in pad_and_zip(VALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL)
        ]
        + [
            ("GetAnchorPlaneIndex", "get_anchor_plane_index", (x,), (x,), int, y)
            for x in VALID_STR
            for y in VALID_INT
        ]
        + [
            ("MarkResultForExport", "mark_result_for_export", (x, y), (x, y), bool, z)
            for x in VALID_STR
            for y in VALID_BOOL
            for z in VALID_BOOL
        ]
        + [
            ("MarkAllResultsForExport", "mark_all_results_for_export", (x,), (x,), bool, y)
            for x in VALID_BOOL
            for y in VALID_BOOL
        ]
        + [
            ("GetResultsFileName", "get_results_file_name", (x,), (x,), str, y)
            for x in VALID_INT
            for y in VALID_STR
        ]
        + [
            ("MarkResultForExportByID", "mark_result_for_export_by_id", (x, y), (x, y), bool, z)
            for x in VALID_INT
            for y in VALID_BOOL
            for z in VALID_BOOL
        ]
        + [
            ("FindDatasetByID", "find_dataset_by_id", (x,), (x,), bool, y)
            for x in VALID_INT
            for y in VALID_BOOL
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_return(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test the functions that return a boolean value.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_plot_manager, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("GetFirstPlot", "get_first_plot"), ("CreateUserPlot", "create_user_plot")],
    )
    def test_attribute_none(
        self, mock_plot_manager: PlotManager, mock_object, pascal_name, property_name
    ):
        """
        Test the functions that return a Plot object.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_plot_manager, property_name)()
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [("GetNextPlot", "get_next_plot", (x,), (x.plot,)) for x in pad_and_zip(VALID_MOCK.PLOT)]
        + [
            ("CreatePlotByDsID2", "create_plot_by_ds_id", (x, y), (x, y.value))
            for x in VALID_INT
            for y in PlotType
        ]
        + [
            ("CreatePlotByName", "create_plot_by_name", (x, y), (x, y))
            for x in VALID_STR
            for y in VALID_BOOL
        ]
        + [("CreateXYPlotByName", "create_xy_plot_by_name", (x,), (x,)) for x in VALID_STR]
        + [
            ("CreateMaterialPlot", "create_material_plot", (x, y, z), (x.value, y.value, z))
            for x in MaterialDatabase
            for y in MaterialIndex
            for z in VALID_INT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_none(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the functions that return a Plot object.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_plot_manager, property_name)(*args)
        assert result is None
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("GetNextPlot", "get_next_plot", (x,)) for x in INVALID_MOCK]
        + [
            ("CreatePlotByName", "create_plot_by_name", (x, y))
            for x in VALID_STR
            for y in INVALID_BOOL
        ]
        + [
            ("CreatePlotByName", "create_plot_by_name", (x, y))
            for x in INVALID_STR
            for y in VALID_BOOL
        ]
        + [("CreateXYPlotByName", "create_xy_plot_by_name", (x,)) for x in INVALID_STR]
        + [("DeletePlotByName", "delete_plot_by_name", (x,)) for x in INVALID_STR]
        + [("DeletePlotByDsID", "delete_plot_by_ds_id", (x,)) for x in INVALID_INT]
        + [("DeletePlot", "delete_plot", (x,)) for x in INVALID_MOCK]
        + [("DataHasXYPlotByDsID", "data_has_xy_plot_by_ds_id", (x,)) for x in INVALID_INT]
        + [("DataHasXYPlotByName", "data_has_xy_plot_by_name", (x,)) for x in INVALID_STR]
        + [
            ("GetScalarData", "get_scalar_data", (x, y, z, u))
            for x, y, z, u in pad_and_zip(
                INVALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetScalarData", "get_scalar_data", (x, y, z, u))
            for x, y, z, u in pad_and_zip(
                VALID_INT, INVALID_MOCK, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            ("GetScalarData", "get_scalar_data", (x, y, z, u))
            for x, y, z, u in pad_and_zip(
                VALID_INT, VALID_MOCK.DOUBLE_ARRAY, INVALID_MOCK, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            ("GetScalarData", "get_scalar_data", (x, y, z, u))
            for x, y, z, u in pad_and_zip(
                VALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.INTEGER_ARRAY, INVALID_MOCK
            )
        ]
        + [
            ("GetVectorData", "get_vector_data", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                INVALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetVectorData", "get_vector_data", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_INT,
                INVALID_MOCK,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetVectorData", "get_vector_data", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetVectorData", "get_vector_data", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetVectorData", "get_vector_data", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetVectorData", "get_vector_data", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                INVALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
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
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                INVALID_MOCK,
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
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            ("GetTensorData", "get_tensor_data", (x, y, z, t11, t22, t33, t12, t13, t23))
            for x, y, z, t11, t22, t33, t12, t13, t23 in pad_and_zip(
                VALID_INT,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                INVALID_MOCK,
            )
        ]
        + [
            ("GetNonmeshData", "get_non_mesh_data", (x, y, z))
            for x, y, z in pad_and_zip(
                INVALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            ("GetNonmeshData", "get_non_mesh_data", (x, y, z))
            for x, y, z in pad_and_zip(VALID_INT, INVALID_MOCK, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            ("GetNonmeshData", "get_non_mesh_data", (x, y, z))
            for x, y, z in pad_and_zip(VALID_INT, VALID_MOCK.DOUBLE_ARRAY, INVALID_MOCK)
        ]
        + [
            ("GetHighlightData", "get_highlight_data", (x, y, z))
            for x, y, z in pad_and_zip(
                INVALID_INT, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            ("GetHighlightData", "get_highlight_data", (x, y, z))
            for x, y, z in pad_and_zip(VALID_INT, INVALID_MOCK, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            ("GetHighlightData", "get_highlight_data", (x, y, z))
            for x, y, z in pad_and_zip(VALID_INT, VALID_MOCK.DOUBLE_ARRAY, INVALID_MOCK)
        ]
        + [("FindDatasetIdByName", "find_dataset_id_by_name", (x,)) for x in INVALID_STR]
        + [("GetIndpVarCount", "get_indp_var_count", (x,)) for x in INVALID_INT]
        + [
            ("GetIndpValues", "get_indp_values", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [("GetIndpValues", "get_indp_values", (x, y)) for x in VALID_INT for y in INVALID_MOCK]
        + [("GetDataNbComponents", "get_data_nb_components", (x,)) for x in INVALID_INT]
        + [("GetDataType", "get_data_type", (x,)) for x in INVALID_INT]
        + [
            ("FindDatasetIdsByName", "find_dataset_ids_by_name", (x, y))
            for x, y in pad_and_zip(INVALID_STR, VALID_MOCK.INTEGER_ARRAY)
        ]
        + [
            ("FindDatasetIdsByName", "find_dataset_ids_by_name", (x, y))
            for x in VALID_STR
            for y in INVALID_MOCK
        ]
        + [
            ("CreateAnchorPlane", "create_anchor_plane", (x, y, z, u))
            for x in INVALID_INT
            for y in VALID_INT
            for z in VALID_INT
            for u in VALID_STR
        ]
        + [
            ("CreateAnchorPlane", "create_anchor_plane", (x, y, z, u))
            for x in VALID_INT
            for y in INVALID_INT
            for z in VALID_INT
            for u in VALID_STR
        ]
        + [
            ("CreateAnchorPlane", "create_anchor_plane", (x, y, z, u))
            for x in VALID_INT
            for y in VALID_INT
            for z in INVALID_INT
            for u in VALID_STR
        ]
        + [
            ("CreateAnchorPlane", "create_anchor_plane", (x, y, z, u))
            for x in VALID_INT
            for y in VALID_INT
            for z in VALID_INT
            for u in INVALID_STR
        ]
        + [
            ("ApplyAnchorPlane", "apply_anchor_plane", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_MOCK.PLOT)
        ]
        + [
            ("ApplyAnchorPlane", "apply_anchor_plane", (x, y))
            for x in VALID_INT
            for y in INVALID_MOCK
        ]
        + [
            ("SetAnchorPlaneNodes", "set_anchor_plane_nodes", (x, y, z, u))
            for x in INVALID_INT
            for y in VALID_INT
            for z in VALID_INT
            for u in VALID_INT
        ]
        + [
            ("SetAnchorPlaneNodes", "set_anchor_plane_nodes", (x, y, z, u))
            for x in VALID_INT
            for y in INVALID_INT
            for z in VALID_INT
            for u in VALID_INT
        ]
        + [
            ("SetAnchorPlaneNodes", "set_anchor_plane_nodes", (x, y, z, u))
            for x in VALID_INT
            for y in VALID_INT
            for z in INVALID_INT
            for u in VALID_INT
        ]
        + [
            ("SetAnchorPlaneNodes", "set_anchor_plane_nodes", (x, y, z, u))
            for x in VALID_INT
            for y in VALID_INT
            for z in VALID_INT
            for u in INVALID_INT
        ]
        + [
            ("GetAnchorPlaneNode", "get_anchor_plane_node", (x, y))
            for x in INVALID_INT
            for y in VALID_INT
        ]
        + [
            ("GetAnchorPlaneNode", "get_anchor_plane_node", (x, y))
            for x in VALID_INT
            for y in INVALID_INT
        ]
        + [
            ("SetAnchorPlaneName", "set_anchor_plane_name", (x, y))
            for x in INVALID_INT
            for y in VALID_STR
        ]
        + [
            ("SetAnchorPlaneName", "set_anchor_plane_name", (x, y))
            for x in VALID_INT
            for y in INVALID_STR
        ]
        + [("DeleteAnchorPlaneByIndex", "delete_anchor_plane_by_index", (x,)) for x in INVALID_INT]
        + [("DeleteAnchorPlaneByName", "delete_anchor_plane_by_name", (x,)) for x in INVALID_STR]
        + [("GetDataDisplayFormat", "get_data_display_format", (x,)) for x in INVALID_INT]
        + [
            ("SetDataDisplayFormat", "set_data_display_format", (x, y))
            for x in INVALID_INT
            for y in VALID_STR
        ]
        + [
            ("SetDataDisplayFormat", "set_data_display_format", (x, y))
            for x in VALID_INT
            for y in INVALID_STR
        ]
        + [
            ("WarpQueryNode", "warp_query_node", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_INT, VALID_INT, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            ("WarpQueryNode", "warp_query_node", (x, y, z))
            for x, y, z in pad_and_zip(VALID_INT, INVALID_INT, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            ("WarpQueryNode", "warp_query_node", (x, y, z))
            for x, y, z in pad_and_zip(VALID_INT, VALID_INT, INVALID_MOCK)
        ]
        + [
            ("WarpQueryBegin", "warp_query_begin", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [("WarpQueryBegin", "warp_query_begin", (x, y)) for x in VALID_INT for y in INVALID_MOCK]
        + [("GetAnchorPlaneIndex", "get_anchor_plane_index", (x,)) for x in INVALID_STR]
        + [
            ("MarkResultForExport", "mark_result_for_export", (x, y))
            for x in INVALID_STR
            for y in VALID_BOOL
        ]
        + [
            ("MarkResultForExport", "mark_result_for_export", (x, y))
            for x in VALID_STR
            for y in INVALID_BOOL
        ]
        + [("MarkAllResultsForExport", "mark_all_results_for_export", (x,)) for x in INVALID_BOOL]
        + [("GetResultsFileName", "get_results_file_name", (x,)) for x in INVALID_INT]
        + [
            ("MarkResultForExportByID", "mark_result_for_export_by_id", (x, y))
            for x in INVALID_INT
            for y in VALID_BOOL
        ]
        + [
            ("MarkResultForExportByID", "mark_result_for_export_by_id", (x, y))
            for x in VALID_INT
            for y in INVALID_BOOL
        ]
        + [("FindDatasetByID", "find_dataset_by_id", (x,)) for x in INVALID_INT]
        + [
            ("CreateMaterialPlot", "create_material_plot", (x, y, z))
            for x in INVALID_INT
            for y in MaterialIndex
            for z in VALID_INT
        ]
        + [
            ("CreateMaterialPlot", "create_material_plot", (x, y, z))
            for x in MaterialDatabase
            for y in INVALID_INT
            for z in VALID_INT
        ]
        + [
            ("CreateMaterialPlot", "create_material_plot", (x, y, z))
            for x in MaterialDatabase
            for y in MaterialIndex
            for z in INVALID_INT
        ]
        + [("FindPlotByName", "find_plot_by_name", (x, y)) for x in INVALID_STR for y in VALID_STR]
        + [
            ("FindPlotByName", "find_plot_by_name", (x, y))
            for x in VALID_STR
            for y in INVALID_STR
            if y is not None
        ]
        + [
            ("SaveResultDataInXML", "save_result_data_in_xml", (x, "sample.xml", y))
            for x in INVALID_INT
            for y in SYSTEM_UNITS_AND_NONE
        ]
        + [
            ("SaveResultDataInXML", "save_result_data_in_xml", (x, y, z))
            for x in VALID_INT
            for y in INVALID_STR
            for z in SYSTEM_UNITS_AND_NONE
        ]
        + [
            ("SaveResultDataInXML", "save_result_data_in_xml", (x, "sample.xml", y))
            for x in VALID_INT
            for y in INVALID_STR
            if y is not None
        ]
        + [("ExportToSDZ", "export_to_sdz", (x,)) for x in INVALID_STR]
        + [
            ("SaveResultDataInPatran", "save_result_data_in_patran", (x, "sample.ele", z))
            for x in INVALID_INT
            for z in SystemUnits
        ]
        + [
            ("SaveResultDataInPatran", "save_result_data_in_patran", (x, y, z))
            for x in VALID_INT
            for y in INVALID_STR
            for z in SystemUnits
        ]
        + [
            ("SaveResultDataInPatran", "save_result_data_in_patran", (x, "sample.ele", z))
            for x in VALID_INT
            for z in [x for x in INVALID_STR if x is not None]
        ]
        + [
            ("FBXExport", "fbx_export", (a, x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                INVALID_MOCK,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                VALID_MOCK.ENT_LIST,
                INVALID_MOCK,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                INVALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                INVALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                INVALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for a, x, y, z, u, v, w in pad_and_zip(
                INVALID_STR,
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                INVALID_STR,
            )
        ]
        + [("ExportToVTK", "export_to_vtk", ("export.vtk", x)) for x in INVALID_BOOL],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_type(
        self, mock_plot_manager: PlotManager, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the functions that return a Plot object with invalid type.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_plot_manager, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, mock_user_plot",
        [("CreateUserPlot", "create_user_plot", VALID_MOCK.USER_PLOT)],
    )
    # pylint: disable-next=R0913, R0917
    def test_attribute_return_user_plot(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        mock_user_plot,
        pascal_name,
        property_name,
    ):
        """
        Test the create_user_plot method.
        """
        setattr(mock_object, pascal_name, mock_user_plot.user_plot)
        result = getattr(mock_plot_manager, property_name)()
        assert isinstance(result, UserPlot)
        assert result.user_plot == mock_user_plot.user_plot

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("CreateMaterialPlot", "create_material_plot", (x, y, z), (x.value, y.value, z))
            for x in MaterialDatabase
            for y in MaterialIndex
            for z in VALID_INT
        ]
        + [
            (
                "CreateMaterialPlot",
                "create_material_plot",
                (x.value, y.value, z),
                (x.value, y.value, z),
            )
            for x in MaterialDatabase
            for y in MaterialIndex
            for z in VALID_INT
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_function_return_material_plot(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the create_material_plot method.
        """
        expected_material_plot = VALID_MOCK.MATERIAL_PLOT
        getattr(mock_object, pascal_name).return_value = expected_material_plot.material_plot
        result = getattr(mock_plot_manager, property_name)(*args)
        assert isinstance(result, MaterialPlot)
        assert result.material_plot == expected_material_plot.material_plot
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, value_type",
        [("GetNumberOfAnchorPlanes", "get_number_of_anchor_planes", x, int) for x in VALID_INT]
        + [("AddDefaultPlots", "add_default_plots", x, bool) for x in VALID_BOOL]
        + [("GetNumberOfResultsFiles", "get_number_of_results_files", x, int) for x in VALID_INT],
    )
    # pylint: disable-next=R0913, R0917
    def test_properties(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        value,
        value_type,
    ):
        """
        Test the properties of the PlotManager class.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_plot_manager, property_name)()
        assert isinstance(result, value_type)
        assert result == value

    @pytest.mark.parametrize(
        "plot_name, dataset_name",
        [(x, y) for x in VALID_STR for y in VALID_STR] + [(x, None) for x in VALID_STR],
    )
    def test_find_plot_by_name(
        self, mock_plot_manager: PlotManager, mock_object, plot_name, dataset_name
    ):
        """
        Test the find_plot_by_name method.
        """
        expected_plot = VALID_MOCK.PLOT
        mock_object.FindPlotByName.return_value = expected_plot.plot
        mock_object.FindPlotByName2.return_value = expected_plot.plot
        result = mock_plot_manager.find_plot_by_name(plot_name, dataset_name)
        assert isinstance(result, Plot)
        assert result.plot == expected_plot.plot
        if dataset_name is None:
            mock_object.FindPlotByName.assert_called_once_with(plot_name)
            mock_object.FindPlotByName2.assert_not_called()
        else:
            mock_object.FindPlotByName.assert_not_called()
            mock_object.FindPlotByName2.assert_called_once_with(plot_name, dataset_name)

    @pytest.mark.parametrize(
        "plot_name, dataset_name",
        [(x, y) for x in VALID_STR for y in VALID_STR] + [(x, None) for x in VALID_STR],
    )
    def test_find_plot_by_name_none(
        self, mock_plot_manager: PlotManager, mock_object, plot_name, dataset_name
    ):
        """
        Test the functions that return a Plot object.
        """
        mock_object.FindPlotByName.return_value = None
        mock_object.FindPlotByName2.return_value = None
        result = mock_plot_manager.find_plot_by_name(plot_name, dataset_name)
        assert result is None
        if dataset_name is None:
            mock_object.FindPlotByName.assert_called_once_with(plot_name)
            mock_object.FindPlotByName2.assert_not_called()
        else:
            mock_object.FindPlotByName.assert_not_called()
            mock_object.FindPlotByName2.assert_called_once_with(plot_name, dataset_name)

    @pytest.mark.parametrize(
        "data_id, unit_sys, unit_sys_expected",
        [(x, y, y.value) for x in VALID_INT for y in SystemUnits]
        + [(x, y.value, y.value) for x in VALID_INT for y in SystemUnits]
        + [(x, "", "") for x in VALID_INT],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions2(
        self, mock_plot_manager: PlotManager, mock_object, data_id, unit_sys, unit_sys_expected
    ):
        """
        Test the save functions with valid file type.

        Args:
            mock_plot: The mock plot object.
            mock_object: The mock object.
            data_id: The data ID.
            file_name: The file name.
            unit_sys: The unit system.
        """
        file_name = "sample.xml"
        mock_object.SaveResultDataInXML.return_value = True
        mock_object.SaveResultDataInXML2.return_value = True
        result = mock_plot_manager.save_result_data_in_xml(data_id, file_name, unit_sys)
        assert isinstance(result, bool)
        assert result is True
        if unit_sys_expected is None:
            unit_sys_expected = ""
        mock_object.SaveResultDataInXML.assert_not_called()
        mock_object.SaveResultDataInXML2.assert_called_once_with(
            data_id, file_name, unit_sys_expected
        )

    @pytest.mark.parametrize(
        "data_id, unit_sys", [(x, y) for x in VALID_INT for y in SYSTEM_UNITS_AND_NONE]
    )
    def test_save_functions2_save_error(
        self, mock_plot_manager: PlotManager, mock_object, data_id, unit_sys, _
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        file_name = "sample.xml"
        mock_object.SaveResultDataInXML.return_value = False
        mock_object.SaveResultDataInXML2.return_value = False
        with pytest.raises(SaveError) as e:
            mock_plot_manager.save_result_data_in_xml(data_id, file_name, unit_sys)
        assert _("Save Error") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [("ExportToSDZ", "export_to_sdz", ("sample.sdz",), ("sample.sdz",))]
        + [
            (
                "SaveResultDataInPatran",
                "save_result_data_in_patran",
                (x, "sample.ele", z),
                (x, "sample.ele", z.value),
            )
            for x in VALID_INT
            for z in SystemUnits
        ]
        + [
            (
                "SaveResultDataInPatran",
                "save_result_data_in_patran",
                (x, "sample.ele", z.value),
                (x, "sample.ele", z.value),
            )
            for x in VALID_INT
            for z in SystemUnits
        ]
        + [
            (
                "FBXExport",
                "fbx_export",
                ("sample.fbx", x, y, z, u, v, w),
                ("sample.fbx", x.ent_list, y.ent_list, z, u, v, w.value),
            )
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            (
                "FBXExport",
                "fbx_export",
                ("sample.fbx", x, y, z, u, v, w.value),
                ("sample.fbx", x.ent_list, y.ent_list, z, u, v, w.value),
            )
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [
            ("ExportToVTK", "export_to_vtk", ("sample.vtk", x), ("sample.vtk", x))
            for x in VALID_BOOL
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions(
        self,
        mock_plot_manager: PlotManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the save functions with valid file type.

        Args:
            mock_plot: The mock plot object.
            mock_object: The mock object.
            pascal_name: The name of the Pascal case function.
            property_name: The name of the property in the PlotManager class.
            args: The arguments to pass to the function.
            expected_args: The expected arguments to pass to the function.
        """
        getattr(mock_object, pascal_name).return_value = True
        result = getattr(mock_plot_manager, property_name)(*args)
        assert isinstance(result, bool)
        assert result is True
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("ExportToSDZ", "export_to_sdz", ("sample.sdz",))]
        + [
            ("SaveResultDataInPatran", "save_result_data_in_patran", (x, "sample.ele", z))
            for x in VALID_INT
            for z in SystemUnits
        ]
        + [
            ("FBXExport", "fbx_export", ("sample.fbx", x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_FLOAT,
                VALID_FLOAT,
                SystemUnits,
            )
        ]
        + [("ExportToVTK", "export_to_vtk", ("sample.vtk", x)) for x in VALID_BOOL],
    )
    # pylint: disable-next=R0913, R0917
    def test_save_functions_save_error(
        self, mock_plot_manager: PlotManager, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test save functions of Plot.

        Args:
            mock_plot: Instance of Plot.
            mock_object: Mock object for the Plot dependency.
        """
        getattr(mock_object, pascal_name).return_value = False
        with pytest.raises(SaveError) as e:
            getattr(mock_plot_manager, property_name)(*args)
        assert _("Save Error") in str(e.value)
