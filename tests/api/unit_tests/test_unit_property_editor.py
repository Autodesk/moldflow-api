# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for PropertyEditor Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import (
    PropertyEditor,
    PropertyType,
    Property,
    CommitActions,
    EntList,
    MaterialDatabaseType,
)
from tests.api.unit_tests.conftest import VALID_MOCK, INVALID_MOCK_WITH_NONE
from tests.conftest import (
    VALID_INT,
    VALID_BOOL,
    VALID_STR,
    INVALID_BOOL,
    INVALID_INT,
    INVALID_STR,
    pad_and_zip,
)


@pytest.mark.unit
class TestUnitPropertyEditor:
    """
    Test suite for the PropertyEditor class.
    """

    @pytest.fixture
    def mock_property_editor(self, mock_object) -> PropertyEditor:
        """
        Fixture to create a mock instance of PropertyEditor.
        Args:
            mock_object: Mock object for the PropertyEditor dependency.
        Returns:
            PropertyEditor: An instance of PropertyEditor with the mock object.
        """
        return PropertyEditor(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("CreateEntityList", "create_entity_list")]
    )
    def test_attribute_return_ent_list(
        self, mock_property_editor: PropertyEditor, mock_object, pascal_name, property_name
    ):
        """
        Test for attributes with a return value of type EntList.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
        """
        expected_ent_list = VALID_MOCK.ENT_LIST
        setattr(mock_object, pascal_name, expected_ent_list.ent_list)
        result = getattr(mock_property_editor, property_name)()
        assert isinstance(result, EntList)
        assert result.ent_list == expected_ent_list.ent_list

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [
            ("DeleteProperty", "delete_property", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_INT)
        ]
        + [
            ("DeleteProperty", "delete_property", (x, y))
            for x, y in pad_and_zip(PropertyType, INVALID_INT)
        ]
        + [
            ("CreateProperty", "create_property", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_INT, VALID_INT, VALID_BOOL)
        ]
        + [
            ("CreateProperty", "create_property", (x, y, z))
            for x, y, z in pad_and_zip(PropertyType, INVALID_INT, VALID_BOOL)
        ]
        + [
            ("CreateProperty", "create_property", (x, y, z))
            for x, y, z in pad_and_zip(PropertyType, VALID_INT, INVALID_BOOL)
        ]
        + [
            ("FindProperty", "find_property", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_INT)
        ]
        + [
            ("FindProperty", "find_property", (x, y))
            for x, y in pad_and_zip(PropertyType, INVALID_INT)
        ]
        + [("CommitChanges", "commit_changes", (x,)) for x in pad_and_zip(INVALID_STR)]
        + [
            ("SetProperty", "set_property", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK_WITH_NONE, VALID_MOCK.PROP)
        ]
        + [
            ("SetProperty", "set_property", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_MOCK_WITH_NONE)
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v))
            for x, y, z, u, v in pad_and_zip(
                INVALID_INT, VALID_INT, VALID_STR, MaterialDatabaseType, VALID_INT
            )
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v))
            for x, y, z, u, v in pad_and_zip(
                PropertyType, INVALID_INT, VALID_STR, MaterialDatabaseType, VALID_INT
            )
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v))
            for x, y, z, u, v in pad_and_zip(
                PropertyType, VALID_INT, INVALID_STR, MaterialDatabaseType, VALID_INT
            )
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v))
            for x, y, z, u, v in pad_and_zip(
                PropertyType, VALID_INT, VALID_STR, INVALID_STR, VALID_INT
            )
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v))
            for x, y, z, u, v in pad_and_zip(
                PropertyType, VALID_INT, VALID_STR, MaterialDatabaseType, INVALID_INT
            )
        ]
        + [("GetFirstProperty", "get_first_property", (x,)) for x in pad_and_zip(INVALID_INT)]
        + [
            ("GetNextProperty", "get_next_property", (x,))
            for x in pad_and_zip(INVALID_MOCK_WITH_NONE)
        ]
        + [
            ("GetNextPropertyOfType", "get_next_property_of_type", (x,))
            for x in pad_and_zip(INVALID_MOCK_WITH_NONE)
        ]
        + [
            ("GetEntityProperty", "get_entity_property", (x,))
            for x in pad_and_zip(INVALID_MOCK_WITH_NONE)
        ]
        + [
            ("GetDataDescription", "get_data_description", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_INT)
        ]
        + [
            ("GetDataDescription", "get_data_description", (x, y))
            for x, y in pad_and_zip(PropertyType, INVALID_INT)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_type(
        self, mock_property_editor: PropertyEditor, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test for functions with no return value.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
            args: Arguments to be passed to the function.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_property_editor, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("CreateProperty", "create_property", (x, y, z), (x.value, y, z))
            for x, y, z in pad_and_zip(PropertyType, VALID_INT, VALID_BOOL)
        ]
        + [
            ("FindProperty", "find_property", (x, y), (x.value, y))
            for x, y in pad_and_zip(PropertyType, VALID_INT)
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v), (x.value, y, z, u.value, v))
            for x, y, z, u, v in pad_and_zip(
                PropertyType, VALID_INT, VALID_STR, MaterialDatabaseType, VALID_INT
            )
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v), (x.value, y, z, u, v))
            for x, y, z, u, v in pad_and_zip(PropertyType, VALID_INT, VALID_STR, [""], VALID_INT)
        ]
        + [
            ("GetFirstProperty", "get_first_property", (x,), (x.value,))
            for x in pad_and_zip(PropertyType)
        ]
        + [
            ("GetNextProperty", "get_next_property", (x,), (x.prop,))
            for x in pad_and_zip(VALID_MOCK.PROP)
        ]
        + [
            ("GetNextPropertyOfType", "get_next_property_of_type", (x,), (x.prop,))
            for x in pad_and_zip(VALID_MOCK.PROP)
        ]
        + [
            ("GetEntityProperty", "get_entity_property", (x,), (x.ent_list,))
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_return_property(
        self,
        mock_property_editor: PropertyEditor,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test for functions with a return value of type Property.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments for the function call.
        """
        expected_property = VALID_MOCK.PROP
        getattr(mock_object, pascal_name).return_value = expected_property.prop
        result = getattr(mock_property_editor, property_name)(*args)
        assert isinstance(result, Property)
        assert result.prop == expected_property.prop
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("CreateProperty", "create_property", (x, y, z), (x.value, y, z))
            for x, y, z in pad_and_zip(PropertyType, VALID_INT, VALID_BOOL)
        ]
        + [
            ("FindProperty", "find_property", (x, y), (x.value, y))
            for x, y in pad_and_zip(PropertyType, VALID_INT)
        ]
        + [
            ("FetchProperty", "fetch_property", (x, y, z, u, v), (x.value, y, z, u.value, v))
            for x, y, z, u, v in pad_and_zip(
                PropertyType, VALID_INT, VALID_STR, MaterialDatabaseType, VALID_INT
            )
        ]
        + [
            ("GetFirstProperty", "get_first_property", (x,), (x.value,))
            for x in pad_and_zip(PropertyType)
        ]
        + [
            ("GetNextProperty", "get_next_property", (x,), (x.prop,))
            for x in pad_and_zip(VALID_MOCK.PROP)
        ]
        + [
            ("GetNextPropertyOfType", "get_next_property_of_type", (x,), (x.prop,))
            for x in pad_and_zip(VALID_MOCK.PROP)
        ]
        + [
            ("GetEntityProperty", "get_entity_property", (x,), (x.ent_list,))
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_none(
        self,
        mock_property_editor: PropertyEditor,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test for functions with a return value of None.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments for the function call.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_property_editor, property_name)(*args)
        assert result is None
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("CreateEntityList", "create_entity_list")]
    )
    def test_attributes_none(
        self, mock_property_editor: PropertyEditor, mock_object, pascal_name, property_name
    ):
        """
        Test for functions with a return value of None.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_property_editor, property_name)()
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            ("CommitChanges", "commit_changes", (x,), (x.value,), bool, y)
            for x, y in pad_and_zip(CommitActions, VALID_BOOL)
        ]
        + [
            ("CommitChanges", "commit_changes", (x,), (x,), bool, y)
            for x, y in pad_and_zip(["Undo", "Redo"], VALID_BOOL)
        ]
        + [
            ("SetProperty", "set_property", (x, y), (x.ent_list, y.prop), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.PROP, VALID_BOOL)
        ]
        + [
            ("GetDataDescription", "get_data_description", (x, y), (x.value, y), str, z)
            for x, y, z in pad_and_zip(PropertyType, VALID_INT, VALID_STR)
        ]
        + [
            ("DeleteProperty", "delete_property", (x, y), (x.value, y), bool, z)
            for x, y, z in pad_and_zip(PropertyType, VALID_INT, VALID_BOOL)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions(
        self,
        mock_property_editor: PropertyEditor,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test for functions with a return value.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments for the function call.
            return_type: Expected return type of the function.
            return_value: Expected return value of the function.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_property_editor, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, return_value",
        [
            ("RemoveUnusedProperties", "remove_unused_properties", int, y)
            for y in pad_and_zip(VALID_INT)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_attribute(
        self,
        mock_property_editor: PropertyEditor,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        return_value,
    ):
        """
        Test for functions with a return value.
        Args:
            mock_property_editor: Mock instance of PropertyEditor.
            mock_object: Mock object for the PropertyEditor dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Name of the property to be tested.
            return_type: Expected return type of the function.
            return_value: Expected return value of the function.
        """
        setattr(mock_object, pascal_name, return_value)
        result = getattr(mock_property_editor, property_name)()
        assert isinstance(result, return_type)
        assert result == return_value
