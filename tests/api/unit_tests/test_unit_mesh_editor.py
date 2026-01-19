# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for MeshEditor Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock, patch
from win32com.client import VARIANT
import pythoncom
import pytest
from moldflow import MeshEditor, EntList, Property, Vector
from tests.api.unit_tests.conftest import VALID_MOCK
from tests.conftest import (
    INVALID_BOOL,
    INVALID_FLOAT,
    VALID_BOOL,
    VALID_FLOAT,
    VALID_INT,
    pad_and_zip,
)


@pytest.mark.unit
class TestUnitMeshEditor:
    """
    Test suite for the MeshEditor class.
    """

    @pytest.fixture
    def mock_mesh_editor(self, mock_object) -> MeshEditor:
        """
        Fixture to create a mock instance of MeshEditor.
        Args:
            mock_object: Mock object for the MeshEditor dependency.
        Returns:
            MeshEditor: An instance of MeshEditor with the mock object.
        """
        return MeshEditor(mock_object)

    @pytest.mark.parametrize(
        "name, property_name, expected",
        [
            ("auto_fix", "AutoFix", True),
            ("purge_nodes", "PurgeNodes", True),
            ("imprint_visible_triangles", "ImprintVisibleTriangles", True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_run_function(self, mock_mesh_editor, mock_object, name, property_name, expected):
        """
        Test running function with no args of MeshEditor.
        """

        setattr(mock_object, property_name, expected)
        result = getattr(mock_mesh_editor, name)()
        assert result == expected

    def test_create_entity_list(self, mock_mesh_editor, mock_object):
        """
        Test creating an entity list using MeshEditor.
        """
        mock_object.create_entity_list = 1
        result = mock_mesh_editor.create_entity_list()
        assert isinstance(result, EntList)

    @pytest.mark.parametrize("expected", [True, False])
    def test_swap_edge(self, mock_mesh_editor, mock_object, expected):
        """
        Test swapping edges using MeshEditor.
        """
        mock_object.SwapEdge.return_value = expected
        tri1 = Mock(spec=EntList)
        tri1.ent_list = Mock()
        tri2 = Mock(spec=EntList)
        tri2.ent_list = Mock()
        feat = True
        result = mock_mesh_editor.swap_edge(tri1, tri2, feat)
        assert isinstance(result, bool)
        mock_object.SwapEdge.assert_called_once_with(tri1.ent_list, tri2.ent_list, feat)

    @pytest.mark.parametrize(
        "tri1, tri2, feat",
        [
            (Mock(spec=EntList), Mock(spec=EntList), None),
            (Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), Mock(spec=EntList), "String"),
            (Mock(spec=EntList), 1, True),
            (Mock(spec=EntList), 1.0, True),
            (Mock(spec=EntList), "String", True),
            (Mock(spec=EntList), True, True),
            (1, Mock(spec=EntList), True),
            (1.0, Mock(spec=EntList), True),
            ("String", Mock(spec=EntList), True),
            (True, Mock(spec=EntList), True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_swap_edge_invalid(self, mock_mesh_editor, mock_object, tri1, tri2, feat, _):
        """
        Test swapping edges with invalid arguments using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.swap_edge(tri1, tri2, feat)
        assert _("Invalid") in str(e.value)
        mock_object.SwapEdge.assert_not_called()

    @pytest.mark.parametrize(
        "nodes, expected",
        [(Mock(spec=EntList), True), (Mock(spec=EntList), False), (None, False), (None, True)],
    )
    def test_stitch_free_edges(self, mock_mesh_editor, mock_object, nodes, expected):
        """
        Test stitching free edges using MeshEditor.
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            mock_object.StitchFreeEdges.return_value = expected
            mock_object.StitchFreeEdges2.return_value = expected
            if nodes is None:
                result = mock_mesh_editor.stitch_free_edges(nodes, 1.0)
                mock_object.StitchFreeEdges2.assert_called_once_with(mock_func(), 1.0)
            else:
                nodes.ent_list = Mock()
                result = mock_mesh_editor.stitch_free_edges(nodes, 1.0)
                mock_object.StitchFreeEdges2.assert_called_once_with(nodes.ent_list, 1.0)
            assert result == expected

    @pytest.mark.parametrize(
        "tolerance, nodes",
        [
            (True, Mock(spec=EntList)),
            ("String", None),
            (None, None),
            (1.0, 1),
            (1.0, 1.0),
            (1.0, "String"),
        ],
    )
    def test_stitch_free_edges_invalid(self, mock_mesh_editor, mock_object, tolerance, nodes, _):
        """
        Test stitching free edges with invalid arguments using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.stitch_free_edges(nodes, tolerance)
        assert _("Invalid") in str(e.value)
        mock_object.StitchFreeEdges.assert_not_called()
        mock_object.StitchFreeEdges2.assert_not_called()

    def test_insert_node(self, mock_mesh_editor, mock_object):
        """
        Test inserting a node using MeshEditor.
        """
        mock_object.InsertNode.return_value = 1
        node1 = Mock(spec=EntList)
        node1.ent_list = Mock()
        node2 = Mock(spec=EntList)
        node2.ent_list = Mock()
        result = mock_mesh_editor.insert_node(node1, node2)
        assert isinstance(result, EntList)
        mock_object.InsertNode.assert_called_once_with(node1.ent_list, node2.ent_list)

    @pytest.mark.parametrize(
        "node1, node2",
        [
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), 1),
            (Mock(spec=EntList), "String"),
            (Mock(spec=EntList), True),
            (1.0, Mock(spec=EntList)),
            (1, Mock(spec=EntList)),
            ("String", Mock(spec=EntList)),
            (True, Mock(spec=EntList)),
        ],
    )
    def test_insert_node_invalid(self, mock_mesh_editor, mock_object, node1, node2, _):
        """
        Test inserting a node with invalid arguments using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.insert_node(node1, node2)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNode.assert_not_called()

    @pytest.mark.parametrize(
        "node1, node2, node3",
        [
            (Mock(spec=EntList), Mock(spec=EntList), None),
            (Mock(spec=EntList), None, Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), None, None),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_insert_node_in_tri(self, mock_mesh_editor, mock_object, node1, node2, node3):
        """
        Test inserting a node in a triangle using MeshEditor.
        """

        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            expected1 = 1
            expected2 = 2
            node1.size = 3
            result1 = None
            result2 = None
            result3 = None
            if node1:
                node1.ent_list = Mock()
                result1 = node1.ent_list
            if node2:
                node2.ent_list = Mock()
                result2 = node2.ent_list
            else:
                result2 = mock_func()
            if node3:
                node3.ent_list = Mock()
                result3 = node3.ent_list
            else:
                result3 = mock_func()

            mock_object.InsertNodeInTri2.return_value = expected1
            mock_object.InsertNodeInTri.return_value = expected2

            result = mock_mesh_editor.insert_node_in_tri(node1, node2, node3)

            if node2 is None and node3 is None:
                assert result.ent_list == expected1
                assert result.ent_list != expected2
                mock_object.InsertNodeInTri2.assert_called_once_with(result1)
                mock_object.InsertNodeInTri.assert_not_called()
            else:
                assert result.ent_list == expected2
                assert result.ent_list != expected1
                mock_object.InsertNodeInTri.assert_called_once_with(result1, result2, result3)
                mock_object.InsertNodeInTri2.assert_not_called()

    @pytest.mark.parametrize(
        "node1, node2, node3",
        [
            (1, Mock(spec=EntList), Mock(spec=EntList)),
            ("String", Mock(spec=EntList), Mock(spec=EntList)),
            (True, Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), 1, Mock(spec=EntList)),
            (Mock(spec=EntList), True, Mock(spec=EntList)),
            (Mock(spec=EntList), "String", Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), True),
            (Mock(spec=EntList), Mock(spec=EntList), "String"),
            (1.0, 1, 1.0),
            ("String", "String", "String"),
            (True, True, True),
            (1.0, None, None),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_insert_node_in_tri_invalid(
        self, mock_mesh_editor, mock_object, node1, node2, node3, _
    ):
        """
        Test inserting a node in a triangle with invalid arguments using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.insert_node_in_tri(node1, node2, node3)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNodeInTri2.assert_not_called()
        mock_object.InsertNodeInTri.assert_not_called()

    @pytest.mark.parametrize("size", [1, 2, 4])
    def test_insert_node_in_tri_invalid_size(self, mock_mesh_editor, mock_object, size, _):
        """
        Test inserting a node in a triangle with invalid size using MeshEditor.
        """
        node1 = Mock(spec=EntList)
        node2 = None
        node3 = None
        node1.size = size
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.insert_node_in_tri(node1, node2, node3)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNodeInTri2.assert_not_called()
        mock_object.InsertNodeInTri.assert_not_called()

    @pytest.mark.parametrize(
        "node1, node2, node3, node4",
        [
            (Mock(spec=EntList), Mock(spec=EntList), None, Mock(spec=EntList)),
            (Mock(spec=EntList), None, Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), None),
            (Mock(spec=EntList), None, None, None),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_insert_node_in_tet(self, mock_mesh_editor, mock_object, node1, node2, node3, node4):
        """
        Test inserting a node in a triangle using MeshEditor.
        """
        expected1 = 1
        expected2 = 2
        node1.size = 4
        result1 = None
        result2 = None
        result3 = None
        result4 = None
        if node1:
            node1.ent_list = Mock()
            result1 = node1.ent_list
        if node2:
            node2.ent_list = Mock()
            result2 = node2.ent_list
        if node3:
            node3.ent_list = Mock()
            result3 = node3.ent_list
        if node4:
            node4.ent_list = Mock()
            result4 = node4.ent_list
        mock_object.InsertNodeInTet.return_value = expected1
        mock_object.InsertNodeInTetByNodes.return_value = expected2
        result = mock_mesh_editor.insert_node_in_tet(node1, node2, node3, node4)

        if node2 is None or node3 is None or node4 is None:
            assert result.ent_list == expected1
            assert result.ent_list != expected2
            mock_object.InsertNodeInTet.assert_called_once_with(result1)
            mock_object.InsertNodeInTetByNodes.assert_not_called()
        else:
            assert result.ent_list == expected2
            assert result.ent_list != expected1
            mock_object.InsertNodeInTetByNodes.assert_called_once_with(
                result1, result2, result3, result4
            )
            mock_object.InsertNodeInTet.assert_not_called()
            mock_mesh_editor.insert_node_in_tet_by_nodes(node1, node2, node3, node4)

    @pytest.mark.parametrize(
        "node1, node2, node3, node4",
        [
            (1, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList)),
            ("String", Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList)),
            (True, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), 1, Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), True, Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), "String", Mock(spec=EntList), Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), True, Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), "String", Mock(spec=EntList)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), True),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), "String"),
            (1.0, 1, 1.0, 1.0),
            ("String", "String", "String", "String"),
            (True, True, True, True),
            (1.0, None, None, None),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_insert_node_in_tet_invalid(
        self, mock_mesh_editor, mock_object, node1, node2, node3, node4, _
    ):
        """
        Test inserting a node in a triangle with invalid arguments using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.insert_node_in_tet(node1, node2, node3, node4)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNodeInTet.assert_not_called()
        mock_object.InsertNodeInTetByNodes.assert_not_called()

    @pytest.mark.parametrize("size", [1, 3, 5])
    def test_insert_node_in_tet_invalid_size(self, mock_mesh_editor, mock_object, size, _):
        """
        Test inserting a node in a triangle with invalid size using MeshEditor.
        """
        node1 = Mock(spec=EntList)
        node2 = None
        node3 = None
        node4 = None
        node1.size = size
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.insert_node_in_tet(node1, node2, node3, node4)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNodeInTet.assert_not_called()
        mock_object.InsertNodeInTetByNodes.assert_not_called()

    def test_insert_node_in_tet_by_nodes(self, mock_mesh_editor, mock_object):
        """
        Test inserting a node in a triangle using MeshEditor.
        """
        expected = 1
        node1 = Mock(spec=EntList)
        node1.ent_list = Mock()
        node2 = Mock(spec=EntList)
        node2.ent_list = Mock()
        node3 = Mock(spec=EntList)
        node3.ent_list = Mock()
        node4 = Mock(spec=EntList)
        node4.ent_list = Mock()
        mock_object.InsertNodeInTetByNodes.return_value = expected
        result = mock_mesh_editor.insert_node_in_tet_by_nodes(node1, node2, node3, node4)
        assert isinstance(result, EntList)
        assert result.ent_list == expected
        mock_object.InsertNodeInTetByNodes.assert_called_once_with(
            node1.ent_list, node2.ent_list, node3.ent_list, node4.ent_list
        )

    @pytest.mark.parametrize(
        "node1, node2, node3, node4",
        [
            (x, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList))
            for x in [1, 1.0, "String", True]
        ]
        + [
            (Mock(spec=EntList), x, Mock(spec=EntList), Mock(spec=EntList))
            for x in [1, 1.0, "String", True]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=EntList), x, Mock(spec=EntList))
            for x in [1, 1.0, "String", True]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), x)
            for x in [1, 1.0, "String", True]
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_insert_node_in_tet_by_nodes_invalid(
        self, mock_mesh_editor, mock_object, node1, node2, node3, node4, _
    ):
        """
        Test inserting a node in a triangle with invalid arguments using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.insert_node_in_tet_by_nodes(node1, node2, node3, node4)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNodeInTetByNodes.assert_not_called()

    @pytest.mark.parametrize(
        "beam, num",
        [(Mock(spec=EntList), 2), (Mock(spec=EntList), 100), (Mock(spec=EntList), 1000)],
    )
    def test_insert_node_on_beam(self, mock_mesh_editor, mock_object, beam, num):
        """
        Test inserting a node on a beam using MeshEditor.
        """
        mock_object.InsertNodeOnBeam.return_value = 1
        beam.ent_list = Mock()
        result = mock_mesh_editor.insert_node_on_beam(beam, num)
        assert isinstance(result, EntList)
        assert result.ent_list == 1
        mock_object.InsertNodeOnBeam.assert_called_once_with(beam.ent_list, num)

    @pytest.mark.parametrize(
        "beam, num",
        [
            (1, 2),
            ("String", 2),
            (True, 2),
            (Mock(spec=EntList), None),
            (Mock(spec=EntList), "String"),
            (Mock(spec=EntList), True),
        ],
    )
    def test_insert_node_on_beam_invalid(self, mock_mesh_editor, beam, num, _):
        """
        Test inserting a node on a beam using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.insert_node_on_beam(beam, num)
        assert _("Invalid") in str(e.value)

    def test_insert_node_on_beam_negative(self, mock_mesh_editor, mock_object, _):
        """
        Test inserting a node on a beam using MeshEditor with negative num.
        """
        beam = Mock(spec=EntList)
        num = -1
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.insert_node_on_beam(beam, num)
        assert _("Invalid") in str(e.value)
        mock_object.InsertNodeOnBeam.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_move_nodes(self, mock_mesh_editor, mock_object, expected):
        """
        Test moving nodes using MeshEditor.
        """
        mock_object.MoveNodes.return_value = expected
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        vector = Mock(spec=Vector)
        vector.vector = Mock()
        loc = not expected
        result = mock_mesh_editor.move_nodes(nodes, vector, loc)
        assert isinstance(result, bool)
        mock_object.MoveNodes.assert_called_once_with(nodes.ent_list, vector.vector, loc)

    @pytest.mark.parametrize(
        "nodes, vector, loc",
        [
            (Mock(spec=EntList), Mock(spec=Vector), 1),
            (Mock(spec=EntList), Mock(spec=Vector), 1.0),
            (Mock(spec=EntList), Mock(spec=Vector), "False"),
            (Mock(spec=EntList), Mock(spec=Vector), None),
            (Mock(spec=EntList), 1, True),
            (Mock(spec=EntList), 1.0, True),
            (Mock(spec=EntList), "True", True),
            (1, Mock(spec=Vector), True),
            (1.0, Mock(spec=Vector), True),
            (True, Mock(spec=Vector), True),
            ("String", Mock(spec=Vector), True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_move_nodes_invalid(self, mock_mesh_editor, mock_object, nodes, vector, loc, _):
        """
        Test moving nodes using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.move_nodes(nodes, vector, loc)
        assert _("Invalid") in str(e.value)
        mock_object.MoveNodes.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_align_nodes(self, mock_mesh_editor, mock_object, expected):
        """
        Test aligning nodes using MeshEditor.
        """
        mock_object.AlignNodes.return_value = expected
        node1 = Mock(spec=EntList)
        node1.ent_list = Mock()
        node2 = Mock(spec=EntList)
        node2.ent_list = Mock()
        to_align = Mock(spec=EntList)
        to_align.ent_list = Mock()
        result = mock_mesh_editor.align_nodes(node1, node2, to_align)
        assert isinstance(result, bool)
        mock_object.AlignNodes.assert_called_once_with(
            node1.ent_list, node2.ent_list, to_align.ent_list
        )

    @pytest.mark.parametrize(
        "node1, node2, to_align",
        [
            (1, Mock(spec=EntList), True),
            (1.0, Mock(spec=EntList), True),
            ("String", Mock(spec=EntList), True),
            (True, Mock(spec=EntList), True),
            (Mock(spec=EntList), 1, True),
            (Mock(spec=EntList), 1.0, True),
            (Mock(spec=EntList), "String", True),
            (Mock(spec=EntList), True, True),
            (Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), "String"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_align_nodes_invalid(self, mock_mesh_editor, mock_object, node1, node2, to_align, _):
        """
        Test aligning nodes using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.align_nodes(node1, node2, to_align)
        assert _("Invalid") in str(e.value)
        mock_object.AlignNodes.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_smooth_nodes(self, mock_mesh_editor, mock_object, expected):
        """
        Test smoothing nodes using MeshEditor.
        """
        mock_object.SmoothNodes.return_value = expected
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        feat_edge = True
        result = mock_mesh_editor.smooth_nodes(nodes, feat_edge)
        assert isinstance(result, bool)
        mock_object.SmoothNodes.assert_called_once_with(nodes.ent_list, feat_edge)

    @pytest.mark.parametrize(
        "nodes, feat",
        [
            (1, True),
            (1.0, True),
            ("String", True),
            (True, True),
            (Mock(spec=EntList), None),
            (Mock(spec=EntList), 1),
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), "String"),
        ],
    )
    def test_smooth_nodes_invalid(self, mock_mesh_editor, mock_object, nodes, feat, _):
        """
        Test smoothing nodes using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.smooth_nodes(nodes, feat)
        assert _("Invalid") in str(e.value)
        mock_object.SmoothNodes.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_orient(self, mock_mesh_editor, mock_object, expected):
        """
        Test orienting nodes using MeshEditor.
        """
        mock_object.Orient.return_value = expected
        fusion = True
        result = mock_mesh_editor.orient(fusion)
        assert isinstance(result, bool)
        mock_object.Orient.assert_called_once_with(fusion)

    @pytest.mark.parametrize("fusion", [None, 1, 1.0, "String"])
    def test_orient_invalid(self, mock_mesh_editor, mock_object, fusion, _):
        """
        Test orienting nodes using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.orient(fusion)
        assert _("Invalid") in str(e.value)
        mock_object.Orient.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_flip_normals(self, mock_mesh_editor, mock_object, expected):
        """
        Test flipping normals using MeshEditor.
        """
        mock_object.FlipNormals.return_value = expected
        tris = Mock(spec=EntList)
        tris.ent_list = Mock()
        result = mock_mesh_editor.flip_normals(tris)
        assert isinstance(result, bool)
        mock_object.FlipNormals.assert_called_once_with(tris.ent_list)

    @pytest.mark.parametrize("tris", [1, 1.0, "String", True])
    def test_flip_normals_invalid(self, mock_mesh_editor, mock_object, tris, _):
        """
        Test flipping normals using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.flip_normals(tris)
        assert _("Invalid") in str(e.value)
        mock_object.FlipNormals.assert_not_called()

    @pytest.mark.parametrize("expected", [1, 2, 3])
    def test_align_normals(self, mock_mesh_editor, mock_object, expected):
        """
        Test aligning normals with MeshEditor
        """
        mock_object.AlignNormals.return_value = expected
        seed_tri = Mock(spec=EntList)
        seed_tri.ent_list = Mock()
        tris = Mock(spec=EntList)
        tris.ent_list = Mock()
        result = mock_mesh_editor.align_normals(seed_tri, tris)
        assert isinstance(result, int)
        mock_object.AlignNormals.assert_called_once_with(seed_tri.ent_list, tris.ent_list)

    @pytest.mark.parametrize(
        "seed_tri, tris",
        [
            (1, Mock(spec=EntList)),
            (1.0, Mock(spec=EntList)),
            ("String", Mock(spec=EntList)),
            (True, Mock(spec=EntList)),
            (Mock(spec=EntList), 1),
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), "String"),
        ],
    )
    def test_align_normals_invalid(self, mock_mesh_editor, mock_object, seed_tri, tris, _):
        """
        Test aligning normals using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.align_normals(seed_tri, tris)
        assert _("Invalid") in str(e.value)
        mock_object.AlignNormals.assert_not_called()

    @pytest.mark.parametrize("fill_hole, expected", [(None, 1), (1, 2), (2, 3)])
    def test_fill_hole(self, mock_mesh_editor, mock_object, fill_hole, expected):
        """
        Test filling hole with MeshEditor
        """
        mock_object.FillHole.return_value = expected
        mock_object.FillHole2.return_value = expected + 1
        tri = Mock(spec=EntList)
        tri.ent_list = Mock()
        result = mock_mesh_editor.fill_hole(tri, fill_hole)
        if fill_hole is None:
            assert isinstance(result, int)
            assert result == expected
            mock_object.FillHole.assert_called_once_with(tri.ent_list)
        else:
            assert isinstance(result, int)
            assert result == expected + 1
            mock_object.FillHole2.assert_called_once_with(tri.ent_list, fill_hole)

    @pytest.mark.parametrize(
        "tri, fill_hole",
        [
            (1, None),
            (1.0, None),
            ("String", None),
            (True, None),
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), "String"),
            (Mock(spec=EntList), True),
        ],
    )
    def test_fill_hole_invalid(self, mock_mesh_editor, mock_object, tri, fill_hole, _):
        """
        Test filling a hole using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.fill_hole(tri, fill_hole)
        assert _("Invalid") in str(e.value)
        mock_object.FillHole.assert_not_called()
        mock_object.FillHole2.assert_not_called()

    @pytest.mark.parametrize("expected", [1, 2, 3])
    def test_fill_hole_from_nodes(self, mock_mesh_editor, mock_object, expected):
        """
        Test preferred nodes-based fill hole with MeshEditor
        """
        mock_object.FillHoleFromNodes.return_value = expected
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        result = mock_mesh_editor.fill_hole_from_nodes(nodes)
        assert isinstance(result, int)
        assert result == expected
        mock_object.FillHoleFromNodes.assert_called_once_with(nodes.ent_list)

    def test_fill_hole_from_nodes_none(self, mock_mesh_editor, mock_object):
        """
        Test preferred nodes-based fill hole with None input (optional dispatch)
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            expected = 5
            mock_object.FillHoleFromNodes.return_value = expected
            result = mock_mesh_editor.fill_hole_from_nodes(None)
            assert isinstance(result, int)
            assert result == expected
            mock_object.FillHoleFromNodes.assert_called_once_with(mock_func())

    @pytest.mark.parametrize("nodes", [1, 1.0, "String", True])
    def test_fill_hole_from_nodes_invalid(self, mock_mesh_editor, mock_object, nodes, _):
        """
        Test preferred nodes-based fill hole invalid arguments
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.fill_hole_from_nodes(nodes)
        assert _("Invalid") in str(e.value)
        mock_object.FillHoleFromNodes.assert_not_called()

    @pytest.mark.parametrize("smooth, expected", [(True, 1), (True, 2), (False, 3)])
    def test_fill_hole_from_triangles(self, mock_mesh_editor, mock_object, smooth, expected):
        """
        Test preferred triangles-based fill hole with MeshEditor
        """
        mock_object.FillHoleFromTriangles.return_value = expected
        triangles = Mock(spec=EntList)
        triangles.ent_list = Mock()
        result = mock_mesh_editor.fill_hole_from_triangles(triangles, smooth)
        assert isinstance(result, int)
        assert result == expected
        # COM now expects a boolean smoothing flag; ints map with (value != 2)
        mock_object.FillHoleFromTriangles.assert_called_once_with(triangles.ent_list, smooth)

    @pytest.mark.parametrize("value, expected_bool", [(True, True), (False, False)])
    def test_fill_hole_from_triangles_bool(
        self, mock_mesh_editor, mock_object, value, expected_bool, _
    ):
        """Test boolean smoothing flag is forwarded to COM as-is."""
        mock_object.FillHoleFromTriangles.return_value = 11
        triangles = Mock(spec=EntList)
        triangles.ent_list = Mock()
        result = mock_mesh_editor.fill_hole_from_triangles(triangles, value)
        assert isinstance(result, int)
        assert result == 11
        mock_object.FillHoleFromTriangles.assert_called_once_with(triangles.ent_list, expected_bool)

    @pytest.mark.parametrize("value", [("BENT",)])  # string not accepted
    def test_fill_hole_from_triangles_invalid_enum_string(
        self, mock_mesh_editor, mock_object, value, _
    ):
        """Invalid string input should raise a TypeError and not call COM."""
        with pytest.raises(TypeError):
            mock_mesh_editor.fill_hole_from_triangles(Mock(spec=EntList), value)
        mock_object.FillHoleFromTriangles.assert_not_called()

    # Enum is no longer supported; keep a simple int mapping test via legacy path removed

    def test_fill_hole_from_triangles_none(self, mock_mesh_editor, mock_object):
        """
        Test preferred triangles-based fill hole with None tri list (optional dispatch)
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            expected = 7
            fill_type = True
            mock_object.FillHoleFromTriangles.return_value = expected
            result = mock_mesh_editor.fill_hole_from_triangles(None, fill_type)
            assert isinstance(result, int)
            assert result == expected
            mock_object.FillHoleFromTriangles.assert_called_once_with(mock_func(), True)

    @pytest.mark.parametrize(
        "triangles, fill_type",
        [
            (1, 0),
            (1.0, 0),
            ("String", 0),
            (Mock(spec=EntList), None),
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), "String"),
            # bool is accepted now for smoothing control
        ],
    )
    def test_fill_hole_from_triangles_invalid(
        self, mock_mesh_editor, mock_object, triangles, fill_type, _
    ):
        """
        Test preferred triangles-based fill hole invalid arguments
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.fill_hole_from_triangles(triangles, fill_type)
        assert _("Invalid") in str(e.value)
        mock_object.FillHoleFromTriangles.assert_not_called()

    @pytest.mark.parametrize("property_value", [Mock(spec=Property), None])
    def test_create_tet(self, mock_mesh_editor, mock_object, property_value):
        """
        Test creating a tetrahedron using MeshEditor.
        """

        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            mock_object.CreateTet.return_value = 1
            node1 = Mock(spec=EntList)
            node1.ent_list = Mock()
            node2 = Mock(spec=EntList)
            node2.ent_list = Mock()
            node3 = Mock(spec=EntList)
            node3.ent_list = Mock()
            node4 = Mock(spec=EntList)
            node4.ent_list = Mock()
            if property_value is not None:
                property_value.prop = Mock()
            result = mock_mesh_editor.create_tet(node1, node2, node3, node4, property_value)
            assert isinstance(result, EntList)
            assert result.ent_list == 1
            if property_value is not None:
                mock_object.CreateTet.assert_called_once_with(
                    node1.ent_list,
                    node2.ent_list,
                    node3.ent_list,
                    node4.ent_list,
                    property_value.prop,
                )
            else:
                mock_object.CreateTet.assert_called_once_with(
                    node1.ent_list, node2.ent_list, node3.ent_list, node4.ent_list, mock_func()
                )

    @pytest.mark.parametrize(
        "node1, node2, node3, node4, prop",
        [
            (1, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (1.0, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (
                "String",
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=Property),
            ),
            (True, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), 1, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), 1.0, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (
                Mock(spec=EntList),
                "String",
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=Property),
            ),
            (Mock(spec=EntList), True, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0, Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, Mock(spec=EntList), Mock(spec=Property)),
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                "string",
                Mock(spec=EntList),
                Mock(spec=Property),
            ),
            (Mock(spec=EntList), Mock(spec=EntList), True, Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1.0, Mock(spec=Property)),
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                "String",
                Mock(spec=Property),
            ),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), True, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1.0),
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                "String",
            ),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_create_tet_invalid(
        self, mock_mesh_editor, mock_object, node1, node2, node3, node4, prop, _
    ):
        """
        Test creating a tetrahedron using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.create_tet(node1, node2, node3, node4, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateTet.assert_not_called()

    @pytest.mark.parametrize("property_value", [Mock(spec=Property), None])
    def test_create_tri(self, mock_mesh_editor, mock_object, property_value):
        """
        Test creating a triangle using MeshEditor.
        """

        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            mock_object.CreateTri.return_value = 1
            node1 = Mock(spec=EntList)
            node1.ent_list = Mock()
            node2 = Mock(spec=EntList)
            node2.ent_list = Mock()
            node3 = Mock(spec=EntList)
            node3.ent_list = Mock()
            if property_value is not None:
                property_value.prop = Mock()
            result = mock_mesh_editor.create_tri(node1, node2, node3, property_value)
            assert isinstance(result, EntList)
            assert result.ent_list == 1
            if property_value is not None:
                mock_object.CreateTri.assert_called_once_with(
                    node1.ent_list, node2.ent_list, node3.ent_list, property_value.prop
                )
            else:
                mock_object.CreateTri.assert_called_once_with(
                    node1.ent_list, node2.ent_list, node3.ent_list, mock_func()
                )

    @pytest.mark.parametrize(
        "node1, node2, node3, prop",
        [
            (1, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (1.0, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            ("String", Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (True, Mock(spec=EntList), Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), 1, Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), 1.0, Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), "String", Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), True, Mock(spec=EntList), Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), "String", Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), True, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), "String"),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_create_tri_invalid(self, mock_mesh_editor, mock_object, node1, node2, node3, prop, _):
        """
        Test creating a triangle using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.create_tri(node1, node2, node3, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateTri.assert_not_called()

    @pytest.mark.parametrize(
        "tet_ref_layer, num_layer, refine_surface, surface_edge_length, expected",
        [(1, 2, True, 1.5, True), (2, 3, False, 2.0, False), (3, 4, True, 3, True)],
    )
    # pylint: disable-next=R0913, R0917
    def test_refine_tetras(
        self,
        mock_mesh_editor,
        mock_object,
        tet_ref_layer,
        num_layer,
        refine_surface,
        surface_edge_length,
        expected,
    ):
        """
        Test refining tetrahedra using MeshEditor.
        """
        mock_object.RefineTetras.return_value = expected
        result = mock_mesh_editor.refine_tetras(
            tet_ref_layer, num_layer, refine_surface, surface_edge_length
        )
        assert isinstance(result, bool)
        assert result == expected
        mock_object.RefineTetras.assert_called_once_with(
            tet_ref_layer, num_layer, refine_surface, surface_edge_length
        )

    @pytest.mark.parametrize(
        "tet_ref_layer, num_layer, refine_surface, surface_edge_length",
        [
            (None, 2, True, 1.5),
            (1, None, True, 1.5),
            (1, 2, None, 1.5),
            (1, 2, True, None),
            ("String", 1, True, 1.5),
            (1, "String", True, 1.5),
            (1, 2, "String", 1.5),
            (1, 2, True, "String"),
            (1.0, 2, True, 1.5),
            (1, 2.0, True, 1.5),
            (1, 2, 3.0, 1.5),
            (True, 2, True, 1.5),
            (1, False, True, 1.5),
            (1, 2, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_refine_tetras_invalid(
        self,
        mock_mesh_editor,
        mock_object,
        tet_ref_layer,
        num_layer,
        refine_surface,
        surface_edge_length,
        _,
    ):
        """
        Test refining tetrahedra using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.refine_tetras(
                tet_ref_layer, num_layer, refine_surface, surface_edge_length
            )
        assert _("Invalid") in str(e.value)
        mock_object.RefineTetras.assert_not_called()

    @pytest.mark.parametrize("tet_ref_layer, num_layer", [(1, -2), (-1, 2), (-1, -2)])
    def test_refine_tetras_invalid_neg_num(
        self, mock_mesh_editor, mock_object, num_layer, tet_ref_layer, _
    ):
        """
        Test refining tetrahedra using MeshEditor with negative num_layer.
        """
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.refine_tetras(tet_ref_layer, num_layer, True, 1.5)
        assert _("Invalid") in str(e.value)
        mock_object.RefineTetras.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_refine_tetras_by_labels(self, mock_mesh_editor, mock_object, expected):
        """
        Test refining tetrahedra by labels using MeshEditor.
        """
        mock_object.RefineTetrasByLabels.return_value = expected
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        num_layer = 2
        isolated = True
        refine_surface = True
        surface_edge_length = 1.5
        result = mock_mesh_editor.refine_tetras_by_labels(
            nodes, num_layer, isolated, refine_surface, surface_edge_length
        )
        assert isinstance(result, bool)
        assert result == expected
        mock_object.RefineTetrasByLabels.assert_called_once_with(
            nodes.ent_list, num_layer, isolated, refine_surface, surface_edge_length
        )

    @pytest.mark.parametrize(
        "nodes, num_layer, isolated, refine_surface, surface_edge_length",
        [
            (None, 2, True, 1.5, 1.5),
            (Mock(spec=EntList), None, True, 1.5, 1.5),
            (Mock(spec=EntList), 2, None, 1.5, 1.5),
            (Mock(spec=EntList), 2, True, None, 1.5),
            (Mock(spec=EntList), 2, True, 1.5, None),
            ("String", Mock(spec=EntList), True, 1.5, 1.5),
            (Mock(spec=EntList), "String", True, 1.5, 1.5),
            (Mock(spec=EntList), Mock(spec=EntList), "String", 1.5, 1.5),
            (Mock(spec=EntList), Mock(spec=EntList), True, "String", 1.5),
            (Mock(spec=EntList), Mock(spec=EntList), True, 1.5, "String"),
            (1, Mock(spec=EntList), True, 1.5, True),
            (Mock(spec=EntList), 1, True, 1.5, True),
            (Mock(spec=EntList), Mock(spec=EntList), 1, 1.5, True),
            (Mock(spec=EntList), Mock(spec=EntList), True, 1.5, 1),
            (1.0, Mock(spec=EntList), True, 1.5, True),
            (Mock(spec=EntList), 1.0, True, 1.5, True),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0, 1.5, True),
            (Mock(spec=EntList), Mock(spec=EntList), True, 1.5, 1.0),
            (True, Mock(spec=EntList), True, 1.5, True),
            (Mock(spec=EntList), True, True, 1.5, True),
            (Mock(spec=EntList), Mock(spec=EntList), True, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_refine_tetras_by_labels_invalid(
        self,
        mock_mesh_editor,
        mock_object,
        nodes,
        num_layer,
        isolated,
        refine_surface,
        surface_edge_length,
        _,
    ):
        """
        Test refining tetrahedra by labels using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.refine_tetras_by_labels(
                nodes, num_layer, isolated, refine_surface, surface_edge_length
            )
        assert _("Invalid") in str(e.value)
        mock_object.RefineTetrasByLabels.assert_not_called()

    @pytest.mark.parametrize("num_layer", [-2, -1, -99])
    def test_refine_tetras_by_labels_invalid_neg_num(
        self, mock_mesh_editor, mock_object, num_layer, _
    ):
        """
        Test refining tetrahedra by labels using MeshEditor with negative num_layer.
        """
        nodes = Mock(spec=EntList)
        isolated = True
        refine_surface = True
        surface_edge_length = 1.5
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.refine_tetras_by_labels(
                nodes, num_layer, isolated, refine_surface, surface_edge_length
            )
        assert _("Invalid") in str(e.value)
        mock_object.RefineTetrasByLabels.assert_not_called()

    @pytest.mark.parametrize("property_value", [Mock(spec=Property), None])
    def test_create_wedge(self, mock_mesh_editor, mock_object, property_value):
        """
        Test creating a wedge using MeshEditor.
        """

        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            expected = Mock(spec=EntList)
            mock_object.CreateWedge.return_value = expected
            nodes1 = Mock(spec=EntList)
            nodes1.ent_list = Mock()
            nodes2 = Mock(spec=EntList)
            nodes2.ent_list = Mock()
            nodes3 = Mock(spec=EntList)
            nodes3.ent_list = Mock()
            nodes4 = Mock(spec=EntList)
            nodes4.ent_list = Mock()
            nodes5 = Mock(spec=EntList)
            nodes5.ent_list = Mock()
            nodes6 = Mock(spec=EntList)
            nodes6.ent_list = Mock()
            if property_value is not None:
                property_value.prop = Mock()
            result = mock_mesh_editor.create_wedge(
                nodes1, nodes2, nodes3, nodes4, nodes5, nodes6, property_value
            )
            assert isinstance(result, EntList)
            assert result.ent_list == expected
            if property_value is not None:
                mock_object.CreateWedge.assert_called_once_with(
                    nodes1.ent_list,
                    nodes2.ent_list,
                    nodes3.ent_list,
                    nodes4.ent_list,
                    nodes5.ent_list,
                    nodes6.ent_list,
                    property_value.prop,
                )
            else:
                mock_object.CreateWedge.assert_called_once_with(
                    nodes1.ent_list,
                    nodes2.ent_list,
                    nodes3.ent_list,
                    nodes4.ent_list,
                    nodes5.ent_list,
                    nodes6.ent_list,
                    mock_func(),
                )

    @pytest.mark.parametrize(
        "node1, node2, node3, node4, node5, node6, prop",
        [
            (
                x,
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=Property),
            )
            for x in [1, 1.0, "String", True]
        ]
        + [
            (
                Mock(spec=EntList),
                x,
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=Property),
            )
            for x in [1, 1.0, "String", True]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                x,
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=Property),
            )
            for x in [1, 1.0, "String", True]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                x,
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=Property),
            )
            for x in [1, 1.0, "String", True]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                x,
                Mock(spec=EntList),
                Mock(spec=Property),
            )
            for x in [1, 1.0, "String", True]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                x,
                Mock(spec=Property),
            )
            for x in [1, 1.0, "String", True]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                Mock(spec=EntList),
                x,
            )
            for x in [1, 1.0, "String", True]
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_create_wedge_invalid(
        self, mock_mesh_editor, mock_object, node1, node2, node3, node4, node5, node6, prop, _
    ):
        """
        Test creating a wedge using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.create_wedge(node1, node2, node3, node4, node5, node6, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateWedge.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_convert_wedges_to_tetras(self, mock_mesh_editor, mock_object, expected):
        """
        Test creating wedges to tetrahedra using MeshEditor.
        """
        mock_object.ConvertWedgesToTetras.return_value = expected
        wedges = Mock(spec=EntList)
        wedges.ent_list = Mock()
        num_layer = 2
        result = mock_mesh_editor.convert_wedges_to_tetras(wedges, num_layer)
        assert isinstance(result, bool)
        assert result is expected
        mock_object.ConvertWedgesToTetras.assert_called_once_with(wedges.ent_list, num_layer)

    @pytest.mark.parametrize(
        "wedges, num_layer",
        [
            (1, 2),
            (1.0, 2),
            ("String", 2),
            (True, 2),
            (Mock(spec=EntList), None),
            (Mock(spec=EntList), True),
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), "String"),
        ],
    )
    def test_convert_wedges_to_tetras_invalid(
        self, mock_mesh_editor, mock_object, wedges, num_layer, _
    ):
        """
        Test creating wedges to tetrahedra using MeshEditor.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.convert_wedges_to_tetras(wedges, num_layer)
        assert _("Invalid") in str(e.value)
        mock_object.ConvertWedgesToTetras.assert_not_called()

    @pytest.mark.parametrize("num_layer", [-2, -1, -99])
    def test_convert_wedges_to_tetras_neg_num(self, mock_mesh_editor, mock_object, num_layer, _):
        """
        Test creating wedges to tetrahedra using MeshEditor with negative num_layer.
        """
        wedges = Mock(spec=EntList)
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.convert_wedges_to_tetras(wedges, num_layer)
        assert _("Invalid") in str(e.value)
        mock_object.ConvertWedgesToTetras.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_create_beams(self, mock_mesh_editor, mock_object, expected):
        """
        Test creating beams using MeshEditor.
        """
        mock_object.CreateBeams.return_value = expected
        node1 = Mock(spec=EntList)
        node1.ent_list = Mock()
        node2 = Mock(spec=EntList)
        node2.ent_list = Mock()
        num_beams = 1
        prop = Mock(spec=Property)
        prop.prop = Mock()
        result = mock_mesh_editor.create_beams(node1, node2, num_beams, prop)
        assert isinstance(result, EntList)
        assert result.ent_list == expected
        mock_object.CreateBeams.assert_called_once_with(
            node1.ent_list, node2.ent_list, num_beams, prop.prop
        )

    @pytest.mark.parametrize(
        "node1, node2, num_beams, prop",
        [
            (1, Mock(spec=EntList), 1, Mock(spec=Property)),
            (1.0, Mock(spec=EntList), 1, Mock(spec=Property)),
            ("String", Mock(spec=EntList), 1, Mock(spec=Property)),
            (True, Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), 1, 1, Mock(spec=Property)),
            (Mock(spec=EntList), 1.0, 1, Mock(spec=Property)),
            (Mock(spec=EntList), "String", 1, Mock(spec=Property)),
            (Mock(spec=EntList), True, 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), None, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), "String", Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), True, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, 1),
            (Mock(spec=EntList), Mock(spec=EntList), 1, 1.0),
            (Mock(spec=EntList), Mock(spec=EntList), 1, "String"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_create_beams_invalid(
        self, mock_mesh_editor, mock_object, node1, node2, num_beams, prop, _
    ):
        """
        Test creating beams using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.create_beams(node1, node2, num_beams, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateBeams.assert_not_called()

    @pytest.mark.parametrize("num_beams", [-2, -1, -99])
    def test_create_beams_neg_num(self, mock_mesh_editor, mock_object, num_beams, _):
        """
        Test creating beams using MeshEditor with negative num_beams.
        """
        node1 = Mock(spec=EntList)
        node2 = Mock(spec=EntList)
        prop = Mock(spec=Property)
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.create_beams(node1, node2, num_beams, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateBeams.assert_not_called()

    def test_find_property(self, mock_mesh_editor, mock_object):
        """
        Test finding a property using MeshEditor.
        """
        prop = Mock(spec=Property)
        mock_object.FindProperty.return_value = prop
        prop_type = 1
        prop_id = 2
        result = mock_mesh_editor.find_property(prop_type, prop_id)
        assert isinstance(result, Property)
        assert result.prop == prop
        mock_object.FindProperty.assert_called_once_with(prop_type, prop_id)

    @pytest.mark.parametrize(
        "prop_type, prop_id",
        [
            (None, 2),
            (1.0, 2),
            ("String", 2),
            (True, 2),
            (1, None),
            (1, 1.0),
            (1, "String"),
            (1, True),
        ],
    )
    def test_find_property_invalid(self, mock_mesh_editor, mock_object, prop_type, prop_id, _):
        """
        Test finding a property using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.find_property(prop_type, prop_id)
        assert _("Invalid") in str(e.value)
        mock_object.FindProperty.assert_not_called()

    def test_delete(self, mock_mesh_editor, mock_object):
        """
        Test deleting a mesh using MeshEditor.
        """
        expected = Mock(spec=EntList)
        mock_object.Delete.return_value = expected
        mesh = Mock(spec=EntList)
        mesh.ent_list = Mock()
        result = mock_mesh_editor.delete(mesh)
        assert isinstance(result, EntList)
        assert result.ent_list == expected
        mock_object.Delete.assert_called_once_with(mesh.ent_list)

    @pytest.mark.parametrize("entity", [1, 1.0, "String", True])
    def test_delete_invalid(self, mock_mesh_editor, mock_object, entity, _):
        """
        Test deleting a mesh using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.delete(entity)
        assert _("Invalid") in str(e.value)
        mock_object.Delete.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_remesh_area(self, mock_mesh_editor, mock_object, expected):
        """
        Test remeshing an area using MeshEditor.
        """
        mock_object.RemeshArea2.return_value = expected
        tris = Mock(spec=EntList)
        tris.ent_list = Mock()
        size = 1.5
        imprint = True
        smooth = 0.5
        result = mock_mesh_editor.remesh_area(tris, size, imprint, smooth)
        assert isinstance(result, bool)
        assert result == expected

        mock_object.RemeshArea2.assert_called_once_with(tris.ent_list, size, imprint, smooth)

    @pytest.mark.parametrize(
        "tris, size, imprint, smooth",
        [
            (None, 1.5, True, True),
            (1, 1.5, True, True),
            (1.0, 1.5, True, True),
            ("String", 1.5, True, True),
            (True, 1.5, True, True),
            (Mock(spec=EntList), None, True, True),
            (Mock(spec=EntList), "String", True, True),
            (Mock(spec=EntList), True, True, True),
            (Mock(spec=EntList), 1.5, None, True),
            (Mock(spec=EntList), 1.5, 1, True),
            (Mock(spec=EntList), 1.5, 1.0, True),
            (Mock(spec=EntList), 1.5, "String", True),
            (Mock(spec=EntList), 1.5, True, None),
            (Mock(spec=EntList), 1.5, True, True),
            (Mock(spec=EntList), 1.5, True, False),
            (Mock(spec=EntList), 1.5, True, "String"),
            (Mock(spec=EntList), 1.5, True, None),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_remesh_area_invalid(
        self, mock_mesh_editor, mock_object, tris, size, imprint, smooth, _
    ):
        """
        Test remeshing an area using MeshEditor with invalid arguments.
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.remesh_area(tris, size, imprint, smooth)
        assert _("Invalid") in str(e.value)
        mock_object.RemeshArea2.assert_not_called()

    @pytest.mark.parametrize("expected", (1, 2, 3, 4))
    def test_match_nodes(self, mock_mesh_editor, mock_object, expected):
        """
        Test matching the nodes using MeshEditor
        """
        mock_object.MatchNodes.return_value = expected
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        tris = Mock(spec=EntList)
        tris.ent_list = Mock()
        layer = "LayerName"
        result = mock_mesh_editor.match_nodes(nodes, tris, layer)
        assert isinstance(result, int)
        assert result == expected
        mock_object.MatchNodes.assert_called_once_with(nodes.ent_list, tris.ent_list, layer)

    @pytest.mark.parametrize(
        "nodes, tris, layer",
        [
            (Mock(spec=EntList), Mock(spec=EntList), None),
            (Mock(spec=EntList), Mock(spec=EntList), 1),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), Mock(spec=EntList), True),
            (Mock(spec=EntList), 1, "String"),
            (Mock(spec=EntList), 1.0, "String"),
            (Mock(spec=EntList), True, "String"),
            (Mock(spec=EntList), "String", "String"),
            (1, Mock(spec=EntList), "String"),
            (1.0, Mock(spec=EntList), "String"),
            (True, Mock(spec=EntList), "String"),
            ("String", Mock(spec=EntList), "String"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_match_nodes_invalid(self, mock_mesh_editor, mock_object, nodes, tris, layer, _):
        """
        Test matching the nodes using MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.match_nodes(nodes, tris, layer)
        assert _("Invalid") in str(e.value)
        mock_object.RemeshArea2.assert_not_called()

    @pytest.mark.parametrize("expected, prop", [(1, None), (10, Mock(spec=Property))])
    def test_make_region(self, mock_mesh_editor, mock_object, expected, prop):
        """
        Test making geometric regions using MeshEditor
        """
        mock_object.MakeRegion2.return_value = expected
        mock_object.MakeRegion.return_value = expected
        tol = 1.5
        is_angular = False
        mesh = True
        test_prop = None
        if prop is not None:
            prop.prop = Mock()
            test_prop = prop.prop
        result = mock_mesh_editor.make_region(tol, is_angular, mesh, prop)
        assert isinstance(result, int)
        assert result == expected
        if prop is None:
            mock_object.MakeRegion.assert_called_once_with(tol, is_angular)
        else:
            mock_object.MakeRegion2.assert_called_once_with(tol, is_angular, mesh, test_prop)

    @pytest.mark.parametrize(
        "tol, is_angular, mesh, prop",
        [
            (None, True, False, Mock(spec=Property)),
            (False, True, False, Mock(spec=Property)),
            ("String", True, False, Mock(spec=Property)),
            (5.6, None, False, Mock(spec=Property)),
            (5.6, 1, False, Mock(spec=Property)),
            (5.6, 1.0, False, Mock(spec=Property)),
            (5.6, "String", False, Mock(spec=Property)),
            (5.6, True, None, Mock(spec=Property)),
            (5.6, True, 1, Mock(spec=Property)),
            (5.6, True, 1.0, Mock(spec=Property)),
            (5.6, True, "String", Mock(spec=Property)),
            (5.6, True, False, 1),
            (5.6, True, False, 1.0),
            (5.6, True, False, "String"),
            (5.6, True, False, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_make_region_invalid(
        self, mock_mesh_editor, mock_object, tol, is_angular, mesh, prop, _
    ):
        """
        Test making geometric regions using MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.make_region(tol, is_angular, mesh, prop)
        assert _("Invalid") in str(e.value)
        mock_object.MakeRegion.assert_not_called()
        mock_object.MakeRegion2.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_move_beam_node(self, mock_mesh_editor, mock_object, expected):
        """
        Test moving a beam node using MeshEditor
        """
        mock_object.MoveBeamNode.return_value = expected
        moving_node = Mock(spec=EntList)
        moving_node.ent_list = Mock()
        target = Mock(spec=Vector)
        target.vector = Mock()
        result = mock_mesh_editor.move_beam_node(moving_node, target)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.MoveBeamNode.assert_called_once_with(moving_node.ent_list, target.vector)

    @pytest.mark.parametrize(
        "moving_node, target",
        [
            (1, Mock(spec=Vector)),
            (1.0, Mock(spec=Vector)),
            (True, Mock(spec=Vector)),
            ("String", Mock(spec=Vector)),
            (Mock(spec=EntList), 1),
            (Mock(spec=EntList), 1.0),
            (Mock(spec=EntList), True),
            (Mock(spec=EntList), "String"),
        ],
    )
    def test_move_beam_node_invalid(self, mock_mesh_editor, mock_object, moving_node, target, _):
        """
        Test moving beam node using MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.move_beam_node(moving_node, target)
        assert _("Invalid") in str(e.value)
        mock_object.MoveBeamNode.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_move_node_to_edge(self, mock_mesh_editor, mock_object, expected):
        """
        Test moving a node to a triangle edge
        """
        node = Mock(spec=EntList)
        node.ent_list = Mock()
        edge1 = Mock(spec=EntList)
        edge1.ent_list = Mock()
        edge2 = Mock(spec=EntList)
        edge2.ent_list = Mock()
        param = 0.5
        mock_object.MoveNodeToEdge.return_value = expected
        result = mock_mesh_editor.move_node_to_edge(node, edge1, edge2, param)
        assert isinstance(result, bool)
        assert result is expected
        mock_object.MoveNodeToEdge.assert_called_once_with(
            node.ent_list, edge1.ent_list, edge2.ent_list, param
        )

    @pytest.mark.parametrize(
        "node, edge1, edge2, loc",
        [
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), None),
            ("String", Mock(spec=EntList), Mock(spec=EntList), 0),
            (Mock(spec=EntList), "String", Mock(spec=EntList), 0),
            (Mock(spec=EntList), Mock(spec=EntList), "String", 0),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), "String"),
            (1, Mock(spec=EntList), Mock(spec=EntList), 0),
            (Mock(spec=EntList), 2, Mock(spec=EntList), 0),
            (Mock(spec=EntList), Mock(spec=EntList), 3, 0),
            (4.0, Mock(spec=EntList), Mock(spec=EntList), 0),
            (Mock(spec=EntList), 5.0, Mock(spec=EntList), 0),
            (Mock(spec=EntList), Mock(spec=EntList), 6.0, 0),
            (True, Mock(spec=EntList), Mock(spec=EntList), 0),
            (Mock(spec=EntList), True, Mock(spec=EntList), 0),
            (Mock(spec=EntList), Mock(spec=EntList), True, 0),
            (Mock(spec=EntList), Mock(spec=EntList), Mock(spec=EntList), True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_move_node_to_edge_invalid(
        self, mock_mesh_editor, mock_object, node, edge1, edge2, loc, _
    ):
        """
        Test moving a node to a triangle edge with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.move_node_to_edge(node, edge1, edge2, loc)
        assert _("Invalid") in str(e.value)
        mock_object.MoveNodeToEdge.assert_not_called()

    @pytest.mark.parametrize("loc", [-1, 1.1])
    def test_move_node_to_edge_range(self, mock_mesh_editor, mock_object, loc, _):
        """
        Test moving a node to a triangle edge with invalid range
        """
        node = Mock(spec=EntList)
        edge1 = Mock(spec=EntList)
        edge2 = Mock(spec=EntList)
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.move_node_to_edge(node, edge1, edge2, loc)
        assert _("Invalid") in str(e.value)
        mock_object.MoveNodeToEdge.assert_not_called()

    @pytest.mark.parametrize("smooth", [-1, 1.1])
    def test_remesh_area_smoothing(self, mock_mesh_editor, mock_object, smooth, _):
        """
        Test remeshing area with invalid smoothing factor
        """
        node = Mock(spec=EntList)
        size = 1
        imprint = True
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.remesh_area(node, size, imprint, smooth)
        assert _("Invalid") in str(e.value)
        mock_object.RemeshArea.assert_not_called()

    def test_create_beams_by_points(self, mock_mesh_editor, mock_object):
        """
        Test creating beams by points with MeshEditor
        """
        expected = Mock(spec=EntList)
        pt1 = Mock(spec=Vector)
        pt1.vector = Mock()
        pt2 = Mock(spec=Vector)
        pt2.vector = Mock()
        num = 3
        prop = Mock(spec=Property)
        prop.prop = Mock()
        mock_object.CreateBeamsByPoints.return_value = expected
        result = mock_mesh_editor.create_beams_by_points(pt1, pt2, num, prop)
        assert result.ent_list == expected
        mock_object.CreateBeamsByPoints.assert_called_once_with(
            pt1.vector, pt2.vector, num, prop.prop
        )

    @pytest.mark.parametrize(
        "pt1, pt2, num, prop",
        [
            (None, Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), None, 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), None, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, None),
            (1.0, Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), 1.0, 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, 1.0),
            (1, Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), 1, 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, 1),
            (True, Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), True, 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), True, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, True),
            ("String", Mock(spec=EntList), 1, Mock(spec=Property)),
            (Mock(spec=EntList), "String", 1, Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), "String", Mock(spec=Property)),
            (Mock(spec=EntList), Mock(spec=EntList), 1, "String"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_create_beams_by_points_invalid(
        self, mock_mesh_editor, mock_object, pt1, pt2, num, prop, _
    ):
        """
        Test creating beams by points with MeshEditor with invalid values
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.create_beams_by_points(pt1, pt2, num, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateBeamsByPoints.assert_not_called()

    @pytest.mark.parametrize("num", [-1, -5, -99])
    def test_create_beams_by_points_neg_num(self, mock_mesh_editor, mock_object, num, _):
        """
        Test creating beams by points with MeshEditor with invalid num
        """
        pt1 = Mock(spec=Vector)
        pt2 = Mock(spec=Vector)
        prop = Mock(spec=Property)
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.create_beams_by_points(pt1, pt2, num, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateBeamsByPoints.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_project_mesh(self, mock_mesh_editor, mock_object, expected):
        """
        Test projecting mesh with MeshEditor
        """
        tris = Mock(spec=EntList)
        tris.ent_list = Mock()
        mock_object.ProjectMesh.return_value = expected
        result = mock_mesh_editor.project_mesh(tris)
        assert result is expected
        mock_object.ProjectMesh.assert_called_once_with(tris.ent_list)

    @pytest.mark.parametrize("tris", [(None, True, 1, 1.0, "String")])
    def test_project_mesh_invalid(self, mock_mesh_editor, mock_object, tris, _):
        """
        Test projecting mesh with MeshEditor with invalid values
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.project_mesh(tris)
        assert _("Invalid") in str(e.value)
        mock_object.ProjectMesh.assert_not_called()

    @pytest.mark.parametrize(
        "property_value, expected",
        [(Mock(spec=Property), 1), (None, 2), (Mock(spec=Property), 66), (Mock(spec=Property), 8)],
    )
    def test_convert_to_beams(self, mock_mesh_editor, mock_object, property_value, expected):
        """
        Test converting mesh to beam elements
        """

        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            start_node = Mock(spec=EntList)
            start_node.ent_list = Mock()
            if property_value is not None:
                property_value.prop = Mock()
            junction = True
            num_branch = 1
            mock_object.ConvertToBeams.return_value = expected
            result = mock_mesh_editor.convert_to_beams(
                start_node, property_value, junction, num_branch
            )
            assert result is expected
            assert isinstance(result, int)
            if property_value is not None:
                mock_object.ConvertToBeams.assert_called_once_with(
                    start_node.ent_list, property_value.prop, junction, num_branch
                )
            else:
                mock_object.ConvertToBeams.assert_called_once_with(
                    start_node.ent_list, mock_func(), junction, num_branch
                )

    @pytest.mark.parametrize(
        "start_node, prop, junction, num_branch",
        [
            (Mock(spec=EntList), Mock(spec=Property), None, 1),
            (Mock(spec=EntList), Mock(spec=Property), True, None),
            (True, Mock(spec=Property), True, 1),
            (Mock(spec=EntList), True, True, 1),
            (Mock(spec=EntList), Mock(spec=Property), True, True),
            ("String", Mock(spec=Property), True, 1),
            (Mock(spec=EntList), "String", True, 1),
            (Mock(spec=EntList), Mock(spec=Property), "String", 1),
            (Mock(spec=EntList), Mock(spec=Property), True, "String"),
            (1.0, Mock(spec=Property), True, 1),
            (Mock(spec=EntList), 1.0, True, 1),
            (Mock(spec=EntList), Mock(spec=Property), 1.0, 1),
            (Mock(spec=EntList), Mock(spec=Property), True, 1.0),
            (1, Mock(spec=Property), True, 1),
            (Mock(spec=EntList), 1, True, 1),
            (Mock(spec=EntList), Mock(spec=Property), 1, 1),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_convert_to_beams_invalid(
        self, mock_mesh_editor, mock_object, start_node, prop, junction, num_branch, _
    ):
        """
        Test converting mesh to beam elements with invalid values
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.convert_to_beams(start_node, prop, junction, num_branch)
        assert _("Invalid") in str(e.value)
        mock_object.ConvertToBeams.assert_not_called()

    @pytest.mark.parametrize("num_branch", [-1, -5, -99])
    def test_convert_to_beams_neg_num(self, mock_mesh_editor, mock_object, num_branch, _):
        """
        Test converting mesh to beam elements with invalid num_branches
        """
        start_node = Mock(spec=EntList)
        prop = Mock(spec=Property)
        junction = True
        with pytest.raises(ValueError) as e:
            mock_mesh_editor.convert_to_beams(start_node, prop, junction, num_branch)
        assert _("Invalid") in str(e.value)
        mock_object.ConvertToBeams.assert_not_called()

    @pytest.mark.parametrize("expected", [1, 5, 7])
    def test_contact_stitch_interface(self, mock_mesh_editor, mock_object, expected):
        """
        Test stitching contact interface with MeshEditor
        """
        merge_tol = 0.5
        mock_object.ContactStitchInterface.return_value = expected
        result = mock_mesh_editor.contact_stitch_interface(merge_tol)
        assert result is expected
        assert isinstance(result, int)
        mock_object.ContactStitchInterface.assert_called_once_with(merge_tol)

    @pytest.mark.parametrize("merge_tol", [None, "String", True])
    def test_contact_stitch_interface_invalid(self, mock_mesh_editor, mock_object, merge_tol, _):
        """
        Test stitching contact interface with MeshEditor with invalid arguments
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.contact_stitch_interface(merge_tol)
        assert _("Invalid") in str(e.value)
        mock_object.ContactStitchInterface.assert_not_called()

    @pytest.mark.parametrize("expected", [1, 2, 0])
    def test_view_contact_stitch(self, mock_mesh_editor, mock_object, expected):
        """
        Test viewing contact surface layer
        """
        merge_tol = 0.5
        mock_object.ViewContactStitch.return_value = expected
        result = mock_mesh_editor.view_contact_stitch(merge_tol)
        assert result is expected
        assert isinstance(result, int)
        mock_object.ViewContactStitch.assert_called_once_with(merge_tol)

    @pytest.mark.parametrize("merge_tol", [None, "String", True])
    def test_view_contact_stitch_invalid(self, mock_mesh_editor, mock_object, merge_tol, _):
        """
        Test viewing contact surface layer with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.view_contact_stitch(merge_tol)
        assert _("Invalid") in str(e.value)
        mock_object.ViewContactStitch.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_cut_triangles_by_plane(self, mock_mesh_editor, mock_object, expected):
        """
        Test cutting triangles by plane
        """
        plane_normal = Mock(spec=Vector)
        plane_normal.vector = Mock()
        ref_point = Mock(spec=Vector)
        ref_point.vector = Mock()
        fill = True
        smooth = True
        mock_object.CutTrianglesByPlane.return_value = expected
        result = mock_mesh_editor.cut_triangles_by_plane(plane_normal, ref_point, fill, smooth)
        assert isinstance(result, bool)
        assert result is expected
        mock_object.CutTrianglesByPlane.assert_called_once_with(
            plane_normal.vector, ref_point.vector, fill, smooth
        )

    @pytest.mark.parametrize(
        "plane_normal, ref_point, fill, smooth",
        [
            (Mock(spec=Vector), Mock(spec=Vector), None, True),
            (Mock(spec=Vector), Mock(spec=Vector), True, None),
            (1, Mock(spec=Vector), True, True),
            (Mock(spec=Vector), 1, True, True),
            (Mock(spec=Vector), Mock(spec=Vector), 1, True),
            (Mock(spec=Vector), Mock(spec=Vector), True, 1),
            (1.0, Mock(spec=Vector), True, True),
            (Mock(spec=Vector), 1.0, True, True),
            (Mock(spec=Vector), Mock(spec=Vector), 1.0, True),
            (Mock(spec=Vector), Mock(spec=Vector), True, 1.0),
            ("String", Mock(spec=Vector), True, True),
            (Mock(spec=Vector), "String", True, True),
            (Mock(spec=Vector), Mock(spec=Vector), "String", True),
            (Mock(spec=Vector), Mock(spec=Vector), True, "String"),
            (True, Mock(spec=Vector), True, True),
            (Mock(spec=Vector), True, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_cut_triangles_by_plane_invalid(
        self, mock_mesh_editor, mock_object, plane_normal, ref_point, fill, smooth, _
    ):
        """
        Test cutting triangles by plane with invalid input
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.cut_triangles_by_plane(plane_normal, ref_point, fill, smooth)
        assert _("Invalid") in str(e.value)
        mock_object.CutTrianglesByPlane.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_offset_triangles(self, mock_mesh_editor, mock_object, expected):
        """
        Test offsetting triangles by a given distance with MeshEditor
        """
        offset_tri = Mock(spec=EntList)
        offset_tri.ent_list = Mock()
        offset_dist = 2.5
        falloff_dist = 1.5
        smooth_nb = True
        mock_object.OffsetTriangles.return_value = expected
        result = mock_mesh_editor.offset_triangles(offset_tri, offset_dist, falloff_dist, smooth_nb)
        assert result is expected
        assert isinstance(result, bool)
        mock_object.OffsetTriangles.assert_called_once_with(
            offset_tri.ent_list, offset_dist, falloff_dist, smooth_nb
        )

    @pytest.mark.parametrize(
        "offset_tri, offset_dist, falloff_dist, smooth_nb",
        [
            (Mock(spec=EntList), None, 1.5, True),
            (Mock(spec=EntList), 1.5, None, True),
            (Mock(spec=EntList), 1.5, 1.5, None),
            ("String", 1.5, 1.5, True),
            (Mock(spec=EntList), "String", 1.5, True),
            (Mock(spec=EntList), 1.5, "String", True),
            (Mock(spec=EntList), 1.5, 1.5, "String"),
            (1, 1.5, 1.5, True),
            (Mock(spec=EntList), 1.5, 1.5, 1),
            (1.0, 1.5, 1.5, True),
            (Mock(spec=EntList), 1.5, 1.5, 1.0),
            (True, 1.5, 1.5, True),
            (Mock(spec=EntList), True, 1.5, True),
            (Mock(spec=EntList), 1.5, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_offset_triangles_invalid(
        self, mock_mesh_editor, mock_object, offset_tri, offset_dist, falloff_dist, smooth_nb, _
    ):
        """
        Test offsetting triangles by a given distance with MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.offset_triangles(offset_tri, offset_dist, falloff_dist, smooth_nb)
        assert _("Invalid") in str(e.value)
        mock_object.OffsetTriangles.assert_not_called()

    @pytest.mark.parametrize(
        "property_value, expected", [(Mock(spec=Property), True), (None, False)]
    )
    def test_extrude_triangles(self, mock_mesh_editor, mock_object, property_value, expected):
        """
        Test extruding triangles with MeshEditor
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            offset_tri = Mock(spec=EntList)
            offset_tri.ent_list = Mock()
            dist = 1.5
            scale = 1.5
            smooth_nb = True
            create_new_body = False
            if property_value is not None:
                property_value.prop = Mock()
            mock_object.ExtrudeTriangles.return_value = expected
            result = mock_mesh_editor.extrude_triangles(
                offset_tri, dist, scale, smooth_nb, create_new_body, property_value
            )
            assert result is expected
            assert isinstance(result, bool)
            if property_value is not None:
                mock_object.ExtrudeTriangles.assert_called_once_with(
                    offset_tri.ent_list,
                    dist,
                    scale,
                    smooth_nb,
                    create_new_body,
                    property_value.prop,
                )
            else:
                mock_object.ExtrudeTriangles.assert_called_once_with(
                    offset_tri.ent_list, dist, scale, smooth_nb, create_new_body, mock_func()
                )

    @pytest.mark.parametrize(
        "offset_tri, dist, scale, smooth_nb, create_new_body, prop",
        [
            (Mock(spec=EntList), None, 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, None, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, None, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, None, Mock(spec=Property)),
            (1, 1.5, 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, 1, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, 1, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, True, 1),
            (1.0, 1.5, 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, 1.0, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, 1.0, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, True, 1.0),
            ("String", 1.5, 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), "String", 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, "String", True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, "String", True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, "String", Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, True, "String"),
            (True, 1.5, 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), True, 3.5, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, True, True, True, Mock(spec=Property)),
            (Mock(spec=EntList), 1.5, 3.5, True, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_extrude_triangles_invalid(
        self,
        mock_mesh_editor,
        mock_object,
        offset_tri,
        dist,
        scale,
        smooth_nb,
        create_new_body,
        prop,
        _,
    ):
        """
        Test extruding triangles with MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.extrude_triangles(
                offset_tri, dist, scale, smooth_nb, create_new_body, prop
            )
        assert _("Invalid") in str(e.value)
        mock_object.ExtrudeTriangles.assert_not_called()

    @pytest.mark.parametrize("expected", [True, False])
    def test_imprint_selected_triangles(self, mock_mesh_editor, mock_object, expected):
        """
        Test aligning nodes and triangle with MeshEditor
        """
        tri = Mock(spec=EntList)
        tri.ent_list = Mock()
        mock_object.ImprintSelectedTriangles.return_value = expected
        result = mock_mesh_editor.imprint_selected_triangles(tri)
        assert isinstance(result, bool)
        assert result is expected
        mock_object.ImprintSelectedTriangles.assert_called_once_with(tri.ent_list)

    @pytest.mark.parametrize("tri", [1, 1.0, True, "String"])
    def test_imprint_selected_triangles_invalid(self, mock_mesh_editor, mock_object, tri, _):
        """
        Test aligning nodes and triangle with MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.imprint_selected_triangles(tri)
        assert _("Invalid") in str(e.value)
        mock_object.ImprintSelectedTriangles.assert_not_called()

    @pytest.mark.parametrize(
        "args, passed_args, expected",
        [
            ((a, b, c, d, e, f, g), (a, b, c, d, e, f, g), h)
            for a, b, c, d, e, f, g, h in pad_and_zip(
                VALID_FLOAT,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_INT,
            )
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_global_merge(self, mock_mesh_editor, mock_object, args, passed_args, expected):
        """
        Test merging nodes with specified tolerance with MeshEditor
        """
        mock_object.GlobalMerge3.return_value = expected
        result = mock_mesh_editor.global_merge(*args)
        assert isinstance(result, int)
        assert result == expected
        mock_object.GlobalMerge3.assert_called_once_with(*passed_args)

    @pytest.mark.parametrize(
        "args, invalid_val",
        [
            (
                [
                    VALID_FLOAT[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ],
    )
    def test_global_merge_invalid(self, mock_mesh_editor, mock_object, args, invalid_val, _):
        """
        Test merging nodes with specified tolerance with MeshEditor with invalid inputs
        """
        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(TypeError) as e:
                mock_mesh_editor.global_merge(*args)
            assert _("Invalid") in str(e.value)
            mock_object.GlobalMerge3.assert_not_called()

    @pytest.mark.parametrize("expected", [1, 2, 3])
    def test_merge_nodes(self, mock_mesh_editor, mock_object, expected):
        """
        Test merging nodes with MeshEditor
        """
        target = Mock(spec=EntList)
        target.ent_list = Mock()
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        fusion = True
        use_mid = True
        mock_object.MergeNodes2.return_value = expected
        result = mock_mesh_editor.merge_nodes(target, nodes, fusion, use_mid)
        assert isinstance(result, int)
        assert result == expected
        mock_object.MergeNodes2.assert_called_once_with(
            target.ent_list, nodes.ent_list, fusion, use_mid
        )

    @pytest.mark.parametrize(
        "target, nodes, fusion, use_mid",
        [
            (Mock(spec=EntList), Mock(spec=EntList), None, True),
            (Mock(spec=EntList), Mock(spec=EntList), True, None),
            (1, Mock(spec=EntList), True, True),
            (Mock(spec=EntList), 1, True, True),
            (Mock(spec=EntList), Mock(spec=EntList), 1, True),
            (Mock(spec=EntList), Mock(spec=EntList), True, 1),
            (1.0, Mock(spec=EntList), True, True),
            (Mock(spec=EntList), 1.0, True, True),
            (Mock(spec=EntList), Mock(spec=EntList), 1.0, True),
            (Mock(spec=EntList), Mock(spec=EntList), True, 1.0),
            ("String", Mock(spec=EntList), True, True),
            (Mock(spec=EntList), "String", True, True),
            (Mock(spec=EntList), Mock(spec=EntList), "String", True),
            (Mock(spec=EntList), Mock(spec=EntList), True, "String"),
            (False, Mock(spec=EntList), True, True),
            (Mock(spec=EntList), False, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_merge_nodes_invalid(
        self, mock_mesh_editor, mock_object, target, nodes, fusion, use_mid, _
    ):
        """
        Test merging nodes with MeshEditor with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.merge_nodes(target, nodes, fusion, use_mid)
        assert _("Invalid") in str(e.value)
        mock_object.MergeNodes2.assert_not_called()

    @pytest.mark.parametrize("expected", [1, 5, 10])
    def test_fix_aspect_ratio(self, mock_mesh_editor, mock_object, expected):
        """
        Test reducing triangle aspect ratio
        """
        target = 1.5
        mock_object.FixAspectRatio.return_value = expected
        result = mock_mesh_editor.fix_aspect_ratio(target)
        assert isinstance(result, int)
        assert result == expected
        mock_object.FixAspectRatio.assert_called_once_with(target)

    @pytest.mark.parametrize("target", [None, "String", True])
    def test_fix_aspect_ratio_invalid(self, mock_mesh_editor, mock_object, target, _):
        """
        Test reducing triangle aspect ratio with invalid inputs
        """
        with pytest.raises(TypeError) as e:
            mock_mesh_editor.fix_aspect_ratio(target)
        assert _("Invalid") in str(e.value)
        mock_object.FixAspectRatio.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [
            ("InsertNode", "insert_node", (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST)),
            (
                "InsertNodeInTri",
                "insert_node_in_tri",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST),
            ),
            (
                "InsertNodeInTetByNodes",
                "insert_node_in_tet",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                ),
            ),
            (
                "InsertNodeInTetByNodes",
                "insert_node_in_tet_by_nodes",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                ),
            ),
            ("InsertNodeOnBeam", "insert_node_on_beam", (VALID_MOCK.ENT_LIST, 1)),
            (
                "CreateTet",
                "create_tet",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.PROP,
                ),
            ),
            (
                "CreateTri",
                "create_tri",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.PROP),
            ),
            (
                "CreateWedge",
                "create_wedge",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.PROP,
                ),
            ),
            ("ConvertWedgesToTetras", "convert_wedges_to_tetras", (VALID_MOCK.ENT_LIST, 1)),
            ("FindProperty", "find_property", (1, 1)),
            ("Delete", "delete", (VALID_MOCK.ENT_LIST,)),
            (
                "CreateBeamsByPoints",
                "create_beams_by_points",
                (VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, 1, VALID_MOCK.PROP),
            ),
            (
                "CreateBeams",
                "create_beams",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, 1, VALID_MOCK.PROP),
            ),
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self, mock_mesh_editor: MeshEditor, mock_object, pascal_name, property_name, args
    ):
        """
        Test the return value of the function is None.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_mesh_editor, property_name)(*args)
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, size_prop, size_val",
        [
            (
                "InsertNodeInTri2",
                "insert_node_in_tri",
                (VALID_MOCK.ENT_LIST, None, None),
                "size",
                3,
            ),
            (
                "InsertNodeInTet",
                "insert_node_in_tet",
                (VALID_MOCK.ENT_LIST, None, None, None),
                "size",
                4,
            ),
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none2(
        self,
        mock_mesh_editor: MeshEditor,
        mock_object,
        pascal_name,
        property_name,
        args,
        size_prop,
        size_val,
    ):
        """
        Test the return value of the function is None.
        """
        setattr(args[0], size_prop, size_val)
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_mesh_editor, property_name)(*args)
        assert result is None

    def test_create_entity_list_return_none(self, mock_mesh_editor: MeshEditor, mock_object):
        """
        Test the return value of the function is None.
        """
        mock_object.CreateEntityList = None
        result = mock_mesh_editor.create_entity_list()
        assert result is None
