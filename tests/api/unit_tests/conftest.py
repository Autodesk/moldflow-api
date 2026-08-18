# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""This module contains pytest fixtures for the moldflow-api tests.
Fixtures:
    mock_object: A pytest fixture that provides a mock object for the class instantiation."""

import re
from unittest.mock import Mock

import pytest
from moldflow.constants import COLOR_BAND_RANGE
from tests.api.unit_tests.mock_container import MockContainer

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from CLI output."""
    return _ANSI_ESCAPE.sub("", text)


VALID_COLOR_BAND_VALUES = COLOR_BAND_RANGE

VALID_MOCK = MockContainer()

INVALID_MOCK = ["Test", 1.1, 5.9, True, False, 1, 10]
INVALID_MOCK_WITH_NONE = INVALID_MOCK + [None]


@pytest.fixture()
def mock_object():
    """
    A pytest fixture that provides a mock object for synergy for the class instantiation.
    """
    return Mock()
