# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for FolderManager Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import FolderManager, EntList, EntityType, DisplayOption
from tests.api.unit_tests.conftest import INVALID_MOCK, VALID_MOCK
from tests.conftest import (
    VALID_BOOL,
    VALID_INT,
    NON_NEGATIVE_INT,
    VALID_STR,
    INVALID_BOOL,
    INVALID_INT,
    INVALID_STR,
    pad_and_zip,
)

INVALID_RGB = [256, -1]


@pytest.mark.unit
class TestUnitFolderManager:
    """
    Test suite for the FolderManager class.
    """

    @pytest.fixture
    def mock_folder_manager(self, mock_object) -> FolderManager:
        """
        Fixture to create a mock instance of FolderManager.
        Args:
            mock_object: Mock object for the FolderManager dependency.
        Returns:
            FolderManager: An instance of FolderManager with the mock object.
        """
        return FolderManager(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            (
                "AddObjectsToFolder",
                "add_objects_to_folder",
                (x, y),
                (x.ent_list, y.ent_list),
                bool,
                z,
            )
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            ("RemoveObjectsFromFolder", "remove_objects_from_folder", (x,), (x.ent_list,), bool, y)
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            ("DeleteFolder", "delete_folder", (x, y), (x.ent_list, y), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL)
        ]
        + [
            ("ToggleFolder", "toggle_folder", (x,), (x.ent_list,), bool, y)
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            (
                "ExpandFolder",
                "expand_folder",
                (x, y, z, u, v, w, a),
                (x.ent_list, y, z, u, v, w, a),
                int,
                b,
            )
            for x, y, z, u, v, w, a, b in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_INT,
            )
        ]
        + [
            ("SetFolderName", "set_folder_name", (x, y), (x.ent_list, y), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_STR, VALID_BOOL)
        ]
        + [
            ("ShowFolders", "show_folders", (x, y), (x.ent_list, y), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL)
        ]
        + [
            (
                "SetTypeColor",
                "set_type_color",
                (x, y, z, u, v, w),
                (x.ent_list, y.value, z, u, v, w),
                bool,
                a,
            )
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                EntityType,
                VALID_BOOL,
                NON_NEGATIVE_INT,
                NON_NEGATIVE_INT,
                NON_NEGATIVE_INT,
                VALID_BOOL,
            )
        ]
        + [
            ("SetTypeVisible", "set_type_visible", (x, y, z), (x.ent_list, y.value, z), bool, u)
            for x, y, z, u in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_BOOL)
        ]
        + [
            (
                "SetTypeDisplayOption",
                "set_type_display_option",
                (x, y, z),
                (x.ent_list, y.value, z.value),
                bool,
                u,
            )
            for x, y, z, u in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, DisplayOption, VALID_BOOL
            )
        ]
        + [
            ("GetName", "get_name", (x,), (x.ent_list,), str, y)
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_STR)
        ]
        + [
            ("ShowLabels", "show_labels", (x, y), (x.ent_list, y), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL)
        ]
        + [
            ("ShowGlyphs", "show_glyphs", (x, y), (x.ent_list, y), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL)
        ]
        + [
            (
                "SetTypeShowLabels",
                "set_type_show_labels",
                (x, y, z),
                (x.ent_list, y.value, z),
                bool,
                u,
            )
            for x, y, z, u in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_BOOL)
        ]
        + [
            (
                "SetTypeShowGlyphs",
                "set_type_show_glyphs",
                (x, y, z),
                (x.ent_list, y.value, z),
                bool,
                u,
            )
            for x, y, z, u in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_BOOL)
        ]
        + [
            ("HideAllOtherFolders", "hide_all_other_folders", (x,), (x.ent_list,), bool, y)
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL)
        ]
        + [
            ("AllowClipping", "allow_clipping", (x, y), (x.ent_list, y), bool, z)
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions(
        self,
        mock_folder_manager: FolderManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test the functions of the FolderManager class.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments for the function call.
            return_type: Expected return type of the function.
            return_value: Expected return value of the function.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_folder_manager, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, return_value",
        [("CreateFolder", "create_folder", bool, x) for x in pad_and_zip(VALID_BOOL)]
        + [("ShowAllFolders", "show_all_folders", bool, x) for x in pad_and_zip(VALID_BOOL)]
        + [
            ("RemoveEmptyFolders", "remove_empty_folders", bool, x) for x in pad_and_zip(VALID_BOOL)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_attributes(
        self,
        mock_folder_manager: FolderManager,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        return_value,
    ):
        """
        Test the functions of the FolderManager class.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
            return_type: Expected return type of the function.
            return_value: Expected return value of the function.
        """
        setattr(mock_object, pascal_name, return_value)
        result = getattr(mock_folder_manager, property_name)()
        assert isinstance(result, return_type)
        assert result == return_value

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("CreateChildLayer", "create_child_layer", (x,)) for x in pad_and_zip(INVALID_MOCK)]
        + [("CreateChildFolder", "create_child_folder", (x,)) for x in pad_and_zip(INVALID_MOCK)]
        + [
            ("AddObjectsToFolder", "add_objects_to_folder", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, VALID_MOCK.ENT_LIST)
        ]
        + [
            ("AddObjectsToFolder", "add_objects_to_folder", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_MOCK)
        ]
        + [
            ("RemoveObjectsFromFolder", "remove_objects_from_folder", (x,))
            for x in pad_and_zip(INVALID_MOCK)
        ]
        + [
            ("DeleteFolder", "delete_folder", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, VALID_BOOL)
        ]
        + [
            ("DeleteFolder", "delete_folder", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_BOOL)
        ]
        + [("ToggleFolder", "toggle_folder", (x,)) for x in pad_and_zip(INVALID_MOCK)]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                INVALID_MOCK, VALID_INT, VALID_BOOL, VALID_BOOL, VALID_BOOL, VALID_BOOL, VALID_BOOL
            )
        ]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                INVALID_INT,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                INVALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_BOOL,
                INVALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_BOOL,
                VALID_BOOL,
                INVALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                INVALID_BOOL,
                VALID_BOOL,
            )
        ]
        + [
            ("ExpandFolder", "expand_folder", (x, y, z, u, v, w, a))
            for x, y, z, u, v, w, a in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_INT,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                INVALID_BOOL,
            )
        ]
        + [
            ("SetFolderName", "set_folder_name", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, VALID_STR)
        ]
        + [
            ("SetFolderName", "set_folder_name", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_STR)
        ]
        + [
            ("ShowFolders", "show_folders", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, VALID_BOOL)
        ]
        + [
            ("ShowFolders", "show_folders", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_BOOL)
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                INVALID_MOCK, EntityType, VALID_BOOL, VALID_INT, VALID_INT, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, INVALID_STR, VALID_BOOL, VALID_INT, VALID_INT, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, INVALID_BOOL, VALID_INT, VALID_INT, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, INVALID_INT, VALID_INT, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_INT, INVALID_INT, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_INT, VALID_INT, INVALID_INT
            )
        ]
        + [
            ("SetTypeVisible", "set_type_visible", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_MOCK, EntityType, VALID_BOOL)
        ]
        + [
            ("SetTypeVisible", "set_type_visible", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_STR, VALID_BOOL)
        ]
        + [
            ("SetTypeVisible", "set_type_visible", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, INVALID_BOOL)
        ]
        + [
            ("SetTypeDisplayOption", "set_type_display_option", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_MOCK, EntityType, DisplayOption)
        ]
        + [
            ("SetTypeDisplayOption", "set_type_display_option", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_STR, DisplayOption)
        ]
        + [
            ("SetTypeDisplayOption", "set_type_display_option", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, INVALID_STR)
        ]
        + [("GetNext", "get_next", (x,)) for x in pad_and_zip(INVALID_MOCK)]
        + [("GetName", "get_name", (x,)) for x in pad_and_zip(INVALID_MOCK)]
        + [("ShowLabels", "show_labels", (x, y)) for x, y in pad_and_zip(INVALID_MOCK, VALID_BOOL)]
        + [
            ("ShowLabels", "show_labels", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_BOOL)
        ]
        + [("ShowGlyphs", "show_glyphs", (x, y)) for x, y in pad_and_zip(INVALID_MOCK, VALID_BOOL)]
        + [
            ("ShowGlyphs", "show_glyphs", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_BOOL)
        ]
        + [
            ("SetTypeShowLabels", "set_type_show_labels", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_MOCK, EntityType, VALID_BOOL)
        ]
        + [
            ("SetTypeShowLabels", "set_type_show_labels", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_STR, VALID_BOOL)
        ]
        + [
            ("SetTypeShowLabels", "set_type_show_labels", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, INVALID_BOOL)
        ]
        + [
            ("SetTypeShowGlyphs", "set_type_show_glyphs", (x, y, z))
            for x, y, z in pad_and_zip(INVALID_MOCK, EntityType, VALID_BOOL)
        ]
        + [
            ("SetTypeShowGlyphs", "set_type_show_glyphs", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_STR, VALID_BOOL)
        ]
        + [
            ("SetTypeShowGlyphs", "set_type_show_glyphs", (x, y, z))
            for x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, EntityType, INVALID_BOOL)
        ]
        + [("CreateFolderByName", "create_folder_by_name", (x,)) for x in pad_and_zip(INVALID_STR)]
        + [("FindFolderByName", "find_folder_by_name", (x,)) for x in pad_and_zip(INVALID_STR)]
        + [
            ("HideAllOtherFolders", "hide_all_other_folders", (x,))
            for x in pad_and_zip(INVALID_MOCK)
        ]
        + [
            ("AllowClipping", "allow_clipping", (x, y))
            for x, y in pad_and_zip(INVALID_MOCK, VALID_BOOL)
        ]
        + [
            ("AllowClipping", "allow_clipping", (x, y))
            for x, y in pad_and_zip(VALID_MOCK.ENT_LIST, INVALID_BOOL)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_type(
        self, mock_folder_manager: FolderManager, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the functions of the FolderManager class with invalid types.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
            args: Arguments to be passed to the function.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_folder_manager, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("CreateChildLayer", "create_child_layer", (x,), (x.ent_list,))
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [
            ("CreateChildFolder", "create_child_folder", (x,), (x.ent_list,))
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("GetNext", "get_next", (x,), (x.ent_list,)) for x in pad_and_zip(VALID_MOCK.ENT_LIST)]
        + [
            ("CreateFolderByName", "create_folder_by_name", (x,), (x,))
            for x in pad_and_zip(VALID_STR)
        ]
        + [("FindFolderByName", "find_folder_by_name", (x,), (x,)) for x in pad_and_zip(VALID_STR)],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_return_ent_list(
        self,
        mock_folder_manager: FolderManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the functions of the FolderManager class that return an entity list.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments for the function call.
        """
        expected_ent_list = VALID_MOCK.ENT_LIST
        getattr(mock_object, pascal_name).return_value = expected_ent_list.ent_list
        result = getattr(mock_folder_manager, property_name)(*args)
        assert isinstance(result, EntList)
        assert result.ent_list == expected_ent_list.ent_list
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("CreateEntityList", "create_entity_list"), ("GetFirst", "get_first")],
    )
    def test_attributes_return_ent_list(
        self, mock_folder_manager: FolderManager, mock_object, pascal_name, property_name
    ):
        """
        Test the functions of the FolderManager class that return an entity list.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
        """
        expected_ent_list = VALID_MOCK.ENT_LIST
        setattr(mock_object, pascal_name, expected_ent_list.ent_list)
        result = getattr(mock_folder_manager, property_name)()
        assert isinstance(result, EntList)
        assert result.ent_list == expected_ent_list.ent_list

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("CreateChildLayer", "create_child_layer", (x,), (x.ent_list,))
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [
            ("CreateChildFolder", "create_child_folder", (x,), (x.ent_list,))
            for x in pad_and_zip(VALID_MOCK.ENT_LIST)
        ]
        + [("GetNext", "get_next", (x,), (x.ent_list,)) for x in pad_and_zip(VALID_MOCK.ENT_LIST)]
        + [
            ("CreateFolderByName", "create_folder_by_name", (x,), (x,))
            for x in pad_and_zip(VALID_STR)
        ]
        + [("FindFolderByName", "find_folder_by_name", (x,), (x,)) for x in pad_and_zip(VALID_STR)],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_none(
        self,
        mock_folder_manager: FolderManager,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
    ):
        """
        Test the functions of the FolderManager class that return an entity list.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments for the function call.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_folder_manager, property_name)(*args)
        assert result is None
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("CreateEntityList", "create_entity_list"), ("GetFirst", "get_first")],
    )
    def test_attributes_none(
        self, mock_folder_manager: FolderManager, mock_object, pascal_name, property_name
    ):
        """
        Test the functions of the FolderManager class that return an entity list.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_folder_manager, property_name)()
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, INVALID_RGB, VALID_INT, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_INT, INVALID_RGB, VALID_INT
            )
        ]
        + [
            ("SetTypeColor", "set_type_color", (x, y, z, u, v, w))
            for x, y, z, u, v, w in pad_and_zip(
                VALID_MOCK.ENT_LIST, EntityType, VALID_BOOL, VALID_INT, VALID_INT, INVALID_RGB
            )
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_value(
        self, mock_folder_manager: FolderManager, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the functions of the FolderManager class with invalid values.
        Args:
            mock_folder_manager: Mock instance of FolderManager.
            mock_object: Mock object for the FolderManager dependency.
            pascal_name: Pascal case name of the function to be tested.
            property_name: Property name of the function to be tested.
            args: Arguments to be passed to the function.
        """
        with pytest.raises(ValueError) as e:
            getattr(mock_folder_manager, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()
