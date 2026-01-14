# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Server Class API Wrapper
"""

from .logger import process_log
from .common import LogMessage
from .com_proxy import safe_com


class Server:
    """
    Wrapper for Server class of Moldflow Synergy.
    """

    def __init__(self, _server):
        """
        Initialize the Server with a Server instance from COM.

        Args:
            _server: The Server instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Server")
        self.server = safe_com(_server)

    @property
    def address(self) -> str:
        """
        Address of the server.

        :getter: Get the address of the server.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="address")
        return self.server.Address

    @property
    def name(self) -> str:
        """
        Name of the server.

        :getter: Get the name of the server.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="name")
        return self.server.Name

    @property
    def status(self) -> str:
        """
        Status of the server.

        :getter: Get the status of the server.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="status")
        return self.server.Status
