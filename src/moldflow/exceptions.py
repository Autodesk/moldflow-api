# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"Custom Exceptions for Moldflow API"

from .common import ErrorMessage

class SaveError(Exception):
    """Exception raised when saving a file fails."""

    def __init__(self, message: str) -> None:
        """
        Initialize the SaveError exception.

        Args:
            message (str): The error message.
        """
        super().__init__(message)
        self.message = message

class SynergyError(Exception):
    """Exception raised when Synergy fails to initialize."""

    def __init__(self, message: str = ErrorMessage.SYNERGY_ERROR.value) -> None:
        super().__init__(message)
        self.message = message
