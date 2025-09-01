# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    SystemMessage Class API Wrapper
"""

from .string_array import StringArray
from .double_array import DoubleArray
from .common import SystemUnits
from .logger import process_log, LogMessage
from .helper import check_type, get_enum_value, check_is_non_negative, coerce_optional_dispatch
from .com_proxy import safe_com


class SystemMessage:
    """
    Wrapper for SystemMessage class of Moldflow Synergy.
    """

    def __init__(self, _system_message):
        """
        Initialize the SystemMessage with a SystemMessage instance from COM.

        Args:
            _system_message: The SystemMessage instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="SystemMessage")
        self.system_message = safe_com(_system_message)

    def get_data_message(
        self,
        msgid: int,
        preset_text: StringArray | None,
        preset_vals: DoubleArray | None,
        unit_sys: SystemUnits | str,
    ) -> str:
        """
        Retrieve a formatted text, given a message id and arrays of strings and doubles.

        Args:
            msgid (int): The message id.
            preset_text (StringArray | None): The array of strings to be used in the message.
            preset_vals (DoubleArray | None): The array of doubles to be used in the message.
            unit_sys (SystemUnits | str): The unit system to be used in the message.

        Returns:
            str: The formatted message.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_data_message")
        check_type(msgid, int)
        if preset_text is not None:
            check_type(preset_text, StringArray)
        if preset_vals is not None:
            check_type(preset_vals, DoubleArray)
        check_is_non_negative(msgid)
        unit_sys = get_enum_value(unit_sys, SystemUnits)
        return self.system_message.GetDataMessage(
            msgid,
            coerce_optional_dispatch(preset_text, "string_array"),
            coerce_optional_dispatch(preset_vals, "double_array"),
            unit_sys,
        )
