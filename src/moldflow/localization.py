# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Localization module for Moldflow."""

import os
import gettext
import winreg

from .constants import (
    LOCALE_FILE_NAME,
    THREE_LETTER_TO_BCP_47,
    DEFAULT_BCP_47_STD,
    DEFAULT_THREE_LETTER_CODE,
    LOCALE_DIR,
    USER_LOCALE_KEY,
    LOCALE_ENVIRONMENT_VARIABLE_NAME,
    LOCALE_REGISTRY_VARIABLE_NAME,
    DEFAULT_LOCALE_KEY,
    LOCALE_LOCATION,
)
from .common import LogMessage
from .logger import process_log

_ = gettext.gettext


def get_locale(product_name: str = "Moldflow Synergy", version: str = ""):
    """
    Get the locale of the specified Autodesk product from the Windows registry.
    Args:
        product_name (str): The name of the Autodesk product. Defaults to "Moldflow Synergy".
        version (str): The version of the Autodesk product. Defaults to "2026".
    Returns:
        str: The locale of the product if found, otherwise None.
    Raises:
        FileNotFoundError: If the registry key or value is not found.
    """

    def _process_locale(method: str, product_key: str, value: str):
        """
        Process the locale.

        Args:
            method (str): The method used to fetch the locale.
            product_key (str): The product key.
            value (str): The value to process.
        """
        process_log(__name__, LogMessage.LANG_METHOD, method=method, product_key=product_key)
        process_log(__name__, LogMessage.SYSTEM_SET, name="Language", value=value)

    def _fetch_registry_value(
        winreg_key: int, location: str, value_name: str, registry_method: str
    ):
        """
        Fetch a value from the Windows registry.

        Args:
            winreg_key (int): The Windows registry key.
            location (str): The location of the registry key.
            value_name (str): The name of the registry value.
            registry_method (str): The method used to fetch the registry value.

        Returns:
            str: The value from the Windows registry if found, otherwise None.
        """
        try:
            location = location.format(product_name=product_name, version=version)
            with winreg.OpenKey(winreg_key, location) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                _process_locale(registry_method, f"{location}\\{value_name}", value)
                return value
        except FileNotFoundError:
            return None

    # Environment Variable
    locale = os.getenv(LOCALE_ENVIRONMENT_VARIABLE_NAME)
    if locale:
        _process_locale("Environment Variable", LOCALE_ENVIRONMENT_VARIABLE_NAME, locale)
        return locale

    # Registry - User
    locale = _fetch_registry_value(
        USER_LOCALE_KEY, LOCALE_LOCATION, LOCALE_REGISTRY_VARIABLE_NAME, "Registry - User"
    )
    if locale:
        return locale

    # Registry - Default
    locale = _fetch_registry_value(
        DEFAULT_LOCALE_KEY, LOCALE_LOCATION, LOCALE_REGISTRY_VARIABLE_NAME, "Registry - Default"
    )
    if locale:
        return locale

    # Default
    _process_locale("Default", "", DEFAULT_BCP_47_STD)
    return DEFAULT_THREE_LETTER_CODE


def set_language(product_name: str = "Moldflow Synergy", version: str = "", locale: str = ""):
    """
    Set the language for the application based on the product name and version.
    This function attempts to load the appropriate translation file for the given
    product name and version. If the translation file is not found, it defaults to
    the predefined default language.
    Args:
        product_name (str): The name of the product for which the language is being set.
                            Defaults to "Moldflow Synergy".
        version (str): The version of the product for which the language is being set.
                       Defaults to "".
        locale (str): The locale to set. Defaults to "".

    Returns:
        function: The gettext translation function for the specified language.
    """
    global _
    if not locale:
        locale = get_locale(product_name, version).lower()
    try:
        locale = THREE_LETTER_TO_BCP_47[locale]
    except KeyError:
        locale = DEFAULT_BCP_47_STD

    locale_file_name_custom = f"{LOCALE_FILE_NAME}.{locale}"
    translation = gettext.translation(locale_file_name_custom, LOCALE_DIR, [locale])
    translation.install()
    _ = translation.gettext


def get_localization():
    """
    Get the localization function for the current language.

    Returns:
        function: The gettext translation function for the current language.
    """
    return _
