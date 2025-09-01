# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for BoundaryConditions Wrapper Class of moldflow-api module.
"""
from unittest.mock import Mock, patch
from win32com.client import VARIANT
import pythoncom
import pytest
from moldflow import BoundaryConditions
from moldflow.common import AnalysisType
from moldflow.ent_list import EntList
from moldflow.vector import Vector
from moldflow.prop import Property


@pytest.mark.unit
class TestUnitBoundaryConditions:
    """
    Test suite for the BoundaryConditions class.
    """

    @pytest.fixture
    def mock_boundary_conditions(self, mock_object) -> BoundaryConditions:
        """
        Fixture to create a mock instance of BoundaryConditions.
        Args:
            mock_object: Mock object for the BoundaryConditions dependency.
        Returns:
            BoundaryConditions: An instance of BoundaryConditions with the mock object.
        """
        return BoundaryConditions(mock_object)

    def test_create_entity_list(self, mock_boundary_conditions, mock_object):
        """
        Test the create_entity_list method of BoundaryConditions class.
        Args:
            mock_boundary_conditions: Mock instance of BoundaryConditions.
            mock_object: Mock object for the BoundaryConditions dependency.
        """
        mock_ent_list = Mock()
        mock_object.CreateEntityList = mock_ent_list
        result = mock_boundary_conditions.create_entity_list()
        assert result.ent_list == mock_ent_list
        assert isinstance(result, EntList)

    def test_create_entity_list_none(self, mock_boundary_conditions, mock_object):
        """
        Test the create_entity_list method of BoundaryConditions class with None.
        Args:
            mock_boundary_conditions: Mock instance of BoundaryConditions.
            mock_object: Mock object for the BoundaryConditions dependency.
        """
        mock_object.CreateEntityList = None
        result = mock_boundary_conditions.create_entity_list()
        assert result is None

    @pytest.mark.parametrize(
        "analysis, expected, analysis_value",
        [
            (AnalysisType.STRESS, 5, 1),
            (AnalysisType.CORE_SHIFT, 10, 4),
            (1, 15, 1),
            (4, 20, 4),  # Core shift is value 4
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_fixed_constraints(
        self, mock_boundary_conditions, mock_object, analysis, expected, analysis_value
    ):
        """
        Test the create_fixed_constraints method of BoundaryConditions class.
        Args:
            mock_boundary_conditions: Mock instance of BoundaryConditions.
            mock_object: Mock object for the BoundaryConditions dependency.
            nodes: List of nodes to be used in the test.
            analysis: Analysis type for the test.
            retract_time: Retract time for the test.
            expected: Expected result of the method call.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.CreateFixedConstraints.return_value = expected
        result = mock_boundary_conditions.create_fixed_constraints(nodes, analysis)
        assert result == expected
        mock_object.CreateFixedConstraints.assert_called_once_with(nodes.ent_list, analysis_value)

    @pytest.mark.parametrize("retract_time, expected", [(0.1, 5), (0.5, 10), (2, 15), (1, 20)])
    # pylint: disable=R0913, R0917
    def test_create_core_shift_fixed_constraints(
        self, mock_boundary_conditions, mock_object, retract_time, expected
    ):
        """
        Test the create_fixed_constraints method of BoundaryConditions class.
        Args:
            mock_boundary_conditions: Mock instance of BoundaryConditions.
            mock_object: Mock object for the BoundaryConditions dependency.
            nodes: List of nodes to be used in the test.
            analysis: Analysis type for the test.
            retract_time: Retract time for the test.
            expected: Expected result of the method call.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.CreateFixedConstraints2.return_value = expected
        result = mock_boundary_conditions.create_core_shift_fixed_constraints(nodes, retract_time)
        assert result == expected
        mock_object.CreateFixedConstraints2.assert_called_once_with(nodes.ent_list, retract_time)

    @pytest.mark.parametrize(
        "nodes, analysis",
        [(x, AnalysisType.STRESS) for x in ["", 0, -1, 1.5]]
        + [(Mock(spec=EntList), x) for x in [None, "", 1.5, True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_fixed_constraints_invalid(
        self, mock_boundary_conditions, mock_object, nodes, analysis, _
    ):
        """
        Test the create_fixed_constraints method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_fixed_constraints(nodes, analysis)
        assert _("Invalid") in str(e.value)
        mock_object.CreateFixedConstraints.assert_not_called()
        mock_object.CreateFixedConstraints2.assert_not_called()

    @pytest.mark.parametrize(
        "nodes, retract_time",
        [(x, 0.1) for x in ["", 0, -1, 1.5]]
        + [(Mock(spec=EntList), x) for x in [None, "", True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_core_shift_fixed_constraints_invalid(
        self, mock_boundary_conditions, mock_object, nodes, retract_time, _
    ):
        """
        Test the create_fixed_constraints method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_fixed_constraints(nodes, retract_time)
        assert _("Invalid") in str(e.value)
        mock_object.CreateFixedConstraints.assert_not_called()
        mock_object.CreateFixedConstraints2.assert_not_called()

    @pytest.mark.parametrize(
        "analysis_type, expected, expected_enum",
        [
            (AnalysisType.STRESS, 5, 1),
            (AnalysisType.CORE_SHIFT, 10, 4),
            (1, 15, 1),
            (4, 20, 4),  # Core shift is value 4
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_pin_constraints(
        self, mock_boundary_conditions, mock_object, analysis_type, expected, expected_enum
    ):
        """
        Test the create_pin_constraints method of BoundaryConditions class.
        Args:
            mock_boundary_conditions: Mock instance of BoundaryConditions.
            mock_object: Mock object for the BoundaryConditions dependency.
            analysis_type: Analysis type for the test.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.CreatePinConstraints.return_value = expected
        result = mock_boundary_conditions.create_pin_constraints(nodes, analysis_type)
        assert result == expected
        mock_object.CreatePinConstraints.assert_called_once_with(nodes.ent_list, expected_enum)

    @pytest.mark.parametrize("retract_time, expected", [(0.1, 5), (4.5, 10), (1, 15), (4, 20)])
    # pylint: disable=R0913, R0917
    def test_create_core_shift_pin_constraints(
        self, mock_boundary_conditions, mock_object, retract_time, expected
    ):
        """
        Test the create_pin_constraints method of BoundaryConditions class.
        Args:
            mock_boundary_conditions: Mock instance of BoundaryConditions.
            mock_object: Mock object for the BoundaryConditions dependency.
            analysis_type: Analysis type for the test.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.CreatePinConstraints2.return_value = expected
        result = mock_boundary_conditions.create_core_shift_pin_constraints(nodes, retract_time)
        assert result == expected
        mock_object.CreatePinConstraints2.assert_called_once_with(nodes.ent_list, retract_time)

    @pytest.mark.parametrize(
        "nodes, analysis",
        [(x, AnalysisType.STRESS) for x in ["", 0, -1, 1.5]]
        + [(Mock(spec=EntList), x) for x in [None, "", 1.5, True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_pin_constraints_invalid(
        self, mock_boundary_conditions, mock_object, nodes, analysis, _
    ):
        """
        Test the create_pin_constraints method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_pin_constraints(nodes, analysis)
        assert _("Invalid") in str(e.value)
        mock_object.CreatePinConstraints.assert_not_called()

    @pytest.mark.parametrize(
        "nodes, retract_time",
        [(x, 0.5) for x in ["", 0, -1, 1.5]]
        + [(Mock(spec=EntList), x) for x in [None, "", True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_core_shift_pin_constraints_invalid(
        self, mock_boundary_conditions, mock_object, nodes, retract_time, _
    ):
        """
        Test the create_pin_constraints method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_pin_constraints(nodes, retract_time)
        assert _("Invalid") in str(e.value)
        mock_object.CreatePinConstraints2.assert_not_called()

    @pytest.mark.parametrize(
        "analysis, expected, analysis_val",
        [(AnalysisType.STRESS, 5, 1), (AnalysisType.CORE_SHIFT, 10, 4), (1, 15, 1), (4, 20, 4)],
    )
    # pylint: disable=R0913, R0917
    def test_spring_constraint(
        self, mock_boundary_conditions, mock_object, analysis, expected, analysis_val
    ):
        """
        Test the create_spring_constraints method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        trans = Mock(spec=Vector)
        trans.vector = Mock()
        rot = Mock(spec=Vector)
        rot.vector = Mock()
        mock_object.CreateSpringConstraints.return_value = expected
        mock_object.CreateSpringConstraints2.return_value = expected
        result = mock_boundary_conditions.create_spring_constraints(nodes, analysis, trans, rot)
        assert result == expected
        mock_object.CreateSpringConstraints.assert_called_once_with(
            nodes.ent_list, analysis_val, trans.vector, rot.vector
        )

    @pytest.mark.parametrize("retract_time, expected", [(0.1, 5), (0.2, 10), (0.3, 15), (0.4, 20)])
    # pylint: disable=R0913, R0917
    def test_core_shift_spring_constraint(
        self, mock_boundary_conditions, mock_object, retract_time, expected
    ):
        """
        Test the create_spring_constraints method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        trans = Mock(spec=Vector)
        trans.vector = Mock()
        rot = Mock(spec=Vector)
        rot.vector = Mock()
        mock_object.CreateSpringConstraints2.return_value = expected
        result = mock_boundary_conditions.create_core_shift_spring_constraints(
            nodes, trans, rot, retract_time
        )
        assert result == expected
        mock_object.CreateSpringConstraints2.assert_called_once_with(
            nodes.ent_list, trans.vector, rot.vector, retract_time
        )

    @pytest.mark.parametrize(
        "nodes, analysis, trans, rotation",
        [
            (x, AnalysisType.STRESS, Mock(spec=Vector), Mock(spec=Vector))
            for x in ["", 1.5, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), x, Mock(spec=Vector), Mock(spec=Vector))
            for x in ["", 1.5, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), AnalysisType.CORE_SHIFT, x, Mock(spec=Vector))
            for x in ["", 1.5, True, "abc"]
        ],
    )
    # pylint: disable=R0913, R0917
    def test_spring_constraint_invalid(
        self, mock_boundary_conditions, mock_object, nodes, analysis, trans, rotation, _
    ):
        """
        Test the create_spring_constraints method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_spring_constraints(nodes, analysis, trans, rotation)
        assert _("Invalid") in str(e.value)
        mock_object.CreateSpringConstraints.assert_not_called()

    @pytest.mark.parametrize(
        "nodes, trans, rotation, retract_time",
        [(x, Mock(spec=Vector), Mock(spec=Vector), 0.5) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x, Mock(spec=Vector), 0.5) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=Vector), x, 0.5) for x in ["", 1.5, True, "abc"]]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), Mock(spec=Vector), x) for x in ["", True, "abc"]
        ],
    )
    # pylint: disable=R0913, R0917
    def test_core_shift_spring_constraint_invalid(
        self, mock_boundary_conditions, mock_object, nodes, trans, rotation, retract_time, _
    ):
        """
        Test the create_spring_constraints method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_core_shift_spring_constraints(
                nodes, trans, rotation, retract_time
            )
        assert _("Invalid") in str(e.value)
        mock_object.CreateSpringConstraints2.assert_not_called()

    @pytest.mark.parametrize(
        "analysis, analysis_val, trans_types_val, rotation_types_val, expected",
        [
            (AnalysisType.STRESS, 1, 1, 2, 6),
            (AnalysisType.STRESS_WARP, 3, 2, 1, 6),
            (AnalysisType.WARP, 2, 2, 2, 6),
            (AnalysisType.CORE_SHIFT, 4, 1, 1, 6),
            (AnalysisType.CORE_SHIFT, 4, 3, 2, 6),
            (AnalysisType.CORE_SHIFT, 4, 1, 3, 6),
        ],
    )
    # pylint: disable=R0913, R0917, R0914
    def test_create_general_constraints(
        self,
        mock_boundary_conditions,
        mock_object,
        analysis,
        analysis_val,
        trans_types_val,
        rotation_types_val,
        expected,
    ):
        """
        Test the create_general_constraints method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        trans = Mock(spec=Vector)
        trans.vector = Mock()
        rot = Mock(spec=Vector)
        rot.vector = Mock()
        trans_types = Mock(spec=Vector)
        trans_types.vector = Mock()
        trans_types.x = trans_types_val
        trans_types.y = trans_types_val
        trans_types.z = trans_types_val
        rot_types = Mock(spec=Vector)
        rot_types.vector = Mock()
        rot_types.x = rotation_types_val
        rot_types.y = rotation_types_val
        rot_types.z = rotation_types_val
        mock_object.CreateGeneralConstraints2.return_value = expected
        result = mock_boundary_conditions.create_general_constraints(
            nodes, analysis, trans, rot, trans_types, rot_types
        )
        assert result == expected
        mock_object.CreateGeneralConstraints2.assert_called_once_with(
            nodes.ent_list,
            analysis_val,
            trans.vector,
            rot.vector,
            trans_types.vector,
            rot_types.vector,
        )
        mock_object.CreateGeneralConstraints3.assert_not_called()

    @pytest.mark.parametrize(
        "trans_types_val, rotation_types_val, retract_time, expected, ",
        [
            (1, 2, 0.1, 6),
            (2, 1, 0.1, 6),
            (2, 2, 0.1, 6),
            (1, 1, 0.1, 6),
            (1, 3, 0.1, 6),
            (1, 1, 0.1, 6),
        ],
    )
    # pylint: disable=R0913, R0917, R0914
    def test_create_core_shift_general_constraints(
        self,
        mock_boundary_conditions,
        mock_object,
        trans_types_val,
        rotation_types_val,
        retract_time,
        expected,
    ):
        """
        Test the create_general_constraints method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        trans = Mock(spec=Vector)
        trans.vector = Mock()
        rot = Mock(spec=Vector)
        rot.vector = Mock()
        trans_types = Mock(spec=Vector)
        trans_types.vector = Mock()
        trans_types.x = trans_types_val
        trans_types.y = trans_types_val
        trans_types.z = trans_types_val
        rot_types = Mock(spec=Vector)
        rot_types.vector = Mock()
        rot_types.x = rotation_types_val
        rot_types.y = rotation_types_val
        rot_types.z = rotation_types_val
        mock_object.CreateGeneralConstraints3.return_value = expected
        result = mock_boundary_conditions.create_core_shift_general_constraints(
            nodes, trans, rot, trans_types, rot_types, retract_time
        )
        assert result == expected
        mock_object.CreateGeneralConstraints3.assert_called_once_with(
            nodes.ent_list,
            trans.vector,
            rot.vector,
            trans_types.vector,
            rot_types.vector,
            retract_time,
        )

    @pytest.mark.parametrize(
        "nodes, analysis_val, trans, rot, trans_types, rot_types",
        [
            (x, 1, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector))
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (
                Mock(spec=EntList),
                x,
                Mock(spec=Vector),
                Mock(spec=Vector),
                Mock(spec=Vector),
                Mock(spec=Vector),
            )
            for x in ["", 1.5, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), 1, x, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector))
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), 1, Mock(spec=Vector), x, Mock(spec=Vector), Mock(spec=Vector))
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), 1, Mock(spec=Vector), Mock(spec=Vector), x, Mock(spec=Vector))
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), 1, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), x)
            for x in ["", 1.5, 1, True, "abc"]
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_general_constraints_invalid(
        self,
        mock_boundary_conditions,
        mock_object,
        nodes,
        analysis_val,
        trans,
        rot,
        trans_types,
        rot_types,
        _,
    ):
        """
        Test the create_general_constraints method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_general_constraints(
                nodes, analysis_val, trans, rot, trans_types, rot_types
            )
        assert _("Invalid") in str(e.value)
        mock_object.CreateGeneralConstraints2.assert_not_called()

    @pytest.mark.parametrize(
        "nodes, trans, rot, trans_types, rot_types, retract_time",
        [
            (x, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), 0.5)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), x, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), 0.5)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), x, Mock(spec=Vector), Mock(spec=Vector), 0.5)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), Mock(spec=Vector), x, Mock(spec=Vector), 0.5)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), x, 0.5)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=Vector),
                Mock(spec=Vector),
                Mock(spec=Vector),
                Mock(spec=Vector),
                x,
            )
            for x in ["", True, "abc"]
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_core_shift_general_constraints_invalid(
        self,
        mock_boundary_conditions,
        mock_object,
        nodes,
        trans,
        rot,
        trans_types,
        rot_types,
        retract_time,
        _,
    ):
        """
        Test the create_general_constraints method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_core_shift_general_constraints(
                nodes, trans, rot, trans_types, rot_types, retract_time
            )
        assert _("Invalid") in str(e.value)
        mock_object.CreateGeneralConstraints3.assert_not_called()

    @pytest.mark.parametrize("expected", [4, 1])
    def test_create_nodal_loads(self, mock_boundary_conditions, mock_object, expected):
        """
        Test the create_nodal_loads method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        force = Mock(spec=Vector)
        force.vector = Mock()
        moment = Mock(spec=Vector)
        moment.vector = Mock()
        mock_object.CreateNodalLoads.return_value = expected
        result = mock_boundary_conditions.create_nodal_loads(nodes, force, moment)
        assert result == expected
        mock_object.CreateNodalLoads.assert_called_once_with(
            nodes.ent_list, force.vector, moment.vector
        )

    @pytest.mark.parametrize(
        "nodes, force, moment",
        [(x, Mock(spec=Vector), Mock(spec=Vector)) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x, Mock(spec=Vector)) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=Vector), x) for x in ["", 1.5, True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_nodal_loads_invalid(
        self, mock_boundary_conditions, mock_object, nodes, force, moment, _
    ):
        """
        Test the create_nodal_loads method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_nodal_loads(nodes, force, moment)
        assert _("Invalid") in str(e.value)
        mock_object.CreateNodalLoads.assert_not_called()

    @pytest.mark.parametrize("expected", [3, 2])
    def test_create_edge_loads(self, mock_boundary_conditions, mock_object, expected):
        """
        Test the create_edge_loads method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        force = Mock(spec=Vector)
        force.vector = Mock()
        mock_object.CreateEdgeLoads.return_value = expected
        result = mock_boundary_conditions.create_edge_loads(nodes, force)
        assert result == expected
        mock_object.CreateEdgeLoads.assert_called_once_with(nodes.ent_list, force.vector)

    @pytest.mark.parametrize(
        "nodes, force",
        [(x, Mock(spec=Vector)) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x) for x in ["", 1.5, True, "abc"]],
    )
    def test_create_edge_loads_invalid(
        self, mock_boundary_conditions, mock_object, nodes, force, _
    ):
        """
        Test the create_edge_loads method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_edge_loads(nodes, force)
        assert _("Invalid") in str(e.value)
        mock_object.CreateEdgeLoads.assert_not_called()

    @pytest.mark.parametrize("expected", [3, 2])
    def test_elemental_loads(self, mock_boundary_conditions, mock_object, expected):
        """
        Test the create_elemental_loads method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        force = Mock(spec=Vector)
        force.vector = Mock()
        mock_object.CreateElementalLoads.return_value = expected
        result = mock_boundary_conditions.create_elemental_loads(nodes, force)
        assert result == expected
        mock_object.CreateElementalLoads.assert_called_once_with(nodes.ent_list, force.vector)

    @pytest.mark.parametrize(
        "nodes, force",
        [(x, Mock(spec=Vector)) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x) for x in ["", 1.5, True, "abc"]],
    )
    def test_elemental_loads_invalid(self, mock_boundary_conditions, mock_object, nodes, force, _):
        """
        Test the create_elemental_loads method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_elemental_loads(nodes, force)
        assert _("Invalid") in str(e.value)
        mock_object.CreateElementalLoads.assert_not_called()

    @pytest.mark.parametrize("pressure_val, expected", [(2, 3), (3.0, 2)])
    def test_create_pressure_loads(
        self, mock_boundary_conditions, mock_object, pressure_val, expected
    ):
        """
        Test the create_pressure_loads method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.CreatePressureLoads.return_value = expected
        result = mock_boundary_conditions.create_pressure_loads(nodes, pressure_val)
        assert result == expected
        mock_object.CreatePressureLoads.assert_called_once_with(nodes.ent_list, pressure_val)

    @pytest.mark.parametrize(
        "nodes, pressure_val",
        [(x, 1.5) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x) for x in [None, "", True, "abc"]],
    )
    def test_create_pressure_loads_invalid(
        self, mock_boundary_conditions, mock_object, nodes, pressure_val, _
    ):
        """
        Test the create_pressure_loads method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_pressure_loads(nodes, pressure_val)
        assert _("Invalid") in str(e.value)
        mock_object.CreatePressureLoads.assert_not_called()

    @pytest.mark.parametrize(
        "top, bottom, expected", [(2.5, 3, 4), (3, 2, 1), (3, 2, 1), (3, 2.7, 1)]
    )
    # pylint: disable=R0913, R0917
    def test_create_temperature_loads(
        self, mock_boundary_conditions, mock_object, top, bottom, expected
    ):
        """
        Test the create_temperature_loads method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.CreateTemperatureLoads.return_value = expected
        result = mock_boundary_conditions.create_temperature_loads(nodes, top, bottom)
        assert result == expected
        mock_object.CreateTemperatureLoads.assert_called_once_with(nodes.ent_list, top, bottom)

    @pytest.mark.parametrize(
        "tri, top, bottom",
        [(x, 1.5, 2.5) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x, 2.5) for x in [None, "", True, "abc"]]
        + [(Mock(spec=EntList), 1.5, x) for x in [None, "", True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_temperature_loads_invalid(
        self, mock_boundary_conditions, mock_object, tri, top, bottom, _
    ):
        """
        Test the create_temperature_loads method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_temperature_loads(tri, top, bottom)
        assert _("Invalid") in str(e.value)
        mock_object.CreateTemperatureLoads.assert_not_called()

    @pytest.mark.parametrize("expected", [3, 2])
    def test_create_volume_loads(self, mock_boundary_conditions, mock_object, expected):
        """
        Test the create_volume_loads method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        force = Mock(spec=Vector)
        force.vector = Mock()
        mock_object.CreateVolumeLoads.return_value = expected
        result = mock_boundary_conditions.create_volume_loads(nodes, force)
        assert result == expected
        mock_object.CreateVolumeLoads.assert_called_once_with(nodes.ent_list, force.vector)

    @pytest.mark.parametrize(
        "tri, force",
        [(x, Mock(spec=Vector)) for x in ["", 1.5, True, "abc"]]
        + [(Mock(spec=EntList), x) for x in ["", 1.5, True, "abc"]],
    )
    def test_create_volume_loads_invalid(
        self, mock_boundary_conditions, mock_object, tri, force, _
    ):
        """
        Test the create_volume_loads method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_volume_loads(tri, force)
        assert _("Invalid") in str(e.value)
        mock_object.CreateVolumeLoads.assert_not_called()

    @pytest.mark.parametrize(
        "upper, lower, expected", [(3.6, 4, 5), (3, 4, 5), (2, 1, 6), (2, 1.9, 6)]
    )
    # pylint: disable=R0913, R0917
    def test_create_critical_dimentsion(
        self, mock_boundary_conditions, mock_object, upper, lower, expected
    ):
        """
        Test the create_critical_dimension method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        nodes2 = Mock(spec=EntList)
        nodes2.ent_list = Mock()
        mock_object.CreateCriticalDimension.return_value = expected
        result = mock_boundary_conditions.create_critical_dimension(nodes, nodes2, upper, lower)
        assert result == expected
        mock_object.CreateCriticalDimension.assert_called_once_with(
            nodes.ent_list, nodes2.ent_list, upper, lower
        )

    @pytest.mark.parametrize(
        "node1, node2, upper, lower",
        [(x, Mock(spec=EntList), 2.5, 3) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), x, 2.5, 3) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=EntList), x, 3) for x in [None, "", True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=EntList), 2.5, x) for x in [None, "", True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_create_critical_dimension_invalid(
        self, mock_boundary_conditions, mock_object, node1, node2, upper, lower, _
    ):
        """
        Test the create_critical_dimension method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_critical_dimension(node1, node2, upper, lower)
        assert _("Invalid") in str(e.value)
        mock_object.CreateCriticalDimension.assert_not_called()

    @pytest.mark.parametrize("name, expected", [("test", 3), ("abc", 6)])
    def test_create_doe_critical_dimension(
        self, mock_boundary_conditions, mock_object, name, expected
    ):
        """
        Test the create_doe_critical_dimension method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        nodes2 = Mock(spec=EntList)
        nodes2.ent_list = Mock()
        mock_object.CreateDoeCriticalDimension.return_value = expected
        result = mock_boundary_conditions.create_doe_critical_dimension(nodes, nodes2, name)
        assert result == expected
        mock_object.CreateDoeCriticalDimension.assert_called_once_with(
            nodes.ent_list, nodes2.ent_list, name
        )

    @pytest.mark.parametrize(
        "node1, node2, name",
        [(x, Mock(spec=EntList), "test") for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), x, "test") for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=EntList), x) for x in [None, 1, 1.5, True]],
    )
    # pylint: disable=R0913, R0917
    def test_create_doe_critical_dimension_invalid(
        self, mock_boundary_conditions, mock_object, node1, node2, name, _
    ):
        """
        Test the create_doe_critical_dimension method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_doe_critical_dimension(node1, node2, name)
        assert _("Invalid") in str(e.value)
        mock_object.CreateDoeCriticalDimension.assert_not_called()

    @pytest.mark.parametrize(
        "prop, prop_type, expected",
        [
            (None, 1, None),
            (None, 1, 10),
            (Mock(spec=Property), 11, 2),
            (Mock(spec=Property), 15, None),
            (Mock(spec=Property), 17, 5),
            (Mock(spec=Property), 13, 9),
            (Mock(spec=Property), 19, 5),
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_ndbc(self, mock_boundary_conditions, mock_object, prop, prop_type, expected):
        """
        Test the create_ndbc method of BoundaryConditions class.
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            nodes = Mock(spec=EntList)
            nodes.ent_list = Mock()
            normal = Mock(spec=Vector)
            normal.vector = Mock()
            if prop is not None:
                prop.prop = Mock()
            mock_object.CreateNDBC.return_value = expected
            result = mock_boundary_conditions.create_ndbc(nodes, normal, prop_type, prop)
            if expected is not None:
                assert result.ent_list == expected
                assert isinstance(result, EntList)
            else:
                assert result is None

            if prop is not None:
                mock_object.CreateNDBC.assert_called_once_with(
                    nodes.ent_list, normal.vector, prop_type, prop.prop
                )
            else:
                mock_object.CreateNDBC.assert_called_once_with(
                    nodes.ent_list, normal.vector, prop_type, mock_func()
                )

    @pytest.mark.parametrize(
        "nodes, normal, prop_type, prop",
        [(x, Mock(spec=Vector), 1, Mock(spec=Property)) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), x, 1, Mock(spec=Property)) for x in ["", 1.5, 1, True, "abc"]]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), x, Mock(spec=Property))
            for x in [None, "", "abc", True]
        ]
        + [(Mock(spec=EntList), Mock(spec=Vector), 1, x) for x in ["", 1.5, 1, True]],
    )
    # pylint: disable=R0913, R0917
    def test_create_ndbc_invalid(
        self, mock_boundary_conditions, mock_object, nodes, normal, prop_type, prop, _
    ):
        """
        Test the create_ndbc method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_ndbc(nodes, normal, prop_type, prop)
        assert _("Invalid") in str(e.value)
        mock_object.CreateNDBC.assert_not_called()

    @pytest.mark.parametrize(
        "prop_type, prop, expected",
        [
            (3, None, None),
            (3, None, 10),
            (3, Mock(spec=Property), 123),
            (3, Mock(spec=Property), None),
            (3, Mock(spec=Property), None),
            (3, Mock(spec=Property), None),
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_ndbc_at_xyz(
        self, mock_boundary_conditions, mock_object, prop_type, prop, expected
    ):
        """
        Test the create_ndbc_at_xyz method of BoundaryConditions class.
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            coord = Mock(spec=Vector)
            coord.vector = Mock()
            normal = Mock(spec=Vector)
            normal.vector = Mock()
            if prop is not None:
                prop.prop = Mock()
            mock_object.CreateNDBCAtXYZ.return_value = expected
            result = mock_boundary_conditions.create_ndbc_at_xyz(coord, normal, prop_type, prop)
            if expected is not None:
                assert result.ent_list == expected
                assert isinstance(result, EntList)
            else:
                assert result is None

            if prop is not None:
                mock_object.CreateNDBCAtXYZ.assert_called_once_with(
                    coord.vector, normal.vector, prop_type, prop.prop
                )
            else:
                mock_object.CreateNDBCAtXYZ.assert_called_once_with(
                    coord.vector, normal.vector, prop_type, mock_func()
                )

    @pytest.mark.parametrize("expected", [4, 1])
    def test_move_ndbc(self, mock_boundary_conditions, mock_object, expected):
        """
        Test the move_ndbc method of BoundaryConditions class.
        """
        ndbc = Mock(spec=EntList)
        ndbc.ent_list = Mock()
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        normal = Mock(spec=Vector)
        normal.vector = Mock()
        mock_object.MoveNDBC.return_value = expected
        result = mock_boundary_conditions.move_ndbc(ndbc, nodes, normal)
        assert result == expected
        mock_object.MoveNDBC.assert_called_once_with(ndbc.ent_list, nodes.ent_list, normal.vector)

    @pytest.mark.parametrize(
        "ndbc, nodes, normal",
        [(x, Mock(spec=EntList), Mock(spec=Vector)) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), x, Mock(spec=Vector)) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=EntList), x) for x in ["", 1.5, 1, True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_move_ndbc_invalid(self, mock_boundary_conditions, mock_object, ndbc, nodes, normal, _):
        """
        Test the move_ndbc method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.move_ndbc(ndbc, nodes, normal)
        assert _("Invalid") in str(e.value)
        mock_object.MoveNDBC.assert_not_called()

    @pytest.mark.parametrize("expected", [4, 1])
    def test_move_ndbc_to_xyz(self, mock_boundary_conditions, mock_object, expected):
        """
        Test the move_ndbc_to_xyz method of BoundaryConditions class.
        """
        ndbc = Mock(spec=EntList)
        ndbc.ent_list = Mock()
        coord = Mock(spec=Vector)
        coord.vector = Mock()
        normal = Mock(spec=Vector)
        normal.vector = Mock()
        mock_object.MoveNDBCToXYZ.return_value = expected
        result = mock_boundary_conditions.move_ndbc_to_xyz(ndbc, coord, normal)
        assert result == expected
        mock_object.MoveNDBCToXYZ.assert_called_once_with(
            ndbc.ent_list, coord.vector, normal.vector
        )

    @pytest.mark.parametrize(
        "ndbc, coord, normal",
        [(x, Mock(spec=Vector), Mock(spec=Vector)) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), x, Mock(spec=Vector)) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), Mock(spec=Vector), x) for x in ["", 1.5, 1, True, "abc"]],
    )
    # pylint: disable=R0913, R0917
    def test_move_ndbc_to_xyz_invalid(
        self, mock_boundary_conditions, mock_object, ndbc, coord, normal, _
    ):
        """
        Test the move_ndbc_to_xyz method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.move_ndbc_to_xyz(ndbc, coord, normal)
        assert _("Invalid") in str(e.value)
        mock_object.MoveNDBCToXYZ.assert_not_called()

    @pytest.mark.parametrize(
        "analysis, analysis_val, expected",
        [(AnalysisType.STRESS, 1, 3), (AnalysisType.CORE_SHIFT, 4, 6), (1, 1, 10), (3, 3, 10)],
    )
    # pylint: disable=R0913, R0917
    def test_set_prohibited_gate_nodes(
        self, mock_boundary_conditions, mock_object, analysis, analysis_val, expected
    ):
        """
        Test the set_prohibited_gate_nodes method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        mock_object.SetProhibitedGateNodes.return_value = expected
        result = mock_boundary_conditions.set_prohibited_gate_nodes(nodes, analysis)
        assert result == expected
        mock_object.SetProhibitedGateNodes.assert_called_once_with(nodes.ent_list, analysis_val)

    @pytest.mark.parametrize(
        "nodes, analysis",
        [(x, AnalysisType.STRESS) for x in ["", 1.5, 1, True, "abc"]]
        + [(Mock(spec=EntList), x) for x in [None, "", 1.5, True, "abc"]],
    )
    def test_set_prohibited_gate_nodes_invalid(
        self, mock_boundary_conditions, mock_object, nodes, analysis, _
    ):
        """
        Test the set_prohibited_gate_nodes method with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.set_prohibited_gate_nodes(nodes, analysis)
        assert _("Invalid") in str(e.value)
        mock_object.SetProhibitedGateNodes.assert_not_called()

    @pytest.mark.parametrize(
        "retract_time, expected, pos_type_val, neg_type_val",
        [(0, 1, 1, 2), (1, 2, 2, 2), (20.5, 3000, 3, 3)],
    )
    # pylint: disable=R0913, R0917
    def test_create_one_sided_constraints(
        self,
        mock_boundary_conditions,
        mock_object,
        retract_time,
        expected,
        pos_type_val,
        neg_type_val,
    ):
        """
        Test the create_one_sided_constraints method of BoundaryConditions class.
        """
        nodes = Mock(spec=EntList)
        nodes.ent_list = Mock()
        ptrans = Mock(spec=Vector)
        ptrans.vector = Mock()
        ntrans = Mock(spec=Vector)
        ntrans.vector = Mock()
        ptrans_types = Mock(spec=Vector)
        ptrans_types.vector = Mock()
        ptrans_types.x = pos_type_val
        ptrans_types.y = pos_type_val
        ptrans_types.z = pos_type_val
        ntrans_types = Mock(spec=Vector)
        ntrans_types.vector = Mock()
        ntrans_types.x = neg_type_val
        ntrans_types.y = neg_type_val
        ntrans_types.z = neg_type_val
        mock_object.CreateOneSidedConstraints.return_value = expected
        mock_object.CreateOneSidedConstraints2.return_value = expected
        result = mock_boundary_conditions.create_one_sided_constraints(
            nodes, ptrans, ntrans, ptrans_types, ntrans_types, retract_time
        )
        assert result == expected
        if retract_time == 0:
            mock_object.CreateOneSidedConstraints.assert_called_once_with(
                nodes.ent_list,
                ptrans.vector,
                ntrans.vector,
                ptrans_types.vector,
                ntrans_types.vector,
            )
        else:
            mock_object.CreateOneSidedConstraints2.assert_called_once_with(
                nodes.ent_list,
                ptrans.vector,
                ntrans.vector,
                ptrans_types.vector,
                ntrans_types.vector,
                retract_time,
            )

    @pytest.mark.parametrize(
        "nodes, ptrans, ntrans, ptrans_types, ntrans_types, retract_time",
        [
            (x, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), 0.1)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), x, Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), 0.1)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), x, Mock(spec=Vector), Mock(spec=Vector), 0.1)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), Mock(spec=Vector), x, Mock(spec=Vector), 0.1)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (Mock(spec=EntList), Mock(spec=Vector), Mock(spec=Vector), Mock(spec=Vector), x, 0.1)
            for x in ["", 1.5, 1, True, "abc"]
        ]
        + [
            (
                Mock(spec=EntList),
                Mock(spec=Vector),
                Mock(spec=Vector),
                Mock(spec=Vector),
                Mock(spec=Vector),
                x,
            )
            for x in ["", True, "abc"]
        ],
    )
    # pylint: disable=R0913, R0917
    def test_create_one_sided_constraints_invalid(
        self,
        mock_boundary_conditions,
        mock_object,
        nodes,
        ptrans,
        ntrans,
        ptrans_types,
        ntrans_types,
        retract_time,
        _,
    ):
        """
        Test the create_one_sided_constraints method with invalid parameters.
        """
        if isinstance(ptrans_types, Vector):
            ptrans_types.x = Mock()
            ptrans_types.y = Mock()
            ptrans_types.z = Mock()
        if isinstance(ntrans_types, Vector):
            ntrans_types.x = Mock()
            ntrans_types.y = Mock()
            ntrans_types.z = Mock()
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.create_one_sided_constraints(
                nodes, ptrans, ntrans, ptrans_types, ntrans_types, retract_time
            )
        assert _("Invalid") in str(e.value)
        mock_object.CreateOneSidedConstraints.assert_not_called()

    @pytest.mark.parametrize(
        "prop_id, prop_type, expected", [(1, 2, None), (2, 9, 3), (3, 7, 4), (4, 2, 5), (5, 1, 6)]
    )
    # pylint: disable=R0913, R0917
    def test_find_property(
        self, mock_boundary_conditions, mock_object, prop_id, prop_type, expected
    ):
        """
        Test the find_property method of BoundaryConditions class.
        """
        mock_object.FindProperty.return_value = expected
        result = mock_boundary_conditions.find_property(prop_type, prop_id)
        if expected is not None:
            assert result.prop == expected
            assert isinstance(result, Property)
        else:
            assert result == expected
        mock_object.FindProperty.assert_called_once_with(prop_type, prop_id)

    @pytest.mark.parametrize(
        "prop_type, prop_id",
        [(x, 2) for x in [None, "", 1.5, True, "abc"]]
        + [(1, x) for x in [None, "", 1.5, True, "abc"]],
    )
    def test_find_property_invalid(
        self, mock_boundary_conditions, mock_object, prop_type, prop_id, _
    ):
        """
        Test the find_property method of BoundaryConditions class with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_conditions.find_property(prop_type, prop_id)
        assert _("Invalid") in str(e.value)
        mock_object.FindProperty.assert_not_called()
