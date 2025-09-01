# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for MeshGenerator Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import MeshGenerator
from moldflow.common import (
    GeomType,
    NurbsAlgorithm,
    CoolType,
    TriClassification,
    GradingFactor,
    Mesher3DType,
    CADContactMesh,
)


@pytest.mark.unit
class TestUnitMeshGenerator:
    """
    Test suite for the MeshGenerator class.
    """

    @pytest.fixture
    def mock_mesh_generator(self, mock_object) -> MeshGenerator:
        """
        Fixture to create a mock instance of MeshGenerator.
        Args:
            mock_object: Mock object for the MeshGenerator dependency.
        Returns:
            MeshGenerator: An instance of MeshGenerator with the mock object.
        """
        return MeshGenerator(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, expected",
        [
            ("Generate", "generate", bool, True),
            ("Generate", "generate", bool, False),
            ("SaveOptions", "save_options", bool, True),
            ("SaveOptions", "save_options", bool, False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_no_args(
        self,
        mock_mesh_generator: MeshGenerator,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        expected,
    ):
        """
        Test the create_layer method of MeshGenerator.
        """
        setattr(mock_object, pascal_name, expected)
        result = getattr(mock_mesh_generator, property_name)()
        assert isinstance(result, return_type)
        assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, expected, expected_type",
        [
            ("edge_length", "EdgeLength", 0.1, float),
            ("edge_length", "EdgeLength", 0.15, float),
            ("edge_length", "EdgeLength", 1, int),
            ("merge_tolerance", "MergeTolerance", 0.15, float),
            ("merge_tolerance", "MergeTolerance", 1.15, float),
            ("merge_tolerance", "MergeTolerance", 5, int),
            ("match", "Match", True, bool),
            ("match", "Match", False, bool),
            ("smoothing", "Smoothing", True, bool),
            ("smoothing", "Smoothing", False, bool),
            ("element_reduction", "ElementReduction", True, bool),
            ("element_reduction", "ElementReduction", False, bool),
            ("surface_optimization", "SurfaceOptimization", True, bool),
            ("surface_optimization", "SurfaceOptimization", False, bool),
            ("automatic_tetra_optimization", "AutomaticTetraOptimization", True, bool),
            ("automatic_tetra_optimization", "AutomaticTetraOptimization", False, bool),
            ("tetra_refine", "TetraRefine", True, bool),
            ("tetra_refine", "TetraRefine", False, bool),
            ("tetra_layers", "TetraLayers", 4, int),
            ("tetra_layers", "TetraLayers", 20, int),
            ("tetra_layers", "TetraLayers", 40, int),
            ("tetra_layers_for_cores", "TetraLayersForCores", 4, int),
            ("tetra_layers_for_cores", "TetraLayersForCores", 20, int),
            ("tetra_layers_for_cores", "TetraLayersForCores", 10, int),
            ("tetra_max_ar", "TetraMaxAR", 1.5, float),
            ("tetra_max_ar", "TetraMaxAR", 2.0, float),
            ("tetra_max_ar", "TetraMaxAR", 5, int),
            ("maximum_match_distance", "MaximumMatchDistance", 1, int),
            ("maximum_match_distance", "MaximumMatchDistance", 5.5, (int, float)),
            ("maximum_match_distance", "MaximumMatchDistance", 9, int),
            ("maximum_match_distance_option", "MaximumMatchDistanceOption", 1, int),
            ("maximum_match_distance_option", "MaximumMatchDistanceOption", 2, int),
            ("maximum_match_distance_option", "MaximumMatchDistanceOption", 3, int),
            ("use_tetras_on_edge", "UseTetrasOnEdge", True, bool),
            ("use_tetras_on_edge", "UseTetrasOnEdge", False, bool),
            ("remesh_all", "RemeshAll", True, bool),
            ("remesh_all", "RemeshAll", False, bool),
            ("use_active_layer", "UseActiveLayer", True, bool),
            ("use_active_layer", "UseActiveLayer", False, bool),
            ("post_mesh_actions", "PostMeshActions", True, bool),
            ("post_mesh_actions", "PostMeshActions", False, bool),
            ("chord_height", "ChordHeight", 0.1, (int, float)),
            ("chord_height", "ChordHeight", 0.58, (int, float)),
            ("chord_height", "ChordHeight", 2, (int, float)),
            ("chord_height_control", "ChordHeightControl", True, bool),
            ("chord_height_control", "ChordHeightControl", False, bool),
            ("nurbs_mesher", "NurbsMesher", 1, int),
            ("nurbs_mesher", "NurbsMesher", 0, int),
            ("source_geom_type", "SourceGeomType", "Auto-Detect", str),
            ("chord_ht_proximity", "ChordHtProximity", True, bool),
            ("chord_ht_proximity", "ChordHtProximity", False, bool),
            ("chord_ht_aspect_ratio", "ChordHtAspectRatio", True, bool),
            ("chord_ht_aspect_ratio", "ChordHtAspectRatio", False, bool),
            ("merge_cavity_runner", "MergeCavityRunner", True, bool),
            ("merge_cavity_runner", "MergeCavityRunner", False, bool),
            ("chord_angle_select", "ChordAngleSelect", True, bool),
            ("chord_angle_select", "ChordAngleSelect", False, bool),
            ("chord_angle", "ChordAngle", 0.1, (int, float)),
            ("chord_angle", "ChordAngle", 0.62, (int, float)),
            ("chord_angle", "ChordAngle", 1, (int, float)),
            ("chord_angle", "ChordAngle", 2, (int, float)),
            ("use_auto_size", "UseAutoSize", True, bool),
            ("use_auto_size", "UseAutoSize", False, bool),
            ("cad_auto_size_scale", "CadAutoSizeScale", 0.1, (int, float)),
            ("cad_auto_size_scale", "CadAutoSizeScale", 0.268, (int, float)),
            ("cad_auto_size_scale", "CadAutoSizeScale", 1, (int, float)),
            ("cad_auto_size_scale", "CadAutoSizeScale", 50, (int, float)),
            ("cad_sliver_remove", "CadSliverRemove", True, bool),
            ("cad_sliver_remove", "CadSliverRemove", False, bool),
            ("cad_mesh_grading_factor", "CadMeshGradingFactor", 0, int),
            ("cad_mesh_grading_factor", "CadMeshGradingFactor", 1, int),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                0.2,
                (int, float),
            ),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                5.92,
                (int, float),
            ),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                5,
                (int, float),
            ),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                7,
                (int, float),
            ),
            ("use_fallbacks", "UseFallbacks", True, bool),
            ("use_fallbacks", "UseFallbacks", False, bool),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                0.1,
                (int, float),
            ),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                7.123,
                (int, float),
            ),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                3,
                (int, float),
            ),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                7,
                (int, float),
            ),
            ("eltt_ratio", "ELTTRatio", 0.4, (int, float)),
            ("eltt_ratio", "ELTTRatio", 1.5, (int, float)),
            ("eltt_ratio", "ELTTRatio", 1, (int, float)),
            ("eltt_ratio", "ELTTRatio", 0.8, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 0.4, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 1.5, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 1, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 0.8, (int, float)),
            ("mesher_3d", "Mesher3D", "Legacy", str),
            ("cool_type", "CoolType", 1, int),
            ("cad_contact_mesh_type", "CadContactMeshType", "Precise match", str),
            ("mesh_component_type", "MeshComponentType", 1, int),
            ("inc_thk_dd", "IncThkDD", True, bool),
            ("inc_thk_dd", "IncThkDD", False, bool),
            ("use_gate_ref", "UseGateRef", True, bool),
            ("gate_el_factor", "GateELFactor", 10, (int, float)),
            ("gate_el_factor", "GateELFactor", 50, (int, float)),
            ("gate_el_factor", "GateELFactor", 32.5, (int, float)),
            ("mesh_curves_by_gel", "MeshCurvesByGEL", True, bool),
            ("mesh_curves_by_gel", "MeshCurvesByGEL", False, bool),
            ("surface_edge_length_scale_factor", "SurfaceEdgeLengthScaleFactor", 0.4, (int, float)),
            ("surface_edge_length_scale_factor", "SurfaceEdgeLengthScaleFactor", 5, (int, float)),
            ("surface_edge_length_scale_factor", "SurfaceEdgeLengthScaleFactor", 4.5, (int, float)),
            ("edge_length_ratio_runner", "EdgeLengthRatioRunner", 0.1, (int, float)),
            ("edge_length_ratio_runner", "EdgeLengthRatioRunner", 4, (int, float)),
            ("edge_length_ratio_runner", "EdgeLengthRatioRunner", 2.5, (int, float)),
            ("edge_length_ratio_circuits", "EdgeLengthRatioCircuits", 0.5, (int, float)),
            ("edge_length_ratio_circuits", "EdgeLengthRatioCircuits", 8, (int, float)),
            ("edge_length_ratio_circuits", "EdgeLengthRatioCircuits", 5.5, (int, float)),
            ("max_chord_height_ratio_curve", "MaxChordHeightRatioCurv", 0.02, (int, float)),
            ("max_chord_height_ratio_curve", "MaxChordHeightRatioCurv", 3, (int, float)),
            ("max_chord_height_ratio_curve", "MaxChordHeightRatioCurv", 1.5, (int, float)),
            ("min_num_elm_gates", "MinNumElmGates", 1, int),
            ("min_num_elm_gates", "MinNumElmGates", 8, int),
            ("min_num_elm_gates", "MinNumElmGates", 4, int),
            ("min_num_elm_baffle_bubblers", "MinNumElmBaffleBubblers", 3, int),
            ("min_num_elm_baffle_bubblers", "MinNumElmBaffleBubblers", 25, int),
            ("min_num_elm_baffle_bubblers", "MinNumElmBaffleBubblers", 50, int),
            ("tri_classification_opt", "TriClassificationOpt", 0, int),
            ("tri_classification_opt", "TriClassificationOpt", 1, int),
            ("tri_classification_opt", "TriClassificationOpt", 2, int),
        ],
    )  # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_mesh_generator, mock_object, pascal_name, property_name, expected, expected_type
    ):
        """
        Test the get methods of MeshGenerator properties.
        """
        setattr(mock_object, pascal_name, expected)
        result = getattr(mock_mesh_generator, property_name)
        assert isinstance(result, expected_type)
        assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, expected, expected_type",
        [
            ("edge_length", "EdgeLength", 0.1, float),
            ("edge_length", "EdgeLength", 0.15, float),
            ("edge_length", "EdgeLength", 1, int),
            ("merge_tolerance", "MergeTolerance", 0.15, float),
            ("merge_tolerance", "MergeTolerance", 1.15, float),
            ("merge_tolerance", "MergeTolerance", 5, int),
            ("match", "Match", True, bool),
            ("match", "Match", False, bool),
            ("smoothing", "Smoothing", True, bool),
            ("smoothing", "Smoothing", False, bool),
            ("element_reduction", "ElementReduction", True, bool),
            ("element_reduction", "ElementReduction", False, bool),
            ("surface_optimization", "SurfaceOptimization", True, bool),
            ("surface_optimization", "SurfaceOptimization", False, bool),
            ("automatic_tetra_optimization", "AutomaticTetraOptimization", True, bool),
            ("automatic_tetra_optimization", "AutomaticTetraOptimization", False, bool),
            ("tetra_refine", "TetraRefine", True, bool),
            ("tetra_refine", "TetraRefine", False, bool),
            ("tetra_layers", "TetraLayers", 4, int),
            ("tetra_layers", "TetraLayers", 20, int),
            ("tetra_layers", "TetraLayers", 40, int),
            ("tetra_layers_for_cores", "TetraLayersForCores", 4, int),
            ("tetra_layers_for_cores", "TetraLayersForCores", 20, int),
            ("tetra_layers_for_cores", "TetraLayersForCores", 10, int),
            ("tetra_max_ar", "TetraMaxAR", 1.5, float),
            ("tetra_max_ar", "TetraMaxAR", 2.0, float),
            ("tetra_max_ar", "TetraMaxAR", 5, int),
            ("maximum_match_distance", "MaximumMatchDistance", 1, int),
            ("maximum_match_distance", "MaximumMatchDistance", 5.5, (int, float)),
            ("maximum_match_distance", "MaximumMatchDistance", 9, int),
            ("maximum_match_distance_option", "MaximumMatchDistanceOption", 1, int),
            ("maximum_match_distance_option", "MaximumMatchDistanceOption", 2, int),
            ("maximum_match_distance_option", "MaximumMatchDistanceOption", 3, int),
            ("use_tetras_on_edge", "UseTetrasOnEdge", True, bool),
            ("use_tetras_on_edge", "UseTetrasOnEdge", False, bool),
            ("remesh_all", "RemeshAll", True, bool),
            ("remesh_all", "RemeshAll", False, bool),
            ("use_active_layer", "UseActiveLayer", True, bool),
            ("use_active_layer", "UseActiveLayer", False, bool),
            ("post_mesh_actions", "PostMeshActions", True, bool),
            ("post_mesh_actions", "PostMeshActions", False, bool),
            ("chord_height", "ChordHeight", 0.1, (int, float)),
            ("chord_height", "ChordHeight", 0.58, (int, float)),
            ("chord_height", "ChordHeight", 2, (int, float)),
            ("chord_height_control", "ChordHeightControl", True, bool),
            ("chord_height_control", "ChordHeightControl", False, bool),
            ("nurbs_mesher", "NurbsMesher", 1, int),
            ("nurbs_mesher", "NurbsMesher", 0, int),
            ("source_geom_type", "SourceGeomType", "Auto-Detect", str),
            ("chord_ht_proximity", "ChordHtProximity", True, bool),
            ("chord_ht_proximity", "ChordHtProximity", False, bool),
            ("chord_ht_aspect_ratio", "ChordHtAspectRatio", True, bool),
            ("chord_ht_aspect_ratio", "ChordHtAspectRatio", False, bool),
            ("merge_cavity_runner", "MergeCavityRunner", True, bool),
            ("merge_cavity_runner", "MergeCavityRunner", False, bool),
            ("chord_angle_select", "ChordAngleSelect", True, bool),
            ("chord_angle_select", "ChordAngleSelect", False, bool),
            ("chord_angle", "ChordAngle", 0.1, (int, float)),
            ("chord_angle", "ChordAngle", 0.62, (int, float)),
            ("chord_angle", "ChordAngle", 1, (int, float)),
            ("chord_angle", "ChordAngle", 2, (int, float)),
            ("use_auto_size", "UseAutoSize", True, bool),
            ("use_auto_size", "UseAutoSize", False, bool),
            ("cad_auto_size_scale", "CadAutoSizeScale", 0.1, (int, float)),
            ("cad_auto_size_scale", "CadAutoSizeScale", 0.268, (int, float)),
            ("cad_auto_size_scale", "CadAutoSizeScale", 1, (int, float)),
            ("cad_auto_size_scale", "CadAutoSizeScale", 50, (int, float)),
            ("cad_sliver_remove", "CadSliverRemove", True, bool),
            ("cad_sliver_remove", "CadSliverRemove", False, bool),
            ("cad_mesh_grading_factor", "CadMeshGradingFactor", 0, int),
            ("cad_mesh_grading_factor", "CadMeshGradingFactor", 1, int),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                0.2,
                (int, float),
            ),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                5.92,
                (int, float),
            ),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                5,
                (int, float),
            ),
            (
                "cad_mesh_minimum_curvature_percentage",
                "CadMeshMinimumCurvaturePercentage",
                7,
                (int, float),
            ),
            ("use_fallbacks", "UseFallbacks", True, bool),
            ("use_fallbacks", "UseFallbacks", False, bool),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                0.1,
                (int, float),
            ),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                7.123,
                (int, float),
            ),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                3,
                (int, float),
            ),
            (
                "max_edge_length_in_thickness_direction",
                "MaxEdgeLengthInThicknessDirection",
                7,
                (int, float),
            ),
            ("eltt_ratio", "ELTTRatio", 0.4, (int, float)),
            ("eltt_ratio", "ELTTRatio", 1.5, (int, float)),
            ("eltt_ratio", "ELTTRatio", 1, (int, float)),
            ("eltt_ratio", "ELTTRatio", 0.8, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 0.4, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 1.5, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 1, (int, float)),
            ("eltt_ratio_al", "ELTTRatioAL", 0.8, (int, float)),
            ("mesher_3d", "Mesher3D", "Legacy", str),
            ("cool_type", "CoolType", 1, int),
            ("cad_contact_mesh_type", "CadContactMeshType", "Precise match", str),
            ("mesh_component_type", "MeshComponentType", 1, int),
            ("inc_thk_dd", "IncThkDD", True, bool),
            ("inc_thk_dd", "IncThkDD", False, bool),
            ("use_gate_ref", "UseGateRef", True, bool),
            ("gate_el_factor", "GateELFactor", 10, (int, float)),
            ("gate_el_factor", "GateELFactor", 50, (int, float)),
            ("gate_el_factor", "GateELFactor", 32.5, (int, float)),
            ("mesh_curves_by_gel", "MeshCurvesByGEL", True, bool),
            ("mesh_curves_by_gel", "MeshCurvesByGEL", False, bool),
            ("surface_edge_length_scale_factor", "SurfaceEdgeLengthScaleFactor", 0.4, (int, float)),
            ("surface_edge_length_scale_factor", "SurfaceEdgeLengthScaleFactor", 5, (int, float)),
            ("surface_edge_length_scale_factor", "SurfaceEdgeLengthScaleFactor", 4.5, (int, float)),
            ("edge_length_ratio_runner", "EdgeLengthRatioRunner", 0.1, (int, float)),
            ("edge_length_ratio_runner", "EdgeLengthRatioRunner", 4, (int, float)),
            ("edge_length_ratio_runner", "EdgeLengthRatioRunner", 2.5, (int, float)),
            ("edge_length_ratio_circuits", "EdgeLengthRatioCircuits", 0.5, (int, float)),
            ("edge_length_ratio_circuits", "EdgeLengthRatioCircuits", 8, (int, float)),
            ("edge_length_ratio_circuits", "EdgeLengthRatioCircuits", 5.5, (int, float)),
            ("max_chord_height_ratio_curve", "MaxChordHeightRatioCurv", 0.02, (int, float)),
            ("max_chord_height_ratio_curve", "MaxChordHeightRatioCurv", 3, (int, float)),
            ("max_chord_height_ratio_curve", "MaxChordHeightRatioCurv", 1.5, (int, float)),
            ("min_num_elm_gates", "MinNumElmGates", 1, int),
            ("min_num_elm_gates", "MinNumElmGates", 8, int),
            ("min_num_elm_gates", "MinNumElmGates", 4, int),
            ("min_num_elm_baffle_bubblers", "MinNumElmBaffleBubblers", 3, int),
            ("min_num_elm_baffle_bubblers", "MinNumElmBaffleBubblers", 25, int),
            ("min_num_elm_baffle_bubblers", "MinNumElmBaffleBubblers", 50, int),
            ("tri_classification_opt", "TriClassificationOpt", 0, int),
            ("tri_classification_opt", "TriClassificationOpt", 1, int),
            ("tri_classification_opt", "TriClassificationOpt", 2, int),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_mesh_generator, mock_object, pascal_name, property_name, expected, expected_type
    ):
        """
        Test the get and set methods of MeshGenerator properties.
        """
        setattr(mock_mesh_generator, property_name, expected)
        result = getattr(mock_object, pascal_name)
        assert isinstance(result, expected_type)
        assert result == expected

    @pytest.mark.parametrize(
        "property_name, invalid_value",
        [("edge_length", x) for x in ["abc", True, None]]
        + [("merge_tolerance", x) for x in ["abc", True, None]]
        + [("match", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("smoothing", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("element_reduction", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("surface_optimization", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("automatic_tetra_optimization", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("tetra_refine", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("tetra_layers", x) for x in ["abc", True, 1.0, 1.5, None]]
        + [("tetra_layers_for_cores", x) for x in ["abc", True, 1.0, 1.5, None]]
        + [("tetra_max_ar", x) for x in ["abc", True, None]]
        + [("maximum_match_distance_option", x) for x in ["abc", True, 1.5, 1.0, None]]
        + [("maximum_match_distance", x) for x in ["abc", True, None]]
        + [("use_tetras_on_edge", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("remesh_all", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("use_active_layer", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("post_mesh_actions", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("chord_height", x) for x in ["abc", True, None]]
        + [("chord_height_control", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("nurbs_mesher", x) for x in ["abc", True, 1.5, None]]
        + [("source_geom_type", x) for x in [True, None, 1.5, 10, 1, 0]]
        + [("chord_ht_proximity", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("chord_ht_aspect_ratio", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("merge_cavity_runner", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("chord_angle_select", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("chord_angle", x) for x in ["abc", True, None]]
        + [("use_auto_size", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("cad_auto_size_scale", x) for x in ["abc", True, None]]
        + [("cad_sliver_remove", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("cad_mesh_grading_factor", x) for x in ["abc", True, 1.5, None]]
        + [("cad_mesh_minimum_curvature_percentage", x) for x in ["abc", True, None]]
        + [("use_fallbacks", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("max_edge_length_in_thickness_direction", x) for x in ["abc", True, None]]
        + [("eltt_ratio_al", x) for x in ["abc", True, None]]
        + [("eltt_ratio", x) for x in ["abc", True, None]]
        + [("mesher_3d", x) for x in [True, None, 1.5, 1, 0]]
        + [("cool_type", x) for x in ["abc", True, None, 1.5]]
        + [("cad_contact_mesh_type", x) for x in [True, None, 1.5]]
        + [("mesh_component_type", x) for x in ["abc", True, None, 1.5]]
        + [("inc_thk_dd", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("use_gate_ref", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("gate_el_factor", x) for x in ["abc", True, None]]
        + [("mesh_curves_by_gel", x) for x in ["abc", -1, 1.0, 1, 1.5, None]]
        + [("surface_edge_length_scale_factor", x) for x in ["abc", True, None]]
        + [("edge_length_ratio_runner", x) for x in ["abc", True, None]]
        + [("edge_length_ratio_circuits", x) for x in ["abc", True, None]]
        + [("max_chord_height_ratio_curve", x) for x in ["abc", True, None]]
        + [("min_num_elm_gates", x) for x in ["abc", True, 1.5, None]]
        + [("min_num_elm_baffle_bubblers", x) for x in ["abc", True, 2.5, None]]
        + [("tri_classification_opt", x) for x in ["abc", True, None, 1.5]],
    )
    def test_set_properties_invalid_type(
        self, mock_mesh_generator, mock_object, property_name, invalid_value, _
    ):
        """
        Test the get and set methods of MeshGenerator properties with invalid values.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_mesh_generator, property_name, invalid_value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, property_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, invalid_value",
        [("min_num_elm_gates", x) for x in [-1, 10, 9]]
        + [("min_num_elm_baffle_bubblers", x) for x in [-1, 51, 2]]
        + [("gate_el_factor", x) for x in [-1, 51, 9]],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties_invalid_value(
        self, mock_mesh_generator, mock_object, property_name, invalid_value, _
    ):
        """
        Test the get and set methods of MeshGenerator properties with invalid values.
        """
        with pytest.raises(ValueError) as e:
            setattr(mock_mesh_generator, property_name, invalid_value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, property_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, invalid_value",
        [("nurbs_mesher", x) for x in [-1, 10, 5]]
        + [("cad_contact_mesh_type", x) for x in ["abc", "Something"]]
        + [("cad_mesh_grading_factor", x) for x in [-1, 10, 5]]
        + [("source_geom_type", x) for x in ["Hello", "abc"]]
        + [("cool_type", x) for x in [-1, 10, 5]]
        + [("tri_classification_opt", x) for x in [-1, 10, 5]],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties_invalid_enum(
        self, mock_mesh_generator, property_name, invalid_value, _, caplog
    ):
        """
        Test the get and set methods of MeshGenerator properties with invalid values.
        """
        setattr(mock_mesh_generator, property_name, invalid_value)
        assert _("this may cause function call to fail") in caplog.text
        assert getattr(mock_mesh_generator, property_name) == invalid_value

    def test_gel_false(self, mock_mesh_generator, mock_object):
        """
        Test the get and set methods of MeshGenerator properties.
        """
        mock_object.MeshCurvesByGEL = False

        mock_mesh_generator.edge_length_ratio_circuits = 0.5
        assert mock_object.EdgeLengthRatioCircuits == 0.5

        mock_mesh_generator.edge_length_ratio_runner = 0.1
        assert mock_object.EdgeLengthRatioRunner == 0.1

    @pytest.mark.parametrize(
        "property_name, pascal_name, value, expected, expected_type",
        [("nurbs_mesher", "NurbsMesher", x, x.value, int) for x in NurbsAlgorithm]
        + [("nurbs_mesher", "NurbsMesher", x.value, x.value, int) for x in NurbsAlgorithm]
        + [("cool_type", "CoolType", x, x.value, int) for x in CoolType]
        + [("cool_type", "CoolType", x.value, x.value, int) for x in CoolType]
        + [("cad_contact_mesh_type", "CadContactMeshType", x, x.value, str) for x in CADContactMesh]
        + [
            ("cad_contact_mesh_type", "CadContactMeshType", x.value, x.value, str)
            for x in CADContactMesh
        ]
        + [
            ("tri_classification_opt", "TriClassificationOpt", x, x.value, int)
            for x in TriClassification
        ]
        + [
            ("tri_classification_opt", "TriClassificationOpt", x.value, x.value, int)
            for x in TriClassification
        ]
        + [
            ("cad_mesh_grading_factor", "CadMeshGradingFactor", x, x.value, int)
            for x in GradingFactor
        ]
        + [
            ("cad_mesh_grading_factor", "CadMeshGradingFactor", x.value, x.value, int)
            for x in GradingFactor
        ]
        + [("mesher_3d", "Mesher3D", x, x.value, str) for x in Mesher3DType]
        + [("mesher_3d", "Mesher3D", x.value, x.value, str) for x in Mesher3DType]
        + [("source_geom_type", "SourceGeomType", x, x.value, str) for x in GeomType]
        + [("source_geom_type", "SourceGeomType", x.value, x.value, str) for x in GeomType],
    )
    # pylint: disable=R0913, R0917
    def test_set_enum_values(
        self,
        mock_mesh_generator,
        mock_object,
        property_name,
        pascal_name,
        value,
        expected,
        expected_type,
    ):
        """
        Test the set methods of MeshGenerator properties with enum values.
        """
        setattr(mock_mesh_generator, property_name, value)
        result = getattr(mock_object, pascal_name)
        assert isinstance(result, expected_type)
        assert result == expected
