# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
MessageBox convenience wrapper for Moldflow scripts.

Provides simple info/warning/error dialogs, confirmation prompts, and a text
input dialog. Uses Win32 MessageBox for standard dialogs and a lightweight
custom Win32 dialog (ctypes) for text input.
"""

from enum import Enum, auto
from typing import Optional, Union, Callable, TypeAlias
from dataclasses import dataclass
import ctypes
from dataclasses import dataclass
import platform
from ctypes import windll, wintypes, byref, create_unicode_buffer, c_int, c_wchar_p, WINFUNCTYPE
import struct
from .i18n import get_text


# Win32 MessageBox flags (from winuser.h)
WIN_MB_OK = 0x00000000
WIN_MB_OKCANCEL = 0x00000001
WIN_MB_ABORTRETRYIGNORE = 0x00000002
WIN_MB_YESNOCANCEL = 0x00000003
WIN_MB_YESNO = 0x00000004
WIN_MB_RETRYCANCEL = 0x00000005
WIN_MB_CANCELTRYCONTINUE = 0x00000006

WIN_MB_ICONERROR = 0x00000010
WIN_MB_ICONQUESTION = 0x00000020
WIN_MB_ICONWARNING = 0x00000030
WIN_MB_ICONINFORMATION = 0x00000040

WIN_MB_DEFBUTTON2 = 0x00000100
WIN_MB_DEFBUTTON3 = 0x00000200
WIN_MB_DEFBUTTON4 = 0x00000300

WIN_MB_SYSTEMMODAL = 0x00001000
WIN_MB_TASKMODAL = 0x00002000
WIN_MB_HELP = 0x00004000
WIN_MB_SETFOREGROUND = 0x00010000
WIN_MB_TOPMOST = 0x00040000
WIN_MB_RIGHT = 0x00080000
WIN_MB_RTLREADING = 0x00100000

# Win32 MessageBox return IDs
WIN_IDOK = 1
WIN_IDCANCEL = 2
WIN_IDABORT = 3
WIN_IDRETRY = 4
WIN_IDIGNORE = 5
WIN_IDYES = 6
WIN_IDNO = 7
WIN_IDTRYAGAIN = 10
WIN_IDCONTINUE = 11

# Win32 dialog and control style flags (used by input dialog)
WIN_DS_SETFONT = 0x00000040
WIN_DS_MODALFRAME = 0x00000080
WIN_WS_CAPTION = 0x00C00000
WIN_WS_SYSMENU = 0x00080000

WIN_WS_CHILD = 0x40000000
WIN_WS_VISIBLE = 0x10000000
WIN_WS_TABSTOP = 0x00010000
WIN_WS_GROUP = 0x00020000
WIN_WS_BORDER = 0x00800000

WIN_ES_AUTOHSCROLL = 0x00000080
WIN_ES_PASSWORD = 0x00000020
WIN_SS_LEFT = 0x00000000
WIN_BS_DEFPUSHBUTTON = 0x00000001
WIN_BS_PUSHBUTTON = 0x00000000

# Window messages
WIN_WM_INITDIALOG = 0x0110
WIN_WM_COMMAND = 0x0111

# Edit control helpers
WIN_EM_SETCUEBANNER = 0x1501
WIN_EN_CHANGE = 0x0300
WIN_EM_LIMITTEXT = 0x00C5

# SetWindowPos flags and system metrics
WIN_SWP_NOSIZE = 0x0001
WIN_SWP_NOZORDER = 0x0004
WIN_SWP_NOACTIVATE = 0x0010
WIN_SM_CXSCREEN = 0
WIN_SM_CYSCREEN = 1

# Predefined control classes
WIN_CLASS_BUTTON = 0x0081
WIN_CLASS_EDIT = 0x0080
WIN_CLASS_STATIC = 0x0082

# Control IDs
WIN_ID_EDIT = 1001
WIN_ID_OK = 1
WIN_ID_CANCEL = 2

# Defaults
DEFAULT_TITLE = "Moldflow"


class MessageBoxType(Enum):
    """
    Message box types supported by the convenience API.

    - INFO: Informational message with OK button
    - WARNING: Warning message with OK button
    - ERROR: Error message with OK button
    - YES_NO: Confirmation dialog with Yes/No buttons
    - YES_NO_CANCEL: Confirmation dialog with Yes/No/Cancel buttons
    - OK_CANCEL: Prompt with OK/Cancel buttons
    - RETRY_CANCEL: Prompt with Retry/Cancel buttons
    - ABORT_RETRY_IGNORE: Prompt with Abort/Retry/Ignore buttons
    - CANCEL_TRY_CONTINUE: Prompt with Cancel/Try Again/Continue buttons
    - INPUT: Text input dialog returning a string
    """

    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    YES_NO = auto()
    YES_NO_CANCEL = auto()
    OK_CANCEL = auto()
    RETRY_CANCEL = auto()
    ABORT_RETRY_IGNORE = auto()
    CANCEL_TRY_CONTINUE = auto()
    INPUT = auto()


class MessageBoxResult(Enum):
    """
    Result of a message box interaction.

    For INPUT type, the MessageBox.show() method returns a string rather than
    a MessageBoxResult. For other types, it returns one of these values.
    """

    OK = auto()
    CANCEL = auto()
    YES = auto()
    NO = auto()
    RETRY = auto()
    ABORT = auto()
    IGNORE = auto()
    TRY_AGAIN = auto()
    CONTINUE = auto()


# Public type alias for show() return value
MessageBoxReturn: TypeAlias = Union[MessageBoxResult, Optional[str]]


class MessageBoxIcon(Enum):
    """
    Icon to display on the message box. If not provided, a sensible default is
    chosen based on the MessageBoxType.
    """

    NONE = auto()
    INFORMATION = auto()
    WARNING = auto()
    ERROR = auto()
    QUESTION = auto()


class MessageBoxModality(Enum):
    """Modality for the message box window."""

    APPLICATION = auto()  # Default Win32 behavior (no explicit flag)
    SYSTEM = auto()
    TASK = auto()


class MessageBoxDefaultButton(Enum):
    """Which button is the default (activated by Enter)."""

    BUTTON1 = auto()
    BUTTON2 = auto()
    BUTTON3 = auto()
    BUTTON4 = auto()


# Mapping dictionaries (module-level) for flags and results
MAPPING_MESSAGEBOX_TYPE = {
    MessageBoxType.INFO: (WIN_MB_OK, MessageBoxIcon.INFORMATION, 1),
    MessageBoxType.WARNING: (WIN_MB_OK, MessageBoxIcon.WARNING, 1),
    MessageBoxType.ERROR: (WIN_MB_OK, MessageBoxIcon.ERROR, 1),
    MessageBoxType.YES_NO: (WIN_MB_YESNO, MessageBoxIcon.QUESTION, 2),
    MessageBoxType.YES_NO_CANCEL: (WIN_MB_YESNOCANCEL, MessageBoxIcon.QUESTION, 3),
    MessageBoxType.OK_CANCEL: (WIN_MB_OKCANCEL, MessageBoxIcon.INFORMATION, 2),
    MessageBoxType.RETRY_CANCEL: (WIN_MB_RETRYCANCEL, MessageBoxIcon.WARNING, 2),
    MessageBoxType.ABORT_RETRY_IGNORE: (WIN_MB_ABORTRETRYIGNORE, MessageBoxIcon.ERROR, 3),
    MessageBoxType.CANCEL_TRY_CONTINUE: (WIN_MB_CANCELTRYCONTINUE, MessageBoxIcon.WARNING, 3),
}

ICON_TO_FLAG = {
    MessageBoxIcon.INFORMATION: WIN_MB_ICONINFORMATION,
    MessageBoxIcon.WARNING: WIN_MB_ICONWARNING,
    MessageBoxIcon.ERROR: WIN_MB_ICONERROR,
    MessageBoxIcon.QUESTION: WIN_MB_ICONQUESTION,
}

DEFAULT_BUTTON_TO_FLAG = {
    MessageBoxDefaultButton.BUTTON2: (WIN_MB_DEFBUTTON2, 2),
    MessageBoxDefaultButton.BUTTON3: (WIN_MB_DEFBUTTON3, 3),
    MessageBoxDefaultButton.BUTTON4: (WIN_MB_DEFBUTTON4, 4),
}

MODALITY_TO_FLAG = {
    MessageBoxModality.SYSTEM: WIN_MB_SYSTEMMODAL,
    MessageBoxModality.TASK: WIN_MB_TASKMODAL,
}

ID_TO_RESULT = {
    WIN_IDOK: MessageBoxResult.OK,
    WIN_IDCANCEL: MessageBoxResult.CANCEL,
    WIN_IDYES: MessageBoxResult.YES,
    WIN_IDNO: MessageBoxResult.NO,
    WIN_IDRETRY: MessageBoxResult.RETRY,
    WIN_IDABORT: MessageBoxResult.ABORT,
    WIN_IDIGNORE: MessageBoxResult.IGNORE,
    WIN_IDTRYAGAIN: MessageBoxResult.TRY_AGAIN,
    WIN_IDCONTINUE: MessageBoxResult.CONTINUE,
}


@dataclass(frozen=True)
class MessageBoxOptions:
    """
    Optional advanced options for MessageBox.

    - icon: Overrides the default icon
    - default_button: Choose default button (2/3/4). BUTTON1 is implicit default
    - topmost: Keep message box on top of other windows
    - modality: Application (default), Task-modal, or System-modal
    - rtl_reading: Use right-to-left reading order
    - right_align: Right align the message text
    - help_button: Show a Help button
    - set_foreground: Force the message box to the foreground
    """

    icon: Optional[MessageBoxIcon] = None
    default_button: Optional[MessageBoxDefaultButton] = None
    topmost: bool = False
    modality: Optional[MessageBoxModality] = None
    rtl_reading: bool = False
    right_align: bool = False
    help_button: bool = False
    set_foreground: bool = False
    owner_hwnd: Optional[int] = None
    # Input dialog enhancements
    default_text: Optional[str] = None
    placeholder: Optional[str] = None
    validator: Optional[Callable[[str], bool]] = None
    font_face: str = "Segoe UI"
    font_size_pt: int = 9
    is_password: bool = False
    char_limit: Optional[int] = None
    width_dlu: Optional[int] = None
    height_dlu: Optional[int] = None

    def __post_init__(self) -> None:
        # Normalize strings
        normalized_face = (self.font_face or "Segoe UI").strip()
        object.__setattr__(self, "font_face", normalized_face or "Segoe UI")

        # Clamp font size
        size = self.font_size_pt
        if not isinstance(size, int):
            try:
                size = int(size)
            except Exception:
                size = 9
        if size < 6:
            size = 6
        if size > 24:
            size = 24
        object.__setattr__(self, "font_size_pt", size)

        # Owner HWND must be non-negative
        if self.owner_hwnd is not None and self.owner_hwnd < 0:
            object.__setattr__(self, "owner_hwnd", 0)

        # Normalize default_text/placeholder
        if self.default_text is not None:
            object.__setattr__(self, "default_text", str(self.default_text))
        if self.placeholder is not None:
            object.__setattr__(self, "placeholder", str(self.placeholder))

        # Validate char_limit
        if self.char_limit is not None and self.char_limit < 0:
            object.__setattr__(self, "char_limit", 0)


class MessageBox:
    """
    MessageBox convenience class.

    Example:
        from moldflow import MessageBox, MessageBoxType

        # Information message
        MessageBox("Operation completed.", MessageBoxType.INFO).show()

        # Yes/No prompt
        result = MessageBox("Proceed with analysis?", MessageBoxType.YES_NO).show()
        if result == MessageBoxResult.YES:
            ...

        # Text input
        material_id = MessageBox("Enter your material ID:", MessageBoxType.INPUT).show()
        if material_id:
            ...
    """

    def __init__(
        self,
        text: str,
        box_type: MessageBoxType = MessageBoxType.INFO,
        title: Optional[str] = None,
        options: Optional[MessageBoxOptions] = None,
    ) -> None:
        if platform.system() != "Windows":
            raise OSError("MessageBox is only supported on Windows.")
        self.text = str(text)
        self.box_type = box_type
        self.title = title or DEFAULT_TITLE
        self.options = options or MessageBoxOptions()

    def show(self) -> MessageBoxReturn:
        """
        Show the message box.

        Returns:
            - MessageBoxResult for INFO/WARNING/ERROR/YES_NO/OK_CANCEL
            - str | None for INPUT (user-entered text or None if cancelled)
        """

        if self.box_type == MessageBoxType.INPUT:
            return self._show_input_dialog()
        return self._show_standard_dialog()

    @classmethod
    def info(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        return cls(text, MessageBoxType.INFO, title, options).show()  # type: ignore[return-value]

    @classmethod
    def warning(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        return cls(text, MessageBoxType.WARNING, title, options).show()  # type: ignore[return-value]

    @classmethod
    def error(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        return cls(text, MessageBoxType.ERROR, title, options).show()  # type: ignore[return-value]

    @classmethod
    def confirm_yes_no(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        return cls(text, MessageBoxType.YES_NO, title, options).show()  # type: ignore[return-value]

    @classmethod
    def prompt_text(
        cls,
        prompt: str,
        title: Optional[str] = None,
        *,
        default_text: Optional[str] = None,
        placeholder: Optional[str] = None,
        validator: Optional[Callable[[str], bool]] = None,
        options: Optional[MessageBoxOptions] = None,
    ) -> Optional[str]:
        opts = options or MessageBoxOptions()
        # Merge provided options with overrides for input UX
        opts = MessageBoxOptions(
            icon=opts.icon,
            default_button=opts.default_button,
            topmost=opts.topmost,
            modality=opts.modality,
            rtl_reading=opts.rtl_reading,
            right_align=opts.right_align,
            help_button=opts.help_button,
            set_foreground=opts.set_foreground,
            owner_hwnd=opts.owner_hwnd,
            default_text=default_text if default_text is not None else opts.default_text,
            placeholder=placeholder if placeholder is not None else opts.placeholder,
            validator=validator if validator is not None else opts.validator,
            font_face=opts.font_face,
            font_size_pt=opts.font_size_pt,
        )
        return cls(prompt, MessageBoxType.INPUT, title, opts).show()  # type: ignore[return-value]

    def _show_standard_dialog(self) -> MessageBoxResult:
        from ctypes import windll, c_wchar_p, c_int

        # Base type from box_type via module-level mapping dict
        base_tuple = MAPPING_MESSAGEBOX_TYPE.get(
            self.box_type, (WIN_MB_OK, MessageBoxIcon.INFORMATION, 1)
        )
        u_type, default_icon, button_count = base_tuple

        # Icon selection (options override default)
        icon = self.options.icon or default_icon
        u_type |= ICON_TO_FLAG.get(icon, 0)
        # NONE -> no icon flag

        # Default button
        if self.options.default_button:
            flag, required = DEFAULT_BUTTON_TO_FLAG.get(self.options.default_button, (0, 1))
            if button_count < required:
                raise ValueError(
                    f"default_button {self.options.default_button.name} requires at least {required} buttons for type {self.box_type.name}"
                )
            u_type |= flag

        # Modality
        if self.options.modality:
            u_type |= MODALITY_TO_FLAG.get(self.options.modality, 0)

        # Z-order / positioning
        if self.options.topmost:
            u_type |= WIN_MB_TOPMOST
        if self.options.set_foreground:
            u_type |= WIN_MB_SETFOREGROUND

        # Layout
        if self.options.right_align:
            u_type |= WIN_MB_RIGHT
        if self.options.rtl_reading:
            u_type |= WIN_MB_RTLREADING

        # Help button
        if self.options.help_button:
            u_type |= WIN_MB_HELP

        owner = self.options.owner_hwnd or 0
        # Trim whitespace to avoid accidental spaces
        text = (self.text or "").strip()
        # Do not translate titles
        title = (self.title or "").strip()
        result = windll.user32.MessageBoxW(
            owner, c_wchar_p(text), c_wchar_p(title), c_int(u_type)
        )
        if result == -1:
            err = windll.kernel32.GetLastError()
            raise ctypes.WinError(err)

        if result in ID_TO_RESULT:
            return ID_TO_RESULT[result]
        # Fallback
        return MessageBoxResult.CANCEL

    def _show_input_dialog(self) -> Optional[str]:
        dialog = _Win32InputDialog(self.title, self.text, self.options)
        return dialog.run()


class _Win32InputDialog:
    """
    Modal input dialog using DialogBoxIndirectParamW with an in-memory DLGTEMPLATE.
    """

    ID_EDIT = WIN_ID_EDIT
    ID_OK = WIN_ID_OK
    ID_CANCEL = WIN_ID_CANCEL

    DS_SETFONT = WIN_DS_SETFONT
    DS_MODALFRAME = WIN_DS_MODALFRAME
    WS_CAPTION = WIN_WS_CAPTION
    WS_SYSMENU = WIN_WS_SYSMENU

    WS_CHILD = WIN_WS_CHILD
    WS_VISIBLE = WIN_WS_VISIBLE
    WS_TABSTOP = WIN_WS_TABSTOP
    WS_GROUP = WIN_WS_GROUP
    WS_BORDER = WIN_WS_BORDER

    ES_AUTOHSCROLL = WIN_ES_AUTOHSCROLL
    SS_LEFT = WIN_SS_LEFT
    BS_DEFPUSHBUTTON = WIN_BS_DEFPUSHBUTTON
    BS_PUSHBUTTON = WIN_BS_PUSHBUTTON

    WM_INITDIALOG = WIN_WM_INITDIALOG
    WM_COMMAND = WIN_WM_COMMAND

    def __init__(self, title: str, prompt: str, options: MessageBoxOptions) -> None:
        self.title = title
        self.prompt = prompt
        self.options = options
        self._result_text: Optional[str] = None

    def _wcs(self, s: str) -> bytes:
        return s.encode("utf-16le") + b"\x00\x00"

    def _align_dword(self, buf: bytearray) -> None:
        while len(buf) % 4 != 0:
            buf += b"\x00"

    def _pack_word(self, buf: bytearray, val: int) -> None:
        buf += struct.pack("<H", val & 0xFFFF)

    def _pack_dword(self, buf: bytearray, val: int) -> None:
        buf += struct.pack("<I", val & 0xFFFFFFFF)

    def _pack_short(self, buf: bytearray, val: int) -> None:
        buf += struct.pack("<h", val & 0xFFFF)

    def _build_template(self) -> bytes:
        # Dialog units and layout
        cx = self.options.width_dlu if self.options.width_dlu is not None else 240
        cy = self.options.height_dlu if self.options.height_dlu is not None else 70
        margin = 7
        static_h = 8
        edit_h = 12
        btn_w, btn_h = 50, 14
        spacing = 4

        ok_x = cx - margin - (btn_w * 2 + spacing)
        cancel_x = cx - margin - btn_w
        btn_y = cy - margin - btn_h

        buf = bytearray()

        style = self.DS_MODALFRAME | self.DS_SETFONT | self.WS_CAPTION | self.WS_SYSMENU
        self._pack_dword(buf, style)  # style
        self._pack_dword(buf, 0)  # dwExtendedStyle
        self._pack_word(buf, 4)  # cdit: static, edit, OK, Cancel
        self._pack_short(buf, margin)  # x
        self._pack_short(buf, margin)  # y
        self._pack_short(buf, cx)  # cx
        self._pack_short(buf, cy)  # cy

        self._pack_word(buf, 0)  # menu = 0
        self._pack_word(buf, 0)  # windowClass = 0 (default)
        # Do not translate titles
        buf += self._wcs(self.title)  # title

        # Font (since DS_SETFONT)
        self._pack_word(buf, max(6, int(self.options.font_size_pt)))  # point size
        buf += self._wcs(self.options.font_face or "Segoe UI")

        # DLGITEMTEMPLATEs must be DWORD-aligned
        # 1) Static: prompt
        self._align_dword(buf)
        self._pack_dword(buf, self.WS_CHILD | self.WS_VISIBLE)
        self._pack_dword(buf, 0)  # ex style
        self._pack_short(buf, margin)
        self._pack_short(buf, margin)
        self._pack_short(buf, cx - 2 * margin)
        self._pack_short(buf, static_h)
        self._pack_word(buf, 0)  # id for static is usually 0
        # class: 0xFFFF, 0x0082 (STATIC)
        self._pack_word(buf, 0xFFFF)
        self._pack_word(buf, WIN_CLASS_STATIC)
        # Do not translate prompt; callers pass text explicitly
        buf += self._wcs(self.prompt)  # title
        self._pack_word(buf, 0)  # no extra data

        # 2) Edit control
        self._align_dword(buf)
        edit_style = (
            self.WS_CHILD
            | self.WS_VISIBLE
            | self.WS_BORDER
            | self.ES_AUTOHSCROLL
            | self.WS_TABSTOP
        )
        if self.options.is_password:
            edit_style |= self.ES_PASSWORD
        self._pack_dword(buf, edit_style)
        self._pack_dword(buf, 0)
        self._pack_short(buf, margin)
        self._pack_short(buf, margin + static_h + 2)
        self._pack_short(buf, cx - 2 * margin)
        self._pack_short(buf, edit_h)
        self._pack_word(buf, self.ID_EDIT)
        # class: 0xFFFF, 0x0080 EDIT
        self._pack_word(buf, 0xFFFF)
        self._pack_word(buf, WIN_CLASS_EDIT)
        self._pack_word(buf, 0)  # empty text
        self._pack_word(buf, 0)  # no extra data

        # 3) OK button (default)
        self._align_dword(buf)
        self._pack_dword(
            buf,
            self.WS_CHILD
            | self.WS_VISIBLE
            | self.WS_TABSTOP
            | self.WS_GROUP
            | self.BS_DEFPUSHBUTTON,
        )
        self._pack_dword(buf, 0)
        self._pack_short(buf, ok_x)
        self._pack_short(buf, btn_y)
        self._pack_short(buf, btn_w)
        self._pack_short(buf, btn_h)
        _ = get_text()
        self._pack_word(buf, self.ID_OK)
        self._pack_word(buf, 0xFFFF)
        self._pack_word(buf, WIN_CLASS_BUTTON)
        buf += self._wcs(_("OK"))
        self._pack_word(buf, 0)

        # 4) Cancel button
        self._align_dword(buf)
        self._pack_dword(
            buf, self.WS_CHILD | self.WS_VISIBLE | self.WS_TABSTOP | self.BS_PUSHBUTTON
        )
        self._pack_dword(buf, 0)
        self._pack_short(buf, cancel_x)
        self._pack_short(buf, btn_y)
        self._pack_short(buf, btn_w)
        self._pack_short(buf, btn_h)
        self._pack_word(buf, self.ID_CANCEL)
        self._pack_word(buf, 0xFFFF)
        self._pack_word(buf, WIN_CLASS_BUTTON)
        buf += self._wcs(_("Cancel"))
        self._pack_word(buf, 0)

        self._align_dword(buf)
        return bytes(buf)

    def run(self) -> Optional[str]:
        user32 = windll.user32
        kernel32 = windll.kernel32

        template_bytes = self._build_template()
        # Keep buffer alive by storing on self
        self._template_buffer = (wintypes.BYTE * len(template_bytes)).from_buffer_copy(
            template_bytes
        )

        DLGPROC = WINFUNCTYPE(
            wintypes.INT_PTR, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
        )

        @DLGPROC
        def _dlgproc(hwnd, msg, wparam, lparam):
            if msg == self.WM_INITDIALOG:
                # Set focus to edit control and prefill text / placeholder
                h_edit = user32.GetDlgItem(hwnd, self.ID_EDIT)
                user32.SetFocus(h_edit)
                # Default text
                if self.options.default_text:
                    user32.SetWindowTextW(h_edit, c_wchar_p(self.options.default_text))
                # Placeholder (cue banner) if available
                if self.options.placeholder:
                    try:
                        # wParam=BOOL drawWhenNotFocused=1
                        user32.SendMessageW(
                            h_edit, WIN_EM_SETCUEBANNER, 1, c_wchar_p(self.options.placeholder)
                        )
                    except Exception:
                        pass
                # Validator initial state
                if self.options.validator is not None:
                    try:
                        is_valid = bool(self.options.validator(self.options.default_text or ""))
                    except Exception:
                        is_valid = True
                    user32.EnableWindow(
                        user32.GetDlgItem(hwnd, self.ID_OK), wintypes.BOOL(1 if is_valid else 0)
                    )
                # Character limit
                if self.options.char_limit is not None:
                    user32.SendMessageW(h_edit, WIN_EM_LIMITTEXT, self.options.char_limit, 0)

                # Center dialog over owner
                try:
                    owner_hwnd = self.options.owner_hwnd or user32.GetActiveWindow()
                    if owner_hwnd:
                        rect = wintypes.RECT()
                        user32.GetWindowRect(owner_hwnd, byref(rect))
                        owner_cx = rect.right - rect.left
                        owner_cy = rect.bottom - rect.top

                        dlg_rect = wintypes.RECT()
                        user32.GetWindowRect(hwnd, byref(dlg_rect))
                        dlg_w = dlg_rect.right - dlg_rect.left
                        dlg_h = dlg_rect.bottom - dlg_rect.top

                        x = rect.left + (owner_cx - dlg_w) // 2
                        y = rect.top + (owner_cy - dlg_h) // 2
                        user32.SetWindowPos(
                            hwnd, 0, x, y, 0, 0, WIN_SWP_NOSIZE | WIN_SWP_NOZORDER | WIN_SWP_NOACTIVATE
                        )
                except Exception:
                    pass
                return 0
            if msg == self.WM_COMMAND:
                cid = wparam & 0xFFFF
                notify_code = (wparam >> 16) & 0xFFFF
                # Live validation
                if notify_code == WIN_EN_CHANGE and self.options.validator is not None:
                    h_edit = user32.GetDlgItem(hwnd, self.ID_EDIT)
                    length = user32.GetWindowTextLengthW(h_edit)
                    buf = create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(h_edit, buf, length + 1)
                    try:
                        is_valid = bool(self.options.validator(buf.value))
                    except Exception:
                        is_valid = True
                    user32.EnableWindow(
                        user32.GetDlgItem(hwnd, self.ID_OK), wintypes.BOOL(1 if is_valid else 0)
                    )
                if cid == self.ID_OK:
                    # Read text
                    h_edit = user32.GetDlgItem(hwnd, self.ID_EDIT)
                    length = user32.GetWindowTextLengthW(h_edit)
                    buf = create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(h_edit, buf, length + 1)
                    self._result_text = buf.value
                    user32.EndDialog(hwnd, self.ID_OK)
                    return 1
                if cid == self.ID_CANCEL:
                    self._result_text = None
                    user32.EndDialog(hwnd, self.ID_CANCEL)
                    return 1
            return 0

        hInstance = kernel32.GetModuleHandleW(None)
        owner = self.options.owner_hwnd or user32.GetActiveWindow()
        res = user32.DialogBoxIndirectParamW(
            hInstance, byref(self._template_buffer), owner, _dlgproc, 0
        )
        # res is IDOK/IDCANCEL or -1 on failure
        if res == -1:
            err = kernel32.GetLastError()
            raise ctypes.WinError(err)
        return self._result_text if res == self.ID_OK else None
