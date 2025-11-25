# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Data for testing setting options for Moldflow Synergy API classes.
"""

from moldflow import (
    MeshType,
    ImportUnits,
    MDLKernel,
    MDLContactMeshType,
    CADBodyProperty,
    MaterialDatabase,
    MaterialDatabaseType,
)
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

# --------------------------------------------------------------------------------------------------
# Constants for property tests

# Constants for material property tests
MATERIAL_DB = MaterialDatabase.COOLANT
MATERIAL_DB_TYPE = MaterialDatabaseType.SYSTEM

# Constants for custom property tests
CUSTOM_PROPERTY_DEFAULTS = False
CUSTOM_PROPERTY_NAME = "Test Name"
CUSTOM_PROPERTY_ID = 1
CUSTOM_PROPERTY_TYPE = 10

FIELD_PROPERTIES = {
    1: {
        "id": 20,
        "description": "Test Description",
        "values": [1, 2, 3],
        "units": [],
        "writable": True,
        "hidden": False,
    },
    2: {
        "id": 21,
        "description": "Second Test Description",
        "values": [4, 5, 6],
        "units": [],
        "writable": True,
        "hidden": False,
    },
}

FIELD_INDEX = 1  # Index for the field to be used for single field tests

# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Constants for entity list tests

TEST_ENTITY_LIST_STRING = {
    "dd_model": {
        "items": "T56 T57",
        "predicate": "T56:57",
        "saved_list": "MyTest",
        "converted_string": "T56 T57 ",
        "size": 2,
        "entity": {0: "T56 ", 1: "T57 "},
    },
    "midplane_model": {
        "items": "T56 T57",
        "predicate": "T56:57",
        "saved_list": "MyTest",
        "converted_string": "T56 T57 ",
        "size": 2,
        "entity": {0: "T56 ", 1: "T57 "},
    },
    "3d_model": {
        "items": "TE3798 TE3799",
        "predicate": "TE3798:3799",
        "saved_list": "MyTest",
        "converted_string": "TE3798 TE3799 ",
        "size": 2,
        "entity": {0: "TE3798 ", 1: "TE3799 "},
    },
}


# --------------------------------------------------------------------------------------------------
