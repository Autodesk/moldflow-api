# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    EntList Class API Wrapper
"""

from .helper import (
    check_index,
    check_type,
    check_optional_type,
    check_and_coerce_optional,
    coerce_optional_dispatch,
)
from .com_proxy import safe_com, expose_oleobj
from .predicate import Predicate
from .common import LogMessage
from .logger import process_log


class EntList:
    """
    Wrapper for EntList class of Moldflow Synergy.
    """

    def __init__(self, _ent_list):
        """
        Initialize the EntList with a EntList instance from COM.

        Args:
            _ent_list: The EntList instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="EntList")
        self.ent_list = safe_com(_ent_list)
        # Expose _oleobj_ so EntList can be passed directly to COM APIs
        expose_oleobj(self, "ent_list")

    def entity(self, index: int) -> "EntList":
        """
        Get the entity at the specified index.

        Args:
            index (int): The index of the entity to get.

        Returns:
            EntList: The entity at the specified index.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="entity")
        check_type(index, int)
        check_index(index, 0, self.size)
        return EntList(self.ent_list.Entity(index))

    def select_from_string(self, entity_string: str) -> None:
        """
        Converts a string to a list of entities

        Args:
            entity_string (str): string containing entity names.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="select_from_string")
        check_type(entity_string, str)
        self.ent_list.SelectFromString(entity_string)

    def select_from_predicate(self, predicate: Predicate | None) -> None:
        """
        Converts a predicate into a list of entities

        Args:
            predicate (Predicate | None): Predicate object that defines the criterion for
                inclusion of an entity.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="select_from_predicate")

        self.ent_list.SelectFromPredicate(check_and_coerce_optional(predicate, Predicate))

    def convert_to_string(self) -> str:
        """
        Convert a list of entities into a string.

        Returns:
            str: The string representation of the list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="convert_to_string")
        return self.ent_list.ConvertToString

    def select_from_saved_list(self, list_name: str) -> None:
        """
        Selects entities from a saved list.

        Args:
            list_name (str): The name of the saved list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="select_from_saved_list")
        check_type(list_name, str)
        self.ent_list.SelectFromSavedList(list_name)

    @property
    def size(self):
        """
        The number of entities in the list.

        :getter: Get the number of entities in the list.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size")
        return self.ent_list.Size
