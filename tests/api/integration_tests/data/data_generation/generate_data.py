# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Script to generate data for integration tests.

Usage:
    generate_data.py [<markers>...]
"""

import docopt
import sys
from datetime import datetime
from moldflow import Synergy
from tests.api.integration_tests.data.data_generation.generate_data_helper import (
    generate_json,
    clean_up_temp_files,
    get_generate_data_functions,
    get_available_markers,
    fetch_data_on_markers,
)
from tests.api.integration_tests.data.data_generation.generate_data_logger import (
    generate_data_logger,
)
from tests.api.integration_tests.constants import FileSet
from tests.api.integration_tests.conftest import get_study_files


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


@generate_json(file_set=None)
def generate_synergy_data(synergy: Synergy = None):
    """
    Generate data for the Synergy class.
    Returns a dict with relevant properties.
    """

    build_number_parts = synergy.build_number.split(".")
    build_number_major_minor = ".".join(build_number_parts[:2])

    return {"version": synergy.version, "build_number": build_number_major_minor}


def main():
    """Main entry point for this script"""
    args = docopt.docopt(__doc__)
    DATE_TIME = datetime.now()

    try:
        markers = args.get('<markers>') or []
        get_study_files()
        generate_functions = get_generate_data_functions(globals())

        for marker in markers:
            if marker not in generate_functions.keys():
                generate_data_logger.error(f'Invalid marker: {marker}')
                generate_data_logger.error(get_available_markers(generate_functions))
                return 0

        if len(markers) > 0:
            fetch_data_on_markers(markers, generate_functions, DATE_TIME)
        else:
            fetch_data_on_markers(generate_functions.keys(), generate_functions, DATE_TIME)

    except Exception as err:
        generate_data_logger.error(f'FAILURE: {err}')
        clean_up_temp_files()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
