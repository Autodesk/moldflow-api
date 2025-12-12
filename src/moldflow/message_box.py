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
import platform
from ctypes import windll, wintypes, byref, create_unicode_buffer, c_int, c_wchar_p, WINFUNCTYPE
import signal
import struct
from .i18n import get_text
from .logger import get_logger

# This module intentionally contains a large amount of Windows interop glue
# and UI layout code.
# pylint: disable=C0301,C0302,R0902,W0212,R0911,R0914,R0902,W0201

# Fallbacks for missing wintypes aliases on some Python versions
if not hasattr(wintypes, "LRESULT"):
    # LONG_PTR
    wintypes.LRESULT = ctypes.c_ssize_t  # type: ignore[attr-defined]
if not hasattr(wintypes, "HMENU"):
    wintypes.HMENU = ctypes.c_void_p  # type: ignore[attr-defined]
if not hasattr(wintypes, "HCURSOR"):
    wintypes.HCURSOR = ctypes.c_void_p  # type: ignore[attr-defined]
if not hasattr(wintypes, "HICON"):
    wintypes.HICON = ctypes.c_void_p  # type: ignore[attr-defined]
if not hasattr(wintypes, "HBRUSH"):
    wintypes.HBRUSH = ctypes.c_void_p  # type: ignore[attr-defined]
if not hasattr(wintypes, "HINSTANCE"):
    wintypes.HINSTANCE = ctypes.c_void_p  # type: ignore[attr-defined]

# Extra Win32 constants used by CreateWindowEx path
WIN_WM_SETFONT = 0x0030
WIN_WS_EX_DLGMODALFRAME = 0x00000001
WIN_WS_EX_CONTROLPARENT = 0x00010000
WIN_DEFAULT_CHARSET = 1
WIN_OUT_DEFAULT_PRECIS = 0
WIN_CLIP_DEFAULT_PRECIS = 0
WIN_CLEARTYPE_QUALITY = 5
WIN_DEFAULT_PITCH = 0
WIN_FF_DONTCARE = 0
WIN_FW_NORMAL = 400
WIN_LOGPIXELSY = 90
WIN_WM_CLOSE = 0x0010
WIN_WM_KEYDOWN = 0x0100
WIN_VK_RETURN = 0x0D
WIN_VK_ESCAPE = 0x1B

# Helper alias for pointer-sized integer type used by Win32 callbacks
# Return type for DLGPROC should be an integer type matching pointer size,
# not a pointer type. Using a pointer type here can corrupt the stack on 64-bit.
# pylint: disable=invalid-name
INT_PTR = ctypes.c_ssize_t

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
WIN_WS_POPUP = 0x80000000

WIN_WS_CHILD = 0x40000000
WIN_WS_VISIBLE = 0x10000000
WIN_WS_TABSTOP = 0x00010000
WIN_WS_GROUP = 0x00020000
WIN_WS_BORDER = 0x00800000
WIN_WS_THICKFRAME = 0x00040000
WIN_WS_MINIMIZEBOX = 0x00020000
WIN_WS_MAXIMIZEBOX = 0x00010000

WIN_ES_AUTOHSCROLL = 0x00000080
WIN_ES_PASSWORD = 0x00000020
WIN_SS_LEFT = 0x00000000
WIN_BS_DEFPUSHBUTTON = 0x00000001
WIN_BS_PUSHBUTTON = 0x00000000

# Window messages
WIN_WM_INITDIALOG = 0x0110
WIN_WM_COMMAND = 0x0111
WIN_WM_CTLCOLORSTATIC = 0x0138

# Edit control helpers
WIN_EM_SETCUEBANNER = 0x1501
WIN_EN_CHANGE = 0x0300
WIN_EM_LIMITTEXT = 0x00C5

# DrawText flags
WIN_DT_WORDBREAK = 0x0010
WIN_DT_CALCRECT = 0x0400
WIN_DT_NOPREFIX = 0x0800

# SetWindowPos flags and system metrics
WIN_SWP_NOSIZE = 0x0001
WIN_SWP_NOZORDER = 0x0004
WIN_SWP_NOACTIVATE = 0x0010
WIN_SM_CXSCREEN = 0
WIN_SM_CYSCREEN = 1

