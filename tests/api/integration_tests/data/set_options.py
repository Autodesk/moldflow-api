# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Data for testing setting options for Moldflow Synergy API classes.
"""

from moldflow.common import MeshType, ImportUnits, MDLKernel, MDLContactMeshType, CADBodyProperty
from tests.conftest import VALID_BOOL, NON_NEGATIVE_FLOAT, NON_NEGATIVE_INT


def data_dict(data_class):
    """
    Data dictionary for testing setting options for Moldflow Synergy API classes.
    """
    result_dict = {}
    for data_value in data_class:
        result_dict[data_value] = data_value
    return result_dict


def enum_dict(enum_class):
    """
    Enum dictionary for testing setting options for Moldflow Synergy API classes.
    """
    result_dict = {}
    for enum_value in enum_class:
        result_dict[enum_value] = enum_value.value
        result_dict[enum_value.value] = enum_value.value
    return result_dict


import_options_set_options = {
    "mesh_type": enum_dict(MeshType),
    "units": enum_dict(ImportUnits),
    "mdl_mesh": data_dict(VALID_BOOL),
    "mdl_surfaces": data_dict(VALID_BOOL),
    "use_mdl": data_dict(VALID_BOOL),
    "mdl_kernel": enum_dict(MDLKernel),
    "mdl_auto_edge_select": data_dict(VALID_BOOL),
    "mdl_edge_length": data_dict(NON_NEGATIVE_FLOAT),
    "mdl_tetra_layers": data_dict(NON_NEGATIVE_INT),
    "mdl_chord_angle_select": data_dict(VALID_BOOL),
    "mdl_chord_angle": data_dict(NON_NEGATIVE_FLOAT),
    "mdl_sliver_removal": data_dict(VALID_BOOL),
    "use_layer_name_based_on_cad": data_dict(VALID_BOOL),
    "mdl_show_log": data_dict(VALID_BOOL),
    "mdl_contact_mesh_type": enum_dict(MDLContactMeshType),
    "cad_body_property": enum_dict(CADBodyProperty),
}
