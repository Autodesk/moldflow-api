#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Static check: validate string localization for user-facing messages.

This script runs comprehensive localization management by default:
- Scans Python files for strings that need localization (calls to _() function)
- Extracts string literals from message enums (ErrorMessage, LogMessage, ValueErrorReason)
- Checks if these strings exist in .po files
- Automatically adds missing strings from source code to locale files
- Automatically fills translation gaps with English fallback text
- Automatically removes orphaned strings from non-English locales

Operations run by default:
1. --autofix: Adds missing strings from source code
2. --fix-gaps: Fills missing translations with English fallback
3. --cleanup-orphaned: Removes stale strings no longer in English base

Focuses on user-facing messages sent through process_log calls and error handling.

Usage:
  python scripts/check_localization.py [--path PATH] [--locale-path PATH]
  python scripts/check_localization.py --check-only          # Only check, no fixes
  python scripts/check_localization.py --no-autofix         # Skip adding missing strings
  python scripts/check_localization.py --no-fix-gaps        # Skip fixing translation gaps
  python scripts/check_localization.py --no-cleanup-orphaned # Skip removing orphaned strings
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


# Strings that are acceptable to remain identical across locales
ALLOW_EQUAL_MSGSTR: set[str] = {
    "OK",
}

@dataclass
class PoEntry:
    msgid: str
    msgstr: str
    line_no: int


@dataclass
class LocalizationFix:
    string_value: str
    source_file: str
    line_no: int
    context: str  # Description of where the string was found


class PoFileParser:
    """Parser for gettext .po files."""

    def __init__(self, po_file_path: Path):
        self.po_file_path = po_file_path
        self.entries: Dict[str, PoEntry] = {}
        self._parse()

    def _parse(self):
        """Parse the .po file and extract msgid/msgstr pairs."""
        if not self.po_file_path.exists():
            return

        content = self.po_file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                i += 1
                continue

            # Look for msgid
            if line.startswith('msgid "'):
                msgid_line_no = i + 1
                msgid = self._extract_string(line)

                # Handle multi-line strings
                i += 1
                while i < len(lines) and lines[i].strip().startswith('"'):
                    msgid += self._extract_string(lines[i])
                    i += 1

                # Look for corresponding msgstr
                if i < len(lines) and lines[i].strip().startswith('msgstr "'):
                    msgstr = self._extract_string(lines[i])

                    # Handle multi-line strings
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith('"'):
                        msgstr += self._extract_string(lines[i])
                        i += 1

                    # Skip empty msgid (file header)
                    if msgid:
                        self.entries[msgid] = PoEntry(msgid, msgstr, msgid_line_no)
                else:
                    i += 1
            else:
                i += 1

    def _extract_string(self, line: str) -> str:
        """Extract string content from a .po line."""
        # Remove msgid/msgstr prefix and quotes
        if line.strip().startswith('msgid "'):
            content = line.strip()[7:-1]  # Remove 'msgid "' and trailing '"'
        elif line.strip().startswith('msgstr "'):
            content = line.strip()[8:-1]  # Remove 'msgstr "' and trailing '"'
        elif line.strip().startswith('"') and line.strip().endswith('"'):
            content = line.strip()[1:-1]  # Remove quotes
        else:
            content = line.strip()

        # Unescape common escape sequences
        content = content.replace('\\"', '"')
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = content.replace('\\\\', '\\')

        return content

    def has_string(self, string: str) -> bool:
        """Check if a string exists in the .po file."""
        return string in self.entries

    def add_entry(self, msgid: str, msgstr: str = "") -> None:
        """Add a new entry to the .po file."""
        if not msgstr:
            msgstr = msgid  # Default to English for base language

        self.entries[msgid] = PoEntry(msgid, msgstr, -1)

    def write_back(self) -> None:
        """Write the entries back to the .po file."""
        if not self.po_file_path.exists():
            # Create directory if it doesn't exist
            self.po_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing content to preserve headers and comments
        existing_content = ""
        if self.po_file_path.exists():
            existing_content = self.po_file_path.read_text(encoding="utf-8")

        # Find where entries start (after the header)
        lines = existing_content.splitlines()
        header_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('msgid ""') and i > 0:
                # Find the end of the header entry
                j = i + 1
                while j < len(lines) and (lines[j].strip().startswith('msgstr') or lines[j].strip().startswith('"')):
                    j += 1
                header_end = j
                break

        # Preserve header
        header_lines = lines[:header_end] if header_end > 0 else [
            'msgid ""',
            'msgstr ""',
            '"Content-Type: text/plain; charset=UTF-8\\n"',
            f'"Language: {self.po_file_path.parent.parent.name}\\n"',
            ''
        ]

        # Sort entries for consistent output
        sorted_entries = sorted(self.entries.values(), key=lambda x: x.msgid)

        # Build new content
        new_lines = header_lines.copy()
        if new_lines and new_lines[-1]:  # Add empty line after header if needed
            new_lines.append('')

        for entry in sorted_entries:
            if entry.msgid:  # Skip empty msgid (header)
                new_lines.append(f'msgid "{self._escape_string(entry.msgid)}"')
                new_lines.append(f'msgstr "{self._escape_string(entry.msgstr)}"')
                new_lines.append('')

        self.po_file_path.write_text('\n'.join(new_lines), encoding="utf-8")

    def _escape_string(self, string: str) -> str:
        """Escape string for .po file format."""
        string = string.replace('\\', '\\\\')
        string = string.replace('"', '\\"')
        string = string.replace('\n', '\\n')
        string = string.replace('\t', '\\t')
        return string


