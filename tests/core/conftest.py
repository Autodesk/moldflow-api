# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""This module contains pytest fixtures for the moldflow-api tests."""

import os
import pytest
from moldflow.constants import DEFAULT_THREE_LETTER_CODE, LOCALE_ENVIRONMENT_VARIABLE_NAME

DEFAULT_LANG = DEFAULT_THREE_LETTER_CODE
TEST_STRING = "Test String"
TEST_TRANSLATION_DICT = {
    "deu": "Testzeichenfolge",
    "enu": "Test String",
    "esn": "Cadena de prueba",
    "fra": "Strime de test",
    "ita": "Stringa di prova",
    "jpn": "テスト文字列",
    "kor": "테스트 문자열",
    "ptg": "String de teste",
    "chs": "测试字符串",
    "cht": "測試字符串",
}

ENV_LANG = os.getenv(LOCALE_ENVIRONMENT_VARIABLE_NAME, DEFAULT_LANG)


@pytest.fixture
def environment_locale():
    """
    Fixture to set the environment locale.
    """
    env_value = os.getenv(LOCALE_ENVIRONMENT_VARIABLE_NAME, None)
    if LOCALE_ENVIRONMENT_VARIABLE_NAME in os.environ:
        del os.environ[LOCALE_ENVIRONMENT_VARIABLE_NAME]
    yield
    if env_value:
        os.environ[LOCALE_ENVIRONMENT_VARIABLE_NAME] = env_value
