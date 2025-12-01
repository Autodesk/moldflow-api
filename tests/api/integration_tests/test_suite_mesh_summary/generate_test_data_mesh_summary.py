# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for the MeshSummary class.
"""

from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet


@generate_json(file_set=FileSet.MESHED)
def generate_mesh_summary_data(synergy: Synergy = None):
    """
    Extract mesh summary data from a study.
    Returns a dict with relevant properties.
    """
    mesh_summary = synergy.diagnosis_manager.get_mesh_summary(
        element_only=False, inc_beams=True, inc_match=True, recalculate=True
    )

    return {
        "min_aspect_ratio": mesh_summary.min_aspect_ratio,
        "max_aspect_ratio": mesh_summary.max_aspect_ratio,
        "ave_aspect_ratio": mesh_summary.ave_aspect_ratio,
        "free_edges_count": mesh_summary.free_edges_count,
        "manifold_edges_count": mesh_summary.manifold_edges_count,
        "non_manifold_edges_count": mesh_summary.non_manifold_edges_count,
        "triangles_count": mesh_summary.triangles_count,
        "tetras_count": mesh_summary.tetras_count,
        "nodes_count": mesh_summary.nodes_count,
        "beams_count": mesh_summary.beams_count,
        "connectivity_regions": mesh_summary.connectivity_regions,
        "unoriented": mesh_summary.unoriented,
        "intersection_elements": mesh_summary.intersection_elements,
        "overlap_elements": mesh_summary.overlap_elements,
        "match_ratio": mesh_summary.match_ratio,
        "reciprocal_match_ratio": mesh_summary.reciprocal_match_ratio,
        "mesh_volume": mesh_summary.mesh_volume,
        "runner_volume": mesh_summary.runner_volume,
        "fusion_area": mesh_summary.fusion_area,
        "duplicated_beams": mesh_summary.duplicated_beams,
        "zero_triangles": mesh_summary.zero_triangles,
        "zero_beams": mesh_summary.zero_beams,
        "percent_tets_ar_gt_thresh": mesh_summary.percent_tets_ar_gt_thresh,
        "max_dihedral_angle": mesh_summary.max_dihedral_angle,
        "percent_tets_mda_gt_thresh": mesh_summary.percent_tets_mda_gt_thresh,
        "max_volume_ratio": mesh_summary.max_volume_ratio,
        "percent_tets_vr_gt_thresh": mesh_summary.percent_tets_vr_gt_thresh,
    }


if __name__ == "__main__":
    generate_mesh_summary_data()
