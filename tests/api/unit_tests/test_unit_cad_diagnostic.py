"""
Test for CADDiagnostic Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import CADDiagnostic, EntList
from tests.api.unit_tests.conftest import VALID_MOCK, INVALID_MOCK
from tests.conftest import pad_and_zip, VALID_BOOL


@pytest.mark.unit
class TestUnitCADDiagnostic:
    """
    Test suite for the CADDiagnostic class.
    """

    @pytest.fixture
    def mock_cad_diagnostic(self, mock_object) -> CADDiagnostic:
        """
        Fixture to create a mock instance of CADDiagnostic.
        Args:
            mock_object: Mock object for the CADDiagnostic dependency.
        Returns:
            CADDiagnostic: An instance of CADDiagnostic with the mock object.
        """
        return CADDiagnostic(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            ("Compute", "compute", (x,), (x.ent_list,), bool, y)
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            (
                "GetEdgeEdgeIntersectDiagnostic",
                "get_edge_edge_intersect_diagnostic",
                (x, y, z),
                (x.integer_array, y.integer_array, z.double_array),
                bool,
                a,
            )
            for x, y, z, a in pad_and_zip(
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_BOOL,
            )
        ]
        + [
            (
                "GetFaceFaceIntersectDiagnostic",
                "get_face_face_intersect_diagnostic",
                (x, y, z),
                (x.integer_array, y.integer_array, z.double_array),
                bool,
                a,
            )
            for x, y, z, a in pad_and_zip(
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
                VALID_BOOL,
            )
        ]
        + [
            (
                "GetEdgeSelfIntersectDiagnostic",
                "get_edge_self_intersect_diagnostic",
                (x, y),
                (x.integer_array, y.double_array),
                bool,
                z,
            )
            for x, y, z in pad_and_zip(
                VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL
            )
        ]
        + [
            (
                "GetFaceSelfIntersectDiagnostic",
                "get_face_self_intersect_diagnostic",
                (x, y),
                (x.integer_array, y.double_array),
                bool,
                z,
            )
            for x, y, z in pad_and_zip(
                VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL
            )
        ]
        + [
            (
                "GetNonManifoldBodyDiagnostic",
                "get_non_manifold_body_diagnostic",
                (x,),
                (x.integer_array,),
                bool,
                y,
            )
            for x, y in pad_and_zip(VALID_MOCK.INTEGER_ARRAY, VALID_BOOL)
        ]
        + [
            (
                "GetNonManifoldEdgeDiagnostic",
                "get_non_manifold_edge_diagnostic",
                (x,),
                (x.integer_array,),
                bool,
                y,
            )
            for x, y in pad_and_zip(VALID_MOCK.INTEGER_ARRAY, VALID_BOOL)
        ]
        + [
            (
                "GetToxicBodyDiagnostic",
                "get_toxic_body_diagnostic",
                (x,),
                (x.integer_array,),
                bool,
                y,
            )
            for x, y in pad_and_zip(VALID_MOCK.INTEGER_ARRAY, VALID_BOOL)
        ]
        + [
            (
                "GetSliverFaceDiagnostic",
                "get_sliver_face_diagnostic",
                (x,),
                (x.integer_array,),
                bool,
                y,
            )
            for x, y in pad_and_zip(VALID_MOCK.INTEGER_ARRAY, VALID_BOOL)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions(
        self,
        mock_cad_diagnostic: CADDiagnostic,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test the functions of the CADDiagnostic class.

        Args:
            mock_cad_diagnostic: The mock instance of CADDiagnostic.
            mock_object: The mock object for the CADDiagnostic dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments after processing.
            return_type: Expected return type of the function.
            return_value: Expected return value of the function.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_cad_diagnostic, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("Compute", "compute", (x,)) for x in pad_and_zip(INVALID_MOCK)]
        + [
            ("GetEdgeEdgeIntersectDiagnostic", "get_edge_edge_intersect_diagnostic", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_MOCK, INVALID_MOCK, INVALID_MOCK)
        ]
        + [
            ("GetFaceFaceIntersectDiagnostic", "get_face_face_intersect_diagnostic", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_MOCK, INVALID_MOCK, INVALID_MOCK)
        ]
        + [
            ("GetEdgeSelfIntersectDiagnostic", "get_edge_self_intersect_diagnostic", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, INVALID_MOCK)
        ]
        + [
            ("GetFaceSelfIntersectDiagnostic", "get_face_self_intersect_diagnostic", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, INVALID_MOCK)
        ]
        + [
            ("GetNonManifoldBodyDiagnostic", "get_non_manifold_body_diagnostic", (x,))
            for x in pad_and_zip(INVALID_MOCK)
        ]
        + [
            ("GetNonManifoldEdgeDiagnostic", "get_non_manifold_edge_diagnostic", (x,))
            for x in pad_and_zip(INVALID_MOCK)
        ]
        + [
            ("GetToxicBodyDiagnostic", "get_toxic_body_diagnostic", (x,))
            for x in pad_and_zip(INVALID_MOCK)
        ]
        + [
            ("GetSliverFaceDiagnostic", "get_sliver_face_diagnostic", (x,))
            for x in pad_and_zip(INVALID_MOCK)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_type(
        self, mock_cad_diagnostic: CADDiagnostic, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the functions of the CADDiagnostic class with invalid types.

        Args:
            mock_cad_diagnostic: The mock instance of CADDiagnostic.
            mock_object: The mock object for the CADDiagnostic dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: Arguments to be passed to the function.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_cad_diagnostic, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, expected_return, type_instance",
        [("CreateEntityList", "create_entity_list", EntList, VALID_MOCK.ENT_LIST, "ent_list")],
    )
    # pylint: disable-next=R0913, R0917
    def test_function_return_classes(
        self,
        mock_cad_diagnostic: CADDiagnostic,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        expected_return,
        type_instance,
    ):
        """
        Test the method of the CADDiagnostic class.

        Args:
            mock_cad_diagnostic: The mock instance of CADDiagnostic.
            mock_object: The mock object for the CADDiagnostic dependency.
        """
        expected_return_instance = getattr(expected_return, type_instance)
        setattr(mock_object, pascal_name, expected_return_instance)
        result = getattr(mock_cad_diagnostic, property_name)()
        assert isinstance(result, return_type)
        assert getattr(result, type_instance) == expected_return_instance

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("CreateEntityList", "create_entity_list")]
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self, mock_cad_diagnostic: CADDiagnostic, mock_object, pascal_name, property_name
    ):
        """
        Test the return value of the function is None.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_cad_diagnostic, property_name)()
        assert result is None
