# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for CADManager Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the CADManager class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import CADManager, Synergy, EntList
from tests.api.integration_tests.constants import FileSet


@pytest.mark.integration
@pytest.mark.cad_manager
@pytest.mark.file_set(FileSet.CAD_MANAGER)
class TestIntegrationCADManager:
    """
    Integration test suite for the CADManager class.
    """

    @pytest.fixture
    def cad_manager(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a real CADManager instance for integration testing.
        """
        return synergy.cad_manager

    def test_create_entity_list(self, cad_manager: CADManager):
        """
        Test the create_entity_list method of the CADManager class.
        """
        entity_list = cad_manager.create_entity_list()
        assert entity_list is not None
        assert entity_list.ent_list is not None
        assert isinstance(entity_list, EntList)

    def test_modify_cad_surfaces_by_normal(self, cad_manager: CADManager):
        """
        Test the modify_cad_surfaces_by_normal method of the CADManager class.
        """
        faces = cad_manager.create_entity_list()
        faces.select_from_string("F443")
        transit_faces = cad_manager.create_entity_list()
        distance = 1.0
        result = cad_manager.modify_cad_surfaces_by_normal(faces, transit_faces, distance)
        assert result is True

    def test_modify_cad_surfaces_by_vector(self, synergy: Synergy, cad_manager: CADManager):
        """
        Test the modify_cad_surfaces_by_vector method of the CADManager class.
        """
        faces = cad_manager.create_entity_list()
        faces.select_from_string("F443")
        transit_faces = cad_manager.create_entity_list()
        vector = synergy.create_vector()
        vector.set_xyz(1.0, 1.0, 1.0)
        result = cad_manager.modify_cad_surfaces_by_vector(faces, transit_faces, vector)
        assert result is True

    def test_modify_cad_surfaces_by_normal_none(self, cad_manager: CADManager):
        """
        Test the modify_cad_surfaces_by_normal method of the CADManager class.
        """
        result = cad_manager.modify_cad_surfaces_by_normal(None, None, 1.0)
        assert result is False

    def test_modify_cad_surfaces_by_vector_none(self, cad_manager: CADManager):
        """
        Test the modify_cad_surfaces_by_vector method of the CADManager class.
        """
        result = cad_manager.modify_cad_surfaces_by_vector(None, None, None)
        assert result is False
