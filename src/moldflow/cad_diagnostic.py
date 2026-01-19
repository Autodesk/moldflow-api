"""
Usage:
    CADDiagnostic Class API Wrapper
"""

from .logger import process_log, LogMessage
from .double_array import DoubleArray
from .ent_list import EntList
from .integer_array import IntegerArray
from .helper import check_type, coerce_optional_dispatch


class CADDiagnostic:
    """
    Wrapper for CADDiagnostic class of Moldflow Synergy.
    """

    def __init__(self, _cad_diagnostic):
        """
        Initialize the CADDiagnostic with a CADDiagnostic instance from COM.

        Args:
            _cad_diagnostic: The CADDiagnostic instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="CADDiagnostic")
        self.cad_diagnostic = _cad_diagnostic

    def create_entity_list(self) -> EntList:
        """
        Creates an empty EntList object
        """
        result = self.cad_diagnostic.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def compute(self, bodies: EntList | None) -> bool:
        """
        CAD quality assessment to identify any potential geometric issues in the CAD model.
        This function will identify potential geometric difficulties that may include :
        - edge-to-edge intersection
        - face-to-face intersection
        - edge self intersection
        - face self intersection
        - non-manifold bodies
        - non manifold edges
        - toxic bodies
        - sliver faces

        Args:
            bodies (EntList): The bodies to compute CAD diagnostics for.

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="compute")
        if bodies is not None:
            check_type(bodies, EntList)
        return self.cad_diagnostic.Compute(coerce_optional_dispatch(bodies, "ent_list"))

    def get_edge_edge_intersect_diagnostic(
        self,
        edge_id_pair1: IntegerArray | None,
        edge_id_pair2: IntegerArray | None,
        intersect_coordinates: DoubleArray | None,
    ) -> bool:
        """
        Retrieves intersecting CAD edge-to-edge information

        Args:
            edge_id_pair1 (IntegerArray): The first set of edge identifiers
            edge_id_pair2 (IntegerArray): The second set of edge identifiers
            intersect_coordinates (DoubleArray): The intersected coordinates

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_edge_edge_intersect_diagnostic"
        )
        if edge_id_pair1 is not None:
            check_type(edge_id_pair1, IntegerArray)
        if edge_id_pair2 is not None:
            check_type(edge_id_pair2, IntegerArray)
        if intersect_coordinates is not None:
            check_type(intersect_coordinates, DoubleArray)
        return self.cad_diagnostic.GetEdgeEdgeIntersectDiagnostic(
            coerce_optional_dispatch(edge_id_pair1, "integer_array"),
            coerce_optional_dispatch(edge_id_pair2, "integer_array"),
            coerce_optional_dispatch(intersect_coordinates, "double_array"),
        )

    def get_face_face_intersect_diagnostic(
        self,
        face_id_pair1: IntegerArray | None,
        face_id_pair2: IntegerArray | None,
        intersect_coordinates: DoubleArray | None,
    ) -> bool:
        """
        Retrieves intersecting CAD face-to-face information

        Args:
            face_id_pair1 (IntegerArray): The first set of face identifiers
            face_id_pair2 (IntegerArray): The second set of face identifiers
            intersect_coordinates (DoubleArray): The intersected coordinates

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_face_face_intersect_diagnostic"
        )
        if face_id_pair1 is not None:
            check_type(face_id_pair1, IntegerArray)
        if face_id_pair2 is not None:
            check_type(face_id_pair2, IntegerArray)
        if intersect_coordinates is not None:
            check_type(intersect_coordinates, DoubleArray)
        return self.cad_diagnostic.GetFaceFaceIntersectDiagnostic(
            coerce_optional_dispatch(face_id_pair1, "integer_array"),
            coerce_optional_dispatch(face_id_pair2, "integer_array"),
            coerce_optional_dispatch(intersect_coordinates, "double_array"),
        )

    def get_edge_self_intersect_diagnostic(
        self, edge_id: IntegerArray | None, intersect_coordinates: DoubleArray | None
    ) -> bool:
        """
        Retrieves self-intersecting CAD edges

        Args:
            edge_id (IntegerArray): The edge identifiers
            intersect_coordinates (DoubleArray): The intersected coordinates

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_edge_self_intersect_diagnostic"
        )
        if edge_id is not None:
            check_type(edge_id, IntegerArray)
        if intersect_coordinates is not None:
            check_type(intersect_coordinates, DoubleArray)
        return self.cad_diagnostic.GetEdgeSelfIntersectDiagnostic(
            coerce_optional_dispatch(edge_id, "integer_array"),
            coerce_optional_dispatch(intersect_coordinates, "double_array"),
        )

    def get_face_self_intersect_diagnostic(
        self, face_id: IntegerArray | None, intersect_coordinates: DoubleArray | None
    ) -> bool:
        """
        Retrieves self-intersecting CAD faces

        Args:
            face_id (IntegerArray): The face identifiers
            intersect_coordinates (DoubleArray): The intersected coordinates

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_face_self_intersect_diagnostic"
        )
        if face_id is not None:
            check_type(face_id, IntegerArray)
        if intersect_coordinates is not None:
            check_type(intersect_coordinates, DoubleArray)
        return self.cad_diagnostic.GetFaceSelfIntersectDiagnostic(
            coerce_optional_dispatch(face_id, "integer_array"),
            coerce_optional_dispatch(intersect_coordinates, "double_array"),
        )

    def get_non_manifold_body_diagnostic(self, body_id: IntegerArray | None) -> bool:
        """
        Retrieves CAD non-manifold bodies

        Args:
            body_id (IntegerArray): The body identifiers

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_non_manifold_bodies_diagnostic"
        )
        if body_id is not None:
            check_type(body_id, IntegerArray)
        return self.cad_diagnostic.GetNonManifoldBodyDiagnostic(
            coerce_optional_dispatch(body_id, "integer_array")
        )

    def get_non_manifold_edge_diagnostic(self, edge_id: IntegerArray | None) -> bool:
        """
        Retrieves non-manifold edges

        Args:
            edge_id (IntegerArray): The edge identifiers

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_non_manifold_edge_diagnostic"
        )
        if edge_id is not None:
            check_type(edge_id, IntegerArray)
        return self.cad_diagnostic.GetNonManifoldEdgeDiagnostic(
            coerce_optional_dispatch(edge_id, "integer_array")
        )

    def get_toxic_body_diagnostic(self, body_id: IntegerArray | None) -> bool:
        """
        Retrieves toxic bodies

        Args:
            body_id (IntegerArray): The body identifiers

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_toxic_body_diagnostic")
        if body_id is not None:
            check_type(body_id, IntegerArray)
        return self.cad_diagnostic.GetToxicBodyDiagnostic(
            coerce_optional_dispatch(body_id, "integer_array")
        )

    def get_sliver_face_diagnostic(self, face_id: IntegerArray | None) -> bool:
        """
        Retrieves sliver faces

        Args:
            face_id (IntegerArray): The face identifiers

        Returns:
            True if operation is successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_sliver_face_diagnostic")
        if face_id is not None:
            check_type(face_id, IntegerArray)
        return self.cad_diagnostic.GetSliverFaceDiagnostic(
            coerce_optional_dispatch(face_id, "integer_array")
        )
