# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Configuration and constants for integration tests.
"""

import pytest
from moldflow import Synergy


@pytest.fixture(scope="class")
def synergy():
    """
    Fixture to create a real Synergy instance for integration testing.
    """
    synergy_instance = Synergy()
    yield synergy_instance
    synergy_instance.quit(False)
