# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    MaterialFinder Class API Wrapper
"""

from .prop import Property
from .common import MaterialDatabase, MaterialDatabaseType
from .logger import process_log
from .helper import check_type, check_optional_type, check_and_coerce_optional, get_enum_value, coerce_optional_dispatch
from .com_proxy import safe_com
from .common import LogMessage


class MaterialFinder:
    """
    Wrapper for MaterialFinder class of Moldflow Synergy.
    """

    def __init__(self, _material_finder):
        """
        Initialize the MaterialFinder with a MaterialFinder instance from COM.

        Args:
            _material_finder: The MaterialFinder instance from COM.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="MaterialFinder")
        self.material_finder = safe_com(_material_finder)

    def set_data_domain(
        self,
        material_database: MaterialDatabase | int,
        material_database_type: MaterialDatabaseType | str,
    ) -> None:
        """
        Set the material database, and its type for material finder.

        Args:
            material_database (MaterialDatabase | int): The material database to set.
            material_database_type (MaterialDatabaseType | str): The type of material
                database to set.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_data_domain")
        material_database = get_enum_value(material_database, MaterialDatabase)
        material_database_type = get_enum_value(material_database_type, MaterialDatabaseType)

        self.material_finder.SetDataDomain(material_database, material_database_type)

    def get_first_material(self) -> Property:
        """
        Get the first material.

        Returns:
            Property: The first material.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_material")
        result = self.material_finder.GetFirstMaterial
        if result is None:
            return None
        return Property(result)

    def get_next_material(self, material: Property | None) -> Property:
        """
        Get the next material.

        Args:
            material (Property | None): The current material.

        Returns:
            Property: The next material.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_material")

        material_disp = check_and_coerce_optional(material, Property)
        result = self.material_finder.GetNextMaterial(material_disp)
        if result is None:
            return None
        return Property(result)

    @property
    def file_type(self) -> str:
        """
        Get the material database type.

        Returns:
            str: The material database type (System or User).
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="file_type")
        return self.material_finder.FileType
