# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Internationalization helpers for Moldflow.

This module owns translation installation and accessors.
"""

import builtins
import gettext
from typing import Callable


_translator: Callable[[str], str] | None = None


def install_translation(
    domain: str, localedir: str, languages: list[str] | None
) -> Callable[[str], str]:
    """
    Install the active translation and set global translator.
    """
    global _translator
    translation = gettext.translation(domain=domain, localedir=localedir, languages=languages)
    translation.install()
    _translator = translation.gettext

    return _translator


def get_text() -> Callable[[str], str]:
    """
    Return the active gettext function.

    Preference order:
    1) builtins._ if present and callable (e.g., set by gettext.install)
    2) internal translator if previously installed via install_translation
    3) identity function
    """
    # Prefer a globally installed builtins._ first so callers that patch it
    # (e.g., tests) always take effect.
    builtin_fn = getattr(builtins, "_", None)
    if callable(builtin_fn):
        return builtin_fn

    if _translator is not None:
        return _translator

    return lambda s: s
