# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for run.py helper behaviors."""

from unittest.mock import patch

import pytest

import run as run_script


@pytest.mark.unit
def test_install_package_uses_direct_file_uri_with_cli_extras():
    """A local wheel should be installed via PEP 508 direct reference with extras."""
    run_script.VERSION = "1.2.3"
    wheel_name = "moldflow-1.2.3-py3-none-any.whl"

    with patch("run.os.listdir", return_value=[wheel_name]), patch(
        "run.os.path.getmtime", return_value=1
    ), patch("run.run_command") as mock_run_command:
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
