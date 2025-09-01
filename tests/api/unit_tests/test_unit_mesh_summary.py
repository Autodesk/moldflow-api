# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for MeshSummary Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import MeshSummary


@pytest.mark.unit
class TestUnitMeshSummary:
    """
    Test suite for the MeshSummary class.
    """

    @pytest.fixture
    def mock_mesh_summary(self, mock_object) -> MeshSummary:
        """
        Fixture to create a mock instance of MeshSummary.
        Args:
            mock_object: Mock object for the MeshSummary dependency.
        Returns:
            MeshSummary: An instance of MeshSummary with the mock object.
        """
        return MeshSummary(mock_object)

    @pytest.mark.parametrize(
        "property_name, pascal_name",
        [
            ("min_aspect_ratio", "MinAspectRatio"),
            ("max_aspect_ratio", "MaxAspectRatio"),
            ("ave_aspect_ratio", "AveAspectRatio"),
            ("free_edges_count", "FreeEdgesCount"),
            ("manifold_edges_count", "ManifoldEdgesCount"),
            ("non_manifold_edges_count", "NonManifoldEdgesCount"),
            ("triangles_count", "TrianglesCount"),
            ("tetras_count", "TetrasCount"),
            ("nodes_count", "NodesCount"),
            ("beams_count", "BeamsCount"),
            ("connectivity_regions", "ConnectivityRegions"),
            ("unoriented", "Unoriented"),
            ("intersection_elements", "IntersectionElements"),
            ("overlap_elements", "OverlapElements"),
            ("duplicated_beams", "DuplicatedBeams"),
            ("match_ratio", "MatchRatio"),
            ("reciprocal_match_ratio", "ReciprocalMatchRatio"),
            ("mesh_volume", "MeshVolume"),
            ("runner_volume", "RunnerVolume"),
            ("zero_triangles", "ZeroTriangles"),
            ("zero_beams", "ZeroBeams"),
            ("fusion_area", "FusionArea"),
            ("percent_tets_ar_gt_thresh", "PercentTetsARgtThresh"),
            ("max_dihedral_angle", "MaxDihedralAngle"),
            ("percent_tets_mda_gt_thresh", "PercentTetsMDAgtThresh"),
            ("max_volume_ratio", "MaxVolumeRatio"),
            ("percent_tets_vr_gt_thresh", "PercentTetsVRgtThresh"),
        ],
    )
    def test_get_property(self, mock_mesh_summary, mock_object, property_name, pascal_name):
        """
        Test the property getter methods of MeshSummary.
        """
        expected_value = 1
        setattr(mock_object, pascal_name, expected_value)
        result = getattr(mock_mesh_summary, property_name)
        assert result == expected_value
