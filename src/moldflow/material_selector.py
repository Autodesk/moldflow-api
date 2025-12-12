# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    MaterialSelector Class API Wrapper
"""

from .common import MaterialDatabaseType, MaterialIndex
from .logger import process_log
from .helper import check_type, check_is_non_negative, check_range, get_enum_value
from .com_proxy import safe_com

class MaterialSelector:
    """
    Wrapper for MaterialSelector class of Moldflow Synergy.
    """

    def __init__(self, _material_selector):
        """
        Initialize the MaterialSelector with a MaterialSelector instance from COM.

        Args:
            _material_selector: The MaterialSelector instance.
        """
        self.material_selector = safe_com(_material_selector)

    def select(
        self,
        filename: str,
        filetype: MaterialDatabaseType | str,
        index: int,
        material: MaterialIndex | int,
    ) -> bool:
        """
        Selects a material from a database file

        Args:
            filename (str): material database file name
            filetype (MaterialDatabaseType | str): file type, which can be one of the following:
                "System": for databases that reside in the "system" database directory,
                "User": for databases that reside in the "user" directory, and
                "": for databases that reside in neither of the above locations;
                the last option should be used with caution since scripts written with
                'absolute' file path names are typically not usable across
                different versions of the software
            index (int): material index in the database that uniquely identifies this material;
                the easiest way to ascertain the material index is to record a macro
                that selects the material from the database
            material (MaterialIndex | int): 0 to select the material as the first molding material
                and 1 to select it as the second molding material

        Returns:
            True if successful; False otherwise
        """
        process_log(__name__, "select", locals(), name="select")
        check_type(filename, str)
        check_type(filetype, (MaterialDatabaseType, str))
        if filetype != "":
            filetype = get_enum_value(filetype, MaterialDatabaseType)
        check_type(index, int)
        check_is_non_negative(index)
        material = get_enum_value(material, MaterialIndex)
        check_range(material, 0, 1, True, True)
        return self.material_selector.Select(filename, filetype, index, material)

    def select_via_dialog(self, material: MaterialIndex | int, process_id: int) -> bool:
        """
        Allows the user to selects a material from a dialog for the current study

        Args:
            material (MaterialIndex | int): 0 to select the material as the first molding material
                and 1 to select it as the second molding material
            process_id (int): process ID of the client application that is requesting the dialog;
                this is the process ID of the application that is running the script

        Returns:
            True if successful; False otherwise
        """
        process_log(__name__, "select_via_dialog", locals(), name="select_via_dialog")
        material = get_enum_value(material, MaterialIndex)
        check_range(material, 0, 1, True, True)
        check_type(process_id, int)
        return self.material_selector.SelectViaDialog(material, process_id)

    def get_material_file(self, material: MaterialIndex | int) -> str:
        """
        Allows the user to query the current material file name of the current study

        Args:
            material (MaterialIndex | int): 0 to select the material as the first molding material
                and 1 to select it as the second molding material

        Returns:
            Material File Name if successful; "" otherwise
        """
        process_log(__name__, "get_material_file", locals(), name="get_material_file")
        material = get_enum_value(material, MaterialIndex)
        check_range(material, 0, 1, True, True)
        return self.material_selector.GetMaterialFile(material)

    def get_material_file_type(self, material: MaterialIndex | int) -> str:
        """
        Allows the user to query the current material file type of the current study

        Args:
            material (MaterialIndex | int): 0 to select the material as the first molding material
                and 1 to select it as the second molding material

        Returns:
            Material File Type if successful; "" otherwise
        """
        process_log(__name__, "get_material_file_type", locals(), name="get_material_file_type")
        material = get_enum_value(material, MaterialIndex)
        check_range(material, 0, 1, True, True)
        return self.material_selector.GetMaterialFileType(material)

    def get_material_index(self, material: MaterialIndex | int) -> int:
        """
        Allows the user to query the current material index of the current study

        Args:
            material (MaterialIndex | int): 0 to select the material as the first molding material
                and 1 to select it as the second molding material

        Returns:
            Material Index if successful; -1 otherwise
        """
        process_log(__name__, "get_material_index", locals(), name="get_material_index")
        material = get_enum_value(material, MaterialIndex)
        check_range(material, 0, 1, True, True)
        return self.material_selector.GetMaterialIndex(material)
