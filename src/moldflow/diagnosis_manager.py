# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Usage:
    DiagnosisManager Class API Wrapper
"""

from .logger import process_log
from .common import LogMessage
from .helper import check_type, check_min_max, coerce_optional_dispatch
from .com_proxy import safe_com
from .ent_list import EntList
from .mesh_summary import MeshSummary
from .integer_array import IntegerArray
from .double_array import DoubleArray


class DiagnosisManager:
    """
    Wrapper for DiagnosisManager class of Moldflow Synergy.
    """

    def __init__(self, _diagnosis_manager):
        """
        Initialize the DiagnosisManager with a DiagnosisManager instance from COM.

        Args:
            _diagnosis_manager: The DiagnosisManager instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="DiagnosisManager")
        self.diagnosis_manager = safe_com(_diagnosis_manager)

    def show_diagnosis(self, visible: bool = False) -> None:
        """
        Show/hide the selected mesh diagnostic

        Args:
            visible (bool): Show/hide mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_diagnosis")
        check_type(visible, bool)
        self.diagnosis_manager.ShowDiagnosis(visible)

    def show_thickness(
        self, min_value: float, max_value: float, assign_layer: bool, visible: bool = False
    ) -> None:
        """
        Generates thickness diagnostics

        Args:
            min_value (float): Minimum thickness value.
            max_value (float): Maximum thickness value.
            assign_layer (bool): Assign layer to the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_thickness")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowThickness2(min_value, max_value, assign_layer, visible)

    # pylint: disable=R0913, R0917
    def show_aspect_ratio(
        self,
        min_value: float,
        max_value: float,
        std_ar: bool,
        assign_layer: bool,
        show_txt: bool,
        visible: bool = False,
    ) -> None:
        """
        Generates aspect ratio diagnostics

        Args:
            min_value (float): Minimum aspect ratio value.
            max_value (float): Maximum aspect ratio value.
            std_ar (bool): Standard aspect ratio.
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_aspect_ratio")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        check_type(std_ar, bool)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowAspectRatio2(
            min_value, max_value, std_ar, assign_layer, show_txt, visible
        )

    def create_entity_list(self) -> EntList:
        """
        Creates an empty EntList object

        Returns:
            EntList: The created entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.diagnosis_manager.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    # pylint: disable=R0913, R0917
    def show_connect(
        self,
        nodes: EntList | None,
        ex_beam: bool,
        assign_layer: bool,
        show_txt: bool,
        visible: bool = False,
    ) -> None:
        """
        Generates connectivity diagnostics

        Args:
            nodes (EntList | None): The nodes to show connectivity for.
            ex_beam (bool): Show external beam.
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_connect")
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(ex_beam, bool)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowConnect2(
            coerce_optional_dispatch(nodes, "ent_list"), ex_beam, assign_layer, show_txt, visible
        )

    def show_edges(
        self, non_manifold: bool, assign_layer: bool, show_txt: bool, visible: bool = False
    ) -> None:
        """
        Generates free and manifold edge diagnostics

        Args:
            non_manifold (bool): Show non-manifold edges.
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_edges")
        check_type(non_manifold, bool)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowEdges2(non_manifold, assign_layer, show_txt, visible)

    # pylint: disable=R0913, R0917
    def show_overlapping(
        self,
        overlap: bool,
        intersect: bool,
        ex_tri: bool,
        ex_beam: bool,
        assign_layer: bool,
        show_txt: bool,
        visible: bool = False,
    ) -> None:
        """
        Generates diagnostics for overlaps and intersections

        Args:
            overlap (bool): Show overlapping elements.
            intersect (bool): Show intersecting elements.
            ex_tri (bool): Show external triangles.
            ex_beam (bool): Show external beams.
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_overlapping")
        check_type(overlap, bool)
        check_type(intersect, bool)
        check_type(ex_tri, bool)
        check_type(ex_beam, bool)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowOverlapping3(
            overlap, intersect, ex_tri, ex_beam, assign_layer, show_txt, visible
        )

    def show_overlapping_txt(self, overlap: bool, intersect: bool) -> None:
        """
        Generates diagnostics for overlaps and intersections

        Args:
            overlap (bool): Show overlapping elements.
            intersect (bool): Show intersecting elements.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_overlapping_txt")
        check_type(overlap, bool)
        check_type(intersect, bool)
        self.diagnosis_manager.ShowOverlappingTxt(overlap, intersect)

    def show_match_info(self, assign_layer: bool, show_txt: bool, reciprocal: bool = False) -> None:
        """
        Generates mesh match diagnostics

        Args:
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            reciprocal (bool): Show reciprocal mesh matching
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_match_info")
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(reciprocal, bool)
        self.diagnosis_manager.ShowMatchInfo2(assign_layer, show_txt, reciprocal)

    def show_occurrence(self, assign_layer: bool, visible: bool = False) -> None:
        """
        Generates occurrence number diagnostics

        Args:
            assign_layer (bool): Assign layer to the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_occurrence")
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowOccurrence2(assign_layer, visible)

    def show_orient(self, assign_layer: bool, show_txt: bool, visible: bool = False) -> None:
        """
        Generates mesh orientation diagnostics

        Args:
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_orient")
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowOrient2(assign_layer, show_txt, visible)

    def show_summary(
        self, element_only: bool = False, inc_beams: bool = True, inc_match: bool = True
    ) -> None:
        """
        Generates diagnostics summary

        Args:
            element_only (bool):
                True - to get element counts summary only, which includes TrianglesCount,
                    NodesCount, BeamsCount, MeshVolume and RunnerVolume
                False - to get all mesh summary

            inc_beams (bool):
                True - to get mesh summary including beam elements. Multiple cavities connected by
                    beams will be counted as one region
                False - to get mesh summary without beam elements. Multiple cavities connected by
                    beams will be counted as separate regions

            inc_match (bool):
                True - to get mesh summary including match ratios
                False - to get mesh summary without match ratios. This will be faster when match
                    ratios are not needed
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_summary")
        check_type(element_only, bool)
        check_type(inc_beams, bool)
        check_type(inc_match, bool)
        self.diagnosis_manager.ShowSummary2(element_only, inc_beams, inc_match)

    def show_summary_for_beams(self, visible: bool = False) -> None:
        """
        Generates diagnostics summary for beams

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_summary_for_beams")
        check_type(visible, bool)
        self.diagnosis_manager.ShowSummaryForBeams(visible)

    def show_summary_for_tris(self, visible: bool, inc_extra_info: bool) -> None:
        """
        Generates diagnostics summary for triangles

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
            inc_extra_info (bool): Include defects information in the diagnosis
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_summary_for_tris")
        check_type(visible, bool)
        check_type(inc_extra_info, bool)
        self.diagnosis_manager.ShowSummaryForTris(visible, inc_extra_info)

    def show_summary_for_tets(self, visible: bool) -> None:
        """
        Generates diagnostics summary for tetrahedra

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_summary_for_tets")
        check_type(visible, bool)
        self.diagnosis_manager.ShowSummaryForTets(visible)

    def get_thickness_diagnosis(
        self,
        min_value: float,
        max_value: float,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get thickness diagnostics

        Args:
            min_value (float): Minimum thickness value. 0 for all thickness
            max_value (float): Maximum thickness value. 0 for all thickness
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of thickness diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_thickness_diagnosis")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetThicknessDiagnosis2(
            min_value,
            max_value,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_aspect_ratio_diagnosis(
        self,
        min_value: float,
        max_value: float,
        std_ar: bool,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get aspect ratio diagnostics

        Args:
            min_value (float): Minimum aspect ratio value.
            max_value (float): Maximum aspect ratio value.
            std_ar (bool): Standard aspect ratio.
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of aspect ratio diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_aspect_ratio_diagnosis")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        check_type(std_ar, bool)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetAspectRatioDiagnosis2(
            min_value,
            max_value,
            std_ar,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_connectivity_diagnosis(
        self,
        nodes: EntList | None,
        ex_beam: bool,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get connectivity diagnostics

        Args:
            nodes (EntList | None): The nodes to show connectivity for.
            ex_beam (bool): Show external beam.
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of connectivity diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_connectivity_diagnosis")
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(ex_beam, bool)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetConnectivityDiagnosis2(
            coerce_optional_dispatch(nodes, "ent_list"),
            ex_beam,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_edges_diagnosis(
        self,
        non_manifold: bool,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get free and manifold edge diagnostics

        Args:
            non_manifold (bool): Show non-manifold edges.
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): bit field for freeedge / non-manifold

        Returns:
            int: The number of free and manifold edge diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_edges_diagnosis")
        check_type(non_manifold, bool)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetEdgesDiagnosis2(
            non_manifold,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_overlap_diagnosis(
        self,
        overlap: bool,
        intersect: bool,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get overlap diagnostics

        Args:
            overlap (bool): Show overlapping elements.
            intersect (bool): Show intersecting elements.
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): intersect/overlap value 1 - Intersect,

        Returns:
            int: The number of overlap diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_overlap_diagnosis")
        check_type(overlap, bool)
        check_type(intersect, bool)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetOverlapDiagnosis2(
            overlap,
            intersect,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_occurrence_diagnosis(
        self, visible: bool, element_id: IntegerArray | None, value: DoubleArray | None
    ) -> int:
        """
        Get occurrence number diagnostics

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of occurrence diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_occurrence_diagnosis")
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetOccurrenceDiagnosis2(
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_match_info_diagnosis(
        self, element_id: IntegerArray | None, value: DoubleArray | None
    ) -> int:
        """
        Get mesh match diagnostics

        Args:
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of mesh match diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_match_info_diagnosis")
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetMatchInfoDiagnosis(
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_orientation_diagnosis(
        self, visible: bool, element_id: IntegerArray | None, value: DoubleArray | None
    ) -> int:
        """
        Get mesh orientation diagnostics

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of mesh match diagnostics.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_orientation_diagnosis")
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetOrientationDiagnosis2(
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def show_zero_area_elements(
        self, min_value: float, assign_layer: bool, show_txt: bool, visible: bool = False
    ) -> None:
        """
        Generates zero area element diagnostics

        Args:
            min_value (float): Minimum area value. ZeroArea = Sqrt(3)/4 * aMin * aMin
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_zero_area_elements")
        check_type(min_value, (float, int))
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowZeroAreaElements2(min_value, assign_layer, show_txt, visible)

    def get_zero_area_elements_diagnosis(
        self,
        min_value: float,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get zero area element diagnostics

        Args:
            min_value (float): Minimum area value. ZeroArea = Sqrt(3)/4 * aMin * aMin
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of zero area elements.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_zero_area_elements_diagnosis"
        )
        check_type(min_value, (float, int))
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetZeroAreaElementsDiagnosis2(
            min_value,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_mesh_summary(
        self,
        element_only: bool,
        inc_beams: bool = True,
        inc_match: bool = True,
        recalculate: bool = False,
    ) -> MeshSummary:
        """
        Get the mesh summary.

        Args:
            element_only (bool): bool: If True, get element counts summary only.
            inc_beams (bool): bool: If True, include beam elements in the summary.
            inc_match (bool): bool: If True, include match ratios in the summary.
            recalculate (bool): bool: If True, recalculate the summary.

        Returns:
            MeshSummary: The mesh summary object.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_mesh_summary")
        check_type(element_only, bool)
        check_type(inc_beams, bool)
        check_type(inc_match, bool)
        check_type(recalculate, bool)
        result = self.diagnosis_manager.GetMeshSummary2(
            element_only, inc_beams, inc_match, recalculate
        )
        if result is None:
            return None
        return MeshSummary(result)

    def show_degen_elements(self, min_value: float, assign_layer: bool, show_txt: bool) -> None:
        """
        Generates degenerate element diagnostics

        Args:
            min_value (float): Minimum area value. ZeroArea = Sqrt(3)/4 * aMin * aMin
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_degen_elements")
        check_type(min_value, (float, int))
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        self.diagnosis_manager.ShowDegenElements(min_value, assign_layer, show_txt)

    def show_surface_defects_for_3d(
        self, focus: int, assign_layer: bool, show_txt: bool, visible: bool = False
    ) -> None:
        """
        Generates surface defects diagnostics for 3D

        Args:
            focus (int): Focus on the surface defects.
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="show_surface_defects_for_3d"
        )
        check_type(focus, int)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowSurfaceDefectsFor3D(focus, assign_layer, show_txt, visible)

    def show_surface_with_bad_trim_curve(
        self,
        outer_loop: bool,
        inner_loop: bool,
        surf_def: bool,
        assign_layer: bool,
        show_txt: bool,
        visible: bool = False,
    ) -> None:
        """
        Generates surface with bad trim curvature diagnostics

        Args:
            outer_loop (bool): Test surface outer loops for errors
            inner_loop (bool): Test surface inner loops for errors
            surf_def (bool): Test underlying surface definition for errors
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="show_surface_with_bad_trim_curve"
        )
        check_type(outer_loop, bool)
        check_type(inner_loop, bool)
        check_type(surf_def, bool)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowSurfWithBadTrimCurv(
            outer_loop, inner_loop, surf_def, assign_layer, show_txt, visible
        )

    def get_surface_with_bad_trim_curve(
        self,
        outer_loop: bool,
        inner_loop: bool,
        surf_def: bool,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get surface with bad trim curvature diagnostics

        Args:
            outer_loop (bool): Test surface outer loops for errors
            inner_loop (bool): Test surface inner loops for errors
            surf_def (bool): Test underlying surface definition for errors
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of surface with bad trim curvature.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_surface_with_bad_trim_curve"
        )
        check_type(outer_loop, bool)
        check_type(inner_loop, bool)
        check_type(surf_def, bool)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetSurfWithBadTrimCurv(
            outer_loop,
            inner_loop,
            surf_def,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_surface_with_free_trim_curve(
        self,
        free: bool,
        non_manifold: bool,
        visible: bool,
        element_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get surface with free trim curvature diagnostics

        Args:
            free (bool): Test surface outer loops for errors
            non_manifold (bool): Test surface inner loops for errors
            visible (bool): Show/hide the selected mesh diagnosis.
            element_id (IntegerArray | None): The element ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of surface with bad trim curvature.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_surface_with_free_trim_curve"
        )
        check_type(free, bool)
        check_type(non_manifold, bool)
        check_type(visible, bool)
        if element_id is not None:
            check_type(element_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        return self.diagnosis_manager.GetSurfWithFreeTrimCurv(
            free,
            non_manifold,
            visible,
            coerce_optional_dispatch(element_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    # pylint: disable=R0913, R0917
    def show_surface_with_free_trim_curve(
        self,
        free: bool,
        non_manifold: bool,
        assign_layer: bool,
        show_txt: bool,
        visible: bool = False,
    ) -> None:
        """
        Generates surface with free trim curvature diagnostics

        Args:
            free (bool): Test surface outer loops for errors
            non_manifold (bool): Test surface inner loops for errors
            assign_layer (bool): Assign layer to the mesh.
            show_txt (bool): Show text on the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="show_surface_with_free_trim_curve"
        )
        check_type(free, bool)
        check_type(non_manifold, bool)
        check_type(assign_layer, bool)
        check_type(show_txt, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowSurfWithFreeTrimCurv(
            free, non_manifold, assign_layer, show_txt, visible
        )

    def show_ld_ratio(
        self, min_value: float, max_value: float, assign_layer: bool, visible: bool = False
    ) -> None:
        """
        Generates LD ratio diagnostics

        Args:
            min_value (float): Minimum LD ratio value.
            max_value (float): Maximum LD ratio value.
            assign_layer (bool): Assign layer to the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_ld_ratio")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowLDRatio(min_value, max_value, assign_layer, visible)

    def show_centroid_closeness(self, assign_layer: bool, visible: bool = False) -> None:
        """
        Generates centroid closeness diagnostics

        Args:
            assign_layer (bool): Push the elements within the diagnosis range into a
                diagnostics layer
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_centroid_closeness")
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowCentroidCloseness(assign_layer, visible)

    def show_beam_element_count(
        self, min_value: int, max_value: int, assign_layer: bool, visible: bool = False
    ) -> None:
        """
        Generates beam element count diagnostics

        Args:
            min_value (int): Minimum beam element count value.
            max_value (int): Maximum beam element count value.
            assign_layer (bool): Assign layer to the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_beam_element_count")
        check_type(min_value, (int, float))
        check_type(max_value, (int, float))
        check_min_max(min_value, max_value)
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowBeamElementCount(min_value, max_value, assign_layer, visible)

    def show_cooling_circuit_validity(self, assign_layer: bool, visible: bool = False) -> None:
        """
        Generates cooling circuit validity diagnostics

        Args:
            assign_layer (bool): Push the elements within the diagnosis range into a
                diagnostics layer
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="show_cooling_circuit_validity"
        )
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowCoolingCircuitValidity(assign_layer, visible)

    def show_bubbler_baffle_check(self, assign_layer: bool, visible: bool = False) -> None:
        """
        Generates bubbler baffle check diagnostics

        Args:
            assign_layer (bool): Push the elements within the diagnosis range into a
                diagnostics layer
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_bubbler_baffle_check")
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowBubblerBaffleCheck(assign_layer, visible)

    def show_trapped_beam(self, assign_layer: bool, visible: bool = False) -> None:
        """
        Generates trapped beam diagnostics

        Args:
            assign_layer (bool): Push the elements within the diagnosis range into a
                diagnostics layer
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_trapped_beam")
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowTrappedBeam(assign_layer, visible)

    def update_thickness_display(self, min_value: float, max_value: float) -> None:
        """
        Update the thickness display with the given minimum and maximum values.

        Args:
            min_value (float): The minimum thickness value.
            max_value (float): The maximum thickness value.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="update_thickness_display")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        self.diagnosis_manager.UpdateThicknessDisplay(min_value, max_value)

    def show_dimensions(
        self, min_value: float, max_value: float, assign_layer: bool, visible: bool = False
    ) -> None:
        """
        Generates dimensions diagnostics

        Args:
            min_value (float): Minimum dimension value.
            max_value (float): Maximum dimension value.
            assign_layer (bool): Assign layer to the mesh.
            visible (bool): Show/hide the selected mesh diagnosis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_dimensions")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        check_type(assign_layer, bool)
        check_type(visible, bool)
        self.diagnosis_manager.ShowDimensions(min_value, max_value, assign_layer, visible)

    def update_dimensional_display(self, min_value: float, max_value: float) -> None:
        """
        Update the dimensions display with the given minimum and maximum values.

        Args:
            min_value (float): The minimum dimension value.
            max_value (float): The maximum dimension value.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="update_dimensional_display")
        check_type(min_value, (float, int))
        check_type(max_value, (float, int))
        check_min_max(min_value, max_value)
        self.diagnosis_manager.UpdateDimensionalDisplay(min_value, max_value)

    def get_inverted_tetras(self, visible: bool, tetra_id: IntegerArray | None) -> int:
        """
        Get inverted tetrahedra diagnostics

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.

        Returns:
            int: The number of inverted tetras.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_inverted_tetras")
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetInvertedTetras(
            visible, coerce_optional_dispatch(tetra_id, "integer_array")
        )

    def get_collapsed_faces(self, visible: bool, tetra_id: IntegerArray | None) -> int:
        """
        Get collapsed faces diagnostics

        Args:
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.

        Returns:
            int: The number of collapsed faces.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_collapsed_faces")
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetCollapsedFaces(
            visible, coerce_optional_dispatch(tetra_id, "integer_array")
        )

    def get_insufficient_refinement_through_thickness(
        self, min_layer: int, visible: bool, tetra_id: IntegerArray | None
    ) -> int:
        """
        Get insufficient refinement through thickness diagnostics

        Args:
            min_layer (int): The minimum layer value.
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.

        Returns:
            int: The number of collapsed faces.
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="get_insufficient_refinement_through_thickness",
        )
        check_type(min_layer, int)
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetInsufficientRefinementThroughThickness(
            min_layer, visible, coerce_optional_dispatch(tetra_id, "integer_array")
        )

    def get_internal_long_edges(
        self,
        max_edge_length_ratio: float,
        visible: bool,
        tetra_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get internal long edges diagnostics

        Args:
            max_edge_length_ratio (float): The maximum edge length ratio.
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of internal long edges.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_internal_long_edges")
        check_type(max_edge_length_ratio, (float, int))
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetInternalLongEdges(
            max_edge_length_ratio,
            visible,
            coerce_optional_dispatch(tetra_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_tetras_with_extremely_large_volume(
        self,
        max_volume_ratio: float,
        visible: bool,
        tetra_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get tetras with extremely large volume diagnostics

        Args:
            max_volume_ratio (float): The maximum volume ratio.
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of internal long edges.
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="get_tetras_with_extremely_large_volume",
        )
        check_type(max_volume_ratio, (float, int))
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetTetrasWithExtremelyLargeVolume(
            max_volume_ratio,
            visible,
            coerce_optional_dispatch(tetra_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_tetras_with_high_aspect_ratio(
        self,
        max_aspect_ratio: float,
        visible: bool,
        tetra_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get tetras with high aspect ratio diagnostics

        Args:
            max_aspect_ratio (float): The maximum aspect ratio.
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of tetras with high aspect ratio.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_tetras_with_high_aspect_ratio"
        )
        check_type(max_aspect_ratio, (float, int))
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetTetrasWithHighAspectRatio(
            max_aspect_ratio,
            visible,
            coerce_optional_dispatch(tetra_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_tetras_with_extreme_min_angle_between_faces(
        self,
        min_angle: float,
        visible: bool,
        tetra_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get tetras with extreme minimum angle between faces diagnostics

        Args:
            min_angle (float): The minimum angle.
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of tetras with extreme minimum angle between faces.
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="get_tetras_with_extreme_min_angle_between_faces",
        )
        check_type(min_angle, (float, int))
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetTetrasWithExtremeMinAngleBetweenFaces(
            min_angle,
            visible,
            coerce_optional_dispatch(tetra_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )

    def get_tetras_with_extreme_max_angle_between_faces(
        self,
        max_angle: float,
        visible: bool,
        tetra_id: IntegerArray | None,
        value: DoubleArray | None,
    ) -> int:
        """
        Get tetras with extreme maximum angle between faces diagnostics

        Args:
            max_angle (float): The maximum angle.
            visible (bool): Show/hide the selected mesh diagnosis.
            tetra_id (IntegerArray | None): The tetrahedron ID array.
            value (DoubleArray | None): The value array.

        Returns:
            int: The number of tetras with extreme maximum angle between faces.
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="get_tetras_with_extreme_max_angle_between_faces",
        )
        check_type(max_angle, (float, int))
        if tetra_id is not None:
            check_type(tetra_id, IntegerArray)
        if value is not None:
            check_type(value, DoubleArray)
        check_type(visible, bool)
        return self.diagnosis_manager.GetTetrasWithExtremeMaxAngleBetweenFaces(
            max_angle,
            visible,
            coerce_optional_dispatch(tetra_id, "integer_array"),
            coerce_optional_dispatch(value, "double_array"),
        )
