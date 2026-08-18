# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused tests for moldflow CLI entrypoint behavior."""

from __future__ import annotations

from unittest.mock import patch
from unittest.mock import Mock
import importlib
import runpy
import sys

import pytest


@pytest.mark.cli
@pytest.mark.unit
def test_cli_entrypoint_installed_and_callable():
    """Smoke test that the CLI builder is importable via the package entrypoint."""
    mod = importlib.import_module("moldflow_cli.__main__")
    assert hasattr(mod, "build_cli_app") or hasattr(mod, "main")


@pytest.mark.cli
@pytest.mark.unit
def test_cli_main_only_converts_missing_cli_deps_to_user_message():
    """Missing typer/rich should print guidance; unrelated import errors should surface."""
    mod = importlib.import_module("moldflow_cli.__main__")

    def _import_missing_typer(name: str):
        if name == "typer":
            raise ModuleNotFoundError("No module named 'typer'")
        return object()

    with patch("importlib.import_module", side_effect=_import_missing_typer):
        with pytest.raises(SystemExit) as exc_info:
            mod.main()
        assert exc_info.value.code == 1

    with patch(
        "importlib.import_module", side_effect=ModuleNotFoundError("No module named 'otherpkg'")
    ):
        with pytest.raises(ModuleNotFoundError):
            mod.main()


@pytest.mark.cli
@pytest.mark.unit
def test_cli_main_reconfigures_stdio_to_utf8_when_supported():
    """CLI entrypoint should best-effort configure stdout/stderr to UTF-8."""
    mod = importlib.import_module("moldflow_cli.__main__")
    fake_stdout = Mock()
    fake_stderr = Mock()
    with patch("sys.stdout", fake_stdout), patch("sys.stderr", fake_stderr):
        getattr(mod, "_ensure_utf8_stdio")()

    fake_stdout.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")
    fake_stderr.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")


@pytest.mark.cli
@pytest.mark.unit
def test_cli_module_execution_invokes_main():
    """Executing python -m moldflow_cli should invoke main() and run the app."""
    app_called = {"count": 0}

    class _FakeApp:
        def __call__(self):
            app_called["count"] += 1

    cached_main = sys.modules.pop("moldflow_cli.__main__", None)
    try:
        with patch("moldflow_cli.commands.build_cli_app", return_value=_FakeApp()):
            runpy.run_module("moldflow_cli.__main__", run_name="__main__")
    finally:
        if cached_main is not None:
            sys.modules["moldflow_cli.__main__"] = cached_main

    assert app_called["count"] == 1
