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
import pytest
from moldflow.localization import set_language, get_localization
from moldflow.constants import LOCALE_ENVIRONMENT_VARIABLE_NAME
from tests.core.conftest import TEST_STRING, TEST_TRANSLATION_DICT, DEFAULT_LANG, ENV_LANG
from tests.conftest import TEST_VERSION, VALID_STR


@pytest.mark.core
class TestLocalization:
    """
    Test suite for Localization.
    """

    @pytest.mark.parametrize("locale", list(TEST_TRANSLATION_DICT.keys()))
    def test_set_language(self, locale):
        """
        Test set_language function.
        """
        set_language(locale=locale)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[locale]

    @pytest.mark.parametrize("version", VALID_STR)
    def test_set_language_invalid_version(self, version):
        """
        Test set_language function with invalid version.
        """
        set_language(version=version)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[ENV_LANG]

    @pytest.mark.usefixtures("environment_locale")
    @pytest.mark.parametrize("version", VALID_STR)
    def test_set_language_invalid_version_reg(self, version):
        """
        Test set_language function with invalid version.
        """
        set_language(version=version)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[DEFAULT_LANG]

    @pytest.mark.parametrize("locale", VALID_STR)
    def test_set_language_invalid_locale(self, locale):
        """
        Test set_language function with invalid locale.
        """
        set_language(version=TEST_VERSION, locale=locale)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[DEFAULT_LANG]

    def test_set_language_none(self):
        """
        Test set_language function with invalid locale.
        """
        set_language(version=TEST_VERSION, locale=None)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[ENV_LANG]

    def test_set_language_empty(self):
        """
        Test set_language function with invalid locale.
        """
        set_language(version=TEST_VERSION)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[ENV_LANG]

    @pytest.mark.usefixtures("environment_locale")
    def test_set_language_reg(self):
        """
        Test set_language function with invalid locale.
        """
        set_language(version=TEST_VERSION)
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[DEFAULT_LANG]

    def test_set_language_no_param(self):
        """
        Test set_language function with invalid locale.
        """
        set_language()
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[ENV_LANG]

    @pytest.mark.parametrize("locale", list(TEST_TRANSLATION_DICT.keys()))
    def test_set_language_env(self, locale):
        """
        Test set_language function.
        """
        os.environ[LOCALE_ENVIRONMENT_VARIABLE_NAME] = locale
        set_language()
        _ = get_localization()
        assert _(TEST_STRING) == TEST_TRANSLATION_DICT[locale]
        del os.environ[LOCALE_ENVIRONMENT_VARIABLE_NAME]
