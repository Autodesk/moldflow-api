# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Usage:
    MeshGenerator Class API Wrapper
"""

from .logger import process_log
from .common import (
    LogMessage,
    NurbsAlgorithm,
    CoolType,
    TriClassification,
    GeomType,
    Mesher3DType,
    CADContactMesh,
)
from .helper import check_type, check_range, get_enum_value, deprecated
from .com_proxy import safe_com


class MeshGenerator:
    """
    Wrapper for MeshGenerator class of Moldflow Synergy.
    """

    def __init__(self, _mesh_generator):
        """
        Initialize the MeshGenerator with a MeshGenerator instance from COM.

        Args:
            _mesh_generator: The MeshGenerator instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="MeshGenerator")
        self.mesh_generator = safe_com(_mesh_generator)

    def generate(self) -> bool:
        """
        Generate the mesh using the MeshGenerator instance.

        Returns:
            bool: True if mesh generation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="generate")
        return self.mesh_generator.Generate

    def save_options(self) -> bool:
        """
        Save the mesh generation options.

        Returns:
            bool: True if options were saved successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_options")
        return self.mesh_generator.SaveOptions

    @property
    def edge_length(self) -> float:
        """
        Edge Length of Mesh Generator

        :getter: Get length of the edge in the mesh generator.
        :setter: Set length of the edge in the mesh generator.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="edge_length")
        return self.mesh_generator.EdgeLength

    @edge_length.setter
    def edge_length(self, value: float) -> None:
        """
        Set the edge length of the mesh generator.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="edge_length", value=value)
        check_type(value, (int, float))
        self.mesh_generator.EdgeLength = value

    @property
    def merge_tolerance(self) -> float:
        """
        Merge Tolerance of Mesh Generator
        Nodes within this tolerance will be merged after meshing.

        :getter: Get the merge tolerance
        :setter: Set the merge tolerance
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="merge_tolerance")
        return self.mesh_generator.MergeTolerance

    @merge_tolerance.setter
    def merge_tolerance(self, value: float) -> None:
        """
        Set the merge tolerance of the mesh generator.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="merge_tolerance", value=value
        )
        check_type(value, (int, float))
        self.mesh_generator.MergeTolerance = value

    @property
    def match(self) -> bool:
        """
        Enables/disables matched meshing for fusion models.

        :getter: Get the matched meshing option
        :setter: Set the matched meshing option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="match")
        return self.mesh_generator.Match

    @match.setter
    def match(self, value: bool) -> None:
        """
        Set the matched meshing option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="match", value=value)
        check_type(value, bool)
        self.mesh_generator.Match = value

    @property
    def smoothing(self) -> bool:
        """
        Specifies whether node positions will be smoothed.

        :getter: Get the smoothing option
        :setter: Set the smoothing option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="smoothing")
        return self.mesh_generator.Smoothing

    @smoothing.setter
    def smoothing(self, value: bool) -> None:
        """
        Set the smoothing option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="smoothing", value=value)
        check_type(value, bool)
        self.mesh_generator.Smoothing = value

    @property
    @deprecated()
    def element_reduction(self) -> bool:
        """
        .. deprecated:: 27.0.0

        Enables/disables automatic element size determination
        for fusion meshes from faceted geometry.

        :getter: Get the element reduction option
        :setter: Set the element reduction option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="element_reduction")
        return self.mesh_generator.ElementReduction

    @element_reduction.setter
    def element_reduction(self, value: bool) -> None:
        """
        Set the element reduction option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="element_reduction", value=value
        )
        check_type(value, bool)
        self.mesh_generator.ElementReduction = value

    @property
    def surface_optimization(self) -> bool:
        """
        Specifies whether using surface optimization.

        :getter: Get the surface optimization option
        :setter: Set the surface optimization option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="surface_optimization")
        return self.mesh_generator.SurfaceOptimization

    @surface_optimization.setter
    def surface_optimization(self, value: bool) -> None:
        """
        Set the surface optimization option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="surface_optimization", value=value
        )
        check_type(value, bool)
        self.mesh_generator.SurfaceOptimization = value

    @property
    @deprecated()
    def automatic_tetra_optimization(self) -> bool:
        """
        .. deprecated:: 27.0.0

        Specifies whether optimizing tetras automatically.

        :getter: Get the automatic tetra optimization option
        :setter: Set the automatic tetra optimization option
        :type: bool
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="automatic_tetra_optimization"
        )
        return self.mesh_generator.AutomaticTetraOptimization

    @automatic_tetra_optimization.setter
    def automatic_tetra_optimization(self, value: bool) -> None:
        """
        Set the automatic tetra optimization option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="automatic_tetra_optimization",
            value=value,
        )
        check_type(value, bool)
        self.mesh_generator.AutomaticTetraOptimization = value

    @property
    def tetra_refine(self) -> bool:
        """
        Enables/disables tetrahedral refinement for 3D meshes.

        :getter: Get the tetra refine option
        :setter: Set the tetra refine option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tetra_refine")
        return self.mesh_generator.TetraRefine

    @tetra_refine.setter
    def tetra_refine(self, value: bool) -> None:
        """
        Set the tetra refine option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="tetra_refine", value=value)
        check_type(value, bool)
        self.mesh_generator.TetraRefine = value

    @property
    def tetra_layers(self) -> int:
        """
        Number of tetra layers through thickness for plastic parts [4 : 40].

        :getter: Get the tetra layers option
        :setter: Set the tetra layers option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tetra_layers")
        return self.mesh_generator.TetraLayers

    @tetra_layers.setter
    def tetra_layers(self, value: int) -> None:
        """
        Set the tetra layers option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="tetra_layers", value=value)
        check_type(value, int)
        check_range(value, 4, 40, True, True)
        self.mesh_generator.TetraLayers = value

    @property
    def tetra_layers_for_cores(self) -> int:
        """
        Number of tetra layers through thickness for cores/inserts [4 : 20].

        :getter: Get the tetra layers for cores option
        :setter: Set the tetra layers for cores option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tetra_layers_for_cores")
        return self.mesh_generator.TetraLayersForCores

    @tetra_layers_for_cores.setter
    def tetra_layers_for_cores(self, value: int) -> None:
        """
        Set the tetra layers for cores option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="tetra_layers_for_cores", value=value
        )
        check_type(value, int)
        check_range(value, 4, 20, True, True)
        self.mesh_generator.TetraLayersForCores = value

    @property
    @deprecated()
    def tetra_max_ar(self) -> float:
        """
        .. deprecated:: 27.0.0

        Limit on aspect ratio for tetrahedral meshes.

        :getter: Get the tetra max aspect ratio option
        :setter: Set the tetra max aspect ratio option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tetra_max_ar")
        return self.mesh_generator.TetraMaxAR

    @tetra_max_ar.setter
    def tetra_max_ar(self, value: float) -> None:
        """
        Set the tetra max aspect ratio option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="tetra_max_ar", value=value)
        check_type(value, (int, float))
        self.mesh_generator.TetraMaxAR = value

    @property
    def maximum_match_distance_option(self) -> int:
        """
        Specifies the option to determine the limit on max match dist.

        :getter: Get the maximum match distance option
        :setter: Set the maximum match distance option
        :type: int
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="maximum_match_distance_option"
        )
        return self.mesh_generator.MaximumMatchDistanceOption

    @maximum_match_distance_option.setter
    def maximum_match_distance_option(self, value: int) -> None:
        """
        Set the maximum match distance option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="maximum_match_distance_option",
            value=value,
        )
        check_type(value, int)
        self.mesh_generator.MaximumMatchDistanceOption = value

    @property
    def maximum_match_distance(self) -> float:
        """
        Limit on match distance for wedges.

        :getter: Get the maximum match distance option
        :setter: Set the maximum match distance option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="maximum_match_distance")
        return self.mesh_generator.MaximumMatchDistance

    @maximum_match_distance.setter
    def maximum_match_distance(self, value: float) -> None:
        """
        Set the maximum match distance option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="maximum_match_distance", value=value
        )
        check_type(value, (int, float))
        self.mesh_generator.MaximumMatchDistance = value

    @property
    @deprecated()
    def use_tetras_on_edge(self) -> bool:
        """
        .. deprecated:: 27.0.0

        Specifies whether tetras are to be created on model edges.

        :getter: Get the use tetras on edge option
        :setter: Set the use tetras on edge option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_tetras_on_edge")
        return self.mesh_generator.UseTetrasOnEdge

    @use_tetras_on_edge.setter
    def use_tetras_on_edge(self, value: bool) -> None:
        """
        Set the use tetras on edge option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="use_tetras_on_edge", value=value
        )
        check_type(value, bool)
        self.mesh_generator.UseTetrasOnEdge = value

    @property
    def remesh_all(self) -> bool:
        """
        Specifies whether previously meshed portions of the model will be re-meshed.

        :getter: Get the remesh all option
        :setter: Set the remesh all option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="remesh_all")
        return self.mesh_generator.RemeshAll

    @remesh_all.setter
    def remesh_all(self, value: bool) -> None:
        """
        Set the remesh all option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="remesh_all", value=value)
        check_type(value, bool)
        self.mesh_generator.RemeshAll = value

    @property
    def use_active_layer(self) -> bool:
        """
        Specifies whether the newly generated mesh will be pushed into the active layer.

        :getter: Get the use active layer option
        :setter: Set the use active layer option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_active_layer")
        return self.mesh_generator.UseActiveLayer

    @use_active_layer.setter
    def use_active_layer(self, value: bool) -> None:
        """
        Set the use active layer option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="use_active_layer", value=value
        )
        check_type(value, bool)
        self.mesh_generator.UseActiveLayer = value

    @property
    def post_mesh_actions(self) -> bool:
        """
        Specifies whether post-meshing actions such as smoothing are enabled.

        :getter: Get the post mesh actions option
        :setter: Set the post mesh actions option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="post_mesh_actions")
        return self.mesh_generator.PostMeshActions

    @post_mesh_actions.setter
    def post_mesh_actions(self, value: bool) -> None:
        """
        Set the post mesh actions option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="post_mesh_actions", value=value
        )
        check_type(value, bool)
        self.mesh_generator.PostMeshActions = value

    @property
    def chord_height(self) -> float:
        """
        Chord height value.

        :getter: Get the chord height value
        :setter: Set the chord height value
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="chord_height")
        return self.mesh_generator.ChordHeight

    @chord_height.setter
    def chord_height(self, value: float) -> None:
        """
        Set the chord height option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="chord_height", value=value)
        check_type(value, (int, float))
        self.mesh_generator.ChordHeight = value

    @property
    def chord_height_control(self) -> bool:
        """
        Specifies whether using chord height.

        :getter: Get the chord height control option
        :setter: Set the chord height control option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="chord_height_control")
        return self.mesh_generator.ChordHeightControl

    @chord_height_control.setter
    def chord_height_control(self, value: bool) -> None:
        """
        Set the chord height control option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="chord_height_control", value=value
        )
        check_type(value, bool)
        self.mesh_generator.ChordHeightControl = value

    @property
    def nurbs_mesher(self) -> int:
        """
        Specifies nurbs mesher algorithm using default(0) or Advancing Front(1).

        :getter: Get the nurbs mesher option
        :setter: Set the nurbs mesher option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="nurbs_mesher")
        return self.mesh_generator.NurbsMesher

    @nurbs_mesher.setter
    def nurbs_mesher(self, value: NurbsAlgorithm | int) -> None:
        """
        Set the nurbs mesher option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="nurbs_mesher", value=value)
        value = get_enum_value(value, NurbsAlgorithm)
        self.mesh_generator.NurbsMesher = value

    @property
    def source_geom_type(self) -> str:
        """
        Specifies Source Geometry Type.

        :getter: Get the source geometry type option
        :setter: Set the source geometry type option
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="source_geom_type")
        return self.mesh_generator.SourceGeomType

    @source_geom_type.setter
    def source_geom_type(self, value: GeomType | str) -> None:
        """
        Set the source geometry type option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="source_geom_type", value=value
        )
        value = get_enum_value(value, GeomType)
        self.mesh_generator.SourceGeomType = value

    @property
    def chord_ht_proximity(self) -> bool:
        """
        Specifies whether optimize aspect ratio by proximity control.

        :getter: Get the chord height proximity option
        :setter: Set the chord height proximity option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="chord_ht_proximity")
        return self.mesh_generator.ChordHtProximity

    @chord_ht_proximity.setter
    def chord_ht_proximity(self, value: bool) -> None:
        """
        Set the chord height proximity option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="chord_ht_proximity", value=value
        )
        check_type(value, bool)
        self.mesh_generator.ChordHtProximity = value

    @property
    def chord_ht_aspect_ratio(self) -> bool:
        """
        Specifies whether optimize aspect ratio by surface curvature control.

        :getter: Get the chord height aspect ratio option
        :setter: Set the chord height aspect ratio option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="chord_ht_aspect_ratio")
        return self.mesh_generator.ChordHtAspectRatio

    @chord_ht_aspect_ratio.setter
    def chord_ht_aspect_ratio(self, value: bool) -> None:
        """
        Set the chord height aspect ratio option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="chord_ht_aspect_ratio", value=value
        )
        check_type(value, bool)
        self.mesh_generator.ChordHtAspectRatio = value

    @property
    def merge_cavity_runner(self) -> bool:
        """
        Specifies whether merging cavity runner.

        :getter: Get the merge cavity runner option
        :setter: Set the merge cavity runner option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="merge_cavity_runner")
        return self.mesh_generator.MergeCavityRunner

    @merge_cavity_runner.setter
    def merge_cavity_runner(self, value: bool) -> None:
        """
        Set the merge cavity runner option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="merge_cavity_runner", value=value
        )
        check_type(value, bool)
        self.mesh_generator.MergeCavityRunner = value

    @property
    def chord_angle_select(self) -> bool:
        """
        Specifies whether using chord angle.

        :getter: Get the chord angle select option
        :setter: Set the chord angle select option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="chord_angle_select")
        return self.mesh_generator.ChordAngleSelect

    @chord_angle_select.setter
    def chord_angle_select(self, value: bool) -> None:
        """
        Set the chord angle select option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="chord_angle_select", value=value
        )
        check_type(value, bool)
        self.mesh_generator.ChordAngleSelect = value

    @property
    def chord_angle(self) -> float:
        """
        Chord angle value.

        :getter: Get the chord angle value
        :setter: Set the chord angle value
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="chord_angle")
        return self.mesh_generator.ChordAngle

    @chord_angle.setter
    def chord_angle(self, value: float) -> None:
        """
        Set the chord angle option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="chord_angle", value=value)
        check_type(value, (int, float))
        self.mesh_generator.ChordAngle = value

    @property
    def use_auto_size(self) -> bool:
        """
        Specifies whether to use auto sizing for CAD.

        :getter: Get the use auto size option
        :setter: Set the use auto size option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_auto_size")
        return self.mesh_generator.UseAutoSize

    @use_auto_size.setter
    def use_auto_size(self, value: bool) -> None:
        """
        Set the use auto size option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="use_auto_size", value=value)
        check_type(value, bool)
        self.mesh_generator.UseAutoSize = value

    @property
    def cad_auto_size_scale(self) -> float:
        """
        Scale factor for edge length determined by auto sizing.

        :getter: Get the CAD auto size scale option
        :setter: Set the CAD auto size scale option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cad_auto_size_scale")
        return self.mesh_generator.CadAutoSizeScale

    @cad_auto_size_scale.setter
    def cad_auto_size_scale(self, value: float) -> None:
        """
        Set the CAD auto size scale option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="cad_auto_size_scale", value=value
        )
        check_type(value, (int, float))
        self.mesh_generator.CadAutoSizeScale = value

    @property
    def cad_sliver_remove(self) -> bool:
        """
        Specifies whether removing CAD sliver.

        :getter: Get the CAD sliver remove option
        :setter: Set the CAD sliver remove option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cad_sliver_remove")
        return self.mesh_generator.CadSliverRemove

    @cad_sliver_remove.setter
    def cad_sliver_remove(self, value: bool) -> None:
        """
        Set the CAD sliver remove option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="cad_sliver_remove", value=value
        )
        check_type(value, bool)
        self.mesh_generator.CadSliverRemove = value

    @property
    def cad_mesh_grading_factor(self) -> float:
        """
        Specifies CAD mesh grading factor from slow(0) to fast(1) mesh transition.
        Applicable when mesh with chord angle and/or local density defined on face/edge

        :getter: Get the CAD mesh grading factor option
        :setter: Set the CAD mesh grading factor option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cad_mesh_grading_factor")
        return self.mesh_generator.CadMeshGradingFactor

    @cad_mesh_grading_factor.setter
    def cad_mesh_grading_factor(self, value: float) -> None:
        """
        Set the CAD mesh grading factor option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="cad_mesh_grading_factor", value=value
        )
        check_type(value, (int, float))
        check_range(value, 0, 1, True, True)
        self.mesh_generator.CadMeshGradingFactor = float(value)

    @property
    def cad_mesh_minimum_curvature_percentage(self) -> float:
        """
        Specifies minimum mesh size in percentage with respect to
        global mesh size due to curvature refinement.

        :getter: Get the CAD mesh minimum curvature percentage option
        :setter: Set the CAD mesh minimum curvature percentage option
        :type: float
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_GET,
            locals(),
            name="cad_mesh_minimum_curvature_percentage",
        )
        return self.mesh_generator.CadMeshMinimumCurvaturePercentage

    @cad_mesh_minimum_curvature_percentage.setter
    def cad_mesh_minimum_curvature_percentage(self, value: float) -> None:
        """
        Set the CAD mesh minimum curvature percentage option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="cad_mesh_minimum_curvature_percentage",
            value=value,
        )
        check_type(value, (int, float))
        self.mesh_generator.CadMeshMinimumCurvaturePercentage = value

    @property
    @deprecated()
    def use_fallbacks(self) -> bool:
        """
        .. deprecated:: 27.0.0

        Specifies whether fallback is to be used when CAD meshing fails.

        :getter: Get the use fallbacks option
        :setter: Set the use fallbacks option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_fallbacks")
        return self.mesh_generator.UseFallbacks

    @use_fallbacks.setter
    def use_fallbacks(self, value: bool) -> None:
        """
        Set the use fallbacks option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="use_fallbacks", value=value)
        check_type(value, bool)
        self.mesh_generator.UseFallbacks = value

    @property
    def max_edge_length_in_thickness_direction(self) -> float:
        """
        Specifies maximum edge length in thickness direction.

        :getter: Get the max edge length in thickness direction option
        :setter: Set the max edge length in thickness direction option
        :type: float
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_GET,
            locals(),
            name="max_edge_length_in_thickness_direction",
        )
        return self.mesh_generator.MaxEdgeLengthInThicknessDirection

    @max_edge_length_in_thickness_direction.setter
    def max_edge_length_in_thickness_direction(self, value: float) -> None:
        """
        Set the max edge length in thickness direction option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="max_edge_length_in_thickness_direction",
            value=value,
        )
        check_type(value, (int, float))
        self.mesh_generator.MaxEdgeLengthInThicknessDirection = value

    @property
    def eltt_ratio(self) -> float:
        """
        Specifies edge length through thickness vs. global surface edge length. [0.4 :1.5]

        :getter: Get the ELTT ratio option
        :setter: Set the ELTT ratio option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="eltt_ratio")
        return self.mesh_generator.ELTTRatio

    @eltt_ratio.setter
    def eltt_ratio(self, value: float) -> None:
        """
        Set the ELTT ratio option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="eltt_ratio", value=value)
        check_type(value, (int, float))
        check_range(value, 0.4, 1.5, True, True)
        self.mesh_generator.ELTTRatio = value

    @property
    def eltt_ratio_al(self) -> float:
        """
        ELTTRatioAL

        :getter: Get the ELTTRatioAL option
        :setter: Set the ELTTRatioAL option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="eltt_ratio_al")
        return self.mesh_generator.ELTTRatioAL

    @eltt_ratio_al.setter
    def eltt_ratio_al(self, value: float) -> None:
        """
        Set the ELTT ratio AL option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="eltt_ratio_al", value=value)
        check_type(value, (int, float))
        self.mesh_generator.ELTTRatioAL = value

    @property
    def mesher_3d(self) -> str:
        """
        Specifies 3D mesher type.

        :getter: Get the mesher 3D option
        :setter: Set the mesher 3D option
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesher_3d")
        return self.mesh_generator.Mesher3D

    @mesher_3d.setter
    def mesher_3d(self, value: Mesher3DType | str) -> None:
        """
        Set the mesher 3D option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mesher_3d", value=value)
        value = get_enum_value(value, Mesher3DType)
        self.mesh_generator.Mesher3D = value

    @property
    def cool_type(self) -> int:
        """
        Specifies cool type (1:BEM, 2: FEM)

        :getter: Get the cool type option
        :setter: Set the cool type option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cool_type")
        return self.mesh_generator.CoolType

    @cool_type.setter
    def cool_type(self, value: CoolType | int) -> None:
        """
        Set the cool type option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="cool_type", value=value)
        value = get_enum_value(value, CoolType)
        self.mesh_generator.CoolType = value

    @property
    def cad_contact_mesh_type(self) -> str:
        """
        Specifies CAD contact mesh type.

        :getter: Get the CAD contact mesh type option
        :setter: Set the CAD contact mesh type option
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cad_contact_mesh_type")
        return self.mesh_generator.CadContactMeshType

    @cad_contact_mesh_type.setter
    def cad_contact_mesh_type(self, value: CADContactMesh | str) -> None:
        """
        Set the CAD contact mesh type option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="cad_contact_mesh_type", value=value
        )
        value = get_enum_value(value, CADContactMesh)
        self.mesh_generator.CadContactMeshType = value

    @property
    def mesh_component_type(self) -> int:
        """
        Specifies mesh component type.

        :getter: Get the mesh component type option
        :setter: Set the mesh component type option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_component_type")
        return self.mesh_generator.MeshComponentType

    @mesh_component_type.setter
    def mesh_component_type(self, value: int) -> None:
        """
        Set the mesh component type option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mesh_component_type", value=value
        )
        check_type(value, int)
        self.mesh_generator.MeshComponentType = value

    @property
    def inc_thk_dd(self) -> bool:
        """
        Specifies whether to include thickness calculation.

        :getter: Get the inc thickness calculation option
        :setter: Set the inc thickness calculation option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="inc_thk_dd")
        return self.mesh_generator.IncThkDD

    @inc_thk_dd.setter
    def inc_thk_dd(self, value: bool) -> None:
        """
        Set the inc thickness calculation option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="inc_thk_dd", value=value)
        check_type(value, bool)
        self.mesh_generator.IncThkDD = value

    @property
    def use_gate_ref(self) -> bool:
        """
        Specifies whether to use gate refinement.

        :getter: Get the use gate refinement option
        :setter: Set the use gate refinement option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_gate_ref")
        return self.mesh_generator.UseGateRef

    @use_gate_ref.setter
    def use_gate_ref(self, value: bool) -> None:
        """
        Set the use gate refinement option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="use_gate_ref", value=value)
        check_type(value, bool)
        self.mesh_generator.UseGateRef = value

    @property
    def gate_el_factor(self) -> float:
        """
        Edge length factor for gate refinement [10: 50].

        :getter: Get the gate edge length factor option
        :setter: Set the gate edge length factor option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gate_el_factor")
        return self.mesh_generator.GateELFactor

    @gate_el_factor.setter
    def gate_el_factor(self, value: float) -> None:
        """
        Set the gate edge length factor option.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="gate_el_factor", value=value)
        check_type(value, (int, float))
        check_range(value, 10, 50, True, True)
        self.mesh_generator.GateELFactor = value

    @property
    def mesh_curves_by_gel(self) -> bool:
        """
        Specifies whether to mesh curves by global edge length.
        Default is False and curve edge length will be related to diameters.

        :getter: Get the mesh curves by global edge length option
        :setter: Set the mesh curves by global edge length option
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_curves_by_gel")
        return self.mesh_generator.MeshCurvesByGEL

    @mesh_curves_by_gel.setter
    def mesh_curves_by_gel(self, value: bool) -> None:
        """
        Set the mesh curves by global edge length option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mesh_curves_by_gel", value=value
        )
        check_type(value, bool)
        self.mesh_generator.MeshCurvesByGEL = value

    @property
    def surface_edge_length_scale_factor(self) -> float:
        """
        Edge length scale factor, [0.4:5]. Real edge length = DefaultEdgeLength * scale.

        :getter: Get the surface edge length scale factor option
        :setter: Set the surface edge length scale factor option
        :type: float
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="surface_edge_length_scale_factor"
        )
        return self.mesh_generator.SurfaceEdgeLengthScaleFactor

    @surface_edge_length_scale_factor.setter
    def surface_edge_length_scale_factor(self, value: float) -> None:
        """
        Set the surface edge length scale factor option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="surface_edge_length_scale_factor",
            value=value,
        )
        check_type(value, (int, float))
        check_range(value, 0.4, 5, True, True)
        self.mesh_generator.SurfaceEdgeLengthScaleFactor = value

    @property
    def edge_length_ratio_runner(self) -> float:
        """
        Specifies edge length vs diameter for feed system [0.1 : 4].
        Disabled when mesh curves by global edge length is enabled.

        :getter: Get the edge length ratio runner option
        :setter: Set the edge length ratio runner option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="edge_length_ratio_runner")
        return self.mesh_generator.EdgeLengthRatioRunner

    @edge_length_ratio_runner.setter
    def edge_length_ratio_runner(self, value: float) -> None:
        """
        Set the edge length ratio runner option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="edge_length_ratio_runner",
            value=value,
        )
        check_type(value, (int, float))
        check_range(value, 0.1, 4, True, True)
        if self.mesh_curves_by_gel:  # If global edge length is used, this option is not applicable.
            process_log(
                __name__, LogMessage.NOT_APPLICABLE, locals(), name="edge_length_ratio_runner"
            )
        self.mesh_generator.EdgeLengthRatioRunner = value

    @property
    def edge_length_ratio_circuits(self) -> float:
        """
        Specifies edge length vs diameter for circuits [0.5 : 8].

        :getter: Get the edge length ratio circuits option
        :setter: Set the edge length ratio circuits option
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="edge_length_ratio_circuits")
        return self.mesh_generator.EdgeLengthRatioCircuits

    @edge_length_ratio_circuits.setter
    def edge_length_ratio_circuits(self, value: float) -> None:
        """
        Set the edge length ratio circuits option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="edge_length_ratio_circuits",
            value=value,
        )
        check_type(value, (int, float))
        check_range(value, 0.5, 8, True, True)
        if self.mesh_curves_by_gel:  # If global edge length is used, this option is not applicable.
            process_log(
                __name__, LogMessage.NOT_APPLICABLE, locals(), name="edge_length_ratio_circuits"
            )
        self.mesh_generator.EdgeLengthRatioCircuits = value

    @property
    def max_chord_height_ratio_curve(self) -> float:
        """
        Specifies chord height vs chord length for curves [0.02 : 3].

        :getter: Get the max chord height ratio curve option
        :setter: Set the max chord height ratio curve option
        :type: float
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="max_chord_height_ratio_curve"
        )
        return self.mesh_generator.MaxChordHeightRatioCurv

    @max_chord_height_ratio_curve.setter
    def max_chord_height_ratio_curve(self, value: float) -> None:
        """
        Set the max chord height ratio curve option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="max_chord_height_ratio_curve",
            value=value,
        )
        check_type(value, (int, float))
        check_range(value, 0.02, 3, True, True)
        self.mesh_generator.MaxChordHeightRatioCurv = value

    @property
    def min_num_elm_gates(self) -> int:
        """
        Specifies min beams on gates [1 : 8].

        :getter: Get the min number of elements gates option
        :setter: Set the min number of elements gates option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="min_num_elm_gates")
        return self.mesh_generator.MinNumElmGates

    @min_num_elm_gates.setter
    def min_num_elm_gates(self, value: int) -> None:
        """
        Set the min number of elements gates option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="min_num_elm_gates", value=value
        )
        check_type(value, int)
        check_range(value, 1, 8, True, True)
        self.mesh_generator.MinNumElmGates = value

    @property
    def min_num_elm_baffle_bubblers(self) -> int:
        """
        Specifies minimum number of beams on each curve for baffles and bubblers [3 : 50].

        :getter: Get the min number of elements baffle bubblers option
        :setter: Set the min number of elements baffle bubblers option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="min_num_elm_baffle_bubblers")
        return self.mesh_generator.MinNumElmBaffleBubblers

    @min_num_elm_baffle_bubblers.setter
    def min_num_elm_baffle_bubblers(self, value: int) -> None:
        """
        Set the min number of elements baffle bubblers option.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="min_num_elm_baffle_bubblers",
            value=value,
        )
        check_type(value, int)
        check_range(value, 3, 50, True, True)
        self.mesh_generator.MinNumElmBaffleBubblers = value

    @property
    def tri_classification_opt(self) -> int:
        """
        Specifies triangle classification option for CAD models
        Options:
        0:ignore soft edges and merge slivers
        1:preserve CAD edges except for slivers
        2: preserve all CAD edges

        :getter: Get the triangle classification option
        :setter: Set the triangle classification option
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tri_classification_opt")
        return self.mesh_generator.TriClassificationOpt

    @tri_classification_opt.setter
    def tri_classification_opt(self, value: TriClassification | int) -> None:
        """
        Set the triangle classification option.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="tri_classification_opt", value=value
        )
        value = get_enum_value(value, TriClassification)
        self.mesh_generator.TriClassificationOpt = value
