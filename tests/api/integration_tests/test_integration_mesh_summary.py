# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for MeshSummary Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the MeshSummary class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import MeshSummary, Synergy
from tests.api.integration_tests.constants import FileSet, DataFile


@pytest.mark.integration
@pytest.mark.mesh_summary
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationMeshSummary:
    """
    Integration test suite for the MeshSummary class.
    Tests are run against meshed models to ensure mesh summary data is available.
    """

    json_file_name = DataFile.MESH_SUMMARY

    @pytest.fixture
    def mesh_summary(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a real MeshSummary instance for integration testing.
        """
        model_type, file_path, _, _ = study_with_project

        # Get diagnosis manager and mesh summary
        diagnosis_manager = synergy.diagnosis_manager
        mesh_summary = diagnosis_manager.get_mesh_summary(
            element_only=False, inc_beams=True, inc_match=True, recalculate=True
        )

        if mesh_summary is None:
            pytest.skip(f"No mesh summary available for {model_type.value} model: {file_path}")

        return mesh_summary

    def test_aspect_ratio_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test aspect ratio related properties.
        """
        min_ar = mesh_summary.min_aspect_ratio
        max_ar = mesh_summary.max_aspect_ratio
        ave_ar = mesh_summary.ave_aspect_ratio

        assert isinstance(min_ar, float)
        assert isinstance(max_ar, float)
        assert isinstance(ave_ar, float)

        assert min_ar <= ave_ar <= max_ar

        assert abs(min_ar - expected_values["min_aspect_ratio"]) < 0.01
        assert abs(max_ar - expected_values["max_aspect_ratio"]) < 0.01
        assert abs(ave_ar - expected_values["ave_aspect_ratio"]) < 0.01

    def test_edge_count_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test edge count related properties.
        """
        free_edges = mesh_summary.free_edges_count
        manifold_edges = mesh_summary.manifold_edges_count
        non_manifold_edges = mesh_summary.non_manifold_edges_count

        assert isinstance(free_edges, int)
        assert isinstance(manifold_edges, int)
        assert isinstance(non_manifold_edges, int)

        assert free_edges >= 0
        assert manifold_edges >= 0
        assert non_manifold_edges >= 0

        assert free_edges == expected_values["free_edges_count"]
        assert manifold_edges == expected_values["manifold_edges_count"]
        assert non_manifold_edges == expected_values["non_manifold_edges_count"]

    def test_element_count_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test element count related properties.
        """
        triangles = mesh_summary.triangles_count
        tetras = mesh_summary.tetras_count
        nodes = mesh_summary.nodes_count
        beams = mesh_summary.beams_count

        assert isinstance(triangles, int)
        assert isinstance(tetras, int)
        assert isinstance(nodes, int)
        assert isinstance(beams, int)

        # All counts should be non-negative
        assert triangles >= 0
        assert tetras >= 0
        assert nodes >= 0
        assert beams >= 0

        assert triangles > 0 or tetras > 0, "Meshed model should have triangles or tetrahedra"
        assert nodes > 0, "Meshed model should have nodes"

        assert triangles == expected_values["triangles_count"]
        assert tetras == expected_values["tetras_count"]
        assert nodes == expected_values["nodes_count"]
        assert beams == expected_values["beams_count"]

    def test_mesh_quality_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test mesh quality related properties.
        """
        connectivity_regions = mesh_summary.connectivity_regions
        unoriented = mesh_summary.unoriented
        intersection_elements = mesh_summary.intersection_elements
        overlap_elements = mesh_summary.overlap_elements

        assert isinstance(connectivity_regions, int)
        assert isinstance(unoriented, int)
        assert isinstance(intersection_elements, int)
        assert isinstance(overlap_elements, int)

        assert connectivity_regions >= 0
        assert unoriented >= 0
        assert intersection_elements >= 0
        assert overlap_elements >= 0

        assert connectivity_regions == expected_values["connectivity_regions"]
        assert unoriented == expected_values["unoriented"]
        assert intersection_elements == expected_values["intersection_elements"]
        assert overlap_elements == expected_values["overlap_elements"]

    def test_match_ratio_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test match ratio related properties.
        """
        match_ratio = mesh_summary.match_ratio
        reciprocal_match_ratio = mesh_summary.reciprocal_match_ratio

        assert isinstance(match_ratio, float)
        assert isinstance(reciprocal_match_ratio, float)

        assert match_ratio >= 0
        assert reciprocal_match_ratio >= 0

        assert abs(match_ratio - expected_values["match_ratio"]) < 0.01
        assert abs(reciprocal_match_ratio - expected_values["reciprocal_match_ratio"]) < 0.01

    def test_volume_area_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test volume and area related properties.
        """
        mesh_volume = mesh_summary.mesh_volume
        runner_volume = mesh_summary.runner_volume
        fusion_area = mesh_summary.fusion_area

        assert isinstance(mesh_volume, float)
        assert isinstance(runner_volume, float)
        assert isinstance(fusion_area, float)

        assert mesh_volume >= 0
        assert runner_volume >= 0
        assert fusion_area >= 0

        assert abs(mesh_volume - expected_values["mesh_volume"]) < 0.01
        assert abs(runner_volume - expected_values["runner_volume"]) < 0.01
        assert abs(fusion_area - expected_values["fusion_area"]) < 0.01

    def test_defect_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test mesh defect related properties.
        """
        duplicated_beams = mesh_summary.duplicated_beams
        zero_triangles = mesh_summary.zero_triangles
        zero_beams = mesh_summary.zero_beams

        assert isinstance(duplicated_beams, int)
        assert isinstance(zero_triangles, int)
        assert isinstance(zero_beams, int)

        assert duplicated_beams >= 0
        assert zero_triangles >= 0
        assert zero_beams >= 0

        assert duplicated_beams == expected_values["duplicated_beams"]
        assert zero_triangles == expected_values["zero_triangles"]
        assert zero_beams == expected_values["zero_beams"]

    def test_tetrahedra_quality_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test tetrahedra quality related properties.
        """
        percent_tets_ar_gt_thresh = mesh_summary.percent_tets_ar_gt_thresh
        max_dihedral_angle = mesh_summary.max_dihedral_angle
        percent_tets_mda_gt_thresh = mesh_summary.percent_tets_mda_gt_thresh
        max_volume_ratio = mesh_summary.max_volume_ratio
        percent_tets_vr_gt_thresh = mesh_summary.percent_tets_vr_gt_thresh

        assert isinstance(percent_tets_ar_gt_thresh, float)
        assert isinstance(max_dihedral_angle, float)
        assert isinstance(percent_tets_mda_gt_thresh, float)
        assert isinstance(max_volume_ratio, float)
        assert isinstance(percent_tets_vr_gt_thresh, float)

        assert 0 <= percent_tets_ar_gt_thresh <= 100
        assert 0 <= percent_tets_mda_gt_thresh <= 100
        assert 0 <= percent_tets_vr_gt_thresh <= 100

        assert max_dihedral_angle >= 0
        assert max_volume_ratio >= 0

        assert abs(percent_tets_ar_gt_thresh - expected_values["percent_tets_ar_gt_thresh"]) < 0.01
        assert abs(max_dihedral_angle - expected_values["max_dihedral_angle"]) < 0.01
        assert (
            abs(percent_tets_mda_gt_thresh - expected_values["percent_tets_mda_gt_thresh"]) < 0.01
        )
        assert abs(max_volume_ratio - expected_values["max_volume_ratio"]) < 0.01
        assert abs(percent_tets_vr_gt_thresh - expected_values["percent_tets_vr_gt_thresh"]) < 0.01

    def test_all_properties_accessible(self, mesh_summary: MeshSummary):
        """
        Test that all properties can be accessed without errors.
        This is a comprehensive smoke test for all MeshSummary properties.
        """
        properties_to_test = [
            'min_aspect_ratio',
            'max_aspect_ratio',
            'ave_aspect_ratio',
            'free_edges_count',
            'manifold_edges_count',
            'non_manifold_edges_count',
            'triangles_count',
            'tetras_count',
            'nodes_count',
            'beams_count',
            'connectivity_regions',
            'unoriented',
            'intersection_elements',
            'overlap_elements',
            'match_ratio',
            'reciprocal_match_ratio',
            'mesh_volume',
            'runner_volume',
            'fusion_area',
            'duplicated_beams',
            'zero_triangles',
            'zero_beams',
            'percent_tets_ar_gt_thresh',
            'max_dihedral_angle',
            'percent_tets_mda_gt_thresh',
            'max_volume_ratio',
            'percent_tets_vr_gt_thresh',
        ]

        results = {}
        for prop_name in properties_to_test:
            try:
                value = getattr(mesh_summary, prop_name)
                results[prop_name] = {
                    'value': value,
                    'type': type(value).__name__,
                    'accessible': True,
                }
            except Exception as e:
                results[prop_name] = {'error': str(e), 'accessible': False}

        # All properties should be accessible
        inaccessible_props = [prop for prop, result in results.items() if not result['accessible']]
        assert len(inaccessible_props) == 0, f"Inaccessible properties: {inaccessible_props}"

        # Print summary for debugging (will be visible in verbose mode)
        print("\nMesh Summary Properties Test Results:")
        for prop_name, result in results.items():
            if result['accessible']:
                print(f"  {prop_name}: {result['value']} ({result['type']})")
            else:
                print(f"  {prop_name}: ERROR - {result['error']}")
