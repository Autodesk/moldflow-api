# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Predicate Class API Wrapper
"""

from .logger import process_log
from .common import LogMessage
from .com_proxy import safe_com, expose_oleobj


class Predicate:
    """
    Wrapper for Predicate class of Moldflow Synergy.
    """

    def __init__(self, _predicate):
        """
        Initialize the Predicate with a Predicate instance from COM.

        Args:
            _predicate: The Predicate instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Predicate")
        self.predicate = safe_com(_predicate)
        # Expose _oleobj_ so Predicate can be passed directly to COM APIs
        expose_oleobj(self, "predicate")
