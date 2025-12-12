# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    PropertyEditor Class API Wrapper
"""

from .logger import process_log, LogMessage
from .ent_list import EntList
from .prop import Property
from .helper import get_enum_value, check_type, check_optional_type, check_and_coerce_optional, coerce_optional_dispatch
from .com_proxy import safe_com
from .common import CommitActions, MaterialDatabaseType, PropertyType


class PropertyEditor:
    """
    Wrapper for PropertyEditor class of Moldflow Synergy.
    """

    def __init__(self, _property_editor):
        """
        Initialize the PropertyEditor with a PropertyEditor instance from COM.

        Args:
            _property_editor: The PropertyEditor instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="PropertyEditor")
        self.property_editor = safe_com(_property_editor)

    def delete_property(self, prop_type: PropertyType | int, prop_id: int) -> bool:
        """
        Delete a property

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.

        Returns:
            bool: True if the property was deleted successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_property")
        prop_type = get_enum_value(prop_type, PropertyType)
        check_type(prop_id, int)
        return self.property_editor.DeleteProperty(prop_type, prop_id)

    def create_property(
        self, prop_type: PropertyType | int, prop_id: int, defaults: bool
    ) -> Property:
        """
        Create a property

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.
            defaults (bool): Whether to use default values for property fields.

        Returns:
            Property: The created property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_property")
        prop_type = get_enum_value(prop_type, PropertyType)
        check_type(prop_id, int)
        check_type(defaults, bool)
        prop = self.property_editor.CreateProperty(prop_type, prop_id, defaults)
        if prop is None:
            return None
        return Property(prop)

    def find_property(self, prop_type: PropertyType | int, prop_id: int) -> Property:
        """
        Find a property

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.

        Returns:
            Property: The found property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_property")
        prop_type = get_enum_value(prop_type, PropertyType)
        check_type(prop_id, int)
        prop = self.property_editor.FindProperty(prop_type, prop_id)
        if prop is None:
            return None
        return Property(prop)

    def commit_changes(self, action: CommitActions | str) -> bool:
        """
        Commit changes to the property editor.

        Args:
            action (CommitActions | str): The action to commit.

        Returns:
            bool: True if the changes were committed successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="commit_changes")
        if isinstance(action, CommitActions):
            action = get_enum_value(action, CommitActions)
        else:
            check_type(action, str)
        return self.property_editor.CommitChanges(action)

    def set_property(self, entities: EntList | None, prop: Property | None) -> bool:
        """
        Assigns a property to a list of entities.

        Args:
            entities (EntList | None): The list of entities to assign the property to.
            prop (Property | None): The property to assign.

        Returns:
            bool: True if the property was assigned successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_property")

        return self.property_editor.SetProperty(
            check_and_coerce_optional(entities, EntList), check_and_coerce_optional(prop, Property)
        )

    def create_entity_list(self) -> EntList:
        """
        Create a new entity list.

        Returns:
            EntList: The created entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        ent = self.property_editor.CreateEntityList
        if ent is None:
            return None
        return EntList(ent)

    def remove_unused_properties(self) -> int:
        """
        Remove unused properties in the study.
        Unused properties are those that are not assigned to any entities.

        Returns:
            int: The number of unused properties removed.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="remove_unused_properties")
        return self.property_editor.RemoveUnusedProperties

    # pylint: disable-next=R0913, R0917
    def fetch_property(
        self,
        prop_type: PropertyType | int,
        prop_id: int,
        file_name: str,
        file_type: MaterialDatabaseType | str,
        file_id: int,
    ) -> Property:
        """
        Fetch a property from the property editor.

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.
            file_name (str): The name of the file.
            file_type (MaterialDatabaseType | str): The type of the file.
            - Can take empty string, if the file is not in any of the standard database locations
            - In this case, aFile must be a full path specification
            file_id (int): The ID of the file.

        Returns:
            Property: The fetched property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="fetch_property")
        prop_type = get_enum_value(prop_type, PropertyType)
        check_type(prop_id, int)
        check_type(file_name, str)
        if file_type != "":
            file_type = get_enum_value(file_type, MaterialDatabaseType)
        check_type(file_id, int)
        prop = self.property_editor.FetchProperty(prop_type, prop_id, file_name, file_type, file_id)
        if prop is None:
            return None
        return Property(prop)

    def get_first_property(self, prop_type: PropertyType | int) -> Property:
        """
        Get the first property of a given type.

        Args:
            prop_type (int): The type of the property.

        Returns:
            Property: The first property of the specified type.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_property")
        prop_type = get_enum_value(prop_type, PropertyType)
        prop = self.property_editor.GetFirstProperty(prop_type)
        if prop is None:
            return None
        return Property(prop)

    def get_next_property(self, prop: Property | None) -> Property:
        """
        Get the next property in the list.

        Args:
            prop (Property | None): The current property.

        Returns:
            Property: The next property in the list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_property")

        result = self.property_editor.GetNextProperty(check_and_coerce_optional(prop, Property))
        if result is None:
            return None
        return Property(result)

    def get_next_property_of_type(self, prop: Property | None) -> Property:
        """
        Get the next property of the same type.

        Args:
            prop (Property | None): The current property.

        Returns:
            Property: The next property of the same type.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_property_of_type")

        result = self.property_editor.GetNextPropertyOfType(check_and_coerce_optional(prop, Property))
        if result is None:
            return None
        return Property(result)

    def get_entity_property(self, entities: EntList | None) -> Property:
        """
        Get the property assigned to an entity.

        Args:
            entities (EntList | None): The entity.

        Returns:
            Property: The property of the entities.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_entity_property")

        prop = self.property_editor.GetEntityProperty(
            check_and_coerce_optional(entities, EntList)
        )
        if prop is None:
            return None
        return Property(prop)

    def get_data_description(self, prop_type: PropertyType | int, prop_id: int) -> str:
        """
        Get the field property description.

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.

        Returns:
            str: The data description of the property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_data_description")
        prop_type = get_enum_value(prop_type, PropertyType)
        check_type(prop_id, int)
        return self.property_editor.GetDataDescription(prop_type, prop_id)
