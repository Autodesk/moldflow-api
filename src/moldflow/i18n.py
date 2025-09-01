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

    Falls back to identity if not yet installed so call sites are safe
    before initialization.
    """
    if _translator is not None:
        return _translator

    # Try builtins._ if someone installed via gettext.install directly
    builtin_fn = getattr(builtins, "_", None)

    if callable(builtin_fn):
        return builtin_fn

    return lambda s: s
