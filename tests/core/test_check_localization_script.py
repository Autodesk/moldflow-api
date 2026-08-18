# SPDX-FileCopyrightText: 2026 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the localization checker helper script."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "check_localization.py"


def _load_check_localization_module():
    """Import the standalone localization checker script as a module."""
    spec = spec_from_file_location("check_localization_script", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_base_locale(locale_root: Path) -> None:
    """Create a minimal English locale file for script tests."""
    po_dir = locale_root / "en-US" / "LC_MESSAGES"
    po_dir.mkdir(parents=True)
    (po_dir / "locale.en-US.po").write_text(
        "\n".join(
            [
                'msgid ""',
                'msgstr ""',
                '"Content-Type: text/plain; charset=UTF-8\\n"',
                '"Language: en-US\\n"',
                "",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.core
@pytest.mark.unit
def test_check_localization_detects_get_text_aliases_and_wrappers(tmp_path: Path):
    """The checker should find direct aliases and wrapper-based translation calls."""
    module = _load_check_localization_module()
    src_root = tmp_path / "src"
    locale_root = tmp_path / "locale"
    src_root.mkdir()
    _write_base_locale(locale_root)

    source_file = src_root / "sample_cli.py"
    source_file.write_text(
        "\n".join(
            [
                "from moldflow.i18n import get_text",
                "",
                "_T = get_text()",
                "",
                "def _tr(message: str, **kwargs):",
                "    text = _T(message)",
                "    return text.format(**kwargs) if kwargs else text",
                "",
                "def _validate_batch_mode_inputs(*, translate):",
                "    return translate(\"Batch mode validation\")",
                "",
                "def local_alias():",
                "    _ = get_text()",
                "    return _(\"Local alias message\")",
                "",
                "def main():",
                "    _T(\"Module alias message\")",
                "    _tr(\"Wrapper helper message\")",
                "    _validate_batch_mode_inputs(translate=_T)",
                "    local_alias()",
            ]
        ),
        encoding="utf-8",
    )

    checker = module.LocalizationChecker(src_root, locale_root)
    violations, fixes = checker.check_file(source_file)

    assert violations
    assert {fix.string_value for fix in fixes} == {
        "Batch mode validation",
        "Local alias message",
        "Module alias message",
        "Wrapper helper message",
    }


@pytest.mark.core
@pytest.mark.unit
def test_check_localization_marks_translate_parameter_from_call_site(tmp_path: Path):
    """Translate parameters passed from a call site should be treated as localizers."""
    module = _load_check_localization_module()
    src_root = tmp_path / "src"
    locale_root = tmp_path / "locale"
    src_root.mkdir()
    _write_base_locale(locale_root)

    source_file = src_root / "sample_translate_param.py"
    source_file.write_text(
        "\n".join(
            [
                "from moldflow.i18n import get_text",
                "",
                "def emit_message(translate):",
                "    return translate(\"Translate parameter message\")",
                "",
                "def run():",
                "    translator = get_text()",
                "    return emit_message(translator)",
            ]
        ),
        encoding="utf-8",
    )

    checker = module.LocalizationChecker(src_root, locale_root)
    violations, fixes = checker.check_file(source_file)

    assert violations == [
        (
            f"{source_file}:4: missing localization for "
            "'Translate parameter message' (translate() call)"
        )
    ]
    assert [fix.string_value for fix in fixes] == ["Translate parameter message"]


@pytest.mark.core
@pytest.mark.unit
def test_default_source_paths_include_cli_folder_when_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Default source paths should include both library and CLI roots."""
    module = _load_check_localization_module()
    (monkeypatch.chdir(tmp_path))
    (tmp_path / "src" / "moldflow").mkdir(parents=True)
    (tmp_path / "src" / "moldflow_cli").mkdir(parents=True)

    paths = getattr(module, "_default_source_paths")()

    assert paths == [Path("src/moldflow"), Path("src/moldflow_cli")]


@pytest.mark.core
@pytest.mark.unit
def test_collect_python_files_supports_multiple_roots(tmp_path: Path):
    """Python file collection should aggregate files from all provided roots."""
    module = _load_check_localization_module()
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first_file = first_root / "one.py"
    second_file = second_root / "two.py"
    first_file.write_text("print('one')\n", encoding="utf-8")
    second_file.write_text("print('two')\n", encoding="utf-8")

    py_files = getattr(module, "_collect_python_files")([first_root, second_root])

    assert py_files == [first_file, second_file]
