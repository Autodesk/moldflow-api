# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    LayerManager Class API Wrapper
"""

from .ent_list import EntList
from .common import EntityType, DisplayOption
from .logger import process_log, LogMessage
from .helper import (
    check_type,
    check_and_coerce_optional,
    check_and_coerce_optional,
    check_range,
    get_enum_value,
)
from .com_proxy import safe_com


class LayerManager:
    """
    Wrapper for LayerManager class of Moldflow Synergy.
    """

    def __init__(self, _layer_manager):
        """
        Initialize the LayerManager with a LayerManager instance from COM.

        Args:
            _layer_manager: The LayerManager instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="LayerManager")
        self.layer_manager = safe_com(_layer_manager)

    def active(self, layer: EntList | None) -> bool:
        """
        Returns whether a layer is the active layer or not

        Args:
            layer (EntList): The layer to check.

        Returns:
            bool: True if the layer is active, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="active")

        return self.layer_manager.Active(check_and_coerce_optional(layer, EntList))

    def create_layer(self) -> bool:
        """
        Creates a new layer.

        Returns:
            bool: True if the layer was created successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_layer")
        return self.layer_manager.CreateLayer

    def activate_layer(self, layer: EntList | None) -> bool:
        """
        Activates a layer.

        Args:
            layer (EntList): The layer to activate.

        Returns:
            bool: True if the layer was activated successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="activate_layer")

        return self.layer_manager.ActivateLayer(check_and_coerce_optional(layer, EntList))

    def create_entity_list(self) -> EntList:
        """
        Creates a new entity list.

        Returns:
            EntList: The created entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.layer_manager.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def assign_to_layer(self, elems: EntList | None, layer: EntList | None) -> int:
        """
        Assigns elements to a layer.

        Args:
            elems (EntList): The elements to assign.
            layer (EntList): The layer to assign the elements to.

        Returns:
            int: The number of elements assigned to the layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="assign_to_layer")

        return self.layer_manager.AssignToLayer(
            check_and_coerce_optional(elems, EntList), check_and_coerce_optional(layer, EntList)
        )

    def delete_layer(self, layer: EntList | None, move_ent: bool) -> bool:
        """
        Deletes a layer.

        Args:
            layer (EntList): The layer to delete.
            move_ent (bool): Whether to move entities to the active layer or
                delete them with the layer.

        Returns:
            bool: True if the layer was deleted successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_layer")

        check_type(move_ent, bool)
        return self.layer_manager.DeleteLayer(check_and_coerce_optional(layer, EntList), move_ent)

    def toggle_layer(self, layer: EntList | None) -> bool:
        """
        Toggles the visibility of a layer.

        Args:
            layer (EntList): The layer to toggle.

        Returns:
            bool: True if the layer was toggled successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="toggle_layer")

        return self.layer_manager.ToggleLayer(check_and_coerce_optional(layer, EntList))

    # pylint: disable-next=R0913, R0917
    def expand_layer(
        self,
        layer: EntList | None,
        levels: int,
        expand_new_layer: bool,
        inc_nodes: bool = True,
        inc_tris: bool = True,
        inc_tetras: bool = True,
        inc_beams: bool = True,
    ) -> int:
        """
        Expands layers by a specified number of "levels" with specified entities

        Args:
            layer (EntList): The layer to expand.
            levels (int): The number of levels to expand.
            expand_new_layer (bool): Whether to expand into a new layer or not.
            inc_nodes (bool): Whether to include nodes in the expansion.
            inc_tris (bool): Whether to include triangles in the expansion.
            inc_tetras (bool): Whether to include tetras in the expansion.
            inc_beams (bool): Whether to include beams in the expansion.

        Returns:
            int: The number of elements expanded.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="expand_layer")

        check_type(levels, int)
        check_type(expand_new_layer, bool)
        check_type(inc_nodes, bool)
        check_type(inc_tris, bool)
        check_type(inc_tetras, bool)
        check_type(inc_beams, bool)
        return self.layer_manager.ExpandLayer2(
            check_and_coerce_optional(layer, EntList),
            levels,
            expand_new_layer,
            inc_nodes,
            inc_tris,
            inc_tetras,
            inc_beams,
        )

    def set_layer_name(self, layer: EntList | None, name: str) -> bool:
        """
        Sets the name of a layer.

        Args:
            layer (EntList): The layer to set the name for.
            name (str): The new name for the layer.

        Returns:
            bool: True if the name was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_layer_name")

        check_type(name, str)
        return self.layer_manager.SetLayerName(check_and_coerce_optional(layer, EntList), name)

    def show_all_layers(self) -> bool:
        """
        Shows all layers.

        Returns:
            bool: True if all layers were shown successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_all_layers")
        return self.layer_manager.ShowAllLayers

    def show_layers(self, layers: EntList | None, show: bool) -> bool:
        """
        Shows or hides specified layers.

        Args:
            layers (EntList): The layers to show or hide.
            show (bool): True to show the layers, False to hide them.

        Returns:
            bool: True if the layers were shown or hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_layers")

        check_type(show, bool)
        return self.layer_manager.ShowLayers(check_and_coerce_optional(layers, EntList), show)

    # pylint: disable-next=R0913, R0917
    def set_type_color(
        self,
        layer: EntList | None,
        entity_type: EntityType | str,
        default: bool,
        red: int,
        blue: int,
        green: int,
    ) -> int:
        """
        Sets color of a given entity type in layers

        Args:
            layer (EntList): The layer to set the color for.
            entity_type (EntityType | str): The entity type to set the color for.
            default (bool): Whether to set the default color or not.
            red (int): The red component of the color (0-255).
            blue (int): The blue component of the color (0-255).
            green (int): The green component of the color (0-255).

        Returns:
            int: The integer identifier for the color
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_color")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(default, bool)
        check_range(red, 0, 255, True, True)
        check_range(blue, 0, 255, True, True)
        check_range(green, 0, 255, True, True)
        return self.layer_manager.SetTypeColor(
            check_and_coerce_optional(layer, EntList), entity_type, default, red, blue, green
        )

    def set_type_visible(
        self, layer: EntList | None, entity_type: EntityType | str, visible: bool
    ) -> bool:
        """
        Sets visibility of a given entity type in layers

        Args:
            layer (EntList): The layer to set the visibility for.
            entity_type (EntityType | str): The entity type to set the visibility for.
            visible (bool): Whether to set the type as visible or not.

        Returns:
            bool: True if the visibility was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_visible")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(visible, bool)
        return self.layer_manager.SetTypeVisible(
            check_and_coerce_optional(layer, EntList), entity_type, visible
        )

    def set_type_display_option(
        self, layer: EntList | None, entity_type: EntityType | str, option: DisplayOption | str
    ) -> bool:
        # pylint: disable=C0301
        """
        Sets display option of a given entity type in layers

        Args:
            layer (EntList): The layer to set the display option for.
            entity_type (EntityType | str): The entity type to set the display option for.
            option (DisplayOption | str): The display option to set.
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Display Option              |  Triangle   |    Beam Elements    | Tert Elements  |  Node  |  Surface  |  Region  | STL Facet  | Curve  |
        +=============================+=============+=====================+================+========+===========+==========+============+========+
        | Solid                       | X           | X                   | X              | -      | X         | X        | X          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Solid + Element Edges       | X           | X                   | X              | -      | -         | -        | -          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Transparent                 | X           | X                   | X              | -      | X         | X        | X          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Transparent + Element Edges | X           | X                   | X              | -      | -         | -        | -          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Shrunken                    | X           | X                   | X              | -      | -         | -        | -          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Axis Line Only              | -           | X                   | -              | -      | -         | -        | -          | X      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Point                       | -           | -                   | -              | X      | -         | -        | -          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Triad                       | -           | -                   | -              | X      | -         | -        | -          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Net                         | -           | -                   | -              | -      | X         | X        | X          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Solid + Net                 | -           | -                   | -              | -      | X         | X        | X          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+
        | Transparent + Net           | -           | -                   | -              | -      | X         | X        | X          | -      |
        +-----------------------------+-------------+---------------------+----------------+--------+-----------+----------+------------+--------+

        Returns:
            bool: True if the display option was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_display_option")

        entity_type = get_enum_value(entity_type, EntityType)
        option = get_enum_value(option, DisplayOption)
        return self.layer_manager.SetTypeDisplayOption(
            check_and_coerce_optional(layer, EntList), entity_type, option
        )

    def get_first(self) -> EntList:
        """
        Gets the first layer.

        Returns:
            EntList: The first layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first")
        result = self.layer_manager.GetFirst
        if result is None:
            return None
        return EntList(result)

    def get_next(self, layer: EntList | None) -> EntList:
        """
        Gets the next layer.

        Args:
            layer (EntList): The current layer.

        Returns:
            EntList: The next layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next")

        result = self.layer_manager.GetNext(check_and_coerce_optional(layer, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_name(self, layer: EntList | None) -> str:
        """
        Gets the name of a layer.

        Args:
            layer (EntList): The layer to get the name for.

        Returns:
            str: The name of the layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_name")

        return self.layer_manager.GetName(check_and_coerce_optional(layer, EntList))

    def show_labels(self, layer: EntList | None, show: bool) -> bool:
        """
        Shows or hides labels for a layer.

        Args:
            layer (EntList): The layer to show or hide labels for.
            show (bool): True to show labels, False to hide them.

        Returns:
            bool: True if the labels were shown or hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_labels")

        check_type(show, bool)
        return self.layer_manager.ShowLabels(check_and_coerce_optional(layer, EntList), show)

    def show_glyphs(self, layer: EntList | None, show: bool) -> bool:
        """
        Shows or hides glyphs for a layer.

        Args:
            layer (EntList): The layer to show or hide labels for.
            show (bool): True to show glyphs, False to hide them.

        Returns:
            bool: True if the glyphs were shown or hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_glyphs")

        check_type(show, bool)
        return self.layer_manager.ShowGlyphs(check_and_coerce_optional(layer, EntList), show)

    def set_type_show_labels(
        self, layer: EntList | None, entity_type: EntityType | str, show: bool
    ) -> bool:
        """
        Sets the visibility of labels for a given entity type in layers

        Args:
            layer (EntList): The layer to set the label visibility for.
            entity_type (EntityType | str): The entity type to set the label visibility for.
            show (bool): Whether to set the type as visible or not.

        Returns:
            bool: True if the label visibility was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_show_labels")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(show, bool)
        return self.layer_manager.SetTypeShowLabels(
            check_and_coerce_optional(layer, EntList), entity_type, show
        )

    def set_type_show_glyphs(
        self, layer: EntList | None, entity_type: EntityType | str, show: bool
    ) -> bool:
        """
        Sets the visibility of glyphs for a given entity type in layers

        Args:
            layer (EntList): The layer to set the glyphs visibility for.
            entity_type (EntityType | str): The entity type to set the glyphs visibility for.
            show (bool): Whether to set the type as visible or not.

        Returns:
            bool: True if the glyphs visibility was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_show_glyphs")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(show, bool)
        return self.layer_manager.SetTypeShowGlyphs(
            check_and_coerce_optional(layer, EntList), entity_type, show
        )

    def create_layer_by_name(self, name: str) -> EntList:
        """
        Creates a new layer with the specified name.

        Args:
            name (str): The name of the new layer.

        Returns:
            EntList: The created layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_layer_by_name")
        check_type(name, str)
        result = self.layer_manager.CreateLayerByName(name)
        if result is None:
            return None
        return EntList(result)

    def find_layer_by_name(self, name: str) -> EntList:
        """
        Finds a layer by its name.

        Args:
            name (str): The name of the layer to find.

        Returns:
            EntList: The found layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_layer_by_name")
        check_type(name, str)
        result = self.layer_manager.FindLayerByName(name)
        if result is None:
            return None
        return EntList(result)

    def hide_all_other_layers(self, layer: EntList | None) -> bool:
        """
        Hides all layers except the specified layer.

        Args:
            layer (EntList): The layer to keep visible.

        Returns:
            bool: True if all other layers were hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="hide_all_other_layers")

        return self.layer_manager.HideAllOtherLayers(check_and_coerce_optional(layer, EntList))

    def remove_empty_layers(self) -> bool:
        """
        Delete empty layers.

        Returns:
            bool: True if the empty layers were deleted successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="remove_empty_layers")
        return self.layer_manager.RemoveEmptyLayers

    def get_activated(self, layer: EntList | None) -> bool:
        """
        Returns whether a layer is visible or not

        Args:
            layer (EntList): The layer to check.

        Returns:
            bool: True if the layer is visible, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_activated")

        return self.layer_manager.GetActivated(check_and_coerce_optional(layer, EntList))

    def get_type_visible(self, layer: EntList | None, entity_type: EntityType | str) -> bool:
        """
        Gets the visibility of a given entity type in layers

        Args:
            layer (EntList): The layer to get the visibility for.
            entity_type (EntityType | str): The entity type to get the visibility for.

        Returns:
            bool: True if the entity type is visible, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_type_visible")

        entity_type = get_enum_value(entity_type, EntityType)
        return self.layer_manager.GetTypeVisible(
            check_and_coerce_optional(layer, EntList), entity_type
        )

    def get_number_of_layers(self) -> int:
        """
        Gets the number of layers.

        Returns:
            int: The number of layers.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_number_of_layers")
        return self.layer_manager.GetNumberOfLayers

    def allow_clipping(self, layer: EntList | None, checked: bool) -> bool:
        """
        Sets whether clipping is allowed for a layer.

        Args:
            layer (EntList): The layer to set the clipping for.
            checked (bool): True to allow clipping, False otherwise.

        Returns:
            bool: True if the clipping was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="allow_clipping")

        check_type(checked, bool)
        return self.layer_manager.AllowClipping(check_and_coerce_optional(layer, EntList), checked)
