# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Project Class API Wrapper
"""

from .helper import check_type, get_enum_value, check_index
from .com_proxy import safe_com
from .common import ItemType, DuplicateOption, ImportUnitIndex
from .logger import process_log, LogMessage

class Project:
    """
    Wrapper for Project class of Moldflow Synergy.
    """

    def __init__(self, _project):
        """
        Initialize the Project with a Project instance from COM.

        Args:
            _project: The Project instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Project")
        self.project = safe_com(_project)

    def close(self, prompts: bool = True) -> bool:
        """
        Close the current project.

        Args:
            prompts (bool): Whether to prompt for saving changes.

        Returns:
            bool: True if the project is closed successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="close")
        check_type(prompts, bool)
        result = self.project.Close2(prompts)
        if result:
            self.project = None
        return result

    def save_all(self) -> bool:
        """
        Save all open documents.

        Returns:
            bool: True if the project is saved successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_all")
        return self.project.SaveAll

    def new_study(self, study_name: str) -> bool:
        """
        Create a new study in the project.

        Args:
            study_name (str): The name of the study.

        Returns:
            bool: True if the study is created successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="new_study")
        check_type(study_name, str)
        return self.project.NewStudy(study_name)

    def new_folder(self, folder_name: str) -> bool:
        """
        Create a new folder in the project.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            bool: True if the folder is created successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="new_folder")
        check_type(folder_name, str)
        return self.project.NewFolder(folder_name)

    def select_folder(self, folder_name: str) -> bool:
        """
        Select a folder.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            bool: True if the folder is selected successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="select_folder")
        check_type(folder_name, str)
        return self.project.SelectFolder(folder_name)

    def attach(self, item_name: str) -> bool:
        """
        Attach an item to the project.

        Args:
            item_name (str): The name of the item.

        Returns:
            bool: True if the item is attached successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="attach")
        check_type(item_name, str)
        return self.project.Attach(item_name)

    def compact(self) -> bool:
        """
        Compacts current project by removing redundant restart files.

        Returns:
            bool: True if the project is compacted successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="compact")
        return self.project.Compact

    # pylint: disable=R0913, R0917
    def export(
        self,
        file_name: str,
        selected: bool,
        results: bool,
        criteria_file: str = "",  # pylint: disable=W0613
        restrict: bool = False,  # pylint: disable=W0613
        skip_cad: bool = False,
    ) -> bool:
        """
        Export the project to a file.

        Args:
            file_name (str): The name of the file to export.
            selected (bool): Export selected items only or all.
            results (bool): Export results too.
            criteria_file (str): Export criteria file. - Deprecated value is ignored
            restrict (bool): Restrict export based on criteria contents. - Deprecated
                value is ignored
            skip_cad (bool): Skip CAD Data.

        Returns:
            bool: True if the project is exported successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="export")
        check_type(file_name, str)
        check_type(selected, bool)
        check_type(results, bool)
        check_type(skip_cad, bool)
        return self.project.Export3(file_name, selected, results, "", False, skip_cad)

    def export_model(self, file_name: str, unit_index: ImportUnitIndex | int = None) -> bool:
        """
        Export the model to a file.

        Args:
            file_name (str): The name of the file to export.
            unit_index (optional): The unit index for the export.

        Returns:
            bool: True if the model is exported successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="export_model")
        check_type(file_name, str)
        if unit_index is not None:
            unit_index = get_enum_value(unit_index, ImportUnitIndex)
            return self.project.ExportModel2(file_name, unit_index)
        return self.project.ExportModel(file_name)

    def duplicate_study_by_name(
        self, study_name: str, save_study: bool = False, duplicate_option: DuplicateOption | int = 2
    ) -> bool:
        """
        Duplicate a study by name.

        Args:
            study_name (str): The name of the study.
            save_study (bool): Save the study after duplication.
            duplicate_option (DuplicateOption | int): The option for duplication.
        Returns:
            bool: True if the study is duplicated successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="duplicate_study_by_name")
        check_type(study_name, str)
        check_type(save_study, bool)
        duplicate_option = get_enum_value(duplicate_option, DuplicateOption)
        return self.project.DuplicateStudyByName3(study_name, save_study, duplicate_option)

    def delete_item_by_name(self, item_name: str, item_type: ItemType | str) -> bool:
        """
        Delete an item by name.

        Args:
            item_name (str): The name of the item.
            item_type (ItemType | str): The type of the item.

        Returns:
            bool: True if the item is deleted successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_item_by_name")
        check_type(item_name, str)
        item_type = get_enum_value(item_type, ItemType)
        return self.project.DeleteItemByName(item_name, item_type)

    def rename_item_by_name(self, old_name: str, item_type: ItemType | str, new_name: str) -> bool:
        """
        Rename an item by name.

        Args:
            old_name (str): The old name of the item.
            item_type (ItemType | str): The type of the item.
            new_name (str): The new name of the item.

        Returns:
            bool: True if the item is renamed successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rename_item_by_name")
        check_type(old_name, str)
        item_type = get_enum_value(item_type, ItemType)
        check_type(new_name, str)
        return self.project.RenameItemByName(old_name, item_type, new_name)

    def open_item_by_name(self, item_name: str, item_type: ItemType | str) -> bool:
        """
        Open an item by name.

        Args:
            item_name (str): The name of the item.
            item_type (ItemType | str): The type of the item.

        Returns:
            bool: True if the item is opened successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="open_item_by_name")
        check_type(item_name, str)
        item_type = get_enum_value(item_type, ItemType)
        return self.project.OpenItemByName(item_name, item_type)

    def open_item_by_index(self, item_index: int) -> bool:
        """
        Open an item by index. [1-based indexing]

        Args:
            item_index (int): The index of the item.

        Returns:
            bool: True if the item is opened successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="open_item_by_index")
        check_type(item_index, int)
        return self.project.OpenItemByIndex(item_index)

    def rename_item_by_index(self, index: int, new_name: str) -> bool:
        """
        Rename an item by index.

        Args:
            index (int): The index of the item.
            new_name (str): The new name of the item.

        Returns:
            bool: True if the item is renamed successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rename_item_by_index")
        check_type(index, int)
        check_type(new_name, str)
        return self.project.RenameItemByIndex(index, new_name)

    def delete_item_by_index(self, index: int) -> bool:
        """
        Delete an item by index.

        Args:
            index (int): The index of the item.

        Returns:
            bool: True if the item is deleted successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_item_by_index")
        check_type(index, int)
        return self.project.DeleteItemByIndex(index)

    def move_item_to_folder(
        self, item_name: str, item_type: ItemType | str, folder_name: str
    ) -> bool:
        """
        Move an item to a folder.

        Args:
            item_name (str): The name of the item.
            item_type (ItemType | str): The type of the item.
            folder_name (str): The name of the folder.

        Returns:
            bool: True if the item is moved successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="move_item_to_folder")
        check_type(item_name, str)
        item_type = get_enum_value(item_type, ItemType)
        check_type(folder_name, str)
        return self.project.MoveItemToFolder(item_name, item_type, folder_name)

    def duplicate_study_by_index(
        self, item_index: int, save_study: bool = False, duplicate_option: DuplicateOption | int = 2
    ) -> bool:
        """
        Duplicate a study by index.

        Args:
            item_index (int): The index of the study.
            save_study (bool): Save the study after duplication.
            duplicate_option (DuplicateOption | int): The option for duplication.

        Returns:
            bool: True if the study is duplicated successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="duplicate_study_by_index")
        check_type(item_index, int)
        check_type(save_study, bool)
        duplicate_option = get_enum_value(duplicate_option, DuplicateOption)
        return self.project.DuplicateStudyByIndex3(item_index, save_study, duplicate_option)

    def get_first_study_name(self) -> str:
        """
        Get the first study name.

        Returns:
            str: The name of the first study.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_study_name")
        return self.project.GetFirstStudyName

    def get_next_study_name(self, study_name: str) -> str:
        """
        Get the next study name.

        Args:
            study_name (str): The name of the study.

        Returns:
            str: The name of the next study.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_study_name")
        check_type(study_name, str)
        return self.project.GetNextStudyName(study_name)

    def get_first_report_name(self) -> str:
        """
        Get the first report name.

        Returns:
            str: The name of the first report.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_report_name")
        return self.project.GetFirstReportName

    def get_next_report_name(self, report_name: str) -> str:
        """
        Get the next report name.

        Args:
            report_name (str): The name of the report.

        Returns:
            str: The name of the next report.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_report_name")
        check_type(report_name, str)
        return self.project.GetNextReportName(report_name)

    def get_first_folder_name(self) -> str:
        """
        Get the first folder name.

        Returns:
            str: The name of the first folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_folder_name")
        return self.project.GetFirstFolderName

    def get_next_folder_name(self, folder_name: str) -> str:
        """
        Get the next folder name.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            str: The name of the next folder.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_folder_name")
        check_type(folder_name, str)
        return self.project.GetNextFolderName(folder_name)

    def copy_study_settings(self, from_name: str, to_name: str) -> bool:
        """
        Copy study settings from one study to another.

        Args:
            from_name (str): The name of the source study.
            to_name (str): The name of the destination study.

        Returns:
            bool: True if the settings are copied successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="copy_study_settings")
        check_type(from_name, str)
        check_type(to_name, str)
        return self.project.CopyStudySettings(from_name, to_name)

    def get_number_of_items(self) -> int:
        """
        Get the number of items in the project.

        Returns:
            int: The number of items.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_number_of_items")
        return self.project.GetNumberOfItems

    def get_item_name_by_index(self, index: int) -> str:
        """
        Get the item name by index.[1-based indexing]

        Args:
            index (int): The index of the item.

        Returns:
            str: The name of the item.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_item_name_by_index")
        check_type(index, int)
        check_index(index, 1, self.get_number_of_items() + 1)
        return self.project.GetItemNameByIndex(index)

    def is_open(self, study_name: str) -> bool:
        """
        Check if a study is open.

        Args:
            study_name (str): The name of the study.

        Returns:
            bool: True if the study is open.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="is_open")
        check_type(study_name, str)
        return self.project.IsOpen(study_name)

    def expand_folder(self, folder_name: str) -> bool:
        """
        Expand a folder.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            bool: True if the folder is expanded successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="expand_folder")
        check_type(folder_name, str)
        return self.project.ExpandFolder(folder_name)

    def close_folder(self, folder_name: str) -> bool:
        """
        Close a folder.

        Args:
            folder_name (str): The name of the folder.

        Returns:
            bool: True if the folder is closed successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="close_folder")
        check_type(folder_name, str)
        return self.project.CloseFolder(folder_name)

    @property
    def path(self) -> str:
        """
        The path of the project.

        :getter: Get the path of the project.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="path")
        return self.project.Path

    @property
    def name(self) -> str:
        """
        The name of the project.

        :getter: Get the name of the project.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="name")
        return self.project.Name
