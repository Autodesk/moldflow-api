MessageBox
==========

Convenience wrapper to display message boxes and a simple
text input dialog from Python scripts using the ``moldflow`` package.

Usage
-----

.. code-block:: python

   from moldflow import (
       MessageBox,
       MessageBoxType,
       MessageBoxResult,
       MessageBoxOptions,
       MessageBoxIcon,
       MessageBoxDefaultButton,
       MessageBoxModality,
   )

   # Informational message
   MessageBox("Operation completed.", MessageBoxType.INFO).show()

   # Confirmation
   result = MessageBox("Proceed with analysis?", MessageBoxType.YES_NO).show()
   if result == MessageBoxResult.YES:
       pass

   # Text input
   material_id = MessageBox("Enter your material ID:", MessageBoxType.INPUT).show()
   if material_id:
       pass

   # Advanced options
   opts = MessageBoxOptions(
       icon=MessageBoxIcon.WARNING,
       default_button=MessageBoxDefaultButton.BUTTON2,
       modality=MessageBoxModality.TASK,
       topmost=True,
       right_align=False,
       rtl_reading=False,
       help_button=False,
       set_foreground=True,
       owner_hwnd=None,
   )
   result = MessageBox(
       "Retry failed operation?",
       MessageBoxType.RETRY_CANCEL,
       title="Moldflow",
       options=opts,
   ).show()

Convenience methods
-------------------

.. code-block:: python

   MessageBox.info("Saved")
   MessageBox.warning("Low disk space")
   MessageBox.error("Failed to save")
   if MessageBox.confirm_yes_no("Proceed?") == MessageBoxResult.YES:
       pass

   # Prompt text with validation
   def is_nonempty(s: str) -> bool:
       return bool(s.strip())

   value = MessageBox.prompt_text(
       "Enter ID:",
       default_text="",
       placeholder="e.g. MAT-123",
       validator=is_nonempty,
   )
   if value is not None:
       pass

Options
-------

.. list-table:: MessageBoxOptions
   :header-rows: 1

   * - Parameter
     - Type
     - Description
   * - icon
     - MessageBoxIcon | None
     - Override default icon
   * - default_button
     - MessageBoxDefaultButton | None
     - Set default button (2/3/4). Validated vs type
   * - modality
     - MessageBoxModality | None
     - Application (default), Task-modal, System-modal
   * - topmost
     - bool
     - Keep message box on top
   * - set_foreground
     - bool
     - Force foreground
   * - right_align / rtl_reading
     - bool
     - Layout flags for right-to-left locales
   * - help_button
     - bool
     - Show Help button
   * - owner_hwnd
     - int | None
     - Owner window handle (improves modality/Z-order)
   * - default_text / placeholder
     - str | None
     - Prefill text and cue banner for input dialog
   * - is_password
     - bool
     - Mask input characters
   * - char_limit
     - int | None
     - Maximum characters accepted (client-side)
   * - width_dlu / height_dlu
     - int | None
     - Size the input dialog (dialog units)
   * - validator
     - Callable[[str], bool] | None
     - Enable OK only when input satisfies predicate
   * - font_face / font_size_pt
     - str / int
     - Font for input dialog (default Segoe UI 9pt)

API
---

.. automodule:: moldflow.message_box

Notes
-----

- Localization: button captions ("OK", "Cancel"), title, and prompt are localized via the package i18n system.
- Return type: ``MessageBox.show()`` returns ``MessageBoxReturn`` (``MessageBoxResult | str | None``).
