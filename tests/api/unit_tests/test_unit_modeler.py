# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for Modeler Wrapper Class of moldflow-api module.
"""

from unittest.mock import patch
from win32com.client import VARIANT
import pythoncom
import pytest
from moldflow import Modeler
from moldflow.boundary_list import BoundaryList
from moldflow.common import CurveInitPosition, LCSType
from moldflow.ent_list import EntList
from moldflow.logger import set_is_logging
from moldflow.prop import Property
from tests.api.unit_tests.conftest import INVALID_MOCK_WITH_NONE, VALID_MOCK
from tests.conftest import (
    INVALID_INT,
    INVALID_BOOL,
    INVALID_FLOAT,
    INVALID_STR,
    NEGATIVE_INT,
    NON_POSITIVE_INT,
    VALID_INT,
    NON_NEGATIVE_INT,
    POSITIVE_INT,
    VALID_STR,
    pad_and_zip,
    VALID_BOOL,
    VALID_FLOAT,
    NON_NEGATIVE_FLOAT,
    POSITIVE_FLOAT,
)

CUSTOM_MOCK = INVALID_MOCK_WITH_NONE
CUSTOM_MOCK.remove(None)


@pytest.mark.unit
class TestUnitModeler:
    """
    Test suite for the Modeler class.
    """

    set_is_logging(True)

    @pytest.fixture
    def mock_modeler(self, mock_object) -> Modeler:
        """
        Fixture to create a mock instance of Modeler.
        Args:
            mock_object: Mock object for the Modeler dependency.
        Returns:
            Modeler: An instance of Modeler with the mock object.
        """
        return Modeler(mock_object)

    @pytest.mark.parametrize(
        "property_name, pascal_name, return_type, class_name, expected",
        [("center_lines", "CenterLines", bool, None, a) for a in pad_and_zip(VALID_BOOL)]
        + [
            ("create_entity_list", "CreateEntityList", EntList, "ent_list", a)
            for a in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("create_entity_list", "CreateEntityList", None, None, a) for a in pad_and_zip([None])]
        + [
            ("create_boundary_list", "CreateBoundaryList", BoundaryList, "boundary_list", a)
            for a in pad_and_zip(VALID_MOCK.BOUNDARY_LIST)
        ]
        + [
            ("create_boundary_list", "CreateBoundaryList", None, None, a)
            for a in pad_and_zip([None])
        ],
    )
    # pylint: disable=R0913, R0917
    def test_no_input_bool_return(
        self,
        mock_modeler,
        mock_object,
        property_name,
        pascal_name,
        return_type,
        class_name,
        expected,
    ):
        """
        Test for the no input class return.
        """
        setattr(mock_object, pascal_name, expected)
        result = getattr(mock_modeler, property_name)()
        if return_type is not None:
            assert isinstance(result, return_type)
        if class_name:
            assert getattr(result, class_name) == expected
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args, return_type, class_return, expected",
        [
            ("get_new_edited_cad_study_name", "GetNewEditedCadStudyName", (a,), (a,), str, None, b)
            for a, b in pad_and_zip(VALID_INT, VALID_STR)
        ]
        + [
            (
                "modified_with_inventor_fusion",
                "ModifiedWithInventorFusion",
                (a,),
                (a.ent_list,),
                int,
                None,
                b,
            )
            for a, b in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_INT)
        ]
        + [
            ("break_curves", "BreakCurves", (a, b), (a.ent_list, b.ent_list), bool, None, c)
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            ("set_property", "SetProperty", (a, b), (a.ent_list, b.prop), bool, None, c)
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, VALID_BOOL)
        ]
        + [
            (
                "create_hole_by_boundary",
                "CreateHoleByBoundary",
                (a, b),
                (a.ent_list, b.ent_list),
                bool,
                None,
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            (
                "create_hole_by_nodes",
                "CreateHoleByNodes",
                (a, b),
                (a.ent_list, b.ent_list),
                bool,
                None,
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            (
                "create_hole_by_ruling",
                "CreateHoleByRuling",
                (a, b, c),
                (a.ent_list, b.ent_list, c.ent_list),
                bool,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_BOOL
            )
        ]
        + [
            (
                "create_hole_by_extrusion",
                "CreateHoleByExtrusion",
                (a, b, c),
                (a.ent_list, b.ent_list, c.vector),
                bool,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_BOOL
            )
        ]
        + [
            (
                "reflect",
                "Reflect",
                (a, b, c, d, e),
                (a.ent_list, b.vector, c.vector, d, e),
                bool,
                None,
                f,
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            (
                "scale",
                "Scale",
                (a, b, c, d, e),
                (a.ent_list, b.vector, c.vector, d, e),
                bool,
                None,
                f,
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            (
                "translate",
                "Translate",
                (a, b, c, d, e),
                (a.ent_list, b.vector, c, d, e),
                bool,
                None,
                f,
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                NON_NEGATIVE_INT,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            (
                "rotate",
                "Rotate",
                (a, b, c, d, e, f, g),
                (a.ent_list, b.vector, c.vector, d, e, f, g),
                bool,
                None,
                h,
            )
            for a, b, c, d, e, f, g, h in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                POSITIVE_FLOAT,
                VALID_BOOL,
                NON_NEGATIVE_INT,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            (
                "rotate_3_pts",
                "Rotate3Pts",
                (a, b, c, d, e, f),
                (a.ent_list, b.vector, c.vector, d.vector, e, f),
                bool,
                None,
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("activate_lcs", "ActivateLCS", (a, b, c), (a.ent_list, b, c.value), bool, None, d)
            for a, b, c, d in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, LCSType, VALID_BOOL)
        ]
        + [
            (
                "scale_mesh_density",
                "ScaleMeshDensity",
                (a, b, c),
                (a.ent_list, b.boundary_list, c),
                bool,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.BOUNDARY_LIST, POSITIVE_FLOAT, VALID_BOOL
            )
        ]
        + [
            (
                "is_inventor_fusion_cad_edit_done",
                "IsInventorFusionCadEditDone",
                (a,),
                (a,),
                bool,
                None,
                b,
            )
            for a, b in pad_and_zip(VALID_INT, VALID_BOOL)
        ]
        + [
            (
                "is_inventor_fusion_cad_edit_aborted",
                "IsInventorFusionCadEditAborted",
                (a,),
                (a,),
                bool,
                None,
                b,
            )
            for a, b in pad_and_zip(VALID_INT, VALID_BOOL)
        ]
        + [
            (
                "set_mesh_size",
                "SetMeshSize2",
                (a, b, c, d, e, f),
                (a, b.ent_list, c.boundary_list, d, e.ent_list, f),
                bool,
                None,
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                NON_NEGATIVE_FLOAT,
                VALID_MOCK.ENT_LIST,
                VALID_MOCK.BOUNDARY_LIST,
                POSITIVE_FLOAT,
                VALID_MOCK.ENT_LIST,
                NON_NEGATIVE_INT,
                VALID_BOOL,
            )
        ]
        + [
            ("find_property", "FindProperty", (a, b), (a, b), Property, "prop", c)
            for a, b, c in pad_and_zip(VALID_INT, VALID_INT, VALID_MOCK.PROP)
        ]
        + [
            ("find_property", "FindProperty", (a, b), (a, b), None, None, c)
            for a, b, c in pad_and_zip(VALID_INT, VALID_INT, [None])
        ]
        + [
            ("create_node_by_xyz", "CreateNodeByXYZ", (a,), (a.vector,), EntList, "ent_list", b)
            for a, b in pad_and_zip(VALID_MOCK.VECTOR, VALID_MOCK.ENT_LIST)
        ]
        + [
            ("create_node_by_xyz", "CreateNodeByXYZ", (a,), (a.vector,), None, None, b)
            for a, b in pad_and_zip(VALID_MOCK.VECTOR, [None])
        ]
        + [
            (
                "create_nodes_between",
                "CreateNodesBetween",
                (a, b, c),
                (a.vector, b.vector, c),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, POSITIVE_INT, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_nodes_between",
                "CreateNodesBetween",
                (a, b, c),
                (a.vector, b.vector, c),
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, POSITIVE_INT, [None]
            )
        ]
        + [
            (
                "create_nodes_by_offset",
                "CreateNodesByOffset",
                (a, b, c),
                (a.vector, b.vector, c),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, POSITIVE_INT, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_nodes_by_offset",
                "CreateNodesByOffset",
                (a, b, c),
                (a.vector, b.vector, c),
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, POSITIVE_INT, [None]
            )
        ]
        + [
            (
                "create_nodes_by_divide",
                "CreateNodesByDivide",
                (a, b, c),
                (a.ent_list, b, c),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, POSITIVE_INT, VALID_BOOL, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_nodes_by_divide",
                "CreateNodesByDivide",
                (a, b, c),
                (a.ent_list, b, c),
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(VALID_MOCK.ENT_LIST, POSITIVE_INT, VALID_BOOL, [None])
        ]
        + [
            (
                "create_node_by_intersect",
                "CreateNodeByIntersect",
                (a, b, c),
                (a.ent_list, b.ent_list, c.vector),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_node_by_intersect",
                "CreateNodeByIntersect",
                (a, b, c),
                (a.ent_list, b.ent_list, c.vector),
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, [None]
            )
        ]
        + [
            (
                "create_line",
                "CreateLine",
                (a, b, c, d, e),
                (a.vector, b.vector, c, d.prop, e),
                EntList,
                "ent_list",
                f,
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_MOCK.PROP,
                VALID_BOOL,
                VALID_MOCK.ENT_LIST,
            )
        ]
        + [
            (
                "create_line",
                "CreateLine",
                (a, b, c, d, e),
                (a.vector, b.vector, c, d.prop, e),
                None,
                None,
                f,
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_MOCK.PROP,
                VALID_BOOL,
                [None],
            )
        ]
        + [
            (
                "create_arc_by_angle",
                "CreateArcByAngle",
                (a, b, c, d, e, f),
                (a.vector, b, c, d, e.prop, f),
                EntList,
                "ent_list",
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.VECTOR,
                POSITIVE_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_MOCK.PROP,
                VALID_BOOL,
                VALID_MOCK.ENT_LIST,
            )
        ]
        + [
            (
                "create_arc_by_angle",
                "CreateArcByAngle",
                (a, b, c, d, e, f),
                (a.vector, b, c, d, e.prop, f),
                None,
                None,
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.VECTOR,
                POSITIVE_FLOAT,
                VALID_FLOAT,
                VALID_FLOAT,
                VALID_MOCK.PROP,
                VALID_BOOL,
                [None],
            )
        ]
        + [
            (
                "create_arc_by_points",
                "CreateArcByPoints",
                (a, b, c, d, e, f),
                (a.vector, b.vector, c.vector, d, e.prop, f),
                EntList,
                "ent_list",
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_MOCK.PROP,
                VALID_BOOL,
                VALID_MOCK.ENT_LIST,
            )
        ]
        + [
            (
                "create_arc_by_points",
                "CreateArcByPoints",
                (a, b, c, d, e, f),
                (a.vector, b.vector, c.vector, d, e.prop, f),
                None,
                None,
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_MOCK.VECTOR,
                VALID_BOOL,
                VALID_MOCK.PROP,
                VALID_BOOL,
                [None],
            )
        ]
        + [
            (
                "create_curve_by_connect",
                "CreateCurveByConnect",
                (a, b, c, d, e, f),
                (a.ent_list, b.value, c.ent_list, d.value, e, f.prop),
                EntList,
                "ent_list",
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_FLOAT,
                VALID_MOCK.PROP,
                VALID_MOCK.ENT_LIST,
            )
        ]
        + [
            (
                "create_curve_by_connect",
                "CreateCurveByConnect",
                (a, b, c, d, e, f),
                (a.ent_list, b.value, c.ent_list, d.value, e, f.prop),
                None,
                None,
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_FLOAT,
                VALID_MOCK.PROP,
                [None],
            )
        ]
        + [
            (
                "create_curve_by_connect",
                "CreateCurveByConnect",
                (a, b.value, c, d.value, e, f),
                (a.ent_list, b.value, c.ent_list, d.value, e, f.prop),
                EntList,
                "ent_list",
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_FLOAT,
                VALID_MOCK.PROP,
                VALID_MOCK.ENT_LIST,
            )
        ]
        + [
            (
                "create_curve_by_connect",
                "CreateCurveByConnect",
                (a, b.value, c, d.value, e, f),
                (a.ent_list, b.value, c.ent_list, d.value, e, f.prop),
                None,
                None,
                g,
            )
            for a, b, c, d, e, f, g in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_MOCK.ENT_LIST,
                CurveInitPosition,
                VALID_FLOAT,
                VALID_MOCK.PROP,
                [None],
            )
        ]
        + [
            (
                "create_spline",
                "CreateSpline",
                (a, b, c),
                (a.vector_array, b.prop, c),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR_ARRAY, VALID_MOCK.PROP, VALID_BOOL, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            ("create_spline", "CreateSpline", (a, b, c), (a.vector_array, b.prop, c), None, None, d)
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR_ARRAY, VALID_MOCK.PROP, VALID_BOOL, [None]
            )
        ]
        + [
            (
                "create_region_by_boundary",
                "CreateRegionByBoundary",
                (a, b),
                (a.ent_list, b.prop),
                EntList,
                "ent_list",
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, VALID_MOCK.ENT_LIST)
        ]
        + [
            (
                "create_region_by_boundary",
                "CreateRegionByBoundary",
                (a, b),
                (a.ent_list, b.prop),
                None,
                None,
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, [None])
        ]
        + [
            (
                "create_region_by_nodes",
                "CreateRegionByNodes",
                (a, b),
                (a.ent_list, b.prop),
                EntList,
                "ent_list",
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, VALID_MOCK.ENT_LIST)
        ]
        + [
            (
                "create_region_by_nodes",
                "CreateRegionByNodes",
                (a, b),
                (a.ent_list, b.prop),
                None,
                None,
                c,
            )
            for a, b, c in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, [None])
        ]
        + [
            (
                "create_region_by_ruling",
                "CreateRegionByRuling",
                (a, b, c),
                (a.ent_list, b.ent_list, c.prop),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_region_by_ruling",
                "CreateRegionByRuling",
                (a, b, c),
                (a.ent_list, b.ent_list, c.prop),
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, [None]
            )
        ]
        + [
            (
                "create_region_by_extrusion",
                "CreateRegionByExtrusion",
                (a, b, c),
                (a.ent_list, b.vector, c.prop),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_MOCK.PROP, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_region_by_extrusion",
                "CreateRegionByExtrusion",
                (a, b, c),
                (a.ent_list, b.vector, c.prop),
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_MOCK.PROP, [None]
            )
        ]
        + [
            (
                "create_lcs_by_points",
                "CreateLCSByPoints",
                (a, b, c),
                (a.vector, b.vector, c.vector),
                EntList,
                "ent_list",
                d,
            )
            for a, b, c, d in pad_and_zip(
                VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, VALID_MOCK.ENT_LIST
            )
        ]
        + [
            (
                "create_lcs_by_points",
                "CreateLCSByPoints",
                (a, b, c),
                [a.vector, b, c],
                None,
                None,
                d,
            )
            for a, b, c, d in pad_and_zip(VALID_MOCK.VECTOR, [None], [None], [None])
        ],
    )
    # pylint: disable=R0913,R0917
    def test_function(
        self,
        mock_modeler,
        mock_object,
        property_name,
        pascal_name,
        args,
        passed_args,
        return_type,
        class_return,
        expected,
    ):
        """
        Test modeler functions methods with return.
        """

        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            getattr(mock_object, pascal_name).return_value = expected
            result = getattr(mock_modeler, property_name)(*args)

            for n, arg in enumerate(passed_args):
                if arg is None:
                    passed_args[n] = mock_func()

            getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
            if return_type is not None:
                assert isinstance(result, return_type)
            if class_return:
                assert getattr(result, class_return) == expected
            else:
                assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            ("create_node_by_xyz", "CreateNodeByXYZ", (VALID_MOCK.VECTOR,), x)
            for x in ((index, value) for index, value in enumerate([INVALID_MOCK_WITH_NONE]))
        ]
        + [
            (
                "create_nodes_between",
                "CreateNodesBetween",
                (VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, POSITIVE_INT[0]),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_INT]
                )
            )
        ]
        + [
            (
                "create_nodes_by_offset",
                "CreateNodesByOffset",
                (VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, POSITIVE_INT[0]),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_INT]
                )
            )
        ]
        + [
            (
                "create_nodes_by_divide",
                "CreateNodesByDivide",
                (VALID_MOCK.ENT_LIST, POSITIVE_INT[0], VALID_BOOL[0]),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_INT, INVALID_BOOL])
            )
        ]
        + [
            (
                "create_node_by_intersect",
                "CreateNodeByIntersect",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "create_line",
                "CreateLine",
                (
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    VALID_MOCK.PROP,
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "create_arc_by_angle",
                "CreateArcByAngle",
                (
                    VALID_MOCK.VECTOR,
                    POSITIVE_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_MOCK.PROP,
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "create_arc_by_points",
                "CreateArcByPoints",
                (
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    VALID_MOCK.PROP,
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "create_curve_by_connect",
                "CreateCurveByConnect",
                (
                    VALID_MOCK.ENT_LIST,
                    CurveInitPosition.START,
                    VALID_MOCK.ENT_LIST,
                    CurveInitPosition.END,
                    VALID_FLOAT[0],
                    VALID_MOCK.PROP,
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_INT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_INT,
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "create_spline",
                "CreateSpline",
                (VALID_MOCK.VECTOR_ARRAY, VALID_MOCK.PROP, VALID_BOOL[0]),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "create_region_by_boundary",
                "CreateRegionByBoundary",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.PROP),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "create_region_by_nodes",
                "CreateRegionByNodes",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.PROP),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "create_region_by_ruling",
                "CreateRegionByRuling",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.PROP),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "create_region_by_extrusion",
                "CreateRegionByExtrusion",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR, VALID_MOCK.PROP),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "create_lcs_by_points",
                "CreateLCSByPoints",
                (VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, VALID_MOCK.VECTOR),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, CUSTOM_MOCK, CUSTOM_MOCK])
            )
        ]
        + [
            ("find_property", "FindProperty", (VALID_INT[0], VALID_INT[0]), x)
            for x in ((index, value) for index, value in enumerate([INVALID_INT, INVALID_INT]))
        ]
        + [
            ("break_curves", "BreakCurves", (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST), x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            ("set_property", "SetProperty", (VALID_MOCK.ENT_LIST, VALID_MOCK.PROP), x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "create_hole_by_boundary",
                "CreateHoleByBoundary",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "create_hole_by_nodes",
                "CreateHoleByNodes",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "create_hole_by_ruling",
                "CreateHoleByRuling",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "create_hole_by_extrusion",
                "CreateHoleByExtrusion",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_MOCK.VECTOR),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE]
                )
            )
        ]
        + [
            (
                "reflect",
                "Reflect",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "scale",
                "Scale",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "translate",
                "Translate",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    NON_NEGATIVE_INT[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_INT,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "rotate",
                "Rotate",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    POSITIVE_FLOAT[0],
                    VALID_BOOL[0],
                    NON_NEGATIVE_INT[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_FLOAT,
                        INVALID_BOOL,
                        INVALID_INT,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "rotate_3_pts",
                "Rotate3Pts",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "activate_lcs",
                "ActivateLCS",
                (VALID_MOCK.ENT_LIST, VALID_BOOL[0], LCSType.COORDINATE_SYSTEM),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_BOOL, INVALID_STR])
            )
        ]
        + [
            (
                "scale_mesh_density",
                "ScaleMeshDensity",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.BOUNDARY_LIST, POSITIVE_FLOAT[0]),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_FLOAT]
                )
            )
        ]
        + [
            ("is_inventor_fusion_cad_edit_done", "IsInventorFusionCadEditDone", (VALID_INT[0],), x)
            for x in ((index, value) for index, value in enumerate([INVALID_INT]))
        ]
        + [
            (
                "is_inventor_fusion_cad_edit_aborted",
                "IsInventorFusionCadEditAborted",
                (VALID_INT[0],),
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_INT]))
        ]
        + [
            (
                "set_mesh_size",
                "SetMeshSize2",
                (
                    POSITIVE_FLOAT[0],
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.BOUNDARY_LIST,
                    POSITIVE_FLOAT[0],
                    VALID_MOCK.ENT_LIST,
                    NON_NEGATIVE_INT[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_INT,
                    ]
                )
            )
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_inputs(
        self, mock_modeler, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test modeler functions methods with invalid inputs.
        """
        args = list(args)
        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(TypeError) as e:
                getattr(mock_modeler, property_name)(*tuple(args))
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            (
                "translate",
                "Translate",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_BOOL[0],
                    NON_NEGATIVE_INT[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in ((index, value) for index, value in enumerate([[], [], [], NEGATIVE_INT]))
        ]
        + [
            (
                "rotate",
                "Rotate",
                (
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.VECTOR,
                    VALID_MOCK.VECTOR,
                    VALID_FLOAT[0],
                    VALID_BOOL[0],
                    VALID_INT[0],
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([[], [], [], NEGATIVE_INT, [], NEGATIVE_INT])
            )
        ]
        + [
            (
                "set_mesh_size",
                "SetMeshSize2",
                (
                    POSITIVE_FLOAT[0],
                    VALID_MOCK.ENT_LIST,
                    VALID_MOCK.BOUNDARY_LIST,
                    POSITIVE_FLOAT[0],
                    VALID_MOCK.ENT_LIST,
                    VALID_INT[0],
                ),
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [NON_POSITIVE_INT, [], [], NON_POSITIVE_INT, [], NEGATIVE_INT]
                )
            )
        ]
        + [
            (
                "create_nodes_between",
                "CreateNodesBetween",
                (VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, VALID_INT[0]),
                x,
            )
            for x in ((index, value) for index, value in enumerate([[], [], NON_POSITIVE_INT]))
        ]
        + [
            (
                "create_nodes_by_offset",
                "CreateNodesByOffset",
                (VALID_MOCK.VECTOR, VALID_MOCK.VECTOR, VALID_INT[0]),
                x,
            )
            for x in ((index, value) for index, value in enumerate([[], [], NON_POSITIVE_INT]))
        ]
        + [
            (
                "create_nodes_by_divide",
                "CreateNodesByDivide",
                (VALID_MOCK.ENT_LIST, POSITIVE_INT[0], VALID_BOOL[0]),
                x,
            )
            for x in ((index, value) for index, value in enumerate([[], NON_POSITIVE_INT]))
        ]
        + [
            (
                "create_arc_by_angle",
                "CreateArcByAngle",
                (
                    VALID_MOCK.VECTOR,
                    POSITIVE_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_MOCK.PROP,
                    VALID_BOOL[0],
                ),
                x,
            )
            for x in ((index, value) for index, value in enumerate([[], NON_POSITIVE_INT]))
        ]
        + [
            (
                "scale_mesh_density",
                "ScaleMeshDensity",
                (VALID_MOCK.ENT_LIST, VALID_MOCK.BOUNDARY_LIST, POSITIVE_FLOAT[0]),
                x,
            )
            for x in ((index, value) for index, value in enumerate([[], [], NON_POSITIVE_INT]))
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_value(
        self, mock_modeler, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test modeler functions methods with invalid value.
        """
        args = list(args)
        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(ValueError) as e:
                getattr(mock_modeler, property_name)(*tuple(args))
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()
