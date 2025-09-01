# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for LayerManager Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import LayerManager, EntList, EntityType, DisplayOption


@pytest.mark.unit
class TestUnitLayerManager:
    """
    Test suite for the LayerManager class.
    """

    @pytest.fixture
    def mock_layer_manager(self, mock_object) -> LayerManager:
        """
        Fixture to create a mock instance of LayerManager.
        Args:
            mock_object: Mock object for the LayerManager dependency.
        Returns:
            LayerManager: An instance of LayerManager with the mock object.
        """
        return LayerManager(mock_object)

    @pytest.fixture
    def mock_ent_list(self) -> EntList:
        """
        Fixture to create a mock instance of EntList.
        Returns:
            EntList: An instance of EntList with the mock object.
        """
        ent = Mock(spec=EntList)
        ent.ent_list = Mock()
        return ent

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("Active", "active"),
            ("ActivateLayer", "activate_layer"),
            ("ToggleLayer", "toggle_layer"),
            ("GetNext", "get_next"),
            ("GetName", "get_name"),
            ("HideAllOtherLayers", "hide_all_other_layers"),
            ("GetActivated", "get_activated"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_single_input(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        mock_ent_list,
        pascal_name,
        property_name,
    ):
        """
        Test the active property of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        getattr(mock_object, pascal_name).return_value = True
        result = getattr(mock_layer_manager, property_name)(mock_ent_list)
        assert result
        getattr(mock_object, pascal_name).assert_called_once_with(mock_ent_list.ent_list)

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, expected",
        [
            ("CreateLayer", "create_layer", bool, True),
            ("CreateLayer", "create_layer", bool, False),
            ("ShowAllLayers", "show_all_layers", bool, True),
            ("ShowAllLayers", "show_all_layers", bool, False),
            ("RemoveEmptyLayers", "remove_empty_layers", bool, True),
            ("RemoveEmptyLayers", "remove_empty_layers", bool, False),
            ("GetNumberOfLayers", "get_number_of_layers", int, 0),
            ("GetNumberOfLayers", "get_number_of_layers", int, 1),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_no_args(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        expected,
    ):
        """
        Test the create_layer method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        setattr(mock_object, pascal_name, expected)
        result = getattr(mock_layer_manager, property_name)()
        assert isinstance(result, return_type)
        assert result == expected

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("CreateEntityList", "create_entity_list"), ("GetFirst", "get_first")],
    )
    # pylint: disable-next=R0913, R0917
    def test_return_ent_list(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        pascal_name,
        property_name,
        mock_ent_list,
    ):
        """
        Test the create_layer method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        setattr(mock_object, pascal_name, mock_ent_list.ent_list)
        result = getattr(mock_layer_manager, property_name)()
        assert isinstance(result, EntList)
        assert result.ent_list == mock_ent_list.ent_list

    def test_assign_to_layer(self, mock_layer_manager: LayerManager, mock_object, mock_ent_list):
        """
        Test the assign_to_layer method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        mock_object.AssignToLayer.return_value = True
        result = mock_layer_manager.assign_to_layer(mock_ent_list, mock_ent_list)
        assert result
        mock_object.AssignToLayer.assert_called_once_with(
            mock_ent_list.ent_list, mock_ent_list.ent_list
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, expected",
        [
            ("DeleteLayer", "delete_layer", True, True),
            ("DeleteLayer", "delete_layer", False, False),
            ("SetLayerName", "set_layer_name", "filename", "filename"),
            ("ShowLayers", "show_layers", True, True),
            ("ShowLayers", "show_layers", False, False),
            ("ShowLabels", "show_labels", True, True),
            ("ShowLabels", "show_labels", False, False),
            ("ShowGlyphs", "show_glyphs", True, True),
            ("ShowGlyphs", "show_glyphs", False, False),
            ("AllowClipping", "allow_clipping", True, True),
            ("AllowClipping", "allow_clipping", False, False),
        ]
        + [("GetTypeVisible", "get_type_visible", x, x.value) for x in EntityType]
        + [("GetTypeVisible", "get_type_visible", x.value, x.value) for x in EntityType],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_with_args(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        mock_ent_list,
        pascal_name,
        property_name,
        value,
        expected,
    ):
        """
        Test the delete_layer method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        getattr(mock_object, pascal_name).return_value = True
        result = getattr(mock_layer_manager, property_name)(mock_ent_list, value)
        assert result
        getattr(mock_object, pascal_name).assert_called_once_with(mock_ent_list.ent_list, expected)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("DeleteLayer", "delete_layer", 1),
            ("DeleteLayer", "delete_layer", 1.1),
            ("DeleteLayer", "delete_layer", None),
            ("DeleteLayer", "delete_layer", "True"),
            ("ShowLayers", "show_layers", 1),
            ("ShowLayers", "show_layers", 1.1),
            ("ShowLayers", "show_layers", None),
            ("ShowLayers", "show_layers", "True"),
            ("ShowLabels", "show_labels", 1),
            ("ShowLabels", "show_labels", 1.1),
            ("ShowLabels", "show_labels", None),
            ("ShowLabels", "show_labels", "True"),
            ("ShowGlyphs", "show_glyphs", 1),
            ("ShowGlyphs", "show_glyphs", 1.1),
            ("ShowGlyphs", "show_glyphs", None),
            ("ShowGlyphs", "show_glyphs", "True"),
            ("GetTypeVisible", "get_type_visible", 1),
            ("GetTypeVisible", "get_type_visible", 1.1),
            ("GetTypeVisible", "get_type_visible", None),
            ("GetTypeVisible", "get_type_visible", True),
            ("SetLayerName", "set_layer_name", 1),
            ("SetLayerName", "set_layer_name", 1.1),
            ("SetLayerName", "set_layer_name", None),
            ("SetLayerName", "set_layer_name", True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_with_args_invalid(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        mock_ent_list,
        pascal_name,
        property_name,
        value,
        _,
    ):
        """
        Test the delete_layer method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        getattr(mock_object, pascal_name).return_value = True
        with pytest.raises(TypeError) as e:
            getattr(mock_layer_manager, property_name)(mock_ent_list, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize("red, green, blue", [(1, 2, 3), (0, 0, 0), (255, 255, 255)])
    # pylint: disable-next=R0913, R0917
    def test_set_type_color(
        self, mock_layer_manager: LayerManager, mock_object, mock_ent_list, red, green, blue
    ):
        """
        Test the set_type_color method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        mock_object.SetTypeColor.return_value = True
        result = mock_layer_manager.set_type_color(
            mock_ent_list, EntityType.BEAM, False, red, green, blue
        )
        assert result
        mock_object.SetTypeColor.assert_called_once_with(
            mock_ent_list.ent_list, "B", False, red, green, blue
        )

    @pytest.mark.parametrize(
        "red, green, blue",
        [(-1, 2, 3), (256, 2, 3), (1, -1, 3), (1, 256, 3), (1, 2, -1), (1, 2, 256)],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_type_color_invalid(
        self, mock_layer_manager: LayerManager, mock_object, mock_ent_list, red, green, blue, _
    ):
        """
        Test the set_type_color method of LayerManager with invalid color values.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        mock_object.SetTypeColor.return_value = True
        with pytest.raises(ValueError) as e:
            mock_layer_manager.set_type_color(
                mock_ent_list, EntityType.BEAM, False, red, green, blue
            )
        assert _("Invalid") in str(e.value)
        mock_object.SetTypeColor.assert_not_called()

    @pytest.mark.parametrize(
        "option, expected",
        [(x, x.value) for x in DisplayOption] + [(x.value, x.value) for x in DisplayOption],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_type_display_option(
        self, mock_layer_manager: LayerManager, mock_object, mock_ent_list, option, expected
    ):
        """
        Test the set_type_display_option method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        mock_object.SetTypeDisplayOption.return_value = True
        result = mock_layer_manager.set_type_display_option(mock_ent_list, EntityType.BEAM, option)
        assert result
        mock_object.SetTypeDisplayOption.assert_called_once_with(
            mock_ent_list.ent_list, "B", expected
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name, entity_type, expected_entity, boolean",
        [
            (pascal_name, property_name, x, x.value, boolean)
            for x in EntityType
            for boolean in [True, False]
            for (pascal_name, property_name) in zip(
                ["SetTypeShowLabels", "SetTypeShowGlyphs", "SetTypeVisible"],
                ["set_type_show_labels", "set_type_show_glyphs", "set_type_visible"],
            )
        ]
        + [
            (pascal_name, property_name, x.value, x.value, boolean)
            for x in EntityType
            for boolean in [True, False]
            for (pascal_name, property_name) in zip(
                ["SetTypeShowLabels", "SetTypeShowGlyphs", "SetTypeVisible"],
                ["set_type_show_labels", "set_type_show_glyphs", "set_type_visible"],
            )
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        mock_ent_list,
        pascal_name,
        property_name,
        entity_type,
        expected_entity,
        boolean,
    ):
        """
        Test method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        getattr(mock_object, pascal_name).return_value = True
        result = getattr(mock_layer_manager, property_name)(mock_ent_list, entity_type, boolean)
        assert result
        getattr(mock_object, pascal_name).assert_called_once_with(
            mock_ent_list.ent_list, expected_entity, boolean
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("CreateLayerByName", "create_layer_by_name"), ("FindLayerByName", "find_layer_by_name")],
    )
    # pylint: disable-next=R0913, R0917
    def test_str_return(
        self,
        mock_layer_manager: LayerManager,
        mock_object,
        mock_ent_list,
        pascal_name,
        property_name,
    ):
        """
        Test get_first method of LayerManager with None material.
        Args:
            mock_layer_manager: Instance of LayerManager.
        """
        setattr(mock_object, pascal_name, mock_ent_list.ent_list)
        result = getattr(mock_layer_manager, property_name)("layer_name")
        assert isinstance(result, EntList)
        getattr(mock_object, pascal_name).assert_called_once_with("layer_name")

    def test_expand_layer(self, mock_layer_manager: LayerManager, mock_object, mock_ent_list):
        """
        Test the expand_layer method of LayerManager.
        Args:
            mock_layer_manager: Mock instance of LayerManager.
        """
        mock_object.ExpandLayer2.return_value = True
        result = mock_layer_manager.expand_layer(mock_ent_list, 1, True, False, False, False, False)
        assert result
        mock_object.ExpandLayer2.assert_called_once_with(
            mock_ent_list.ent_list, 1, True, False, False, False, False
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("CreateEntityList", "create_entity_list"), ("GetFirst", "get_first")],
    )
    def test_no_arg_none_return(
        self, mock_layer_manager: LayerManager, mock_object, pascal_name, property_name
    ):
        """
        Test get_first method of LayerManager with None material.
        Args:
            mock_layer_manager: Instance of LayerManager.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_layer_manager, property_name)()
        assert result is None

    def test_get_next_none_return(
        self, mock_layer_manager: LayerManager, mock_object, mock_ent_list
    ):
        """
        Test get_next method of LayerManager with None material.
        Args:
            mock_layer_manager: Instance of LayerManager.
        """
        mock_object.GetNext.return_value = None
        result = mock_layer_manager.get_next(mock_ent_list)
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [("CreateLayerByName", "create_layer_by_name"), ("FindLayerByName", "find_layer_by_name")],
    )
    def test_str_none_return(
        self, mock_layer_manager: LayerManager, mock_object, pascal_name, property_name
    ):
        """
        Test get_first method of LayerManager with None material.
        Args:
            mock_layer_manager: Instance of LayerManager.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_layer_manager, property_name)("layer_name")
        assert result is None
