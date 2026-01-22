# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Defaults for the ImportOptions class.
"""

DEFAULT_IMPORT_OPTIONS = {
    "mesh_type": "",
    "units": "",
    "mdl_mesh": True,
    "mdl_surfaces": False,
    "use_mdl": False,
    "mdl_kernel": "",
    "mdl_auto_edge_select": True,
    "mdl_edge_length": -1.0,
    "mdl_tetra_layers": 6,
    "mdl_chord_angle_select": False,
    "mdl_chord_angle": 0.0,
    "mdl_sliver_removal": False,
    "use_layer_name_based_on_cad": True,
    "mdl_show_log": True,
    "mdl_contact_mesh_type": "Ignore contact",
    "cad_body_property": 0,
}
