# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for the Localization functionality of the moldflow-api module.

Classes:
    TestLocalization: Contains test cases for the Localization module.

Test Methods:
    test_set_language: Validates the set_language function with various locales.
    test_set_language_invalid_version: Ensures set_language handles invalid versions correctly.
    test_set_language_invalid_version_reg: Tests set_language with invalid version for registry.
    test_set_language_invalid_locale: Verifies set_language behavior with invalid locales.
    test_set_language_none: Checks set_language with a None locale.
    test_set_language_empty: Tests set_language with no locale specified.
    test_set_language_reg: Validates set_language with environment locale and default language.
    test_set_language_no_param: Ensures set_language works with no parameters.
    test_set_language_env: Confirms set_language respects the environment variable for locale.
"""

import os
from unittest.mock import patch
import pytest
from moldflow.localization import set_language, _normalize_locale_code
from moldflow.constants import LOCALE_ENVIRONMENT_VARIABLE_NAME, THREE_LETTER_TO_BCP_47
from tests.core.conftest import TEST_STRING, TEST_TRANSLATION_DICT, DEFAULT_LANG, ENV_LANG
from tests.conftest import TEST_VERSION, VALID_STR


EXPECTED_TRANSLATIONS = dict(TEST_TRANSLATION_DICT)
EXPECTED_TRANSLATIONS.update(
    {
        bcp47_locale: TEST_TRANSLATION_DICT[three_letter_locale]
        for three_letter_locale, bcp47_locale in THREE_LETTER_TO_BCP_47.items()
        if three_letter_locale in TEST_TRANSLATION_DICT
    }
)


def _expected_translation_for(locale: str | None) -> str:
    normalized_locale = _normalize_locale_code(locale) or DEFAULT_LANG
    return EXPECTED_TRANSLATIONS[normalized_locale]


@pytest.mark.core
class TestLocalization:
    """
    Test suite for Localization.
    """

    @pytest.fixture(autouse=True)
    def no_windows_locale_fallback(self):
        """Keep legacy tests stable unless they explicitly exercise the OS fallback."""
        with patch("moldflow.localization._get_windows_locale_name", return_value=None):
            yield

    @pytest.mark.parametrize("locale", list(TEST_TRANSLATION_DICT.keys()))
    def test_set_language(self, locale):
        """
        Test set_language function.
        """
        _ = set_language(locale=locale)
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[locale]

    @pytest.mark.parametrize("version", VALID_STR)
    def test_set_language_invalid_version(self, version):
        """
        Test set_language function with invalid version.
        """
        _ = set_language(version=version)
        assert _(TEST_STRING) == _expected_translation_for(ENV_LANG)

    @pytest.mark.usefixtures("environment_locale")
    @pytest.mark.parametrize("version", VALID_STR)
    def test_set_language_invalid_version_reg(self, version):
        """
        Test set_language function with invalid version.
        """
        _ = set_language(version=version)
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[DEFAULT_LANG]

    @pytest.mark.parametrize("locale", VALID_STR)
    def test_set_language_invalid_locale(self, locale):
        """
        Test set_language function with invalid locale.
        """
        _ = set_language(version=TEST_VERSION, locale=locale)
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[DEFAULT_LANG]

    def test_set_language_none(self):
        """
        Test set_language function with invalid locale.
        """
        _ = set_language(version=TEST_VERSION, locale=None)
        assert _(TEST_STRING) == _expected_translation_for(ENV_LANG)

    def test_set_language_empty(self):
        """
        Test set_language function with invalid locale.
        """
        _ = set_language(version=TEST_VERSION)
        assert _(TEST_STRING) == _expected_translation_for(ENV_LANG)

    @pytest.mark.usefixtures("environment_locale")
    def test_set_language_reg(self):
        """
        Test set_language function with invalid locale.
        """
        _ = set_language(version=TEST_VERSION)
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[DEFAULT_LANG]

    def test_set_language_no_param(self):
        """
        Test set_language function with invalid locale.
        """
        _ = set_language()
        assert _(TEST_STRING) == _expected_translation_for(ENV_LANG)

    @pytest.mark.parametrize("locale", list(TEST_TRANSLATION_DICT.keys()))
    def test_set_language_env(self, locale):
        """
        Test set_language function.
        """
        os.environ[LOCALE_ENVIRONMENT_VARIABLE_NAME] = locale
        _ = set_language()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[locale]
        del os.environ[LOCALE_ENVIRONMENT_VARIABLE_NAME]

    def test_set_language_windows_locale_fallback(self):
        """
        Test set_language falls back to the Windows user locale.
        """
        with patch("moldflow.localization._get_windows_locale_name", return_value="ja-JP"):
            _ = set_language(version=TEST_VERSION)
        assert _(TEST_STRING) == "テスト文字列"