class LocalizationChecker:
    """Main class for checking localization."""

    def __init__(self, src_root: Path, locale_root: Path):
        self.src_root = src_root
        self.locale_root = locale_root
        self.base_locale = "en-US"  # English as default
        self.po_files: Dict[str, PoFileParser] = {}
        self._load_po_files()

    def _load_po_files(self):
        """Load all .po files."""
        for locale_dir in self.locale_root.iterdir():
            if locale_dir.is_dir():
                po_file = locale_dir / "LC_MESSAGES" / f"locale.{locale_dir.name}.po"
                if po_file.exists():
                    self.po_files[locale_dir.name] = PoFileParser(po_file)
                else:
                    # Create parser for new locale
                    self.po_files[locale_dir.name] = PoFileParser(po_file)

    def _extract_strings_from_calls(self, node: ast.AST) -> List[Tuple[str, int, str]]:
        """Extract string literals from _() function calls and process_log usage."""
        strings = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Check for _() calls
                if isinstance(child.func, ast.Name) and child.func.id == "_":
                    if child.args and isinstance(child.args[0], ast.Constant) and isinstance(child.args[0].value, str):
                        strings.append((child.args[0].value, child.lineno, "_() call"))

                # Check for get_text()() calls
                elif (isinstance(child.func, ast.Call) and 
                      isinstance(child.func.func, ast.Name) and 
                      child.func.func.id == "get_text"):
                    if child.args and isinstance(child.args[0], ast.Constant) and isinstance(child.args[0].value, str):
                        strings.append((child.args[0].value, child.lineno, "get_text()() call"))

                # Check for process_log calls to see which enum messages are actually used
                elif isinstance(child.func, ast.Name) and child.func.id == "process_log":
                    if len(child.args) >= 2:
                        # Second argument should be LogMessage enum
                        message_arg = child.args[1]
                        if isinstance(message_arg, ast.Attribute):
                            # Look for LogMessage.SOME_MESSAGE pattern
                            if (isinstance(message_arg.value, ast.Name) and 
                                message_arg.value.id == "LogMessage"):
                                # This indicates LogMessage.SOME_MESSAGE is being used
                                # We'll catch the actual string value from the enum definition
                                pass

        return strings

    def _extract_enum_strings(self, node: ast.AST) -> List[Tuple[str, int, str]]:
        """Extract string values from specific message enum definitions."""
        strings = []

        # Only target specific enum classes that contain user-facing messages
        target_enums = {"ErrorMessage", "LogMessage", "ValueErrorReason"}

        # Look for class definitions that might be enums
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef) and child.name in target_enums:
                # Check if it inherits from Enum
                is_enum = any(
                    (isinstance(base, ast.Name) and base.id == "Enum") or
                    (isinstance(base, ast.Attribute) and base.attr == "Enum")
                    for base in child.bases
                )

                if is_enum:
                    # Extract string values from enum members
                    for item in child.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                                        strings.append((
                                            item.value.value, 
                                            item.lineno, 
                                            f"Enum {child.name}.{target.id}"
                                        ))
                                    elif isinstance(item.value, ast.Tuple):
                                        # Handle tuples like (message, log_level) - extract first element (message)
                                        if item.value.elts and isinstance(item.value.elts[0], ast.Constant) and isinstance(item.value.elts[0].value, str):
                                            strings.append((
                                                item.value.elts[0].value, 
                                                item.lineno, 
                                                f"Enum {child.name}.{target.id} message"
                                            ))

        return strings

    def check_file(self, file_path: Path) -> Tuple[List[str], List[LocalizationFix]]:
        """Check a single Python file for localization issues."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            return [f"{file_path}:{getattr(e, 'lineno', '?')}: {e}"], []

        violations = []
        fixes = []

        # Extract strings from _() calls
        call_strings = self._extract_strings_from_calls(tree)

        # Extract strings from enum definitions
        enum_strings = self._extract_enum_strings(tree)

        all_strings = call_strings + enum_strings

        # Check each string against the base locale
        base_po = self.po_files.get(self.base_locale)
        if not base_po:
            violations.append(f"Base locale {self.base_locale} not found")
            return violations, fixes

        for string_value, line_no, context in all_strings:
            if not base_po.has_string(string_value):
                violations.append(f"{file_path}:{line_no}: missing localization for '{string_value}' ({context})")
                fixes.append(LocalizationFix(
                    string_value=string_value,
                    source_file=str(file_path),
                    line_no=line_no,
                    context=context
                ))

        return violations, fixes

    def check_translation_gaps(self) -> List[str]:
        """Check which English strings are missing translations in other locale files."""
        violations = []

        base_po = self.po_files.get(self.base_locale)
        if not base_po:
            return [f"Base locale {self.base_locale} not found"]

        total_strings = len([msgid for msgid in base_po.entries.keys() if msgid])
        total_locales = len(self.po_files) - 1  # Exclude base locale

        if total_locales == 0:
            return []

        # Collect statistics
        locale_stats = {}

        # Check each non-English locale
        for locale_name, po_parser in self.po_files.items():
            if locale_name == self.base_locale:
                continue

            missing_translations = []
            empty_translations = []

            # Check each string in the base locale
            for msgid, entry in base_po.entries.items():
                if msgid:  # Skip empty msgid (header)
                    if not po_parser.has_string(msgid):
                        missing_translations.append(msgid)
                    else:
                        # Check if translation is empty or same as source (untranslated),
                        # with an allowlist for locale-invariant tokens like "OK"
                        target_entry = po_parser.entries[msgid]
                        if (
                            not target_entry.msgstr.strip()
                            or (target_entry.msgstr == msgid and msgid not in ALLOW_EQUAL_MSGSTR)
                        ):
                            empty_translations.append(msgid)

            locale_stats[locale_name] = {
                'missing': missing_translations,
                'empty': empty_translations,
                'translated': total_strings - len(missing_translations) - len(empty_translations)
            }

        # Add summary
        if any(locale_stats[locale]['missing'] or locale_stats[locale]['empty'] for locale in locale_stats):
            violations.append(f"Translation Status Summary (Base: {self.base_locale}, {total_strings} total strings):")
            for locale_name in sorted(locale_stats.keys()):
                stats = locale_stats[locale_name]
                completion = (stats['translated'] / total_strings) * 100 if total_strings > 0 else 0
                violations.append(f"  {locale_name}: {completion:.1f}% complete ({stats['translated']}/{total_strings} translated, {len(stats['missing'])} missing, {len(stats['empty'])} untranslated)")
            violations.append("")  # Empty line for readability

        # Detailed breakdown for each locale
        for locale_name in sorted(locale_stats.keys()):
            stats = locale_stats[locale_name]

            if stats['missing']:
                violations.append(f"Locale {locale_name}: {len(stats['missing'])} strings not present in .po file")
                for msgid in stats['missing'][:5]:  # Show first 5 as examples
                    violations.append(f"  Missing: '{msgid}'")
                if len(stats['missing']) > 5:
                    violations.append(f"  ... and {len(stats['missing']) - 5} more")

            if stats['empty']:
                violations.append(f"Locale {locale_name}: {len(stats['empty'])} strings need translation")
                for msgid in stats['empty'][:3]:  # Show first 3 as examples
                    violations.append(f"  Untranslated: '{msgid}'")
                if len(stats['empty']) > 3:
                    violations.append(f"  ... and {len(stats['empty']) - 3} more")

        return violations

    def apply_fixes(self, fixes: List[LocalizationFix]) -> int:
        """Apply fixes by adding missing strings to .po files."""
        if not fixes:
            return 0

        applied_count = 0

        # Group fixes by string to avoid duplicates
        unique_strings = {}
        for fix in fixes:
            if fix.string_value not in unique_strings:
                unique_strings[fix.string_value] = fix

        # Add to base locale first
        base_po = self.po_files.get(self.base_locale)
        if base_po:
            for string_value, fix in unique_strings.items():
                if not base_po.has_string(string_value):
                    base_po.add_entry(string_value, string_value)  # English uses same for msgid and msgstr
                    applied_count += 1
                    print(f"Added to {self.base_locale}: '{string_value}' (from {fix.source_file}:{fix.line_no})")

            base_po.write_back()

        # Add to other locales (with English text as fallback)
        for locale_name, po_parser in self.po_files.items():
            if locale_name != self.base_locale:
                for string_value in unique_strings.keys():
                    if not po_parser.has_string(string_value):
                        po_parser.add_entry(string_value, string_value)  # Use English as fallback
                        print(f"Added to {locale_name}: '{string_value}' (fallback: English)")

                po_parser.write_back()

        return applied_count

    def apply_translation_gap_fixes(self) -> int:
        """Apply fixes for translation gaps by adding missing strings with English fallback."""
        base_po = self.po_files.get(self.base_locale)
        if not base_po:
            return 0

        applied_count = 0

        # Check each non-English locale and add missing strings
        for locale_name, po_parser in self.po_files.items():
            if locale_name == self.base_locale:
                continue

            added_to_locale = 0
            updated_in_locale = 0

            # Check each string in the base locale
            for msgid, entry in base_po.entries.items():
                if msgid:  # Skip empty msgid (header)
                    if not po_parser.has_string(msgid):
                        # Add missing string with English as fallback
                        po_parser.add_entry(msgid, entry.msgstr)
                        added_to_locale += 1
                    else:
                        # Update empty translations with English fallback
                        target_entry = po_parser.entries[msgid]
                        if not target_entry.msgstr.strip():
                            po_parser.entries[msgid].msgstr = entry.msgstr
                            updated_in_locale += 1

            if added_to_locale > 0 or updated_in_locale > 0:
                po_parser.write_back()
                applied_count += added_to_locale + updated_in_locale

                actions = []
                if added_to_locale > 0:
                    actions.append(f"added {added_to_locale} missing strings")
                if updated_in_locale > 0:
                    actions.append(f"filled {updated_in_locale} empty translations")

                print(f"Fixed {locale_name}: {', '.join(actions)} with English fallback")

        return applied_count

    def check_orphaned_strings(self) -> List[str]:
        """Check for strings in non-English locales that don't exist in the base locale."""
        base_po = self.po_files.get(self.base_locale)
        if not base_po:
            return []

        violations = []
        base_msgids = set(msgid for msgid in base_po.entries.keys() if msgid)

        for locale_name, po_parser in self.po_files.items():
            if locale_name == self.base_locale:
                continue

            orphaned_strings = []
            for msgid in po_parser.entries.keys():
                if msgid and msgid not in base_msgids:
                    orphaned_strings.append(msgid)

            if orphaned_strings:
                violations.append(f"\nLocale {locale_name}: {len(orphaned_strings)} orphaned strings")
                for i, msgid in enumerate(orphaned_strings[:3]):
                    violations.append(f"  Orphaned: '{msgid}'")
                if len(orphaned_strings) > 3:
                    violations.append(f"  ... and {len(orphaned_strings) - 3} more")

        return violations

    def apply_orphaned_string_cleanup(self) -> int:
        """Remove orphaned strings from non-English locales that don't exist in base locale."""
        base_po = self.po_files.get(self.base_locale)
        if not base_po:
            return 0

        removed_count = 0
        base_msgids = set(msgid for msgid in base_po.entries.keys() if msgid)

        for locale_name, po_parser in self.po_files.items():
            if locale_name == self.base_locale:
                continue

            removed_from_locale = 0
            msgids_to_remove = []

            # Find orphaned strings
            for msgid in po_parser.entries.keys():
                if msgid and msgid not in base_msgids:
                    msgids_to_remove.append(msgid)

            # Remove orphaned strings
            for msgid in msgids_to_remove:
                del po_parser.entries[msgid]
                removed_from_locale += 1

            if removed_from_locale > 0:
                po_parser.write_back()
                removed_count += removed_from_locale
                print(f"Cleaned {locale_name}: removed {removed_from_locale} orphaned strings")

        return removed_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("src/moldflow"),
        help="Root directory to scan for Python files containing message enums and localization calls",
    )
    parser.add_argument(
        "--locale-path", 
        type=Path,
        default=Path("src/moldflow/locale"),
        help="Root directory containing locale files"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues without applying any fixes (disables all autofix operations)",
    )
    parser.add_argument(
        "--no-autofix",
        action="store_true",
        help="Skip adding missing message strings from source code",
    )
    parser.add_argument(
        "--no-fix-gaps",
        action="store_true",
        help="Skip fixing translation gaps",
    )
    parser.add_argument(
        "--no-cleanup-orphaned",
        action="store_true",
        help="Skip removing orphaned strings",
    )
    parser.add_argument(
        "--translation-gaps-only",
        action="store_true",
        help="Only check for translation gaps in locale files, skip source code analysis",
    )
    args = parser.parse_args()

    src_root: Path = args.path
    locale_root: Path = args.locale_path

    # Determine which operations to run (all enabled by default unless explicitly disabled)
    run_autofix = not args.check_only and not args.no_autofix and not args.translation_gaps_only
    run_fix_gaps = not args.check_only and not args.no_fix_gaps
    run_cleanup_orphaned = not args.check_only and not args.no_cleanup_orphaned

    # Only require source path if not just checking translation gaps
    if not args.translation_gaps_only and not src_root.exists():
        print(f"Source path not found: {src_root}", file=sys.stderr)
        return 2

    if not locale_root.exists():
        print(f"Locale path not found: {locale_root}", file=sys.stderr)
        return 2

    checker = LocalizationChecker(src_root, locale_root)

    # Show what operations will be performed
    if not args.check_only:
        operations = []
        if run_autofix:
            operations.append("autofix (add missing strings)")
        if run_fix_gaps:
            operations.append("fix-gaps (fill translations)")
        if run_cleanup_orphaned:
            operations.append("cleanup-orphaned (remove stale strings)")

        if operations:
            print(f"Running localization management: {', '.join(operations)}")
        else:
            print("Running localization check only (no fixes will be applied)")
        print()

    all_violations = []
    all_fixes = []

    # Skip source code analysis if only checking translation gaps
    if not args.translation_gaps_only:
        # Handle single file vs directory
        if src_root.is_file():
            if src_root.suffix == ".py":
                py_files = [src_root]
            else:
                print(f"File is not a Python file: {src_root}", file=sys.stderr)
                return 2
        else:
            py_files = [p for p in src_root.rglob("*.py") if p.is_file()]

        for py_file in py_files:
            violations, fixes = checker.check_file(py_file)
            all_violations.extend(violations)
            all_fixes.extend(fixes)

        # Apply fixes if autofix is enabled
        if run_autofix and all_fixes:
            applied_count = checker.apply_fixes(all_fixes)
            if applied_count > 0:
                print(f"\nAdded {applied_count} missing strings to locale files.")

    # Check for translation gaps in other locales
    translation_gaps = checker.check_translation_gaps()

    # Apply translation gap fixes if enabled
    if run_fix_gaps and translation_gaps:
        gap_fixes_applied = checker.apply_translation_gap_fixes()
        if gap_fixes_applied > 0:
            print(f"\nApplied {gap_fixes_applied} translation gap fixes.")
            # Re-check translation gaps to show remaining issues
            translation_gaps = checker.check_translation_gaps()

    # Check for orphaned strings in non-English locales
    orphaned_strings = checker.check_orphaned_strings()

    # Apply orphaned string cleanup if enabled
    if run_cleanup_orphaned and orphaned_strings:
        orphaned_fixes_applied = checker.apply_orphaned_string_cleanup()
        if orphaned_fixes_applied > 0:
            print(f"\nRemoved {orphaned_fixes_applied} orphaned strings from non-English locales.")
            # Re-check orphaned strings to show remaining issues
            orphaned_strings = checker.check_orphaned_strings()

    # Normalize/sort all locale files for consistent ordering when not check-only
    if not args.check_only:
        for po_parser in checker.po_files.values():
            po_parser.write_back()

    # Report violations
    has_violations = False

    if all_violations:
        has_violations = True
        if run_autofix:
            print(f"\nRemaining message localization violations:")
        else:
            print("Message localization violations:")
        for violation in all_violations:
            print(violation)

    if translation_gaps:
        has_violations = True
        if all_violations:
            print()  # Add separator if we already printed violations
        print("Translation gaps found:")
        for gap in translation_gaps:
            print(gap)

    if orphaned_strings:
        has_violations = True
        if all_violations or translation_gaps:
            print()  # Add separator if we already printed violations
        if run_cleanup_orphaned:
            print("Remaining orphaned strings:")
        else:
            print("Orphaned strings found:")
        for orphaned in orphaned_strings:
            print(orphaned)

    if has_violations:
        return 1

    if args.translation_gaps_only:
        print("No translation gaps found. All locales are up to date.")
    else:
        print("No message localization violations found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


