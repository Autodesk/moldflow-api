# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    CADManager Class API Wrapper
"""

from .ent_list import EntList
from .vector import Vector
from .logger import process_log, LogMessage
from .helper import (
    check_type,
    check_optional_type,
    check_and_coerce_optional,
    coerce_optional_dispatch,
)
from .com_proxy import safe_com


class CADManager:
    """
    Wrapper for CADManager class of Moldflow Synergy.
    """

    def __init__(self, _cad_manager):
        """
        Initialize the CADManager with a CADManager instance from COM.

        Args:
            _cad_manager: The CADManager instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="CADManager")
        self.cad_manager = safe_com(_cad_manager)

    def create_entity_list(self) -> EntList:
        """
        Creates an empty EntList object
        When using this function, it will first ask for result invalidation.
        If you want to select entities without checking result, use StudyDoc.create_entity_list().

        Returns:
            EntList: The new entity list.
        """
        result = self.cad_manager.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def modify_cad_surfaces_by_normal(
        self, faces: EntList | None, transit_faces: EntList | None, distance: float
    ) -> bool:
        """
        Modify CAD faces by a given distance

        Args:
            faces (EntList | None): EntList object containing the faces to be modified
            transit_faces (EntList | None): EntList object containing the transit faces
                to be preserved
            distance (float): distance along input faces' normal direction

        Returns:
            bool: True if operation is successful; False otherwise
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="modify_cad_surfaces_by_normal"
        )

        check_type(distance, (float, int))
        return self.cad_manager.ModifyCADSurfacesByNormal(
            check_and_coerce_optional(faces, EntList),
            check_and_coerce_optional(transit_faces, EntList),
            distance,
        )

    def modify_cad_surfaces_by_vector(
        self, faces: EntList | None, transit_faces: EntList | None, vector: Vector | None
    ) -> bool:
        """
        Modify CAD faces by a given vector

        Args:
            faces (EntList | None): EntList object containing the faces to be modified
            transit_faces (EntList | None): EntList object containing the transit
                faces to be preserved
            vector (Vector | None): Vector object that specifies the direction

        Returns:
            bool: True if operation is successful; False otherwise
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="modify_cad_surfaces_by_vector"
        )

        return self.cad_manager.ModifyCADSurfacesByVector(
            check_and_coerce_optional(faces, EntList),
            check_and_coerce_optional(transit_faces, EntList),
            check_and_coerce_optional(vector, Vector),
        )
