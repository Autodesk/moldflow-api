# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for i18n helper module.
"""

import builtins
from unittest.mock import patch
import pytest

from moldflow.i18n import get_text, install_translation


@pytest.mark.core
class TestI18N:
    """
    Test suite for i18n helper module.
    """

    def test_get_text_fallback_identity(self):
        """
        Test get_text fallback to identity.
        """
        # When nothing installed and no builtins._, returns identity
        with patch.object(builtins, "_", None, create=True):
            _ = get_text()
            assert _("Hello") == "Hello"

    def test_get_text_uses_builtins(self):
        """
        Test get_text uses builtins._ if it exists and is callable.
        """

        # If builtins._ exists and is callable, get_text uses it
        def fake_(s: str) -> str:
            return f"X:{s}"

        with patch.object(builtins, "_", fake_, create=True):
            _ = get_text()
            assert _("Hello") == "X:Hello"

    def test_install_sets_translator_and_builtins(self):
        """
        Test install_translation sets translator and builtins._.
        """

        # Patch gettext.translation to control returned object
        class DummyTranslation:
            """
            Dummy translation class.
            """

            def __init__(self):
                """
                Initialize the dummy translation class.
                """
                self.calls = []

            def install(self):
                """
                Simulate gettext.install setting builtins._.
                """
                builtins._ = self.gettext

            def gettext(self, s: str) -> str:
                """
                Return a dummy translation.
                """
                return f"T:{s}"

        with patch("moldflow.i18n.gettext.translation", return_value=DummyTranslation()) as mocked:
            install_translation("locale.en-US", "C:\\Temp\\locales", ["en-US", "en"])

            # Verify gettext.translation called with languages list
            mocked.assert_called_once()
            _, kwargs = mocked.call_args
            assert kwargs["domain"] == "locale.en-US"
            assert kwargs["localedir"] == "C:\\Temp\\locales"
            assert kwargs["languages"] == ["en-US", "en"]

            _ = get_text()
            assert _("Hello") == "T:Hello"
