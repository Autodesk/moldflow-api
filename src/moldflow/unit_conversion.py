# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    UnitConversion Class API Wrapper
"""

from .logger import process_log
from .helper import check_type, get_enum_value
from .com_proxy import safe_com
from .common import LogMessage, SystemUnits


class UnitConversion:
    """
    Wrapper for UnitConversion class of Moldflow Synergy.
    """

    def __init__(self, _unit_conversion):
        """
        Initialize the UnitConversion with a UnitConversion instance from COM.

        Args:
            _unit_conversion: The UnitConversion instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="UnitConversion")
        self.unit_conversion = safe_com(_unit_conversion)

    def convert_to_si(self, unit: str, value: float) -> float:
        """
        Convert value to SI Units.

        Args:
            unit (str): Unit Description
            value (float): Value to be converted

        Returns:
            float: The converted value.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="convert_to_si")
        check_type(unit, str)
        check_type(value, (int, float))
        return self.unit_conversion.ConvertToSI(unit, value)

    def convert_to_unit(self, unit: str, unit_system: SystemUnits | str, value: float) -> float:
        """
        Convert value to 'unit system' units.

        Args:
            unit (str): Unit Description
            unit_system (SystemUnits | str): SystemUnits
            value (float): Value to be converted (Must be in SI)

        Returns:
            float: The converted value.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="convert_to_unit")
        check_type(unit, str)
        unit_system = get_enum_value(unit_system, SystemUnits)
        check_type(value, (int, float))
        return self.unit_conversion.ConvertToUnit(unit, unit_system, value)

    def get_unit_description(self, unit: str, unit_system: SystemUnits | str) -> str:
        """
        Return the unit descriptor in the specified unit System.

        Args:
            unit (str): Unit Description
            unit_system (SystemUnits | str): SystemUnits

        Returns:
            str: The unit descriptor in the specified unit System.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_unit_description")
        check_type(unit, str)
        unit_system = get_enum_value(unit_system, SystemUnits)
        return self.unit_conversion.GetUnitDescription(unit, unit_system)
