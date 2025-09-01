# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Tests that logger uses i18n.get_text translator.
"""

import logging
from unittest.mock import patch
import pytest

from moldflow.common import LogMessage
from moldflow.logger import process_log, set_is_logging


@pytest.mark.core
class TestLoggerI18N:
    """
    Test suite for logger i18n module.
    """

    def test_process_log_uses_translator(self, caplog):
        """
        Test process_log uses translator.
        """
        set_is_logging(True)
        caplog.set_level(logging.INFO)

        def fake_(s: str) -> str:
            return f"TR:{s}"

        with patch("moldflow.logger.get_text", return_value=fake_):
            process_log(__name__, LogMessage.PROPERTY_SET, name="x", value=1)
            assert "TR:Setting x to 1" in caplog.text
