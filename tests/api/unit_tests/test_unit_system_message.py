# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for SystemMessage Wrapper Class of moldflow-api module.
"""

import logging
from unittest.mock import Mock
import pytest
from moldflow import SystemMessage, StringArray, DoubleArray, SystemUnits
from moldflow.logger import set_is_logging


@pytest.mark.unit
class TestSystemUnitsMessage:
    """
    Test suite for the SystemMessage class.
    """

    @pytest.fixture
    def mock_system_message(self, mock_object) -> SystemMessage:
        """
        Fixture to create a mock instance of SystemMessage.
        Args:
            mock_object: Mock object for the SystemMessage dependency.
        Returns:
            SystemMessage: An instance of SystemMessage with the mock object.
        """
        return SystemMessage(mock_object)

    @pytest.mark.parametrize(
        "msgid, unit_sys, expected",
        [
            (1, SystemUnits.METRIC, "Metric"),
            (2, SystemUnits.ENGLISH, "English"),
            (3, "Metric", "Metric"),
            (4, "English", "English"),
        ],
    )
    def test_get_data_message(self, mock_system_message: SystemMessage, msgid, unit_sys, expected):
        """
        Test the get_data_message method of SystemMessage class.
        Args:
            mock_system_message: Mock instance of SystemMessage.
            mocker: Mocking library to create mock objects.
        """
        preset_text = Mock(spec=StringArray)
        preset_text.string_array = Mock()
        preset_vals = Mock(spec=DoubleArray)
        preset_vals.double_array = Mock()
        mock_system_message.system_message.GetDataMessage.return_value = "Formatted message"
        result = mock_system_message.get_data_message(msgid, preset_text, preset_vals, unit_sys)
        assert isinstance(result, str)
        assert result == "Formatted message"
        mock_system_message.system_message.GetDataMessage.assert_called_once_with(
            msgid, preset_text.string_array, preset_vals.double_array, expected
        )

    @pytest.mark.parametrize(
        "msgid, unit_sys",
        [(1, 1), ("2", SystemUnits.ENGLISH), (True, "Metric"), (None, "English"), (4, None)],
    )
    def test_get_data_message_invalid_type(
        self, mock_system_message: SystemMessage, msgid, unit_sys, _
    ):
        """
        Test the get_data_message method of SystemMessage class with invalid types.
        Args:
            mock_system_message: Mock instance of SystemMessage.
            mocker: Mocking library to create mock objects.
        """
        preset_text = Mock(spec=StringArray)
        preset_text.string_array = Mock()
        preset_vals = Mock(spec=DoubleArray)
        preset_vals.double_array = Mock()
        with pytest.raises(TypeError) as e:
            mock_system_message.get_data_message(msgid, preset_text, preset_vals, unit_sys)
        assert _("Invalid") in str(e.value)
        mock_system_message.system_message.GetDataMessage.assert_not_called()

    @pytest.mark.parametrize("msgid, unit_sys", [(-1, SystemUnits.ENGLISH)])
    def test_get_data_message_invalid_value(
        self, mock_system_message: SystemMessage, msgid, unit_sys, _
    ):
        """
        Test the get_data_message method of SystemMessage class with invalid enum values.
        Args:
            mock_system_message: Mock instance of SystemMessage.
            mocker: Mocking library to create mock objects.
        """
        preset_text = Mock(spec=StringArray)
        preset_text.string_array = Mock()
        preset_vals = Mock(spec=DoubleArray)
        preset_vals.double_array = Mock()
        with pytest.raises(ValueError) as e:
            mock_system_message.get_data_message(msgid, preset_text, preset_vals, unit_sys)
        assert _("Invalid") in str(e.value)
        mock_system_message.system_message.GetDataMessage.assert_not_called()

    @pytest.mark.parametrize("msgid, unit_sys", [(1, "Temp"), (2, "Test")])
    # pylint: disable-next=R0913, R0917
    def test_get_data_message_invalid_enum(
        self, mock_system_message: SystemMessage, mock_object, msgid, unit_sys, _, caplog
    ):
        """
        Test the get_data_message method of SystemMessage class with invalid enum values.
        Args:
            mock_system_message: Mock instance of SystemMessage.
            mocker: Mocking library to create mock objects.
        """
        set_is_logging(True)
        moldflow_logger = logging.getLogger("moldflow")
        moldflow_logger.propagate = True
        preset_text = Mock(spec=StringArray)
        preset_text.string_array = Mock()
        preset_vals = Mock(spec=DoubleArray)
        preset_vals.double_array = Mock()
        mock_system_message.get_data_message(msgid, preset_text, preset_vals, unit_sys)
        mock_object.GetDataMessage.assert_called_once_with(
            msgid, preset_text.string_array, preset_vals.double_array, unit_sys
        )
        assert _("this may cause function call to fail") in caplog.text
