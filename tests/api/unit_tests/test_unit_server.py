# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for Server Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import Server


@pytest.mark.unit
class TestUnitServer:
    """
    Test suite for the Server class.
    """

    @pytest.fixture
    def mock_server(self, mock_object) -> Server:
        """
        Fixture to create a mock instance of Server.
        Args:
            mock_object: Mock object for the Server dependency.
        Returns:
            Server: An instance of Server with the mock object.
        """
        return Server(mock_object)

    def test_address(self, mock_server: Server, mock_object):
        """
        Test the address property of Server.
        Args:
            mock_server: Instance of Server with mock object.
            mock_object: Mock object for the Server dependency.
        """
        mock_object.Address = "localhost"
        result = mock_server.address
        assert isinstance(result, str)
        assert result == "localhost"

    def test_name(self, mock_server: Server, mock_object):
        """
        Test the name property of Server.
        Args:
            mock_server: Instance of Server with mock object.
            mock_object: Mock object for the Server dependency.
        """
        mock_object.Name = "abc"
        result = mock_server.name
        assert isinstance(result, str)
        assert result == "abc"

    def test_status(self, mock_server: Server, mock_object):
        """
        Test the status property of Server.
        Args:
            mock_server: Instance of Server with mock object.
            mock_object: Mock object for the Server dependency.
        """
        mock_object.Status = "200"
        result = mock_server.status
        assert isinstance(result, str)
        assert result == "200"
