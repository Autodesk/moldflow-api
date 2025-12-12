# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    PlotManager Class API Wrapper
"""

# pylint: disable=C0302

from .logger import process_log, LogMessage
from .plot import Plot
from .double_array import DoubleArray
from .ent_list import EntList
from .integer_array import IntegerArray
from .material_plot import MaterialPlot
from .user_plot import UserPlot
from .common import MaterialDatabase, MaterialIndex, PlotType, SystemUnits
from .helper import check_type, check_optional_type, check_and_coerce_optional, get_enum_value, check_file_extension, coerce_optional_dispatch
from .com_proxy import safe_com
from .errors import raise_save_error
from .constants import XML_FILE_EXT, SDZ_FILE_EXT, FBX_FILE_EXT, ELE_FILE_EXT

class PlotManager:
    """
    Wrapper for PlotManager class of Moldflow Synergy.
    """

    def __init__(self, _plot_manager):
        """
        Initialize the PlotManager with a PlotManager instance from COM.

        Args:
            _plot_manager: The PlotManager instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="PlotManager")
        self.plot_manager = safe_com(_plot_manager)

    def get_first_plot(self) -> Plot:
        """
        Get the first plot

        Returns:
            Plot: The first plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_plot")
        result = self.plot_manager.GetFirstPlot
        if result is None:
            return None
        return Plot(result)

    def get_next_plot(self, plot: Plot | None) -> Plot:
        """
        Get the next plot

        Args:
            plot (Plot): The current plot.

        Returns:
            Plot: The next plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_plot")
        check_optional_type(plot, Plot)
        result = self.plot_manager.GetNextPlot(coerce_optional_dispatch(plot, "plot"))
        if result is None:
            return None
        return Plot(result)

    def create_plot_by_ds_id(self, ds_id: int, plot_type: PlotType | int) -> Plot:
        """
        Create a plot by dataset ID

        Args:
            ds_id (int): The dataset ID.
            plot_type (PlotType | int): The type of the plot.

        Returns:
            Plot: The created plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_plot_by_ds_id")
        check_type(ds_id, int)
        plot_type = get_enum_value(plot_type, PlotType)
        result = self.plot_manager.CreatePlotByDsID2(ds_id, plot_type)
        if result is None:
            return None
        return Plot(result)

    def create_plot_by_name(self, plot_name: str, is_xy_plot: bool) -> Plot:
        """
        Create a plot by name

        Args:
            plot_name (str): The name of the plot.
            is_xy_plot (bool): Whether an XY plot needs to be created
            (only if this dataset supports XY plots)

        Returns:
            Plot: The created plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_plot_by_name")
        check_type(plot_name, str)
        check_type(is_xy_plot, bool)
        result = self.plot_manager.CreatePlotByName(plot_name, is_xy_plot)
        if result is None:
            return None
        return Plot(result)

    def create_xy_plot_by_name(self, plot_name: str) -> Plot:
        """
        Create an XY plot by name

        Args:
            plot_name (str): The name of the plot.

        Returns:
            Plot: The created XY plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_xy_plot_by_name")
        check_type(plot_name, str)
        result = self.plot_manager.CreateXYPlotByName(plot_name)
        if result is None:
            return None
        return Plot(result)

    def delete_plot_by_name(self, plot_name: str) -> None:
        """
        Delete a plot by name

        Args:
            plot_name (str): The name of the plot to delete.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_plot_by_name")
        check_type(plot_name, str)
        self.plot_manager.DeletePlotByName(plot_name)

    def delete_plot_by_ds_id(self, ds_id: int) -> None:
        """
        Delete a plot by dataset ID

        Args:
            ds_id (int): The dataset ID of the plot to delete.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_plot_by_ds_id")
        check_type(ds_id, int)
        self.plot_manager.DeletePlotByDsID(ds_id)

    def delete_plot(self, plot: Plot | None) -> None:
        """
        Delete a plot
        [You cannot use the plot object after it has been deleted,
        e.g., as a parameter in the GetNextPlot function]

        Args:
            plot (Plot): The plot to delete.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_plot")
        check_optional_type(plot, Plot)
        self.plot_manager.DeletePlot(coerce_optional_dispatch(plot, "plot"))

    def data_has_xy_plot_by_ds_id(self, ds_id: int) -> bool:
        """
        Check if the data has an XY plot by dataset ID

        Args:
            ds_id (int): The dataset ID of the plot.

        Returns:
            bool: True if the data has an XY plot, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="data_has_xy_plot_by_ds_id")
        check_type(ds_id, int)
        return self.plot_manager.DataHasXYPlotByDsID(ds_id)

    def data_has_xy_plot_by_name(self, name: str) -> bool:
        """
        Check if the data has an XY plot by name

        Args:
            name (str): The name of the dataset.

        Returns:
            bool: True if the data has an XY plot, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="data_has_xy_plot_by_name")
        check_type(name, str)
        return self.plot_manager.DataHasXYPlotByName(name)

    def get_scalar_data(
        self,
        ds_id: int,
        indp_values: DoubleArray | None,
        ent_ids: IntegerArray | None,
        scalar_data: DoubleArray | None,
    ) -> bool:
        """
        Get scalar data for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            indp_values (DoubleArray): The independent variable values.
            ent_ids (IntegerArray): The entity IDs.
            scalar_data (DoubleArray): The scalar data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_scalar_data")
        check_type(ds_id, int)

        return self.plot_manager.GetScalarData(
            ds_id,
            check_and_coerce_optional(indp_values, DoubleArray),
            check_and_coerce_optional(ent_ids, IntegerArray),
            check_and_coerce_optional(scalar_data, DoubleArray),
        )

    # pylint: disable-next=R0913, R0917
    def get_vector_data(
        self,
        ds_id: int,
        indp_values: DoubleArray | None,
        ent_ids: IntegerArray | None,
        va: DoubleArray | None,
        vb: DoubleArray | None,
        vc: DoubleArray | None,
    ) -> bool:
        """
        Get vector data for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            indp_values (DoubleArray): The independent variable values.
            ent_ids (IntegerArray): The entity IDs.
            va (DoubleArray): The X component of the vector data.
            vb (DoubleArray): The Y component of the vector data.
            vc (DoubleArray): The Z component of the vector data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_vector_data")
        check_type(ds_id, int)

        return self.plot_manager.GetVectorData(
            ds_id,
            check_and_coerce_optional(indp_values, DoubleArray),
            check_and_coerce_optional(ent_ids, IntegerArray),
            check_and_coerce_optional(va, DoubleArray),
            check_and_coerce_optional(vb, DoubleArray),
            check_and_coerce_optional(vc, DoubleArray),
        )

    # pylint: disable-next=R0913, R0917
    def get_tensor_data(
        self,
        ds_id: int,
        indp_values: DoubleArray | None,
        ent_ids: IntegerArray | None,
        t11: DoubleArray | None,
        t22: DoubleArray | None,
        t33: DoubleArray | None,
        t12: DoubleArray | None,
        t13: DoubleArray | None,
        t23: DoubleArray | None,
    ) -> bool:
        """
        Get tensor data for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            indp_values (DoubleArray): The independent variable values.
            ent_ids (IntegerArray): The entity IDs.
            t11 (DoubleArray): The 11 component of the tensor data.
            t22 (DoubleArray): The 22 component of the tensor data.
            t33 (DoubleArray): The 33 component of the tensor data.
            t12 (DoubleArray): The 12 component of the tensor data.
            t13 (DoubleArray): The 13 component of the tensor data.
            t23 (DoubleArray): The 23 component of the tensor data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_tensor_data")
        check_type(ds_id, int)

        return self.plot_manager.GetTensorData(
            ds_id,
            check_and_coerce_optional(indp_values, DoubleArray),
            check_and_coerce_optional(ent_ids, IntegerArray),
            check_and_coerce_optional(t11, DoubleArray),
            check_and_coerce_optional(t22, DoubleArray),
            check_and_coerce_optional(t33, DoubleArray),
            check_and_coerce_optional(t12, DoubleArray),
            check_and_coerce_optional(t13, DoubleArray),
            check_and_coerce_optional(t23, DoubleArray),
        )

    def get_non_mesh_data(
        self, ds_id: int, indp_values: DoubleArray | None, non_mesh_data: DoubleArray | None
    ) -> bool:
        """
        Get non-mesh data for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            indp_values (DoubleArray): The independent variable values.
            non_mesh_data (DoubleArray): The non-mesh data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_non_mesh_data")
        check_type(ds_id, int)

        return self.plot_manager.GetNonmeshData(
            ds_id,
            check_and_coerce_optional(indp_values, DoubleArray),
            check_and_coerce_optional(non_mesh_data, DoubleArray),
        )

    def get_highlight_data(
        self, ds_id: int, indp_values: DoubleArray | None, highlight_data: DoubleArray | None
    ) -> bool:
        """
        Get highlight data for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            indp_values (DoubleArray): The independent variable values.
            highlight_data (DoubleArray): The highlight data.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_highlight_data")
        check_type(ds_id, int)

        return self.plot_manager.GetHighlightData(
            ds_id,
            check_and_coerce_optional(indp_values, DoubleArray),
            check_and_coerce_optional(highlight_data, DoubleArray),
        )

    def create_user_plot(self) -> UserPlot:
        """
        Create a user plot

        Returns:
            UserPlot: The created user plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_user_plot")
        result = self.plot_manager.CreateUserPlot
        if result is None:
            return None
        return UserPlot(result)

    def find_dataset_id_by_name(self, name: str) -> int:
        """
        Find a dataset ID by name

        Args:
            name (str): The name of the dataset.

        Returns:
            int: The dataset ID.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_dataset_id_by_name")
        check_type(name, str)
        return self.plot_manager.FindDatasetIdByName(name)

    def find_plot_by_name(self, plot_name: str, dataset_name: str | None = None) -> Plot:
        """
        Find a plot by name

        Args:
            plot_name (str): The name of the plot.
            dataset_name (str | None): The name of the data source.

        Returns:
            Plot: The found plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_plot_by_name")
        check_type(plot_name, str)
        result = None
        if dataset_name is None:
            result = self.plot_manager.FindPlotByName(plot_name)
        else:
            check_type(dataset_name, str)
            result = self.plot_manager.FindPlotByName2(plot_name, dataset_name)
        if result is None:
            return None
        return Plot(result)

    def get_indp_var_count(self, ds_id: int) -> int:
        """
        Get the independent variable count for a given dataset ID

        Args:
            ds_id (int): The dataset ID.

        Returns:
            int: The independent variable count.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_indp_var_count")
        check_type(ds_id, int)
        return self.plot_manager.GetIndpVarCount(ds_id)

    def get_indp_values(self, ds_id: int, values: DoubleArray | None) -> bool:
        """
        Get the independent variable values for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            values (DoubleArray): The independent variable values.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_indp_values")
        check_type(ds_id, int)

        return self.plot_manager.GetIndpValues(
            ds_id, check_and_coerce_optional(values, DoubleArray)
        )

    def get_data_nb_components(self, ds_id: int) -> int:
        """
        Get the number of components for a given dataset ID

        Args:
            ds_id (int): The dataset ID.

        Returns:
            int: The number of components. [which could be 1, 3 or 6]
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_data_nb_components")
        check_type(ds_id, int)
        return self.plot_manager.GetDataNbComponents(ds_id)

    def get_data_type(self, ds_id: int) -> str:
        """
        Get the data type for a given dataset ID

        Args:
            ds_id (int): The dataset ID.

        Returns:
            str: The data type string, which can be one of the following
            - LBDT
            - LYDT
            - NDDT
            - ELDT
            - NMDT
            - TXDT
            - HLDT

        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_data_type")
        check_type(ds_id, int)
        return self.plot_manager.GetDataType(ds_id)

    def find_dataset_ids_by_name(self, name: str, ds_ids: IntegerArray | None) -> int:
        """
        Find all dataset IDs by name

        Args:
            name (str): The name of the dataset.
            ds_ids (IntegerArray): The dataset IDs.

        Returns:
            int: The number of dataset IDs found.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_dataset_ids_by_name")
        check_type(name, str)

        return self.plot_manager.FindDatasetIdsByName(
            name, check_and_coerce_optional(ds_ids, IntegerArray)
        )

    def create_anchor_plane(
        self, node_id1: int, node_id2: int, node_id3: int, plane_name: str
    ) -> int:
        """
        Create an anchor plane

        Args:
            node_id1 (int): The first node ID.
            node_id2 (int): The second node ID.
            node_id3 (int): The third node ID.
            plane_name (str): The name of the plane.

        Returns:
            int: The total number of anchor plane, -1 if failed
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_anchor_plane")
        check_type(node_id1, int)
        check_type(node_id2, int)
        check_type(node_id3, int)
        check_type(plane_name, str)
        return self.plot_manager.CreateAnchorPlane(node_id1, node_id2, node_id3, plane_name)

    def apply_anchor_plane(self, anchor_index: int, plot: Plot | None) -> bool:
        """
        Apply an anchor plane to a plot

        Args:
            anchor_index (int): The index of the anchor plane.
            plot (Plot): The plot to apply the anchor plane to.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="apply_anchor_plane")
        check_type(anchor_index, int)
        check_optional_type(plot, Plot)
        return self.plot_manager.ApplyAnchorPlane(
            anchor_index, coerce_optional_dispatch(plot, "plot")
        )

    def set_anchor_plane_nodes(
        self, anchor_index: int, node_id1: int, node_id2: int, node_id3: int
    ) -> bool:
        """
        Set the nodes of an anchor plane

        Args:
            anchor_index (int): The index of the anchor plane.
            node_id1 (int): The first node ID.
            node_id2 (int): The second node ID.
            node_id3 (int): The third node ID.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_anchor_plane_nodes")
        check_type(anchor_index, int)
        check_type(node_id1, int)
        check_type(node_id2, int)
        check_type(node_id3, int)
        return self.plot_manager.SetAnchorPlaneNodes(anchor_index, node_id1, node_id2, node_id3)

    def get_anchor_plane_node(self, anchor_index: int, node_index: int) -> int:
        """
        Get the anchor plane node ID at given index

        Args:
            anchor_index (int): The index of the anchor plane.
            node_index (int): The index of the node.

        Returns:
            int: The node ID.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_anchor_plane_node")
        check_type(anchor_index, int)
        check_type(node_index, int)
        return self.plot_manager.GetAnchorPlaneNode(anchor_index, node_index)

    def set_anchor_plane_name(self, anchor_index: int, name: str) -> bool:
        """
        Set the name of an anchor plane

        Args:
            anchor_index (int): The index of the anchor plane.
            name (str): The name of the anchor plane.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_anchor_plane_name")
        check_type(anchor_index, int)
        check_type(name, str)
        return self.plot_manager.SetAnchorPlaneName(anchor_index, name)

    def get_number_of_anchor_planes(self) -> int:
        """
        Get the number of anchor planes

        Returns:
            int: The number of anchor planes.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="number_of_anchor_planes")
        return self.plot_manager.GetNumberOfAnchorPlanes

    def delete_anchor_plane_by_index(self, anchor_index: int) -> bool:
        """
        Delete an anchor plane by index

        Args:
            anchor_index (int): The index of the anchor plane.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="delete_anchor_plane_by_index"
        )
        check_type(anchor_index, int)
        return self.plot_manager.DeleteAnchorPlaneByIndex(anchor_index)

    def save_result_data_in_xml(
        self, data_id: int, file_name: str, unit_sys: SystemUnits | str = ""
    ) -> bool:
        """
        Save the result in XML format.

        Args:
            data_id (int): The result data ID.
            file_name (str): The file name to save the result.
            unit_sys (SystemUnits | str): The unit system to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_result_data_in_xml")
        check_type(data_id, int)
        check_type(file_name, str)
        file_name = check_file_extension(file_name, XML_FILE_EXT)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot_manager.SaveResultDataInXML2(data_id, file_name, unit_sys)
        if not result:
            raise_save_error(saving="Results", file_name=file_name)
        return result

    def delete_anchor_plane_by_name(self, anchor_name: str) -> bool:
        """
        Delete an anchor plane by name

        Args:
            anchor_name (str): The name of the anchor plane.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="delete_anchor_plane_by_name"
        )
        check_type(anchor_name, str)
        return self.plot_manager.DeleteAnchorPlaneByName(anchor_name)

    def get_data_display_format(self, ds_id: int) -> str:
        """
        Get the display data type for a given dataset ID

        Args:
            ds_id (int): The dataset ID.

        Returns:
            str: The display data type string.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_data_display_format")
        check_type(ds_id, int)
        return self.plot_manager.GetDataDisplayFormat(ds_id)

    def set_data_display_format(self, ds_id: int, format_str: str) -> bool:
        """
        Set the display data type for a given dataset ID

        Args:
            ds_id (int): The dataset ID.
            format_str (str): The the format string(C-style format string).

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_data_display_format")
        check_type(ds_id, int)
        check_type(format_str, str)
        return self.plot_manager.SetDataDisplayFormat(ds_id, format_str)

    def warp_query_end(self) -> None:
        """
        End the warp query

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="warp_query_end")
        self.plot_manager.WarpQueryEnd()

    def warp_query_node(
        self, node_id: int, anchor_index: int, ret_values: DoubleArray | None
    ) -> bool:
        """
        Warp query for a node

        Args:
            node_id (int): The node ID.
            anchor_index (int): The index of the anchor plane.
            ret_values (DoubleArray): The return values.
            Note:
            If anchor plane is specified, the return array contains
            - 18 values which are the following values:
            -- Index 0, 1, 2: X, Y, Z coordinates in global coordinate system before deflection
            -- Index 3, 4, 5: X, Y, Z coordinates in global coordinate system after deflection
            -- Index 6, 7, 8: X, Y, Z coordinates in local coordinate system before deflection
            -- Index 9, 10, 11: X, Y, Z coordinates in local coordinate system after deflection
            -- Index 12, 13, 14: X, Y, Z displacement components in global coordinate system
            -- Index 15, 16, 17: X, Y, Z displacement components in local coordinate system
            - otherwise, the return array contains 9 values which are the following values:
            -- Index 0, 1, 2: X, Y, Z coordinates in global coordinate system before deflection
            -- Index 3, 4, 5: X, Y, Z coordinates in global coordinate system after deflection
            -- Index 6, 7, 8: X, Y, Z displacement components in global coordinate system

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="warp_query_node")
        check_type(node_id, int)
        check_type(anchor_index, int)

        return self.plot_manager.WarpQueryNode(
            node_id, anchor_index, check_and_coerce_optional(ret_values, DoubleArray)
        )

    def warp_query_begin(self, ds_id: int, indp_values: DoubleArray | None) -> bool:
        """
        Begin the warp query

        Args:
            ds_id (int): The dataset ID.
            indp_values (DoubleArray): The independent variable values.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="warp_query_begin")
        check_type(ds_id, int)

        return self.plot_manager.WarpQueryBegin(
            ds_id, check_and_coerce_optional(indp_values, DoubleArray)
        )

    def export_to_sdz(self, file_name: str) -> bool:
        """
        Export the results to a SDZ file

        Args:
            file_name (str): The name of the SDZ file.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="export_to_sdz")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, SDZ_FILE_EXT)
        result = self.plot_manager.ExportToSDZ(file_name)
        if not result:
            raise_save_error(saving="Results", file_name=file_name)
        return result

    def get_anchor_plane_index(self, anchor_name: str) -> int:
        """
        Get the index of an anchor plane by name

        Args:
            anchor_name (str): The name of the anchor plane.

        Returns:
            int: The index of the anchor, otherwise -1.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_anchor_plane_index")
        check_type(anchor_name, str)
        return self.plot_manager.GetAnchorPlaneIndex(anchor_name)

    def mark_result_for_export(self, result_name: str, export: bool) -> bool:
        """
        Mark a result for export

        Args:
            result_name (str): The name of the result.
            export (bool): Whether to export the result.
            True to export, False to not export.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="mark_result_for_export")
        check_type(result_name, str)
        check_type(export, bool)
        return self.plot_manager.MarkResultForExport(result_name, export)

    def mark_all_results_for_export(self, export: bool) -> bool:
        """
        Mark all results for export

        Args:
            export (bool): Whether to export the results.
            True to export, False to not export.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="mark_all_results_for_export"
        )
        check_type(export, bool)
        return self.plot_manager.MarkAllResultsForExport(export)

    def add_default_plots(self) -> bool:
        """
        Add all default plots in the study

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_default_plots")
        return self.plot_manager.AddDefaultPlots

    def save_result_data_in_patran(
        self, data_id: int, file_name: str, unit_sys: SystemUnits | str = ""
    ) -> bool:
        """
        Save the result in Patran format.

        Args:
            data_id (int): The result data ID.
            file_name (str): The file name to save the result.
            unit_sys (SystemUnits | str): The unit system to use.
            None is treated as empty string.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_result_data_in_patran")
        check_type(data_id, int)
        check_type(file_name, str)
        file_name = check_file_extension(file_name, ELE_FILE_EXT)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot_manager.SaveResultDataInPatran(data_id, file_name, unit_sys)
        if not result:
            raise_save_error(saving="Results", file_name=file_name)
        return result

    def get_number_of_results_files(self) -> int:
        """
        Get the number of results files

        Returns:
            int: The number of results files.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_number_of_results_files"
        )
        return self.plot_manager.GetNumberOfResultsFiles

    def get_results_file_name(self, index: int) -> str:
        """
        Get the name of a results file by index

        Args:
            index (int): The index of the results file.

        Returns:
            str: The name of the results file.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_results_file_name")
        check_type(index, int)
        return self.plot_manager.GetResultsFileName(index)

    def mark_result_for_export_by_id(self, ds_id: int, export: bool) -> bool:
        """
        Mark a result for export by dataset ID

        Args:
            ds_id (int): The dataset ID.
            export (bool): Whether to export the result.
            True to export, False to not export.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="mark_result_for_export_by_id"
        )
        check_type(ds_id, int)
        check_type(export, bool)
        return self.plot_manager.MarkResultForExportByID(ds_id, export)

    def find_dataset_by_id(self, ds_id: int) -> bool:
        """
        Check whether the result data with the given id exists in the results files

        Args:
            ds_id (int): The dataset ID.

        Returns:
            bool: True if the dataset exists, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_dataset_by_id")
        check_type(ds_id, int)
        return self.plot_manager.FindDatasetByID(ds_id)

    # pylint: disable-next=R0913, R0917
    def fbx_export(
        self,
        file_name: str,
        geo_list: EntList | None,
        mesh_list: EntList | None,
        export_type: int,
        wp_scale_factor: float,
        sm_scale_factor: float,
        unit_sys: SystemUnits | str = "",
    ) -> bool:
        """
        Export selected geometry entities with sink mark and/or warp results mapped on them

        Args:
            file_name (str): The name of the FBX file.
            geo_list (EntList): The geometry list.
            mesh_list (EntList): The mesh list.
            export_type (int): The export type.
            wp_scale_factor (float): The warp scale factor.
            sm_scale_factor (float): The scale factor for the SM.
            unit_sys (SystemUnits | str): The unit system to use.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="fbx_export")
        check_type(file_name, str)
        file_name = check_file_extension(file_name, FBX_FILE_EXT)

        check_type(export_type, int)
        check_type(wp_scale_factor, (float, int))
        check_type(sm_scale_factor, (float, int))
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        result = self.plot_manager.FBXExport(
            file_name,
            check_and_coerce_optional(geo_list, EntList),
            check_and_coerce_optional(mesh_list, EntList),
            export_type,
            wp_scale_factor,
            sm_scale_factor,
            unit_sys,
        )
        if not result:
            raise_save_error(saving="FBX", file_name=file_name)
        return result

    def create_material_plot(
        self,
        mat_database: MaterialDatabase | int,
        material_index: MaterialIndex | int,
        property_id: int,
    ) -> MaterialPlot:
        """
        Create a material plot

        Args:
            mat_database (MaterialDatabase | int): The material database.
            material_index (MaterialIndex | int): The material index.
            property_id (int): The property ID.

        Returns:
            MaterialPlot: The created material plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_material_plot")
        mat_database = get_enum_value(mat_database, MaterialDatabase)
        material_index = get_enum_value(material_index, MaterialIndex)
        check_type(property_id, int)
        result = self.plot_manager.CreateMaterialPlot(mat_database, material_index, property_id)
        if result is None:
            return None
        return MaterialPlot(result)
