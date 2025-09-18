"""Integration tests for message box permutations (Windows only)."""

import platform
import threading
import time
from ctypes import windll, c_wchar_p

import pytest

from moldflow import (
    MessageBox,
    MessageBoxType,
    MessageBoxResult,
    MessageBoxOptions,
    MessageBoxIcon,
    MessageBoxDefaultButton,
    MessageBoxModality,
)


pytestmark = pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only UI test")


# Win32 constants for automation
WM_COMMAND = 0x0111
IDOK = 1
IDCANCEL = 2
IDYES = 6
IDNO = 7
IDRETRY = 4


def _click_dialog_button_async(dialog_title: str, button_id: int, delay_s: float = 0.4) -> None:
    """Helper: simulate clicking a button on a dialog by title after a small delay."""

    def _worker():
        user32 = windll.user32
        # Wait a moment for the dialog to appear
        time.sleep(delay_s)
        # Try to find and click for up to ~5 seconds
        for _ in range(50):
            hwnd = user32.FindWindowW(None, c_wchar_p(dialog_title))
            if hwnd:
                user32.PostMessageW(hwnd, WM_COMMAND, button_id, 0)
                return
            time.sleep(0.1)

    threading.Thread(target=_worker, daemon=True).start()


def _iter_types_and_defaults():
    """Yield (type, valid default_button flags, button_id_to_click)."""
    mapping = {
        MessageBoxType.INFO: (1, IDOK),
        MessageBoxType.WARNING: (1, IDOK),
        MessageBoxType.ERROR: (1, IDOK),
        MessageBoxType.OK_CANCEL: (2, IDCANCEL),
        MessageBoxType.YES_NO: (2, IDYES),
        MessageBoxType.RETRY_CANCEL: (2, IDCANCEL),
        MessageBoxType.YES_NO_CANCEL: (3, IDYES),
        MessageBoxType.ABORT_RETRY_IGNORE: (3, IDRETRY),
        MessageBoxType.CANCEL_TRY_CONTINUE: (3, IDCANCEL),
    }
    for t, (count, click_id) in mapping.items():
        defaults = [None]
        if count >= 2:
            defaults.append(MessageBoxDefaultButton.BUTTON2)
        if count >= 3:
            defaults.append(MessageBoxDefaultButton.BUTTON3)
        if count >= 4:
            defaults.append(MessageBoxDefaultButton.BUTTON4)
        yield t, defaults, click_id


def test_message_box_permutations():
    """Exercise combinations of types, icons, default buttons and modality."""

    icons = [
        None,
        MessageBoxIcon.INFORMATION,
        MessageBoxIcon.WARNING,
        MessageBoxIcon.ERROR,
        MessageBoxIcon.QUESTION,
    ]
    modalities = [None, MessageBoxModality.TASK, MessageBoxModality.SYSTEM]

    for box_type, default_buttons, click_id in _iter_types_and_defaults():
        for icon in icons:
            for default_button in default_buttons:
                for modality in modalities:
                    opts = MessageBoxOptions(
                        icon=icon, default_button=default_button, modality=modality
                    )
                    title = f"Test: {box_type.name}"
                    # Auto click to allow unattended run
                    _click_dialog_button_async(title, click_id)
                    msg = (
                        f"{box_type.name} - {getattr(icon, 'name', 'NONE')} - "
                        f"{getattr(default_button, 'name', 'BUTTON1')} - "
                        f"{getattr(modality, 'name', 'APPLICATION')}"
                    )
                    result = MessageBox(msg, box_type, title=title, options=opts).show()
                    assert isinstance(result, MessageBoxResult)


def test_message_box_input_variants():
    """
    Exercise input dialog with various options.
    """
    variants = [
        MessageBoxOptions(default_text="auto"),
        MessageBoxOptions(default_text="auto", is_password=True),
        MessageBoxOptions(default_text="auto", char_limit=10),
        MessageBoxOptions(default_text="auto", width_dlu=280, height_dlu=90),
    ]
    for i, opts in enumerate(variants, 1):
        title = f"Test: INPUT #{i}"
        _click_dialog_button_async(title, IDOK)
        value = MessageBox(
            "Enter sample text", MessageBoxType.INPUT, title=title, options=opts
        ).show()
        assert isinstance(value, (str, type(None)))