# Predefined control classes (atoms from winuser.h)
# 0x0080: BUTTON, 0x0081: EDIT, 0x0082: STATIC
WIN_CLASS_BUTTON = 0x0080
WIN_CLASS_EDIT = 0x0081
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
class MessageBoxOptions:  # pylint: disable=too-many-instance-attributes
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
            except Exception as exc:
                logger = get_logger("message_box")
                if logger:
                    logger.debug("Font size parse failed; defaulting to 9: %s", exc)
                size = 9
        # Clamp font size between sensible bounds
        size = max(6, min(size, 24))
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
        .. code-block:: python

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
        """
        Show an informational message box with an OK button.
        """
        inst = cls(text, MessageBoxType.INFO, title, options)
        return inst.show()  # type: ignore[return-value]

    @classmethod
    def warning(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        """
        Show a warning message box with an OK button.
        """
        inst = cls(text, MessageBoxType.WARNING, title, options)
        return inst.show()  # type: ignore[return-value]

    @classmethod
    def error(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        """
        Show an error message box with an OK button.
        """
        inst = cls(text, MessageBoxType.ERROR, title, options)
        return inst.show()  # type: ignore[return-value]

    @classmethod
    def confirm_yes_no(
        cls, text: str, title: Optional[str] = None, options: Optional[MessageBoxOptions] = None
    ) -> MessageBoxResult:
        """
        Show a confirmation message box with Yes/No buttons.
        """
        return cls(text, MessageBoxType.YES_NO, title, options).show()  # type: ignore[return-value]

    @classmethod
    def prompt_text(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        cls,
        prompt: str,
        title: Optional[str] = None,
        default_text: Optional[str] = None,
        placeholder: Optional[str] = None,
        validator: Optional[Callable[[str], bool]] = None,
        options: Optional[MessageBoxOptions] = None,
    ) -> Optional[str]:
        """
        Show a text input dialog.
        """
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
        """
        Show a standard Win32 MessageBox dialog and return the result.
        """
        # Use module-level ctypes imports to avoid reimport and name shadowing

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
                # The error message is intentionally descriptive; allow a
                # slightly longer line here rather than make it unreadable.
                # pylint: disable=line-too-long
                raise ValueError(
                    f"default_button {self.options.default_button.name} requires >={required} buttons for {self.box_type.name}"
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
        result = windll.user32.MessageBoxW(owner, c_wchar_p(text), c_wchar_p(title), c_int(u_type))
        if result == -1:
            err = windll.kernel32.GetLastError()
            raise ctypes.WinError(err)

        if result in ID_TO_RESULT:
            return ID_TO_RESULT[result]
        # Fallback
        return MessageBoxResult.CANCEL

    def _show_input_dialog(self) -> Optional[str]:
        """
        Show a text input dialog.
        """
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
    ES_PASSWORD = WIN_ES_PASSWORD
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
        # Template buffer is created when running the dialog; initialize attribute
        self._template_buffer: Optional[bytes] = None

    def _wcs(self, s: str) -> bytes:
        """Return a UTF-16LE encoded, null-terminated bytestring for s."""
        return s.encode("utf-16le") + b"\x00\x00"

    def _align_dword(self, buf: bytearray) -> None:
        """Pad buffer until its length is a multiple of 4 (DWORD alignment)."""
        while len(buf) % 4 != 0:
            buf += b"\x00"

    def _pack_word(self, buf: bytearray, val: int) -> None:
        """Pack a 16-bit unsigned value into the buffer."""
        buf += struct.pack("<H", val & 0xFFFF)

    def _pack_dword(self, buf: bytearray, val: int) -> None:
        """Pack a 32-bit unsigned value into the buffer."""
        buf += struct.pack("<I", val & 0xFFFFFFFF)

    def _pack_short(self, buf: bytearray, val: int) -> None:
        """Pack a 16-bit signed value into the buffer."""
        buf += struct.pack("<h", val & 0xFFFF)

    def _build_template(self) -> bytes:
        # The dialog template is relatively verbose; allow pylint to accept the
        # complexity here rather than refactor the Win32 packing code.
        # pylint: disable=too-many-locals,too-many-statements
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
        # Position the edit box a bit lower from the label
        edit_y = margin + static_h + 8
        # Move the buttons up: place them below the edit with extra spacing
        btn_y = edit_y + edit_h + spacing * 2

        buf = bytearray()

        style = (
            self.DS_MODALFRAME | self.DS_SETFONT | self.WS_CAPTION | self.WS_SYSMENU | WIN_WS_POPUP
        )
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
            self.WS_CHILD | self.WS_VISIBLE | self.WS_BORDER | self.ES_AUTOHSCROLL | self.WS_TABSTOP
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

        _ = get_text()

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
        """Create and run a modal input window using CreateWindowEx."""
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements,invalid-name
        user32 = windll.user32
        gdi32 = windll.gdi32
        kernel32 = windll.kernel32

        # Win32 function prototypes used
        try:
            user32.CreateWindowExW.restype = wintypes.HWND
            user32.CreateWindowExW.argtypes = [
                wintypes.DWORD,
                c_wchar_p,
                c_wchar_p,
                wintypes.DWORD,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                wintypes.HWND,
                wintypes.HMENU,
                wintypes.HINSTANCE,
                wintypes.LPVOID,
            ]
            user32.DefWindowProcW.restype = wintypes.LRESULT
            user32.DefWindowProcW.argtypes = [
                wintypes.HWND,
                wintypes.UINT,
                wintypes.WPARAM,
                wintypes.LPARAM,
            ]
            user32.RegisterClassW.restype = wintypes.ATOM
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Win32 prototype binding failed: %s", exc)

        # Register window class once
        class_name = "MF_InputDialogWindow"
        if not hasattr(_Win32InputDialog, "_class_registered"):
            WNDPROC = WINFUNCTYPE(
                wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
            )

            @WNDPROC
            def _wndproc(hwnd, msg, wparam, lparam):
                # Retrieve instance from map if present
                inst = _Win32InputDialog._hwnd_to_inst.get(hwnd)
                if msg == WIN_WM_CLOSE:
                    windll.user32.DestroyWindow(hwnd)
                    return 0
                if msg == WIN_WM_KEYDOWN and inst is not None:
                    if wparam == WIN_VK_RETURN:
                        inst._on_ok()
                        return 0
                    if wparam == WIN_VK_ESCAPE:
                        inst._on_cancel()
                        return 0
                if msg == 0x0002:  # WM_DESTROY
                    if inst is not None:
                        # Defer destruction finalization slightly to allow any
                        # late WM_COMMAND or automation posts to drain safely.
                        try:
                            inst._on_destroy()
                        except Exception as exc:
                            logger = get_logger("message_box")
                            if logger:
                                logger.debug("_on_destroy raised: %s", exc)
                    return 0
                if msg == 0x0082:  # WM_NCDESTROY
                    try:
                        if inst is not None:
                            inst._done = True  # type: ignore[attr-defined]
                        _Win32InputDialog._hwnd_to_inst.pop(hwnd, None)
                        # Ensure the modal loop unblocks even if no further messages arrive
                        user32.PostQuitMessage(0)
                    except Exception as exc:
                        logger = get_logger("message_box")
                        if logger:
                            logger.debug("WM_NCDESTROY cleanup failed: %s", exc)
                    return 0
                if inst is None:
                    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
                if msg == 0x0005:  # WM_SIZE
                    inst._on_size()
                    return 0
                if msg == WIN_WM_CTLCOLORSTATIC:
                    # Make label background match dialog background for a flat look
                    try:
                        windll.gdi32.SetBkMode(wparam, 1)  # TRANSPARENT
                    except Exception as exc:
                        logger = get_logger("message_box")
                        if logger:
                            logger.debug("SetBkMode transparent failed: %s", exc)
                    return getattr(_Win32InputDialog, "_bg_brush", 0)
                if msg == _Win32InputDialog.WM_COMMAND:
                    cid = wparam & 0xFFFF
                    notify = (wparam >> 16) & 0xFFFF
                    # Ignore commands from unknown HWNDs to avoid processing
                    # stale messages after controls are destroyed.
                    if lparam not in (inst.h_edit, inst.h_ok, inst.h_cancel):
                        return 0
                    if (
                        notify == WIN_EN_CHANGE
                        and inst.options.validator is not None
                        and lparam == inst.h_edit
                    ):
                        inst._validate_live()
                        return 0
                    if cid == inst.ID_OK:
                        inst._on_ok()
                        return 0
                    if cid == inst.ID_CANCEL:
                        inst._on_cancel()
                        return 0
                return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

            _Win32InputDialog._WNDPROC = _wndproc  # type: ignore[attr-defined]

            class WNDCLASSEX(ctypes.Structure):
                """WNDCLASSEX structure"""

                _fields_ = [
                    ("cbSize", wintypes.UINT),
                    ("style", wintypes.UINT),
                    ("lpfnWndProc", WNDPROC),
                    ("cbClsExtra", ctypes.c_int),
                    ("cbWndExtra", ctypes.c_int),
                    ("hInstance", wintypes.HINSTANCE),
                    ("hIcon", wintypes.HICON),
                    ("hCursor", wintypes.HCURSOR),
                    ("hbrBackground", wintypes.HBRUSH),
                    ("lpszMenuName", c_wchar_p),
                    ("lpszClassName", c_wchar_p),
                    ("hIconSm", wintypes.HICON),
                ]

            # Prototypes for class registration
            try:
                user32.RegisterClassExW.restype = wintypes.ATOM
                user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEX)]
                user32.LoadCursorW.restype = wintypes.HCURSOR
                # Second parameter is MAKEINTRESOURCE on system cursors; accept as void*
                user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]
            except Exception as exc:
                logger = get_logger("message_box")
                if logger:
                    logger.debug("RegisterClassEx/LoadCursor prototype bind failed: %s", exc)

            hInstance = kernel32.GetModuleHandleW(None)
            wcx = WNDCLASSEX()
            wcx.cbSize = ctypes.sizeof(WNDCLASSEX)
            wcx.style = 0
            wcx.lpfnWndProc = _Win32InputDialog._WNDPROC  # type: ignore[attr-defined]
            wcx.cbClsExtra = 0
            wcx.cbWndExtra = 0
            wcx.hInstance = hInstance
            wcx.hIcon = None
            # IDC_ARROW = 32512 (0x7F00). Pass as MAKEINTRESOURCE via c_void_p
            wcx.hCursor = windll.user32.LoadCursorW(None, ctypes.c_void_p(32512))
            # Use COLOR_WINDOW+1 to avoid theme brush quirks under automation
            wcx.hbrBackground = ctypes.c_void_p(5 + 1)
            wcx.lpszMenuName = None
            wcx.lpszClassName = class_name
            wcx.hIconSm = None
            res = user32.RegisterClassExW(ctypes.byref(wcx))
            # If already registered, res==0 with last error 1410 (ERROR_CLASS_ALREADY_EXISTS)
            if not res:
                err = kernel32.GetLastError()
                if err != 1410:  # ERROR_CLASS_ALREADY_EXISTS
                    raise ctypes.WinError(err)
            _Win32InputDialog._class_registered = True  # type: ignore[attr-defined]
            _Win32InputDialog._class_name = class_name  # type: ignore[attr-defined]
            _Win32InputDialog._hwnd_to_inst = {}  # type: ignore[attr-defined]
            # Cache background brush so STATIC controls can paint with same bg
            try:
                _Win32InputDialog._bg_brush = int(wcx.hbrBackground)  # type: ignore[attr-defined]
            except Exception as exc:
                _Win32InputDialog._bg_brush = 0  # type: ignore[attr-defined]
                logger = get_logger("message_box")
                if logger:
                    logger.debug("Caching bg brush failed: %s", exc)

        # Create window
        style = (
            self.WS_CAPTION
            | self.WS_SYSMENU
            | WIN_WS_POPUP
            | WIN_WS_THICKFRAME
            | WIN_WS_MINIMIZEBOX
            | WIN_WS_MAXIMIZEBOX
        )
        ex_style = WIN_WS_EX_DLGMODALFRAME | WIN_WS_EX_CONTROLPARENT
        # Avoid cross-thread/process owner interactions; keep window independent
        owner = 0

        # Size and layout (pixels)
        # Slightly larger default size so action buttons are always visible
        cx = int(self.options.width_dlu if self.options.width_dlu is not None else 420)
        cy = int(self.options.height_dlu if self.options.height_dlu is not None else 220)
        margin = 36
        static_h = 22
        edit_h = 22
        btn_w, btn_h = 96, 28
        spacing = 16

        ok_x = cx - margin - (btn_w * 2 + spacing)
        cancel_x = cx - margin - btn_w
        edit_y = margin + static_h + 8
        btn_y = edit_y + edit_h + spacing * 2

        # Persist layout metrics for resize handling
        self._layout_margin = margin  # type: ignore[attr-defined]
        self._layout_spacing = spacing  # type: ignore[attr-defined]
        self._layout_edit_h = edit_h  # type: ignore[attr-defined]
        self._layout_btn_w = btn_w  # type: ignore[attr-defined]
        self._layout_btn_h = btn_h  # type: ignore[attr-defined]

        hInstance = kernel32.GetModuleHandleW(None)
        hwnd = user32.CreateWindowExW(
            ex_style,
            c_wchar_p(getattr(_Win32InputDialog, "_class_name", class_name)),
            c_wchar_p(self.title),
            style,
            100,
            100,
            cx,
            cy,
            None,
            None,
            hInstance,
            None,
        )
        if not hwnd:
            err = kernel32.GetLastError()
            raise ctypes.WinError(err)

        # Map hwnd to instance
        _Win32InputDialog._hwnd_to_inst[hwnd] = self  # type: ignore[attr-defined]
        self.hwnd = hwnd  # type: ignore[attr-defined]

        # Allow Ctrl+C in the console to close the window gracefully (both
        # Python-level SIGINT and native console control handler for immediate response)
        def _sigint_handler(_signum, _frame):
            try:
                user32.PostMessageW(self.hwnd, WIN_WM_CLOSE, 0, 0)  # type: ignore[attr-defined]
            except Exception as exc:
                logger = get_logger("message_box")
                if logger:
                    logger.debug("Posting WM_CLOSE on SIGINT failed: %s", exc)

        try:
            self._prev_sigint = signal.getsignal(signal.SIGINT)  # type: ignore[attr-defined]
            signal.signal(signal.SIGINT, _sigint_handler)
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Setting SIGINT handler failed: %s", exc)

        # Native console control handler (fires immediately even while Python blocks)
        try:
            HANDLER_ROUTINE = WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

            @HANDLER_ROUTINE
            def _console_ctrl_handler(_ctrl_type):  # CTRL_C_EVENT, CTRL_BREAK_EVENT, etc.
                try:
                    user32.PostMessageW(self.hwnd, WIN_WM_CLOSE, 0, 0)  # type: ignore[attr-defined]
                except Exception as exc:
                    logger = get_logger("message_box")
                    if logger:
                        logger.debug("Posting WM_CLOSE on console control failed: %s", exc)
                return True

            kernel32.SetConsoleCtrlHandler.restype = wintypes.BOOL
            kernel32.SetConsoleCtrlHandler.argtypes = [HANDLER_ROUTINE, wintypes.BOOL]
            kernel32.SetConsoleCtrlHandler(_console_ctrl_handler, True)
            self._console_ctrl_handler = _console_ctrl_handler  # type: ignore[attr-defined]
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Setting console control handler failed: %s", exc)

        # Create child controls
        self.h_static = user32.CreateWindowExW(  # type: ignore[attr-defined]
            0,
            c_wchar_p("STATIC"),
            c_wchar_p(self.prompt),
            self.WS_CHILD | self.WS_VISIBLE | self.SS_LEFT,
            margin,
            margin,
            cx - 2 * margin,
            static_h,
            hwnd,
            wintypes.HMENU(0),
            hInstance,
            None,
        )
        edit_style = (
            self.WS_CHILD | self.WS_VISIBLE | self.WS_BORDER | self.ES_AUTOHSCROLL | self.WS_TABSTOP
        )
        if self.options.is_password:
            edit_style |= self.ES_PASSWORD
        self.h_edit = user32.CreateWindowExW(  # type: ignore[attr-defined]
            0,
            c_wchar_p("EDIT"),
            c_wchar_p(""),
            edit_style,
            margin,
            edit_y,
            cx - 2 * margin,
            edit_h,
            hwnd,
            wintypes.HMENU(self.ID_EDIT),
            hInstance,
            None,
        )
        _ = get_text()
        self.h_ok = user32.CreateWindowExW(  # type: ignore[attr-defined]
            0,
            c_wchar_p("BUTTON"),
            c_wchar_p(_("Submit")),
            self.WS_CHILD | self.WS_VISIBLE | self.WS_TABSTOP | self.BS_DEFPUSHBUTTON,
            ok_x,
            btn_y,
            btn_w,
            btn_h,
            hwnd,
            wintypes.HMENU(self.ID_OK),
            hInstance,
            None,
        )
        self.h_cancel = user32.CreateWindowExW(  # type: ignore[attr-defined]
            0,
            c_wchar_p("BUTTON"),
            c_wchar_p(_("Cancel")),
            self.WS_CHILD | self.WS_VISIBLE | self.WS_TABSTOP | self.BS_PUSHBUTTON,
            cancel_x,
            btn_y,
            btn_w,
            btn_h,
            hwnd,
            wintypes.HMENU(self.ID_CANCEL),
            hInstance,
            None,
        )

        # Apply a system dialog font for consistent look and spacing
        try:
            DEFAULT_GUI_FONT = 17
            hfont = windll.gdi32.GetStockObject(DEFAULT_GUI_FONT)
            if hfont:
                # Send WM_SETFONT to children so they repaint with the font
                for hchild in (self.h_static, self.h_edit, self.h_ok, self.h_cancel):  # type: ignore[attr-defined]
                    if hchild:
                        user32.SendMessageW(hchild, WIN_WM_SETFONT, hfont, 1)
                # Keep a reference so it survives until window is destroyed
                self._hfont = hfont  # type: ignore[attr-defined]

                # Adjust edit height to match font metrics so caret is visually centered
                class TEXTMETRICW(ctypes.Structure):
                    """TEXTMETRICW structure"""

                    _fields_ = [
                        ("tmHeight", ctypes.c_long),
                        ("tmAscent", ctypes.c_long),
                        ("tmDescent", ctypes.c_long),
                        ("tmInternalLeading", ctypes.c_long),
                        ("tmExternalLeading", ctypes.c_long),
                        ("tmAveCharWidth", ctypes.c_long),
                        ("tmMaxCharWidth", ctypes.c_long),
                        ("tmWeight", ctypes.c_long),
                        ("tmOverhang", ctypes.c_long),
                        ("tmDigitizedAspectX", ctypes.c_long),
                        ("tmDigitizedAspectY", ctypes.c_long),
                        # Next four fields are WCHAR in the Win32 API, keep for structure parity
                        ("tmFirstChar", ctypes.c_wchar),
                        ("tmLastChar", ctypes.c_wchar),
                        ("tmDefaultChar", ctypes.c_wchar),
                        ("tmBreakChar", ctypes.c_wchar),
                        ("tmItalic", ctypes.c_ubyte),
                        ("tmUnderlined", ctypes.c_ubyte),
                        ("tmStruckOut", ctypes.c_ubyte),
                        ("tmPitchAndFamily", ctypes.c_ubyte),
                        ("tmCharSet", ctypes.c_ubyte),
                    ]

                hdc_edit = user32.GetDC(self.h_edit)
                if hdc_edit:
                    try:
                        prev = gdi32.SelectObject(hdc_edit, hfont)
                        tm = TEXTMETRICW()
                        if gdi32.GetTextMetricsW(hdc_edit, ctypes.byref(tm)):
                            desired_h = int(tm.tmHeight + tm.tmExternalLeading + 6)
                            desired_h = max(desired_h, 18)
                            # Resize edit control to the desired height and keep x/width constant
                            user32.SetWindowPos(
                                self.h_edit,
                                0,
                                margin,
                                edit_y,
                                cx - 2 * margin,
                                desired_h,
                                WIN_SWP_NOZORDER,
                            )
                            # Reposition buttons directly below the edit
                            new_btn_y = edit_y + desired_h + spacing * 2
                            user32.SetWindowPos(
                                self.h_ok,
                                0,
                                ok_x,
                                new_btn_y,
                                0,
                                0,
                                WIN_SWP_NOSIZE | WIN_SWP_NOZORDER,
                            )
                            user32.SetWindowPos(
                                self.h_cancel,
                                0,
                                cancel_x,
                                new_btn_y,
                                0,
                                0,
                                WIN_SWP_NOSIZE | WIN_SWP_NOZORDER,
                            )
                        if prev:
                            gdi32.SelectObject(hdc_edit, prev)
                    finally:
                        user32.ReleaseDC(self.h_edit, hdc_edit)

                # Recalculate static height for long titles and wrap
                hdc_static = user32.GetDC(self.h_static)
                if hdc_static:
                    try:
                        prev2 = gdi32.SelectObject(hdc_static, hfont)
                        rect = wintypes.RECT()
                        rect.left = 0
                        rect.top = 0
                        rect.right = cx - 2 * margin
                        rect.bottom = 1000
                        user32.DrawTextW(
                            hdc_static,
                            c_wchar_p(self.prompt),
                            -1,
                            byref(rect),
                            WIN_DT_WORDBREAK | WIN_DT_CALCRECT | WIN_DT_NOPREFIX,
                        )
                        new_static_h = max(static_h, rect.bottom - rect.top)
                        if new_static_h != static_h:
                            # Resize static and move controls below it
                            user32.SetWindowPos(
                                self.h_static,
                                0,
                                margin,
                                margin,
                                cx - 2 * margin,
                                new_static_h,
                                WIN_SWP_NOZORDER,
                            )
                            new_edit_y = margin + new_static_h + 8
                            user32.SetWindowPos(
                                self.h_edit,
                                0,
                                margin,
                                new_edit_y,
                                0,
                                0,
                                WIN_SWP_NOSIZE | WIN_SWP_NOZORDER,
                            )
                            new_btn_y = new_edit_y + edit_h + spacing * 2
                            user32.SetWindowPos(
                                self.h_ok,
                                0,
                                ok_x,
                                new_btn_y,
                                0,
                                0,
                                WIN_SWP_NOSIZE | WIN_SWP_NOZORDER,
                            )
                            user32.SetWindowPos(
                                self.h_cancel,
                                0,
                                cancel_x,
                                new_btn_y,
                                0,
                                0,
                                WIN_SWP_NOSIZE | WIN_SWP_NOZORDER,
                            )
                        if prev2:
                            gdi32.SelectObject(hdc_static, prev2)
                    finally:
                        user32.ReleaseDC(self.h_static, hdc_static)
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Applying default GUI font failed: %s", exc)

        # Defaults
        if self.options.default_text:
            user32.SetWindowTextW(self.h_edit, c_wchar_p(self.options.default_text))
        if self.options.placeholder:
            try:
                user32.SendMessageW(
                    self.h_edit, WIN_EM_SETCUEBANNER, 1, c_wchar_p(self.options.placeholder)
                )
            except Exception as exc:
                logger = get_logger("message_box")
                if logger:
                    logger.debug("Setting placeholder text failed: %s", exc)
        if self.options.char_limit is not None:
            user32.SendMessageW(self.h_edit, WIN_EM_LIMITTEXT, self.options.char_limit, 0)

        # Initial validation
        if self.options.validator is not None:
            self._validate_live()

        # Center over owner
        try:
            owner_hwnd = owner or user32.GetActiveWindow()
            if owner_hwnd:
                rect = wintypes.RECT()
                user32.GetWindowRect(owner_hwnd, byref(rect))
                owner_cx = rect.right - rect.left
                owner_cy = rect.bottom - rect.top
                wnd_rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, byref(wnd_rect))
                x = rect.left + (owner_cx - (wnd_rect.right - wnd_rect.left)) // 2
                y = rect.top + (owner_cy - (wnd_rect.bottom - wnd_rect.top)) // 2
                user32.SetWindowPos(
                    hwnd, 0, x, y, 0, 0, WIN_SWP_NOSIZE | WIN_SWP_NOZORDER | WIN_SWP_NOACTIVATE
                )
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Centering dialog over owner failed: %s", exc)

        user32.ShowWindow(hwnd, 5)  # SW_SHOW
        try:
            user32.UpdateWindow(hwnd)
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("UpdateWindow failed: %s", exc)
        if self.h_edit:
            user32.SetFocus(self.h_edit)

        # Modal loop
        self._done = False  # type: ignore[attr-defined]
        msg = wintypes.MSG()
        while not self._done:
            ret = user32.GetMessageW(byref(msg), 0, 0, 0)
            if ret == 0:  # WM_QUIT
                break
            if ret == -1:
                break
            # Let the system process default button (Enter), Esc, and Tab order
            if not user32.IsDialogMessageW(hwnd, byref(msg)):
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))

        # No owner to restore
        # Restore previous SIGINT handler
        try:
            prev = getattr(self, "_prev_sigint", None)
            if prev is not None:
                signal.signal(signal.SIGINT, prev)
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Restoring SIGINT handler failed: %s", exc)
        # Remove native console handler
        try:
            handler = getattr(self, "_console_ctrl_handler", None)
            if handler is not None:
                kernel32.SetConsoleCtrlHandler(handler, False)
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Removing console control handler failed: %s", exc)
        return self._result_text

    # Helper methods for WNDPROC
    def _on_ok(self) -> None:
        user32 = windll.user32
        length = user32.GetWindowTextLengthW(self.h_edit)  # type: ignore[attr-defined]
        buf = create_unicode_buffer(length + 1)
        user32.GetWindowTextW(self.h_edit, buf, length + 1)  # type: ignore[attr-defined]
        self._result_text = buf.value
        user32.DestroyWindow(self.hwnd)  # type: ignore[attr-defined]
        self._done = True  # type: ignore[attr-defined]

    def _on_cancel(self) -> None:
        user32 = windll.user32
        self._result_text = None
        user32.DestroyWindow(self.hwnd)  # type: ignore[attr-defined]
        self._done = True  # type: ignore[attr-defined]

    def _on_destroy(self) -> None:
        self._done = True  # type: ignore[attr-defined]

    def _on_size(self) -> None:
        # Reflow controls on window resize
        try:
            user32 = windll.user32
            rect = wintypes.RECT()
            user32.GetClientRect(self.hwnd, byref(rect))  # type: ignore[attr-defined]
            cx = rect.right - rect.left

            margin = getattr(self, "_layout_margin", 24)
            spacing = getattr(self, "_layout_spacing", 12)
            btn_w = getattr(self, "_layout_btn_w", 88)
            btn_h = getattr(self, "_layout_btn_h", 26)

            # Static keeps same height; stretch width
            # Measure static height
            static_rect = wintypes.RECT()
            user32.GetWindowRect(self.h_static, byref(static_rect))  # type: ignore[attr-defined]
            static_h = static_rect.bottom - static_rect.top
            user32.SetWindowPos(self.h_static, 0, margin, margin, cx - 2 * margin, static_h, WIN_SWP_NOZORDER)  # type: ignore[attr-defined]

            # Edit stretches horizontally, stays below static
            edit_y = margin + static_h + 8
            # Preserve current edit height
            cur_edit_rect = wintypes.RECT()
            user32.GetWindowRect(self.h_edit, byref(cur_edit_rect))  # type: ignore[attr-defined]
            cur_edit_h = cur_edit_rect.bottom - cur_edit_rect.top
            user32.SetWindowPos(self.h_edit, 0, margin, edit_y, cx - 2 * margin, cur_edit_h, WIN_SWP_NOZORDER)  # type: ignore[attr-defined]

            # Buttons right-aligned
            cancel_x = cx - margin - btn_w
            ok_x = cancel_x - spacing - btn_w
            btn_y = edit_y + cur_edit_h + spacing * 2
            user32.SetWindowPos(self.h_ok, 0, ok_x, btn_y, btn_w, btn_h, WIN_SWP_NOZORDER)  # type: ignore[attr-defined]
            user32.SetWindowPos(self.h_cancel, 0, cancel_x, btn_y, btn_w, btn_h, WIN_SWP_NOZORDER)  # type: ignore[attr-defined]
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Resize reflow failed: %s", exc)

    def _validate_live(self) -> None:
        user32 = windll.user32
        length = user32.GetWindowTextLengthW(self.h_edit)  # type: ignore[attr-defined]
        buf = create_unicode_buffer(length + 1)
        user32.GetWindowTextW(self.h_edit, buf, length + 1)  # type: ignore[attr-defined]
        try:
            is_valid = bool(self.options.validator(buf.value)) if self.options.validator else True
        except Exception as exc:
            logger = get_logger("message_box")
            if logger:
                logger.debug("Validator raised exception: %s", exc)
            is_valid = True
        user32.EnableWindow(self.h_ok, wintypes.BOOL(1 if is_valid else 0))  # type: ignore[attr-defined]
