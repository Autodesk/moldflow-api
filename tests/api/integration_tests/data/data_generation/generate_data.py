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
from tests.api.integration_tests.constants import (
    FileSet,
    MATERIAL_DB,
    MATERIAL_DB_TYPE,
    CUSTOM_PROPERTY_NAME,
    CUSTOM_PROPERTY_ID,
    CUSTOM_PROPERTY_TYPE,
    FIELD_PROPERTIES,
)
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


@generate_json(file_set=None)
def generate_material_property_data(synergy: Synergy = None):
    """
    Generate data for the Material Property class.
    Returns a dict with relevant properties.
    """
    mf = synergy.material_finder
    mf.set_data_domain(MATERIAL_DB, MATERIAL_DB_TYPE)
    mat = mf.get_first_material()
    properties = {}

    properties["material_name"] = mat.name
    properties["material_id"] = mat.id
    properties["material_type"] = mat.type

    field_id = mat.get_first_field()
    while field_id != 0:

        try:
            field_values = mat.get_field_values(field_id)
            field_values = field_values.to_list()
        except AttributeError:
            field_values = None

        try:
            field_units = mat.field_units(field_id)
            field_units = field_units.to_list()
        except AttributeError:
            field_units = None

        properties[f"field_{field_id}"] = {
            "field_description": mat.get_field_description(field_id),
            "field_values": field_values,
            "field_units": field_units,
            "field_writable": mat.is_field_writable(field_id),
            "field_hidden": mat.is_field_hidden(field_id),
        }

        field_id = mat.get_next_field(field_id)

    return properties


@generate_json(file_set=None, synergy_required=False)
def generate_custom_property_data():
    """
    Generate data for a new property.
    Returns a dict with relevant properties.
    """
    properties_data = {
        "property_name": CUSTOM_PROPERTY_NAME,
        "property_id": CUSTOM_PROPERTY_ID,
        "property_type": CUSTOM_PROPERTY_TYPE,
        "original_field_data": {
            "field_description": "",
            "field_values": [],
            "field_units": [],
            "field_writable": True,
            "field_hidden": False,
        },
        "hidden_field_data": {
            "field_description": "",
            "field_values": None,
            "field_units": [],
            "field_writable": False,
            "field_hidden": True,
        },
    }

    for index, field_properties in FIELD_PROPERTIES.items():
        properties_data[f"field_data_{index}"] = {
            "field_id": field_properties["id"],
            "field_description": field_properties["description"],
            "field_values": field_properties["values"],
            "field_units": field_properties["units"],
            "field_writable": field_properties["writable"],
            "field_hidden": field_properties["hidden"],
        }

    return properties_data


def generate_prop_data():
    """
    Generate data for the Property class specifically for tests on material and custom properties.
    """
    generate_material_property_data()
    generate_custom_property_data()


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
