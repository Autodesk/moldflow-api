# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for run.py helper behaviors."""

import os
from unittest.mock import patch

import pytest

import run as run_script


@pytest.mark.unit
def test_install_package_uses_direct_file_uri_with_cli_extras():
    """A local wheel should be installed via PEP 508 direct reference with extras."""
    run_script.VERSION = "1.2.3"
    wheel_name = "moldflow-1.2.3-py3-none-any.whl"

    with patch("run.os.path.isdir", return_value=True), patch(
        "run.os.listdir", return_value=[wheel_name]
    ), patch("run.os.path.getmtime", return_value=1), patch("run.run_command") as mock_run_command:
        run_script.install_package(build=False)

    args = mock_run_command.call_args[0][0]
    # pip install ... <package_spec> ...
    package_spec = args[7]
    assert package_spec.startswith("moldflow[cli] @ file:///")
    assert package_spec.endswith(".whl")


@pytest.mark.unit
def test_install_package_falls_back_when_dist_directory_missing():
    """Missing dist directory should not crash install helper."""
    run_script.VERSION = "1.2.3"

    with patch("run.os.path.isdir", return_value=False), patch(
        "run.run_command"
    ) as mock_run_command:
        run_script.install_package(build=False)

    args = mock_run_command.call_args[0][0]
    package_spec = args[7]
    assert package_spec == "moldflow[cli]==1.2.3"


@pytest.mark.unit
def test_cli_smoke_runs_expected_commands_without_rebuilding():
    """CLI smoke should create a venv, install the wheel, and run the smoke commands."""
    wheel_path = os.path.join(run_script.DIST_DIR, "moldflow-1.2.3-py3-none-any.whl")
    expected_python = os.path.join(run_script.CLI_SMOKE_VENV_DIR, "Scripts", "python.exe")
    package_spec = run_script.wheel_package_spec(wheel_path)

    with patch("run.build_package") as mock_build, patch(
        "run.os.path.isfile", return_value=True
    ), patch("run._latest_dist_wheel", return_value=wheel_path), patch(
        "run.run_command"
    ) as mock_run_command:
        run_script.cli_smoke(skip_build=True)

    mock_build.assert_not_called()
    assert [call.args[0] for call in mock_run_command.call_args_list] == [
        run_script.python_module_command("venv", run_script.CLI_SMOKE_VENV_DIR),
        [expected_python, "-m", "pip", "install", "--upgrade", "pip"],
        [expected_python, "-m", "pip", "install", package_spec],
        [expected_python, "-m", "moldflow_cli", "--help"],
        [expected_python, "-m", "moldflow_cli", "invoke", "--help"],
        [expected_python, "-m", "moldflow_cli", "list", "--json"],
    ]


@pytest.mark.unit
def test_cli_smoke_rebuilds_and_replaces_existing_venv():
    """CLI smoke should rebuild by default and clean an existing venv first."""
    wheel_path = os.path.join(run_script.DIST_DIR, "moldflow-1.2.3-py3-none-any.whl")

    with patch("run.build_package") as mock_build, patch(
        "run._remove_directory_if_present"
    ) as mock_remove_dir, patch("run._latest_dist_wheel", return_value=wheel_path), patch(
        "run.os.path.isfile", return_value=True
    ), patch(
        "run.run_command"
    ):
        run_script.cli_smoke()

    mock_build.assert_called_once_with(install=False)
    mock_remove_dir.assert_called_once_with(run_script.CLI_SMOKE_VENV_DIR)


@pytest.mark.unit
def test_cli_smoke_checks_for_built_wheel_before_removing_existing_venv():
    """CLI smoke should fail before deleting the existing smoke venv when no wheel is present."""
    with patch("run.build_package"), patch(
        "run._latest_dist_wheel", side_effect=RuntimeError("missing wheel")
    ), patch("run._remove_directory_if_present") as mock_remove_dir:
        with pytest.raises(RuntimeError, match="missing wheel"):
            run_script.cli_smoke(skip_build=True)

    mock_remove_dir.assert_not_called()


@pytest.mark.unit
def test_cli_smoke_raises_when_venv_python_is_missing():
    """CLI smoke should raise a clear error when venv creation produces no Python."""
    wheel_path = os.path.join(run_script.DIST_DIR, "moldflow-1.2.3-py3-none-any.whl")

    with patch("run._latest_dist_wheel", return_value=wheel_path), patch(
        "run._remove_directory_if_present"
    ) as mock_remove_dir, patch("run.run_command"), patch("run.os.path.isfile", return_value=False):
        with pytest.raises(RuntimeError, match="Python executable was not found"):
            run_script.cli_smoke(skip_build=True)

    assert mock_remove_dir.call_count == 2


@pytest.mark.unit
def test_wheel_package_spec_rejects_non_wheel_paths():
    """Wheel package helper should reject invalid input early."""
    with pytest.raises(ValueError, match="non-empty string"):
        run_script.wheel_package_spec("")
    with pytest.raises(ValueError, match="wheel file"):
        run_script.wheel_package_spec("dist\\not-a-wheel.txt")


@pytest.mark.unit
def test_remove_directory_if_present_tolerates_concurrent_deletion():
    """Directory cleanup should ignore only a concurrent FileNotFound case."""
    with patch("run.os.path.exists", return_value=True), patch(
        "run.os.path.isdir", return_value=True
    ), patch("run.shutil.rmtree", side_effect=FileNotFoundError):
        getattr(run_script, "_remove_directory_if_present")("C:\\temp\\gone")


@pytest.mark.unit
def test_remove_directory_if_present_rejects_file_paths():
    """Directory cleanup should fail clearly when given a file path."""
    with patch("run.os.path.exists", return_value=True), patch(
        "run.os.path.isdir", return_value=False
    ):
        with pytest.raises(NotADirectoryError, match="Expected a directory path"):
            getattr(run_script, "_remove_directory_if_present")("C:\\temp\\not-a-dir")


@pytest.mark.unit
def test_cli_smoke_cleans_up_venv_when_command_fails():
    """CLI smoke should remove the temporary venv again when a smoke command fails."""
    wheel_path = os.path.join(run_script.DIST_DIR, "moldflow-1.2.3-py3-none-any.whl")

    with patch("run._latest_dist_wheel", return_value=wheel_path), patch(
        "run._remove_directory_if_present"
    ) as mock_remove_dir, patch("run.os.path.isfile", return_value=True), patch(
        "run.run_command", side_effect=[None, None, RuntimeError("smoke failed")]
    ):
        with pytest.raises(RuntimeError, match="smoke failed"):
            run_script.cli_smoke(skip_build=True)

    assert mock_remove_dir.call_count == 2
