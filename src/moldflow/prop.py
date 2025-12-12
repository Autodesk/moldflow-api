# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Property Class API Wrapper
"""

from .double_array import DoubleArray
from .string_array import StringArray
from .logger import process_log
from .helper import check_type, check_optional_type, check_and_coerce_optional, check_is_non_negative, coerce_optional_dispatch
from .com_proxy import safe_com
from .common import LogMessage

class Property:
    """
    Wrapper for Property class of Moldflow Synergy.
    """

    def __init__(self, _property):
        """
        Initialize the Property with a Property instance from COM.

        Args:
            _property: The Property instance from COM.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Property")
        self.prop = safe_com(_property)

    def delete_field(self, field_id: int) -> bool:
        """
        Delete field from the property.

        Args:
            field_id (int): The id of the field to delete.

        Returns:
            bool: True if the field is deleted, False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_field")
        check_type(field_id, int)
        return self.prop.DeleteField(field_id)

    def get_first_field(self) -> int:
        """
        Get the first field of the property.

        Returns:
            int: The id of the first field of the property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_field")
        return self.prop.GetFirstField

    def get_next_field(self, field_id: int) -> int:
        """
        Get the first field of the property.

        Args:
            field_id (int): The id of the current field.

        Returns:
            int: The id of the next field.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_field")
        check_type(field_id, int)
        return self.prop.GetNextField(field_id)

    def is_field_hidden(self, field_id: int) -> bool:
        """
        Check if the field is confidential.

        Args:
            field_id (int): The id of the field to check.

        Returns:
            bool: True if the field is confidential, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="is_field_hidden")
        check_type(field_id, int)
        return self.prop.IsFieldHidden(field_id)

    def is_field_writable(self, field_id: int) -> bool:
        """
        Check if the field is writable.

        Args:
            field_id (int): The id of the field to check.

        Returns:
            bool: True if the field is writable, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="is_file_writeable")
        check_type(field_id, int)
        return self.prop.IsFieldWritable(field_id)

    def hide_field(self, field_id: int) -> bool:
        """
        Make field confidential.

        Args:
            field_id (int): The id of the field to make confidential.

        Returns:
            bool: True if the field is made confidential, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="hide_field")
        check_type(field_id, int)
        return self.prop.HideField(field_id)

    @property
    def type(self) -> int:
        """
        Get the type of the property.

        Returns:
            int: The type of the property.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="type")
        return self.prop.Type

    @property
    def id(self) -> int:
        """
        Get the id of the property.

        Returns:
            int: The id of the property.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="id")
        return self.prop.ID

    @property
    def name(self) -> str:
        """
        Get the name of the property.

        Returns:
            str: The name of the property.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="name")
        return self.prop.Name

    @name.setter
    def name(self, value: str) -> None:
        """
        Set the name of the property.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="name", value=value)
        check_type(value, str)
        self.prop.Name = value

    def get_field_description(self, field_id: int) -> str:
        """
        Get the description of the field.

        Args:
            field_id (int): The id of the field.

        Returns:
            str: The description of the field.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_field_description")
        check_type(field_id, int)
        check_is_non_negative(field_id)
        return self.prop.GetFieldDescription(field_id)

    def set_field_description(self, field_id: int, description: str) -> None:
        """
        Set the description of the field.

        Args:
            field_id (int): The id of the field.
            description (str): The description of the field.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_field_description")
        check_type(field_id, int)
        check_is_non_negative(field_id)
        check_type(description, str)
        self.prop.SetFieldDescription(field_id, description)

    def get_field_values(self, field_id: int) -> DoubleArray:
        """
        Get the values of the field.

        Args:
            field_id (int): The id of the field.

        Returns:
            DoubleArray: The values of the field.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_field_values")
        check_type(field_id, int)
        check_is_non_negative(field_id)
        result = self.prop.GetFieldValues(field_id)
        if result is None:
            return None
        return DoubleArray(result)

    def set_field_values(self, field_id: int, values: DoubleArray | None) -> None:
        """
        Set the values of the field.

        Args:
            field_id (int): The id of the field.
            values (DoubleArray | None): The values of the field.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_field_values")
        check_type(field_id, int)
        check_is_non_negative(field_id)

        self.prop.SetFieldValues(field_id, check_and_coerce_optional(values, DoubleArray))

    def field_units(self, field_id: int) -> StringArray:
        """
        Get the units of the field.

        Args:
            field_id (int): The id of the field.

        Returns:
            StringArray: The units of the field values.
        """
        process_log(
            __name__, LogMessage.PROPERTY_PARAM_GET, locals(), name="field_units", value=field_id
        )
        check_type(field_id, int)
        check_is_non_negative(field_id)
        result = self.prop.FieldUnits(field_id)
        if result is None:
            return None
        return StringArray(result)
