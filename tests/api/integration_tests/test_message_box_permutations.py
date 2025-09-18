"""Integration tests for message box permutations (Windows only)."""

# These tests perform UI automation and include short-lived closures and
# complex helper logic. Suppress a few linter warnings that are noisy for
# this test file and do not improve correctness:
# pylint: disable=cell-var-from-loop,unused-argument,too-many-branches,too-many-statements

import threading
import time
import ctypes
from ctypes import windll, c_wchar_p, wintypes

from moldflow import (
    MessageBox,
    MessageBoxType,
    MessageBoxResult,
    MessageBoxOptions,
    MessageBoxIcon,
    MessageBoxDefaultButton,
    MessageBoxModality,
)

# Win32 constants for automation
WM_COMMAND = 0x0111
BM_CLICK = 0x00F5
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
        for _ in range(100):
            hwnd = user32.FindWindowW(None, c_wchar_p(dialog_title))
            if hwnd:
                # Try to find child button control and click it directly
                try:
                    hbtn = user32.GetDlgItem(hwnd, button_id)
                    if hbtn:
                        user32.SendMessageW(hbtn, BM_CLICK, 0, 0)
                        return

                    children = []

                    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                    def _child_enum_proc(hchild, _):
                        # Get class name
                        cname_buf = ctypes.create_unicode_buffer(256)
                        user32.GetClassNameW(hchild, cname_buf, 256)
                        cname = cname_buf.value
                        # Get text
                        tbuf = ctypes.create_unicode_buffer(512)
                        user32.GetWindowTextW(hchild, tbuf, 512)
                        text = tbuf.value
                        # Get control id
                        try:
                            cid = user32.GetDlgCtrlID(hchild)
                        except Exception:
                            cid = 0
                        children.append((hchild, cname, text, cid))
                        return True

                    user32.EnumChildWindows(hwnd, _child_enum_proc, 0)

                    # Try to click first Button child
                    for hchild, cname, _, _ in children:
                        if cname and cname.lower().startswith("button"):
                            user32.SendMessageW(hchild, BM_CLICK, 0, 0)
                            return

                except Exception:
                    # Fallback to posting WM_COMMAND
                    try:
                        user32.PostMessageW(hwnd, WM_COMMAND, button_id, 0)
                        return
                    except Exception:
                        pass
            else:
                # Fallback: enumerate top-level windows and try to find one whose
                # title contains the dialog title as a substring (more tolerant).
                try:
                    found = []

                    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                    def _enum_proc(h, _):
                        buf = ctypes.create_unicode_buffer(512)
                        user32.GetWindowTextW(h, buf, 512)
                        txt = buf.value
                        if txt and dialog_title in txt:
                            found.append(h)
                            return False  # stop enumeration
                        return True

                    user32.EnumWindows(_enum_proc, 0)
                    if found:
                        hwnd = found[0]
                        try:
                            hbtn = user32.GetDlgItem(hwnd, button_id)
                            if hbtn:
                                user32.SendMessageW(hbtn, BM_CLICK, 0, 0)
                                return
                        except Exception:
                            try:
                                user32.PostMessageW(hwnd, WM_COMMAND, button_id, 0)
                                return
                            except Exception:
                                pass
                except Exception:
                    # EnumWindows may fail in some restricted contexts; ignore
                    pass
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
