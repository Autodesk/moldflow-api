# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for ImportOptions Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the ImportOptions class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import ImportOptions, Synergy
from moldflow.common import MeshType, ImportUnits
from tests.api.integration_tests.data.defaults import import_options_defaults
from tests.api.integration_tests.data.set_options import import_options_set_options


@pytest.mark.integration
@pytest.mark.import_options
class TestIntegrationImportOptions:
    """
    Integration test suite for the ImportOptions class.
    """

    @pytest.fixture
    def import_options(self, synergy: Synergy):
        """
        Fixture to create a real ImportOptions instance for integration testing.
        """
        return synergy.import_options

    def test_create_import_options(self, synergy: Synergy):
        """
        Test that ImportOptions can be accessed from Synergy instance.
        """
        import_options = synergy.import_options
        assert import_options.import_options is not None
        assert isinstance(import_options, ImportOptions)

    @pytest.mark.parametrize("default", import_options_defaults.keys())
    def test_defaults(self, import_options: ImportOptions, default: any):
        """
        Test that ImportOptions defaults are set correctly upon initialization.
        """
        assert getattr(import_options, default) == import_options_defaults[default]

    @pytest.mark.parametrize("attribute", import_options_set_options.keys())
    def test_set_options(self, import_options: ImportOptions, attribute: str):
        """
        Test that ImportOptions can be set correctly.
        """
        for value, expected_value in import_options_set_options[attribute].items():
            print(attribute, value, type(value), expected_value, type(expected_value))
            setattr(import_options, attribute, value)
            assert getattr(import_options, attribute) == expected_value

    def test_multiple_import_options_instances(self, synergy: Synergy):
        """
        Test that multiple ImportOptions instances can be created independently.
        Each instance has its own COM object and maintains independent state.
        """
        import_options1 = synergy.import_options
        import_options2 = synergy.import_options

        assert isinstance(import_options1, ImportOptions)
        assert isinstance(import_options2, ImportOptions)

        assert import_options1 is not import_options2
        assert import_options1.import_options is not import_options2.import_options

        # Test that each instance can be configured independently
        # Configure instance 1
        import_options1.mesh_type = MeshType.MESH_3D
        import_options1.units = ImportUnits.MM
        import_options1.mdl_mesh = True
        import_options1.use_mdl = True

        # Configure instance 2 differently
        import_options2.mesh_type = MeshType.MESH_FUSION
        import_options2.units = ImportUnits.CM
        import_options2.mdl_mesh = False
        import_options2.use_mdl = False

        # Verify configurations remain independent
        assert import_options1.mesh_type == MeshType.MESH_3D.value
        assert import_options1.units == ImportUnits.MM.value
        assert import_options1.mdl_mesh is True
        assert import_options1.use_mdl is True

        assert import_options2.mesh_type == MeshType.MESH_FUSION.value
        assert import_options2.units == ImportUnits.CM.value
        assert import_options2.mdl_mesh is False
        assert import_options2.use_mdl is False
