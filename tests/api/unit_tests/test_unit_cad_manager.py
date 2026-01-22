# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for CADManager Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import CADManager, EntList, Vector
from tests.api.unit_tests.conftest import VALID_MOCK


@pytest.mark.unit
@pytest.mark.cad_manager
class TestUnitCADManager:
    """
    Test suite for the CADManager class.
    """

    @pytest.fixture
    def mock_cad_manager(self, mock_object) -> CADManager:
        """
        Fixture to create a mock instance of CADManager.
        Args:
            mock_object: Mock object for the CADManager dependency.
        Returns:
            CADManager: An instance of CADManager with the mock object.
        """
        return CADManager(mock_object)

    def test_create_entity_list(self, mock_cad_manager, mock_object):
        """
        Test the create_entity_list method of the CADManager class.
        """
        ent = Mock(spec=EntList)
        mock_object.CreateEntityList = ent
        result = mock_cad_manager.create_entity_list()
        assert result.ent_list == ent
        assert isinstance(result, EntList)
        assert result.ent_list == ent

    def test_create_entity_list_none(self, mock_cad_manager, mock_object):
        """
        Test the create_entity_list method of the CADManager class when it returns None.
        """
        mock_object.CreateEntityList = None
        result = mock_cad_manager.create_entity_list()
        assert result is None

    @pytest.mark.parametrize("distance, expected", [(1.0, True), (2, True), (3.0, False)])
    def test_modify_cad_surfaces_by_normal(self, mock_cad_manager, mock_object, distance, expected):
        """
        Test the modify_cad_surfaces_by_normal method of the CADManager class.
        """
        faces = VALID_MOCK.ENT_LIST
        transit_faces = VALID_MOCK.ENT_LIST
        mock_object.ModifyCADSurfacesByNormal.return_value = expected
        result = mock_cad_manager.modify_cad_surfaces_by_normal(faces, transit_faces, distance)
        assert result is expected
        mock_object.ModifyCADSurfacesByNormal.assert_called_once_with(
            faces.ent_list, transit_faces.ent_list, distance
        )

    @pytest.mark.parametrize(
        "faces, transit_faces, distance",
        [
            (Mock(spec=EntList), Mock(spec=EntList), None),
            (Mock(spec=EntList), Mock(spec=EntList), True),
            (Mock(spec=EntList), Mock(spec=EntList), "String"),
            (Mock(spec=EntList), 1, 1.0),
            (Mock(spec=EntList), "String", 1.0),
            (Mock(spec=EntList), True, 1.0),
            (1, Mock(spec=EntList), 1.0),
            ("String", Mock(spec=EntList), 1.0),
            (True, Mock(spec=EntList), 1.0),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_modify_cad_surfaces_by_normal_invalid(
        self, mock_cad_manager, mock_object, faces, transit_faces, distance, _
    ):
        """
        Test the modify_cad_surfaces_by_normal method of the CADManager class.
        """
        with pytest.raises(TypeError) as e:
            mock_cad_manager.modify_cad_surfaces_by_normal(faces, transit_faces, distance)
        assert _("Invalid") in str(e.value)
        mock_object.ModifyCADSurfacesByNormal.assert_not_called()

    @pytest.mark.parametrize("expected", [(True), (False)])
    def test_modify_cad_surfaces_by_vector(self, mock_cad_manager, mock_object, expected):
        """
        Test the modify_cad_surfaces_by_vector method of the CADManager class.
        """
        faces = VALID_MOCK.ENT_LIST
        transit_faces = VALID_MOCK.ENT_LIST
        vector = VALID_MOCK.VECTOR
        mock_object.ModifyCADSurfacesByVector.return_value = expected
        result = mock_cad_manager.modify_cad_surfaces_by_vector(faces, transit_faces, vector)
        assert result is expected
        mock_object.ModifyCADSurfacesByVector.assert_called_once_with(
            faces.ent_list, transit_faces.ent_list, vector.vector
        )

    @pytest.mark.parametrize(
        "faces, transit_faces, vector",
        [
            (Mock(spec=EntList), Mock(spec=EntList), True),
            (Mock(spec=EntList), Mock(spec=EntList), "String"),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), 1, Mock(spec=Vector)),
            (Mock(spec=EntList), "String", Mock(spec=Vector)),
            (Mock(spec=EntList), True, Mock(spec=Vector)),
            (1, Mock(spec=EntList), Mock(spec=Vector)),
            ("String", Mock(spec=EntList), Mock(spec=Vector)),
            (True, Mock(spec=EntList), Mock(spec=Vector)),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_modify_cad_surfaces_by_vector_invalid(
        self, mock_cad_manager, mock_object, faces, transit_faces, vector, _
    ):
        """
        Test the modify_cad_surfaces_by_vector method of the CADManager class.
        """
        with pytest.raises(TypeError) as e:
            mock_cad_manager.modify_cad_surfaces_by_vector(faces, transit_faces, vector)
        assert _("Invalid") in str(e.value)
        mock_object.ModifyCADSurfacesByVector.assert_not_called()

    def test_create_entity_list_return_none(self, mock_cad_manager: CADManager, mock_object):
        """
        Test the create_entity_list method of the CADManager class.
        """
        mock_object.CreateEntityList = None
        result = mock_cad_manager.create_entity_list()
        assert result is None
