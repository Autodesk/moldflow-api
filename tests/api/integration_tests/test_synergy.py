# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Synergy integration test for the moldflow-api setup.
"""

import pytest
from moldflow import Synergy


@pytest.mark.integration
class TestSynergy:
    """Synergy integration test class for moldflow-api"""

    def test_synergy(self):
        """
        Test Synergy class
        This test is to check if the Synergy class is working as expected.
        It tests opening synergy and the opening of the most recent project.
        It then tests the quit function.
        """
        synergy = Synergy(logging=False)
        assert synergy.project is None, "Project should be None before opening"
        synergy.open_recent_project(0)
        assert synergy.project is not None, "Project should not be None after opening"
        synergy.quit(False)
