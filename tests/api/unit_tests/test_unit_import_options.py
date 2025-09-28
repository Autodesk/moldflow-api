# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for ImportOptions Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import ImportOptions
from moldflow import MeshType, ImportUnits, MDLKernel, MDLContactMeshType, CADBodyProperty


@pytest.mark.unit
@pytest.mark.import_options
class TestUnitImportOptions:
    """
    Test suite for the ImportOptions class.
    """

    @pytest.fixture
    def mock_import_options(self, mock_object) -> ImportOptions:
        """
        Fixture to create a mock instance of ImportOptions.
        Args:
            mock_object: Mock object for the ImportOptions dependency.
        Returns:
            ImportOptions: An instance of ImportOptions with the mock object.
        """
        return ImportOptions(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("MeshType", "mesh_type", MeshType.MESH_MIDPLANE),
            ("MeshType", "mesh_type", MeshType.MESH_FUSION),
            ("MeshType", "mesh_type", MeshType.MESH_3D),
            ("MeshType", "mesh_type", "MidPlane"),
            ("MeshType", "mesh_type", "Fusion"),
            ("MeshType", "mesh_type", "3D"),
            ("Units", "units", ImportUnits.MM),
            ("Units", "units", ImportUnits.CM),
            ("Units", "units", ImportUnits.M),
            ("Units", "units", ImportUnits.IN),
            ("Units", "units", "mm"),
            ("Units", "units", "cm"),
            ("Units", "units", "m"),
            ("Units", "units", "in"),
            ("MDLMesh", "mdl_mesh", True),
            ("MDLMesh", "mdl_mesh", False),
            ("MDLSurfaces", "mdl_surfaces", True),
            ("MDLSurfaces", "mdl_surfaces", False),
            ("UseMDL", "use_mdl", True),
            ("UseMDL", "use_mdl", False),
            ("MDLKernel", "mdl_kernel", MDLKernel.PARAMETRIC),
            ("MDLKernel", "mdl_kernel", MDLKernel.PARASOLID),
            ("MDLKernel", "mdl_kernel", "Parametric"),
            ("MDLKernel", "mdl_kernel", "Parasolid"),
            ("MDLAutoEdgeSelect", "mdl_auto_edge_select", True),
            ("MDLAutoEdgeSelect", "mdl_auto_edge_select", False),
            ("MDLEdgeLength", "mdl_edge_length", 0.1),
            ("MDLEdgeLength", "mdl_edge_length", 1.0),
            ("MDLTetraLayers", "mdl_tetra_layers", 1),
            ("MDLTetraLayers", "mdl_tetra_layers", 2),
            ("MDLChordAngleSelect", "mdl_chord_angle_select", True),
            ("MDLChordAngleSelect", "mdl_chord_angle_select", False),
            ("MDLChordAngle", "mdl_chord_angle", 0.1),
            ("MDLChordAngle", "mdl_chord_angle", 1.0),
            ("MDLSliverRemoval", "mdl_sliver_removal", True),
            ("MDLSliverRemoval", "mdl_sliver_removal", False),
            ("UseLayerNameBasedOnCad", "use_layer_name_based_on_cad", True),
            ("UseLayerNameBasedOnCad", "use_layer_name_based_on_cad", False),
            ("MDLShowLog", "mdl_show_log", True),
            ("MDLShowLog", "mdl_show_log", False),
            ("MDLContactMeshType", "mdl_contact_mesh_type", MDLContactMeshType.PRECISE_MATCH),
            ("MDLContactMeshType", "mdl_contact_mesh_type", MDLContactMeshType.FAULT_TOLERANCE),
            ("MDLContactMeshType", "mdl_contact_mesh_type", MDLContactMeshType.IGNORE_CONTACT),
            ("MDLContactMeshType", "mdl_contact_mesh_type", "Precise match"),
            ("MDLContactMeshType", "mdl_contact_mesh_type", "Fault tolerant"),
            ("MDLContactMeshType", "mdl_contact_mesh_type", "Ignore contact"),
            ("CadBodyProperty", "cad_body_property", CADBodyProperty.PROPERTY_CAD_COMPONENT),
            ("CadBodyProperty", "cad_body_property", CADBodyProperty.PROPERTY_3D_CHANNEL),
            ("CadBodyProperty", "cad_body_property", CADBodyProperty.PROPERTY_MOLD_COMPONENT),
            ("CadBodyProperty", "cad_body_property", 0),
            ("CadBodyProperty", "cad_body_property", 40915),
            ("CadBodyProperty", "cad_body_property", 40912),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_import_options: ImportOptions, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of ImportOptions.

        Args:
            mock_import_options: Instance of ImportOptions.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_import_options, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, expected",
        [
            ("MeshType", "mesh_type", MeshType.MESH_MIDPLANE, "Midplane"),
            ("MeshType", "mesh_type", MeshType.MESH_FUSION, "Fusion"),
            ("MeshType", "mesh_type", MeshType.MESH_3D, "3D"),
            ("MeshType", "mesh_type", "Midplane", "Midplane"),
            ("MeshType", "mesh_type", "Fusion", "Fusion"),
            ("MeshType", "mesh_type", "3D", "3D"),
            ("Units", "units", ImportUnits.MM, "mm"),
            ("Units", "units", ImportUnits.CM, "cm"),
            ("Units", "units", ImportUnits.M, "m"),
            ("Units", "units", ImportUnits.IN, "in"),
            ("Units", "units", "mm", "mm"),
            ("Units", "units", "cm", "cm"),
            ("Units", "units", "m", "m"),
            ("Units", "units", "in", "in"),
            ("MDLMesh", "mdl_mesh", True, True),
            ("MDLMesh", "mdl_mesh", False, False),
            ("MDLSurfaces", "mdl_surfaces", True, True),
            ("MDLSurfaces", "mdl_surfaces", False, False),
            ("UseMDL", "use_mdl", True, True),
            ("UseMDL", "use_mdl", False, False),
            ("MDLKernel", "mdl_kernel", MDLKernel.PARAMETRIC, "Parametric"),
            ("MDLKernel", "mdl_kernel", MDLKernel.PARASOLID, "Parasolid"),
            ("MDLKernel", "mdl_kernel", "Parametric", "Parametric"),
            ("MDLKernel", "mdl_kernel", "Parasolid", "Parasolid"),
            ("MDLAutoEdgeSelect", "mdl_auto_edge_select", True, True),
            ("MDLAutoEdgeSelect", "mdl_auto_edge_select", False, False),
            ("MDLEdgeLength", "mdl_edge_length", 0.1, 0.1),
            ("MDLEdgeLength", "mdl_edge_length", 1.0, 1.0),
            ("MDLTetraLayers", "mdl_tetra_layers", 1, 1),
            ("MDLTetraLayers", "mdl_tetra_layers", 2, 2),
            ("MDLChordAngleSelect", "mdl_chord_angle_select", True, True),
            ("MDLChordAngleSelect", "mdl_chord_angle_select", False, False),
            ("MDLChordAngle", "mdl_chord_angle", 0.1, 0.1),
            ("MDLChordAngle", "mdl_chord_angle", 1.0, 1.0),
            ("MDLSliverRemoval", "mdl_sliver_removal", True, True),
            ("MDLSliverRemoval", "mdl_sliver_removal", False, False),
            ("UseLayerNameBasedOnCad", "use_layer_name_based_on_cad", True, True),
            ("UseLayerNameBasedOnCad", "use_layer_name_based_on_cad", False, False),
            ("MDLShowLog", "mdl_show_log", True, True),
            ("MDLShowLog", "mdl_show_log", False, False),
            (
                "MDLContactMeshType",
                "mdl_contact_mesh_type",
                MDLContactMeshType.PRECISE_MATCH,
                "Precise match",
            ),
            (
                "MDLContactMeshType",
                "mdl_contact_mesh_type",
                MDLContactMeshType.FAULT_TOLERANCE,
                "Fault tolerant",
            ),
            (
                "MDLContactMeshType",
                "mdl_contact_mesh_type",
                MDLContactMeshType.IGNORE_CONTACT,
                "Ignore contact",
            ),
            ("MDLContactMeshType", "mdl_contact_mesh_type", "Precise match", "Precise match"),
            ("MDLContactMeshType", "mdl_contact_mesh_type", "Fault tolerant", "Fault tolerant"),
            ("MDLContactMeshType", "mdl_contact_mesh_type", "Ignore contact", "Ignore contact"),
            ("CadBodyProperty", "cad_body_property", CADBodyProperty.PROPERTY_CAD_COMPONENT, 0),
            ("CadBodyProperty", "cad_body_property", CADBodyProperty.PROPERTY_3D_CHANNEL, 40915),
            (
                "CadBodyProperty",
                "cad_body_property",
                CADBodyProperty.PROPERTY_MOLD_COMPONENT,
                40912,
            ),
            ("CadBodyProperty", "cad_body_property", 0, 0),
            ("CadBodyProperty", "cad_body_property", 40915, 40915),
            ("CadBodyProperty", "cad_body_property", 40912, 40912),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self,
        mock_import_options: ImportOptions,
        mock_object,
        pascal_name,
        property_name,
        value,
        expected,
    ):
        """
        Test properties of ImportOptions.

        Args:
            mock_import_options: Instance of ImportOptions.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_import_options, property_name, value)
        new_val = getattr(mock_object, pascal_name)
        assert new_val == expected

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("mesh_type", 1),
            ("units", 1),
            ("mdl_mesh", 1),
            ("mdl_surfaces", 1),
            ("use_mdl", 1),
            ("mdl_kernel", 1),
            ("mdl_auto_edge_select", 1),
            ("mdl_auto_edge_select", "Test"),
            ("mdl_edge_length", "Test"),
            ("mdl_tetra_layers", "Test"),
            ("mdl_chord_angle_select", 1),
            ("mdl_chord_angle", "Test"),
            ("mdl_sliver_removal", 1),
            ("use_layer_name_based_on_cad", 1),
            ("mdl_show_log", 1),
            ("mdl_contact_mesh_type", 1),
            ("cad_body_property", "Test"),
            ("mesh_type", None),
            ("units", None),
            ("mdl_mesh", None),
            ("mdl_surfaces", None),
            ("use_mdl", None),
            ("mdl_kernel", None),
            ("mdl_auto_edge_select", None),
            ("mdl_edge_length", None),
            ("mdl_tetra_layers", None),
            ("mdl_chord_angle_select", None),
            ("mdl_chord_angle", None),
            ("mdl_sliver_removal", None),
            ("use_layer_name_based_on_cad", None),
            ("mdl_show_log", None),
            ("mdl_contact_mesh_type", None),
            ("cad_body_property", None),
        ],
    )
    def test_invalid_properties(self, mock_import_options: ImportOptions, property_name, value, _):
        """
        Test invalid properties of ImportOptions.
        Args:
            mock_import_options: Instance of ImportOptions.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_import_options, property_name, value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("mesh_type", "Test"),
            ("units", "Test"),
            ("mdl_kernel", "Test"),
            ("mdl_contact_mesh_type", "Test"),
            ("cad_body_property", 1),
        ],
    )
    def test_invalid_properties_value(
        self, mock_import_options: ImportOptions, property_name, value, _, caplog
    ):
        """
        Test invalid properties of ImportOptions.
        Args:
            mock_import_options: Instance of ImportOptions.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        setattr(mock_import_options, property_name, value)
        assert _("this may cause function call to fail") in caplog.text
        assert getattr(mock_import_options, property_name) == value
