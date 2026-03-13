# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Version checking and update notification functionality for Moldflow API.

This module handles checking for package updates from PyPI and displaying
appropriate update notifications to users.
"""

import os
import re
import sys
import json
import warnings
from pathlib import Path
import urllib.request
from importlib.metadata import version, PackageNotFoundError
from typing import Tuple, Optional

# Module-level constants to avoid repeated literals and improve maintainability
PACKAGE_NAME = "moldflow"
NO_UPDATE_ENV_VAR = "MOLDFLOW_API_NO_UPDATE_CHECK"
VIRTUAL_ENV_ENV_VAR = "VIRTUAL_ENV"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
PYPI_TIMEOUT_SECONDS = 0.5
WARNING_FOOTER = f"To disable this warning, set {NO_UPDATE_ENV_VAR}=1"


def _get_package_version() -> str:
    """
    Get the current package version.

    Returns:
            str: The package version in format 'major.minor.patch'

    Raises:
            RuntimeError: If version information cannot be read from the package
    """
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        # If package is not installed, check version.json in package directory
        pkg_version_file = Path(__file__).parent / "version.json"
        try:
            with open(pkg_version_file, encoding='utf-8') as f:
                data = json.load(f)
                return f"{data['major']}.{data['minor']}.{data['patch']}"
        except (IOError, json.JSONDecodeError, KeyError) as e:
            raise RuntimeError(
                f"Failed to read version from {pkg_version_file}. "
                "This likely indicates a build or packaging issue."
            ) from e


def _parse_version(ver: str) -> tuple:
    """
    Parse version string into a tuple of (major, minor, patch).
    Handles versions like: 1.2.3, 1.2.3rc1, 1.2.3b2, 1.2.3.4, etc.
    Always returns a 3-tuple, ignoring any suffixes or extra segments.

    Args:
        ver (str): The version string to parse.

    Returns:
        tuple: A tuple containing the major, minor, and patch versions.
    """
    nums = [int(x) for x in re.findall(r'\d+', ver)][:3]
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


def _process_pypi_releases(
    releases: dict, current_parsed: tuple
) -> Tuple[Optional[str], Optional[str]]:
    """
    Process release data from PyPI to find updates.

    Args:
        releases (dict): The release data from PyPI.
        current_parsed (tuple): The current parsed version.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing:
            - The latest version string in the same major release, or None if none
            - The latest overall version string if it's a new major, or None if none
    """
    if not releases:
        return None, None

    current_major = current_parsed[0]

    # Filter out pre-releases and yanked releases
    valid_versions = []
    for ver_str, files in releases.items():
        # Skip if version has any alpha characters (pre-releases)
        if re.search(r"[a-zA-Z]", ver_str):
            continue
        # Skip if all files are yanked
        if all(f.get("yanked", False) for f in files):
            continue
        try:
            parsed = _parse_version(ver_str)
            valid_versions.append((parsed, ver_str))
        except (ValueError, IndexError):
            continue

    if not valid_versions:
        return None, None

    # Find latest in the same major version
    same_major_versions = [(p, v) for p, v in valid_versions if p[0] == current_major]
    latest_in_major_version = None
    if same_major_versions:
        latest_in_major_parsed, version_str = max(same_major_versions)
        if latest_in_major_parsed > current_parsed:
            latest_in_major_version = version_str

    # Find next major version
    higher_major_versions = [(p, v) for p, v in valid_versions if p[0] > current_major]
    latest_overall_version = None
    if higher_major_versions:
        # Find the lowest major version that's higher than current
        next_major = min(p[0] for p, _ in higher_major_versions)
        next_major_versions = [(p, v) for p, v in higher_major_versions if p[0] == next_major]
        _, version_str = max(next_major_versions)
        latest_overall_version = version_str

    return latest_in_major_version, latest_overall_version


def _check_for_updates() -> Tuple[Optional[str], Optional[str]]:
    """
    Check PyPI for newer versions of the package.

    Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing:
                    - The latest version string in the same major release, or None if none
                    - The latest overall version string if it's a new major, or None if none
    """
    if os.environ.get(NO_UPDATE_ENV_VAR):
        return None, None

    try:
        current_version = _get_package_version()
        current_parsed = _parse_version(current_version)

        # Query PyPI API
        url = PYPI_JSON_URL
        with urllib.request.urlopen(url, timeout=PYPI_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read())
            releases = data["releases"]

        return _process_pypi_releases(releases, current_parsed)

    except Exception:  # pylint: disable=broad-except
        # Any error (timeout, network issue, etc) should fail silently
        return None, None


def _pip_cmd(version_string: Optional[str] = None) -> str:
    """
    Construct a pip command using the current Python executable.
    Uses 'python -m pip' to ensure the correct Python environment.

    Args:
        version_string (Optional[str]): The version string to install. Defaults to None.

    Returns:
        str: The pip command.
    """
    base = f'"{sys.executable}" -m pip install --upgrade'
    # Use --user if not in a virtual environment
    if not bool(os.environ.get(VIRTUAL_ENV_ENV_VAR)):
        base += " --user"
    base += f" {PACKAGE_NAME}"
    if version_string:
        base += f"=={version_string}"
    return base


def _show_update_message(minor_update: Optional[str], major_update: Optional[str]) -> None:
    """
    Show update notification message.

    Args:
            minor_update (Optional[str]): The latest version in the same major release, or None
            major_update (Optional[str]): The latest overall version if it's a new major, or None
    """
    if not (minor_update or major_update):
        return

    current_version = _get_package_version()
    footer = WARNING_FOOTER

    if major_update:
        current_major = _parse_version(current_version)[0]
        latest_major = _parse_version(major_update)[0]
        current_year = 2000 + current_major
        latest_year = 2000 + latest_major

        pip_cmd = _pip_cmd(major_update)

        body = f"""A new major version of the Moldflow API library is available.
	You are currently on version {current_version}, for Autodesk Moldflow {current_year}.x.
	The latest version is {major_update}, for Autodesk Moldflow {latest_year}.x.

	This is a major update that may contain breaking changes.
	It is only recommended if you are using the corresponding Moldflow product.
	To upgrade, run:
		{pip_cmd}""".strip()

        if minor_update:
            minor_pip_cmd = _pip_cmd(minor_update)
            minor_update_info = f"""
	A compatible update to version {minor_update} is also available.
	To upgrade to this non-breaking version, run:
		{minor_pip_cmd}""".strip()
            body += f"\n{minor_update_info}"

        warning_msg = f"{body}\n\n{footer}"
        warnings.warn(warning_msg, UserWarning)

    elif minor_update:  # Minor update only
        pip_cmd = _pip_cmd()
        body = f"""A new version of {PACKAGE_NAME} is available: {current_version} → {minor_update}
	To upgrade, run:
		{pip_cmd}""".strip()

        warning_msg = f"{body}\n\n{footer}"
        warnings.warn(warning_msg, UserWarning)


def check_for_updates_on_import():
    """
    Perform version check and show update message if updates are available.

    This function is called during module import to check for available updates
    and display notifications to the user.
    """
    # Respect the opt-out environment variable and avoid calling the updater
    if os.environ.get(NO_UPDATE_ENV_VAR):
        return
    minor, major = _check_for_updates()
    if minor or major:
        _show_update_message(minor, major)


def get_version() -> str:
    """
    Get the current package version.

    Returns:
            str: The package version string
    """
    return _get_package_version()
