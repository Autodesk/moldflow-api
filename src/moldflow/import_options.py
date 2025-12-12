# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    ImportOptions Class API Wrapper
"""

from .logger import process_log
from .common import LogMessage, MeshType, ImportUnits, MDLKernel
from .common import MDLContactMeshType, CADBodyProperty
from .helper import get_enum_value, check_type, check_is_non_negative
from .com_proxy import safe_com

class ImportOptions:
    """
    Wrapper for ImportOptions class of Moldflow Synergy.
    """

    def __init__(self, _import_options):
        """
        Initialize the ImportOptions with a ImportOptions instance from COM.

        Args:
            _import_options: The ImportOptions instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="ImportOptions")
        self.import_options = safe_com(_import_options)

    @property
    def mesh_type(self) -> str:
        """
        The mesh type.

        :getter: Get the mesh type.
        :setter: Set the mesh type.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_type")
        return self.import_options.MeshType

    @mesh_type.setter
    def mesh_type(self, value: MeshType | str) -> None:
        """
        The mesh type.

        Args:
            value (MeshType | str): The mesh type to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mesh_type", value=value)
        value = get_enum_value(value, MeshType)
        self.import_options.MeshType = value

    @property
    def units(self) -> str:
        """
        The units.

        :getter: Get the units.
        :setter: Set the units.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="units")
        return self.import_options.Units

    @units.setter
    def units(self, value: ImportUnits | str) -> None:
        """
        The units.

        Args:
            value (str): The units to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="units", value=value)
        value = get_enum_value(value, ImportUnits)
        self.import_options.Units = value

    @property
    def mdl_mesh(self) -> bool:
        """
        Specifies whether MDL should generate a mesh when importing the model.

        :getter: Get the MDL mesh.
        :setter: Set the MDL mesh.
            [True to generate a mesh, False to not generate a mesh.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_mesh")
        return self.import_options.MDLMesh

    @mdl_mesh.setter
    def mdl_mesh(self, value: bool) -> None:
        """
        Specifies whether MDL should generate a mesh when importing the model.

        Args:
            value (bool): The MDL mesh to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mdl_mesh", value=value)
        check_type(value, bool)
        self.import_options.MDLMesh = value

    @property
    def mdl_surfaces(self) -> bool:
        """
        Specifies whether MDL should translate surfaces when importing the model.

        :getter: Get the MDL surfaces.
        :setter: Set the MDL surfaces.
            [True to translate surfaces, False to not translate surfaces.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_surfaces")
        return self.import_options.MDLSurfaces

    @mdl_surfaces.setter
    def mdl_surfaces(self, value: bool) -> None:
        """
        Specifies whether MDL should translate surfaces when importing the model.

        Args:
            value (bool): The MDL surfaces to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mdl_surfaces", value=value)
        check_type(value, bool)
        self.import_options.MDLSurfaces = value

    @property
    def use_mdl(self) -> bool:
        """
        Specifies whether MDL should be used for model import.

        :getter: Get the use MDL.
        :setter: Set the use MDL.
            [True to use MDL, False to not use MDL.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_mdl")
        return self.import_options.UseMDL

    @use_mdl.setter
    def use_mdl(self, value: bool) -> None:
        """
        Specifies whether MDL should be used for model import.

        Args:
            value (bool): The use MDL to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="use_mdl", value=value)
        check_type(value, bool)
        self.import_options.UseMDL = value

    @property
    def mdl_kernel(self) -> str:
        """
        The MDL kernel.

        :getter: Get the MDL kernel.
        :setter: Set the MDL kernel.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_kernel")
        return self.import_options.MDLKernel

    @mdl_kernel.setter
    def mdl_kernel(self, value: MDLKernel | str) -> None:
        """
        The MDL kernel.

        Args:
            value (str): The MDL kernel to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mdl_kernel", value=value)
        value = get_enum_value(value, MDLKernel)
        self.import_options.MDLKernel = value

    @property
    def mdl_auto_edge_select(self) -> bool:
        """
        Specifies whether MDL should automatically select edges for meshing.

        :getter: Get the MDL auto edge select.
        :setter: Set the MDL auto edge select.
            [True to automatically select edges, False to not automatically select edges.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_auto_edge_select")
        return self.import_options.MDLAutoEdgeSelect

    @mdl_auto_edge_select.setter
    def mdl_auto_edge_select(self, value: bool) -> None:
        """
        Specifies whether MDL should automatically select edges for meshing.

        Args:
            value (bool): The MDL auto edge select to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_auto_edge_select", value=value
        )
        check_type(value, bool)
        self.import_options.MDLAutoEdgeSelect = value

    @property
    def mdl_edge_length(self) -> float:
        """
        The MDL edge length.

        :getter: Get the MDL edge length.
        :setter: Set the MDL edge length.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_edge_length")
        return self.import_options.MDLEdgeLength

    @mdl_edge_length.setter
    def mdl_edge_length(self, value: float) -> None:
        """
        The MDL edge length.

        Args:
            value (float): The MDL edge length to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_edge_length", value=value
        )
        check_type(value, (float, int))
        check_is_non_negative(value)
        self.import_options.MDLEdgeLength = value

    @property
    def mdl_tetra_layers(self) -> int:
        """
        Specifies the minimum number of tetra layer through thickness in 3D meshing.

        :getter: Get the MDL tetra layers.
        :setter: Set the MDL tetra layers.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_tetra_layers")
        return self.import_options.MDLTetraLayers

    @mdl_tetra_layers.setter
    def mdl_tetra_layers(self, value: int) -> None:
        """
        Specifies the minimum number of tetra layer through thickness in 3D meshing.

        Args:
            value (int): The MDL tetra layers to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_tetra_layers", value=value
        )
        check_type(value, int)
        check_is_non_negative(value)
        self.import_options.MDLTetraLayers = value

    @property
    def mdl_chord_angle_select(self) -> bool:
        """
        Specifies whether chord angle should be used for meshing.

        :getter: Get the MDL chord angle select.
        :setter: Set the MDL chord angle select.
            [True to use chord angle, False to not use chord angle.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_chord_angle_select")
        return self.import_options.MDLChordAngleSelect

    @mdl_chord_angle_select.setter
    def mdl_chord_angle_select(self, value: bool) -> None:
        """
        Specifies whether chord angle should be used for meshing.

        Args:
            value (bool): The MDL chord angle select to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_chord_angle_select", value=value
        )
        check_type(value, bool)
        self.import_options.MDLChordAngleSelect = value

    @property
    def mdl_chord_angle(self) -> float:
        """
        The MDL chord angle.[in radian]

        :getter: Get the MDL chord angle.
        :setter: Set the MDL chord angle.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_chord_angle")
        return self.import_options.MDLChordAngle

    @mdl_chord_angle.setter
    def mdl_chord_angle(self, value: float) -> None:
        """
        The MDL chord angle.[in radian]

        Args:
            value (float): The MDL chord angle to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_chord_angle", value=value
        )
        check_type(value, (float, int))
        check_is_non_negative(value)
        self.import_options.MDLChordAngle = value

    @property
    def mdl_sliver_removal(self) -> bool:
        """
        Specifies whether sliver removal option should be used for meshing.

        :getter: Get the MDL sliver removal.
        :setter: Set the MDL sliver removal.
            [True to use sliver removal, False to not use sliver removal.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_sliver_removal")
        return self.import_options.MDLSliverRemoval

    @mdl_sliver_removal.setter
    def mdl_sliver_removal(self, value: bool) -> None:
        """
        Specifies whether sliver removal option should be used for meshing.

        Args:
            value (bool): The MDL sliver removal to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_sliver_removal", value=value
        )
        check_type(value, bool)
        self.import_options.MDLSliverRemoval = value

    @property
    def use_layer_name_based_on_cad(self) -> bool:
        """
        Specifies whether using layer name based on CAD for direct import.

        :getter: Get the use layer name based on CAD.
        :setter: Set the use layer name based on CAD.
            [True to use layer name based on CAD, False to not use layer name based on CAD.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_layer_name_based_on_cad")
        return self.import_options.UseLayerNameBasedOnCad

    @use_layer_name_based_on_cad.setter
    def use_layer_name_based_on_cad(self, value: bool) -> None:
        """
        Specifies whether using layer name based on CAD for direct import.

        Args:
            value (bool): The use layer name based on CAD to set.
        """
        process_log(
            __name__,
            LogMessage.PROPERTY_SET,
            locals(),
            name="use_layer_name_based_on_cad",
            value=value,
        )
        check_type(value, bool)
        self.import_options.UseLayerNameBasedOnCad = value

    @property
    def mdl_show_log(self) -> bool:
        """
        Specifies whether to display import log.

        :getter: Get the MDL show log.
        :setter: Set the MDL show log.
            [True to display import log, False to not display import log.]
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_show_log")
        return self.import_options.MDLShowLog

    @mdl_show_log.setter
    def mdl_show_log(self, value: bool) -> None:
        """
        Specifies whether to display import log.

        Args:
            value (bool): The MDL show log to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mdl_show_log", value=value)
        check_type(value, bool)
        self.import_options.MDLShowLog = value

    @property
    def mdl_contact_mesh_type(self) -> str:
        """
        The MDL contact mesh type.

        :getter: Get the MDL contact mesh type.
        :setter: Set the MDL contact mesh type.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mdl_contact_mesh_type")
        return self.import_options.MDLContactMeshType

    @mdl_contact_mesh_type.setter
    def mdl_contact_mesh_type(self, value: MDLContactMeshType | str) -> None:
        """
        The MDL contact mesh type.

        Args:
            value (str): The MDL contact mesh type to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="mdl_contact_mesh_type", value=value
        )
        value = get_enum_value(value, MDLContactMeshType)
        self.import_options.MDLContactMeshType = value

    @property
    def cad_body_property(self) -> int:
        """
        The CAD body property.

        :getter: Get the CAD body property.
        :setter: Set the CAD body property.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cad_body_property")
        return self.import_options.CadBodyProperty

    @cad_body_property.setter
    def cad_body_property(self, value: CADBodyProperty | int) -> None:
        """
        The CAD body property.

        Args:
            value (int): The CAD body property to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="cad_body_property", value=value
        )
        value = get_enum_value(value, CADBodyProperty)
        self.import_options.CadBodyProperty = value
