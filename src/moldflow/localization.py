# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Localization module for Moldflow."""

import ctypes
import os
import winreg

from .constants import (
    DEFAULT_BCP_47_STD,
    DEFAULT_THREE_LETTER_CODE,
    LOCALE_DIR,
    LOCALE_ENVIRONMENT_VARIABLE_NAME,
    LOCALE_FILE_NAME,
    LOCALE_LOCATION,
    LOCALE_REGISTRY_VARIABLE_NAME,
    DEFAULT_LOCALE_KEY,
    USER_LOCALE_KEY,
    THREE_LETTER_TO_BCP_47,
)
from .common import LogMessage
from .i18n import install_translation, get_text
from .logger import process_log


def _normalize_locale_code(locale: str | None) -> str | None:
    """Normalize locale to BCP-47 for gettext."""
    if locale is None:
        return None

    locale_text = str(locale).strip()
    if not locale_text:
        return None

    # Three-letter (from MFSYN_LOCALE / MSI): map to BCP-47
    mapped_locale = THREE_LETTER_TO_BCP_47.get(locale_text.lower())
    if mapped_locale:
        return mapped_locale

    # BCP-47 (from Windows fallback): normalize and pass through
    parts = locale_text.replace("_", "-").split("-")
    if any(not part for part in parts):
        return None
    normalized_parts = []
    for index, part in enumerate(parts):
        if index == 0:
            normalized_parts.append(part.lower())
        elif len(part) == 4 and part.isalpha():
            normalized_parts.append(part.title())
        elif (len(part) == 2 and part.isalpha()) or (len(part) == 3 and part.isdigit()):
            normalized_parts.append(part.upper())
        else:
            normalized_parts.append(part.lower())
    return "-".join(normalized_parts)


def _get_windows_locale_name() -> str | None:
    """Return the Windows user locale as a BCP-47-style tag when available."""
    locale_name_max_length = 85
    buffer = ctypes.create_unicode_buffer(locale_name_max_length)
    get_locale_name = getattr(getattr(ctypes, "windll", None), "kernel32", None)
    if get_locale_name is None:
        return None

    get_user_default_locale_name = getattr(get_locale_name, "GetUserDefaultLocaleName", None)
    if get_user_default_locale_name is None:
        return None

    try:
        result = get_user_default_locale_name(buffer, locale_name_max_length)
    except (AttributeError, OSError, TypeError, ValueError):
        return None

    if not result:
        return None

    return buffer.value or None


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

    def _is_valid_three_letter(value: str) -> bool:
        """Return True if value is a valid three-letter locale (MFSYN_LOCALE / MSI only)."""
        return value.strip().lower() in THREE_LETTER_TO_BCP_47

    # Environment Variable (MFSYN_LOCALE: three-letter only)
    locale = os.getenv(LOCALE_ENVIRONMENT_VARIABLE_NAME)
    if locale and _is_valid_three_letter(locale):
        three_letter = locale.strip().lower()
        _process_locale("Environment Variable", LOCALE_ENVIRONMENT_VARIABLE_NAME, three_letter)
        return three_letter

    # Registry - User (MFSYN_LOCALE: three-letter only)
    locale = _fetch_registry_value(
        USER_LOCALE_KEY, LOCALE_LOCATION, LOCALE_REGISTRY_VARIABLE_NAME, "Registry - User"
    )
    if locale and _is_valid_three_letter(locale):
        return locale.strip().lower()

    # Registry - Default (MFSYN_LOCALE: three-letter only)
    locale = _fetch_registry_value(
        DEFAULT_LOCALE_KEY, LOCALE_LOCATION, LOCALE_REGISTRY_VARIABLE_NAME, "Registry - Default"
    )
    if locale and _is_valid_three_letter(locale):
        return locale.strip().lower()

    # Windows - User Locale (BCP-47-style: accept whatever Windows returns)
    locale = _get_windows_locale_name()
    if locale:
        _process_locale("Windows User Locale", "", locale)
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
    if not locale:
        locale = get_locale(product_name, version)

    locale = _normalize_locale_code(locale) or DEFAULT_BCP_47_STD

    locale_file_name_custom = f"{LOCALE_FILE_NAME}.{locale}"
    try:
        install_translation(locale_file_name_custom, LOCALE_DIR, [locale])
    except FileNotFoundError:
        locale = DEFAULT_BCP_47_STD
        locale_file_name_custom = f"{LOCALE_FILE_NAME}.{locale}"
        install_translation(locale_file_name_custom, LOCALE_DIR, [locale])

    return get_text()
