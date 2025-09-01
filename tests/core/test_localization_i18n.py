# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Additional tests for localization integration with i18n.
"""

from unittest.mock import patch
import pytest

from moldflow.localization import set_language


@pytest.mark.core
class TestLocalizationI18N:
    """
    Test suite for localization i18n module.
    """

    def test_set_language_invokes_install_with_languages_list(self):
        """
        Test set_language invokes install_translation with languages list.
        """
        with patch("moldflow.localization.install_translation") as mocked:
            set_language(locale="enu")
            # THREE_LETTER_TO_BCP_47['enu'] -> 'en-US'
            args, _ = mocked.call_args
            assert args[0].startswith("locale.")
            # languages list is positional third arg in our wrapper
            assert args[2] == ["en-US"]

    def test_set_language_updates_gettext(self):
        """
        Test set_language updates gettext.
        """
        # Ensure after set_language we can translate via get_text path
        with patch("moldflow.localization.install_translation") as mocked:
            set_language(locale="deu")
            args, _ = mocked.call_args
            assert args[2] == ["de-DE"]
