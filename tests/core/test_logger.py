# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for Logger of moldflow-api module.
Test Details:

Classes:
    TestLogger: Test suite for the Logger class.
Test Methods:
    test_configure_file_logging: Tests if configure file exports to a file based on input
    test_set_is_logging: Tests logging is enable or disabled through a boolean
    test_get_logger: Tests the get_logger function with different logging levels and states.
    test_get_logger_set_level: Tests setting different logging levels for a logger.
    test_none_process_log: Tests the process log function with a None Logger
    test_process_log: Tests the process_log function with various log messages and parameters.
"""

import logging
from unittest.mock import patch
import os
import pytest
from moldflow.common import LogMessage
import moldflow.logger
from moldflow.logger import get_logger, process_log, configure_file_logging, set_is_logging
from moldflow.constants import DEFAULT_LOG_FILE


@pytest.mark.core
class TestLogger:
    """
    Test suite for Logger.
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    @pytest.mark.parametrize(
        "cmdlog, log_file, log_file_name, expected_file",
        [
            (True, True, "custom_log", "custom_log.log"),
            (False, False, None, None),
            (True, True, None, DEFAULT_LOG_FILE),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_configure_file_logging(self, cmdlog, log_file, log_file_name, expected_file, caplog):
        """
        Test configure_file_logging with different inputs.
        """
        if log_file_name is not None:
            configure_file_logging(cmdlog, log_file, log_file_name)
        else:
            configure_file_logging(cmdlog, log_file)
        if moldflow.logger._IS_LOGGING:  # pylint: disable=W0212
            logger = get_logger("test_logger")
            logger.info("Test log message")

            if expected_file:
                assert os.path.exists(expected_file)
                for handler in logger.parent.handlers[:]:
                    logger.removeHandler(handler)
                    handler.close()
                os.remove(expected_file)
            else:
                assert not os.path.exists(DEFAULT_LOG_FILE)
        else:
            assert len(caplog.text) == 0
            assert caplog.text == ""

    @pytest.mark.parametrize("is_logging", [True, False])
    def test_set_is_logging(self, is_logging):
        """
        Test enabling and disabling logging using set_logging.
        """
        logger = None
        assert logger is None

        set_is_logging(is_logging)
        if is_logging:
            # Enable logging
            logger = get_logger("test_logger")
            assert logger is not None
            assert isinstance(logger, logging.Logger)
        else:
            # Disable logging
            logger = get_logger("test_logger")
            assert logger is None

    @pytest.mark.parametrize("is_logging", [True, False])
    def test_get_logger(self, is_logging):
        """
        Test getting logger.
        """
        name = "test_name"
        with patch("moldflow.logger._IS_LOGGING", is_logging):
            if not is_logging:  # If _IS_LOGGING is False
                logger = get_logger(name)
                assert logger is None
            else:
                logger = get_logger(name)
                assert name in logger.name

    @pytest.mark.parametrize("is_logging", [True, False])
    def test_none_process_log(self, is_logging, caplog):
        """
        Test processing log
        """
        with patch("moldflow.logger._IS_LOGGING", is_logging):
            if not is_logging:  # If _IS_LOGGING is False
                process_log(__name__, "This will not log")
                assert len(caplog.text) == 0

    @pytest.mark.parametrize("is_logging", [True, False])
    @pytest.mark.parametrize(
        "message, name, value, expected_output",
        [
            (LogMessage.CLASS_INIT, "synergy", None, "Initializing synergy"),
            (LogMessage.PROPERTY_GET, "test2", None, "Getting test2"),
            (LogMessage.PROPERTY_SET, "test3", 50, "Setting test3 to 50"),
            (LogMessage.FUNCTION_CALL, "test4", None, "Executing test4"),
            (LogMessage.VALID_INPUT, "", None, "Valid Input"),
            (LogMessage.VALID_TYPE, "", None, "Valid Input Type"),
            (LogMessage.HELPER_CHECK, "this", "that", "Checking that is this"),
            ("Hello This is a custom message", None, None, "Hello This is a custom message"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_process_log(self, message, name, value, expected_output, caplog, is_logging):
        """
        Test process_log function.
        """
        moldflow_logger = logging.getLogger("moldflow")
        moldflow_logger.propagate = True
        set_is_logging(is_logging)
        if is_logging:
            process_log(__name__, message, name=name, value=value, location=value, product_key=name)
            assert expected_output in caplog.text
        else:
            assert len(caplog.text) == 0
            assert caplog.text == ""

    @pytest.mark.parametrize("is_logging", [True, False])
    @pytest.mark.parametrize(
        "message, local", [("Running Locals", {"Value 1": 5, "Part 2": "String"})]
    )
    def test_process_log_dumps(self, message, local, caplog, is_logging):
        """
        Test the dumps feature in logging
        """
        set_is_logging(is_logging)
        if is_logging:
            process_log(__name__, message, dump=local)

            for n in local.items():
                assert str(n[0]) in caplog.text
                assert str(n[1]) in caplog.text
        else:
            assert len(caplog.text) == 0
            assert caplog.text == ""
