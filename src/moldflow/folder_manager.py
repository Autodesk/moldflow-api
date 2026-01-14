# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    FolderManager Class API Wrapper
"""

from .logger import process_log, LogMessage
from .ent_list import EntList
from .common import EntityType, DisplayOption
from .helper import (
    get_enum_value,
    check_type,
    check_and_coerce_optional,
    check_range,
)
from .com_proxy import safe_com


class FolderManager:
    """
    Wrapper for FolderManager class of Moldflow Synergy.
    """

    def __init__(self, _folder_manager):
        """
        Initialize the FolderManager with a FolderManager instance from COM.

        Args:
            _folder_manager: The FolderManager instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="FolderManager")
        self.folder_manager = safe_com(_folder_manager)

    def create_folder(self) -> bool:
        """
        Create a new layer folder.

        Returns:
            bool: True if the folder was created successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_folder")
        return self.folder_manager.CreateFolder

    def create_child_layer(self, folder: EntList | None) -> EntList:
        """
        Create a child layer in the folder.

        Args:
            folder (EntList): The folder in which to create the child layer.

        Returns:
            EntList: The created child layer.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_child_layer")

        result = self.folder_manager.CreateChildLayer(check_and_coerce_optional(folder, EntList))
        if result is None:
            return None
        return EntList(result)

    def create_child_folder(self, folder: EntList | None) -> EntList:
        """
        Create a child folder in the folder.

        Args:
            folder (EntList): The folder in which to create the child folder.

        Returns:
            EntList: The created child folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_child_folder")

        result = self.folder_manager.CreateChildFolder(check_and_coerce_optional(folder, EntList))
        if result is None:
            return None
        return EntList(result)

    def add_objects_to_folder(self, objects: EntList | None, folder: EntList | None) -> bool:
        """
        Add layers/folders to the folder.

        Args:
            objects (EntList): The objects to add.
            folder (EntList): The folder to which to add the objects.

        Returns:
            bool: True if the objects were added successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_objects_to_folder")

        return self.folder_manager.AddObjectsToFolder(
            check_and_coerce_optional(objects, EntList), check_and_coerce_optional(folder, EntList)
        )

    def remove_objects_from_folder(self, objects: EntList | None) -> bool:
        """
        Remove layers/folders from the parent folder.

        Args:
            objects (EntList): The objects to remove.

        Returns:
            bool: True if the objects were removed successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="remove_objects_from_folder")

        return self.folder_manager.RemoveObjectsFromFolder(
            check_and_coerce_optional(objects, EntList)
        )

    def create_entity_list(self) -> EntList:
        """
        Create an entity list.

        Returns:
            EntList: The created entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.folder_manager.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def delete_folder(self, folder: EntList | None, move_layers: bool) -> bool:
        """
        Delete a folder.

        Args:
            folder (EntList): The folder to delete.
            move_layers (bool): Whether to move layers under the folder to the active layer
            or to delete them.

        Returns:
            bool: True if the folder was deleted successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_folder")

        check_type(move_layers, bool)
        return self.folder_manager.DeleteFolder(
            check_and_coerce_optional(folder, EntList), move_layers
        )

    def toggle_folder(self, folder: EntList | None) -> bool:
        """
        Toggle the visibility of a folder.

        Args:
            folder (EntList): The folder to toggle.

        Returns:
            bool: True if the folder was toggled successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="toggle_folder")

        return self.folder_manager.ToggleFolder(check_and_coerce_optional(folder, EntList))

    # pylint: disable-next=R0913, R0917
    def expand_folder(
        self,
        folder: EntList | None,
        levels: int,
        expand_new_layer: bool,
        inc_nodes: bool,
        inc_tris: bool,
        inc_tetras: bool,
        inc_beams: bool,
    ) -> int:
        """
        Expand a folder to a specified number of levels.

        Args:
            folder (EntList): The folder to expand.
            levels (int): The number of levels to expand.
            expand_new_layer (bool): Whether to create a new layer for the expanded entities.
            inc_nodes (bool): Whether to include mesh nodes.
            inc_tris (bool): Whether to include mesh triangles.
            inc_tetras (bool): Whether to include mesh tetras.
            inc_beams (bool): Whether to include mesh beams.

        Returns:
            int: The number of entities affected.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="expand_folder")

        # pylint: disable=R0801
        check_type(levels, int)
        check_type(expand_new_layer, bool)
        check_type(inc_nodes, bool)
        check_type(inc_tris, bool)
        check_type(inc_tetras, bool)
        check_type(inc_beams, bool)
        return self.folder_manager.ExpandFolder(
            check_and_coerce_optional(folder, EntList),
            levels,
            expand_new_layer,
            inc_nodes,
            inc_tris,
            inc_tetras,
            inc_beams,
        )

    def set_folder_name(self, folder: EntList | None, name: str) -> bool:
        """
        Set the name of a folder.

        Args:
            folder (EntList): The folder to rename.
            name (str): The new name for the folder.

        Returns:
            bool: True if the folder name was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_folder_name")

        check_type(name, str)
        return self.folder_manager.SetFolderName(check_and_coerce_optional(folder, EntList), name)

    def show_all_folders(self) -> bool:
        """
        Show all folders.

        Returns:
            bool: True if all folders were shown successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_all_folders")
        return self.folder_manager.ShowAllFolders

    def show_folders(self, folders: EntList | None, show: bool) -> bool:
        """
        Show or hide folders.

        Args:
            folders (EntList): The folders to show or hide.
            show (bool): Whether to show or hide the folders.

        Returns:
            bool: True if the folders were shown/hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_folders")

        check_type(show, bool)
        return self.folder_manager.ShowFolders(check_and_coerce_optional(folders, EntList), show)

    # pylint: disable-next=R0913, R0917
    def set_type_color(
        self,
        folder: EntList | None,
        entity_type: EntityType | str,
        default: bool,
        red: int,
        green: int,
        blue: int,
    ) -> int:
        """
        Set the color of a folder.

        Args:
            folder (EntList): The folder to set the color for.
            entity_type (EntityType | str): The type of entity.
            default (bool): Whether to use the default color.
            red (int): The red component of the color (0-255).
            green (int): The green component of the color (0-255).
            blue (int): The blue component of the color (0-255).

        Returns:
            int: The integer identifier for the color
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_color")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(default, bool)
        check_type(red, int)
        check_type(green, int)
        check_type(blue, int)
        check_range(red, 0, 255, True, True)
        check_range(green, 0, 255, True, True)
        check_range(blue, 0, 255, True, True)
        return self.folder_manager.SetTypeColor(
            check_and_coerce_optional(folder, EntList), entity_type, default, red, green, blue
        )

    def set_type_visible(
        self, folder: EntList | None, entity_type: EntityType | str, visible: bool
    ) -> bool:
        """
        Set the visibility of a folder.

        Args:
            folder (EntList): The folder to set the visibility for.
            entity_type (EntityType | str): The type of entity.
            visible (bool): Whether to make the folder visible.

        Returns:
            bool: True if the visibility was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_visible")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(visible, bool)
        return self.folder_manager.SetTypeVisible(
            check_and_coerce_optional(folder, EntList), entity_type, visible
        )

    def set_type_display_option(
        self, folder: EntList | None, entity_type: EntityType | str, option: DisplayOption | str
    ) -> bool:
        # pylint: disable=C0301
        """
        Set the display option of a folder.

        Args:
            folder (EntList): The folder to set the display option for.
            entity_type (EntityType | str): The type of entity.
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
        return self.folder_manager.SetTypeDisplayOption(
            check_and_coerce_optional(folder, EntList), entity_type, option
        )

    def get_first(self) -> EntList:
        """
        Get the first folder.

        Returns:
            EntList: The first folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first")
        result = self.folder_manager.GetFirst
        if result is None:
            return None
        return EntList(result)

    def get_next(self, folder: EntList | None) -> EntList:
        """
        Get the next folder.

        Args:
            folder (EntList): The current folder.

        Returns:
            EntList: The next folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next")

        result = self.folder_manager.GetNext(check_and_coerce_optional(folder, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_name(self, folder: EntList | None) -> str:
        """
        Get the name of a folder.

        Args:
            folder (EntList): The folder to get the name of.

        Returns:
            str: The name of the folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_name")

        return self.folder_manager.GetName(check_and_coerce_optional(folder, EntList))

    def show_labels(self, folder: EntList | None, show: bool) -> bool:
        """
        Show or hide labels for a folder.

        Args:
            folder (EntList): The folder to show/hide labels for.
            show (bool): Whether to show or hide the labels.

        Returns:
            bool: True if the labels were shown/hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_labels")

        check_type(show, bool)
        return self.folder_manager.ShowLabels(check_and_coerce_optional(folder, EntList), show)

    def show_glyphs(self, folder: EntList | None, show: bool) -> bool:
        """
        Show or hide glyphs for a folder.

        Args:
            folder (EntList): The folder to show/hide glyphs for.
            show (bool): Whether to show or hide the glyphs.

        Returns:
            bool: True if the glyphs were shown/hidden successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_glyphs")

        check_type(show, bool)
        return self.folder_manager.ShowGlyphs(check_and_coerce_optional(folder, EntList), show)

    def set_type_show_labels(
        self, folder: EntList | None, entity_type: EntityType | str, show: bool
    ) -> bool:
        """
        Set the visibility of labels for a specific entity type in a folder.

        Args:
            folder (EntList): The folder to set the label visibility for.
            entity_type (EntityType | str): The type of entity.
            show (bool): Whether to show or hide the labels.

        Returns:
            bool: True if the label visibility was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_show_labels")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(show, bool)
        return self.folder_manager.SetTypeShowLabels(
            check_and_coerce_optional(folder, EntList), entity_type, show
        )

    def set_type_show_glyphs(
        self, folder: EntList | None, entity_type: EntityType | str, show: bool
    ) -> bool:
        """
        Set the visibility of glyphs for a specific entity type in a folder.

        Args:
            folder (EntList): The folder to set the glyph visibility for.
            entity_type (EntityType | str): The type of entity.
            show (bool): Whether to show or hide the glyphs.

        Returns:
            bool: True if the glyph visibility was set successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_type_show_glyphs")

        entity_type = get_enum_value(entity_type, EntityType)
        check_type(show, bool)
        return self.folder_manager.SetTypeShowGlyphs(
            check_and_coerce_optional(folder, EntList), entity_type, show
        )

    def create_folder_by_name(self, name: str) -> EntList:
        """
        Create a folder by name.

        Args:
            name (str): The name of the folder to create.

        Returns:
            EntList: The created folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_folder_by_name")
        check_type(name, str)
        result = self.folder_manager.CreateFolderByName(name)
        if result is None:
            return None
        return EntList(result)

    def find_folder_by_name(self, name: str) -> EntList:
        """
        Find a folder by name.

        Args:
            name (str): The name of the folder to find.

        Returns:
            EntList: The found folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_folder_by_name")
        check_type(name, str)
        result = self.folder_manager.FindFolderByName(name)
        if result is None:
            return None
        return EntList(result)

    def hide_all_other_folders(self, folder: EntList | None) -> bool:
        """
        Hide all other folders except the specified one.

        Args:
            folder (EntList): The folder to keep visible.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="hide_all_other_folders")

        return self.folder_manager.HideAllOtherFolders(check_and_coerce_optional(folder, EntList))

    def remove_empty_folders(self) -> bool:
        """
        Remove empty folders.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="remove_empty_folders")
        return self.folder_manager.RemoveEmptyFolders

    def allow_clipping(self, folder: EntList | None, checked: bool) -> bool:
        """
        Allow clipping for a folder.

        Args:
            folder (EntList): The folder to set clipping for.
            checked (bool): Whether to allow clipping.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="allow_clipping")

        check_type(checked, bool)
        return self.folder_manager.AllowClipping(
            check_and_coerce_optional(folder, EntList), checked
        )
