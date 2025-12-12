# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    BoundaryList Class API Wrapper
"""

from .helper import check_type, check_index
from .com_proxy import safe_com
from .logger import process_log
from .common import LogMessage

class BoundaryList:
    """
    Wrapper for BoundaryList class of Moldflow Synergy.
    """

    def __init__(self, _boundary_list):
        """
        Initialize the BoundaryList with a BoundaryList instance from COM.

        Args:
            _boundary_list: The BoundaryList instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="BoundaryList")
        self.boundary_list = safe_com(_boundary_list)

    def select_from_string(self, value: str) -> None:
        """
        Selects a list of entities from a string

        Args:
            value (str): String representation of the entities
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="select_from_string")
        check_type(value, str)
        self.boundary_list.SelectFromString(value)

    def convert_to_string(self) -> str:
        """
        Converts boundary list to a string

        Returns:
            string representation of the boundary list
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="convert_to_string")
        return self.boundary_list.ConvertToString

    def entity(self, index: int) -> "BoundaryList":
        """
        Returns entity at a given index

        Args:
            index (int): zero based index

        Returns:
            BoundaryList object containing the object
        """
        process_log(__name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="entity", value=index)
        check_type(index, int)
        check_index(index, 0, self.size)
        result = self.boundary_list.Entity(index)
        if result is None:
            return None
        return BoundaryList(result)

    def cad_entity(self, index: int) -> "BoundaryList":
        """
        Returns CAD entity at a given index

        Args:
            index (int): index between 0 and array.Size-1

        Returns:
            Boundary List object containing the object
        """
        process_log(
            __name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="cad_entity", value=index
        )
        check_type(index, int)
        check_index(index, 0, self.size_cad)
        result = self.boundary_list.CadEntity(index)
        if result is None:
            return None
        return BoundaryList(result)

    @property
    def size(self) -> int:
        """
        Returns boundary list entities size
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.boundary_list.Size

    @property
    def size_cad(self) -> int:
        """
        Returns boundary list entities cad size
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size_cad")
        return self.boundary_list.SizeCad
