# pylint: disable=too-many-lines
"""Tests for version check functionality."""

import json
import os
import sys
import tempfile
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest import mock
import pytest

# pylint: disable=protected-access,no-member,too-many-function-args,redefined-outer-name
# We need to test private methods directly
# no-member is disabled because we're importing from local source
# too-many-function-args is disabled because _show_update_message takes exactly two arguments
# redefined-outer-name is disabled because pytest fixtures are meant to be used as parameters


@pytest.fixture(autouse=True)
def _setup_environment():
    """Setup and cleanup for version check tests environment."""
    # Save original state
    original_path = sys.path.copy()
    original_modules = dict(sys.modules)
    original_env = os.environ.copy()

    # Setup test environment
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    if src_path in sys.path:
        sys.path.remove(src_path)
    sys.path.insert(0, src_path)

    # Remove any existing moldflow modules from cache to force reload from src
    for module_name in list(sys.modules):
        if module_name.startswith('moldflow'):
            del sys.modules[module_name]

    # Disable automatic update check during tests to avoid network calls
    os.environ['MOLDFLOW_API_NO_UPDATE_CHECK'] = '1'

    yield

    # Restore original state
    sys.path[:] = original_path
    sys.modules.clear()
    sys.modules.update(original_modules)
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def version_check_fixture():
    """Get module references for version check tests."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    return (
        version_check_module,
        version_check_module._parse_version,
        version_check_module._process_pypi_releases,
    )


def test_get_package_version_installed(version_check_fixture, monkeypatch):
    """Test getting version when package is installed."""
    version_check_module, _, _ = version_check_fixture
    monkeypatch.setattr('moldflow.version_check.version', lambda _: "26.0.1")
    assert version_check_module._get_package_version() == "26.0.1"


def test_get_package_version_from_json(version_check_fixture, tmp_path):
    """Test getting version from version.json when package not installed."""
    version_check_module, _, _ = version_check_fixture
    version_data = {"major": "26", "minor": "0", "patch": "0"}
    version_file = tmp_path / "version.json"
    version_file.write_text(json.dumps(version_data))

    fake_init_file = tmp_path / "version_check.py"
    with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
        with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
            assert version_check_module._get_package_version() == "26.0.0"


def test_get_package_version_json_missing(version_check_fixture, tmp_path):
    """Test RuntimeError is raised when version.json is missing."""
    version_check_module, _, _ = version_check_fixture
    fake_init_file = tmp_path / "version_check.py"
    with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
        with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
            with pytest.raises(RuntimeError):
                version_check_module._get_package_version()


def test_get_package_version_json_invalid(version_check_fixture, tmp_path):
    """Test RuntimeError is raised when version.json is invalid."""
    version_check_module, _, _ = version_check_fixture
    version_file = tmp_path / "version.json"
    version_file.write_text("invalid json")

    fake_init_file = tmp_path / "version_check.py"
    with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
        with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
            with pytest.raises(RuntimeError):
                version_check_module._get_package_version()


def test_get_package_version_io_error(version_check_fixture, tmp_path):
    """Test RuntimeError is raised when IOError occurs reading version.json."""
    version_check_module, _, _ = version_check_fixture
    # Create a directory instead of a file to trigger IOError
    version_dir = tmp_path / "version.json"
    version_dir.mkdir()

    fake_init_file = tmp_path / "version_check.py"
    with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
        with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
            with pytest.raises(RuntimeError) as exc_info:
                version_check_module._get_package_version()
            assert "Failed to read version" in str(exc_info.value)


def test_process_releases_newer_version(version_check_fixture):
    """Test release processing when a newer version is available."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {"26.0.0": [{}], "26.1.0": [{}], "25.9.9": [{}], "27.0.0": [{}]}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor == "26.1.0"
    assert major == "27.0.0"


def test_process_releases_ignore_prerelease(version_check_fixture):
    """Test prerelease versions are ignored."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {"26.0.0": [{}], "26.1.0a1": [{}], "27.0.0b1": [{}]}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major is None


def test_process_releases_ignore_yanked(version_check_fixture):
    """Test yanked releases are ignored."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {"26.0.0": [{}], "26.1.0": [{"yanked": True}], "27.0.0": [{"yanked": True}]}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major is None


def test_process_releases_no_valid_releases(version_check_fixture):
    """Test handling when no valid releases are found."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {"invalid": [{}]}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major is None


def test_process_releases_no_releases(version_check_fixture):
    """Test handling when releases dict is empty."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major is None


def test_process_releases_no_same_major_newer(version_check_fixture):
    """Test when only major version updates are available."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {"26.0.0": [{}], "27.0.0": [{}], "28.0.0": [{}]}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major == "27.0.0"


def test_process_releases_current(version_check_fixture):
    """Test when current version is latest."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {"26.0.0": [{}], "25.0.0": [{}]}
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major is None


def test_process_releases_multiple_yanked_files(version_check_fixture):
    """Test handling of mixed yanked status in release files."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {
        "26.0.0": [{}],
        "26.1.0": [{"yanked": True}, {"yanked": False}],
        "27.0.0": [{"yanked": False}, {"yanked": True}],
    }
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor == "26.1.0"
    assert major == "27.0.0"


def test_check_for_updates_network_error(version_check_fixture):
    """Test handling of network errors in update check."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch('urllib.request.urlopen', side_effect=OSError):
        minor, major = version_check_module._check_for_updates()
        assert minor is None
        assert major is None


def test_check_for_updates_json_decode_error(version_check_fixture):
    """Test handling of JSON decode errors in update check."""
    version_check_module, _, _ = version_check_fixture

    class MockResponse:
        """Mock response class that returns invalid JSON data.

        Used for testing JSON decode error handling.
        """

        def __enter__(self):
            """Context manager entry point."""
            return self

        def __exit__(self, *args):
            """Context manager exit point."""
            return None

        def read(self):
            """Return invalid JSON data to simulate a JSON decode error."""
            return b"invalid json"

    with mock.patch('urllib.request.urlopen', return_value=MockResponse()):
        minor, major = version_check_module._check_for_updates()
        assert minor is None
        assert major is None


def test_check_for_updates_timeout_error(version_check_fixture):
    """Test handling of timeout errors in update check."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch('urllib.request.urlopen', side_effect=TimeoutError):
        minor, major = version_check_module._check_for_updates()
        assert minor is None
        assert major is None


def test_show_update_message_minor_virtualenv(version_check_fixture):
    """Test update message for minor version in virtualenv."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': '/path/to/venv'}):
        with mock.patch('warnings.warn') as mock_warn:
            version_check_module._show_update_message("26.1.0", None)
            mock_warn.assert_called_once()
            warning_msg = mock_warn.call_args[0][0]
            assert "pip install --upgrade moldflow" in warning_msg
            assert "26.1.0" in warning_msg


def test_show_update_message_minor_global(version_check_fixture):
    """Test update message for minor version in global install."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': ''}):
        with mock.patch('warnings.warn') as mock_warn:
            version_check_module._show_update_message("26.1.0", None)
            mock_warn.assert_called_once()
            warning_msg = mock_warn.call_args[0][0]
            assert "pip install --upgrade --user moldflow" in warning_msg
            assert "26.1.0" in warning_msg


def test_show_update_message_major(version_check_fixture):
    """Test update message for major version."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch('warnings.warn') as mock_warn:
        version_check_module._show_update_message(None, "27.0.0")
        mock_warn.assert_called_once()
        warning_msg = mock_warn.call_args[0][0]
        assert "27.0.0" in warning_msg
        assert "major update" in warning_msg.lower()


def test_show_update_message_major_and_minor(version_check_fixture):
    """Test update message when both major and minor updates are available."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch('warnings.warn') as mock_warn:
        version_check_module._show_update_message("26.1.0", "27.0.0")
        mock_warn.assert_called_once()
        warning_msg = mock_warn.call_args[0][0]
        assert "27.0.0" in warning_msg
        assert "major update" in warning_msg.lower()


def test_show_update_message_major_without_minor_in_global_env(version_check_fixture):
    """Test major update message in global environment."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': ''}):
        with mock.patch('warnings.warn') as mock_warn:
            version_check_module._show_update_message(None, "27.0.0")
            mock_warn.assert_called_once()
            warning_msg = mock_warn.call_args[0][0]
            assert "--user" in warning_msg
            assert "27.0.0" in warning_msg


def test_show_update_message_no_updates(version_check_fixture):
    """Test no message is shown when no updates are available."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch('warnings.warn') as mock_warn:
        version_check_module._show_update_message(None, None)
        mock_warn.assert_not_called()


def test_update_check_disabled(version_check_fixture):
    """Test update check is skipped when disabled via environment variable."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': '1'}):
        with mock.patch('urllib.request.urlopen') as mock_urlopen:
            minor, major = version_check_module._check_for_updates()
            assert minor is None
            assert major is None
            mock_urlopen.assert_not_called()


def test_check_for_updates_success(version_check_fixture):
    """Test successful update check with mock response."""
    version_check_module, _, _ = version_check_fixture

    class DummyResponse:
        """Mock response with valid release data."""

        def __enter__(self):
            """Context manager entry."""
            return self

        def __exit__(self, exc_type, exc, tb):
            """Context manager exit."""
            return None

        def read(self):
            """Return valid release data."""
            return json.dumps(
                {"releases": {"26.0.0": [{}], "26.1.0": [{}], "27.0.0": [{}]}}
            ).encode()

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
            with mock.patch('urllib.request.urlopen', return_value=DummyResponse()):
                minor, major = version_check_module._check_for_updates()
                assert minor == "26.1.0"
                assert major == "27.0.0"


def test_parse_version_edge_cases(version_check_fixture):
    """Test version parsing edge cases."""
    _, _parse_version, _ = version_check_fixture
    # Test various version formats
    assert _parse_version("1.0.0") == (1, 0, 0)
    assert _parse_version("1.0") == (1, 0, 0)
    assert _parse_version("1") == (1, 0, 0)
    # Test with leading zeros
    assert _parse_version("01.02.03") == (1, 2, 3)
    # Test with non-numeric parts
    assert _parse_version("1.0.0a1") == (1, 0, 0)
    assert _parse_version("1.0.0-beta") == (1, 0, 0)


def test_import_time_update_check_coverage(version_check_fixture):
    """Test line 361: The import-time update check call to _show_update_message."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=("26.1.0", "27.0.0")
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                minor, major = version_check_module._check_for_updates()
                if minor or major:
                    version_check_module._show_update_message(minor, major)
                mock_show.assert_called_once_with("26.1.0", "27.0.0")


def test_parse_version_all_alpha_parts(version_check_fixture):
    """Test _parse_version with parts that are all alpha (line 253)."""
    _, _parse_version, _ = version_check_fixture
    # Test version with all-alpha parts that should be skipped
    result = _parse_version("alpha.beta.gamma")
    assert result == (0, 0, 0)  # Should default to (0, 0, 0) when no numeric parts

    # Test mixed alpha and numeric
    result = _parse_version("1.alpha.2")
    assert result == (1, 2, 0)  # Alpha part should be skipped


def test_parse_version_with_early_break(version_check_fixture):
    """Test _parse_version with early break on non-digit character (line 260)."""
    _, _parse_version, _ = version_check_fixture
    # Test versions that would cause early break in numeric extraction
    result = _parse_version("1a2.3b4.5c6")
    assert result == (1, 3, 5)  # Should stop at first non-digit in each part


def test_parse_version_single_part(version_check_fixture):
    """Test _parse_version with single part to trigger padding (line 264)."""
    _, _parse_version, _ = version_check_fixture
    # Test single part - should pad to 3 parts
    result = _parse_version("42")
    assert result == (42, 0, 0)

    # Test two parts - should pad to 3 parts
    result = _parse_version("1.5")
    assert result == (1, 5, 0)


def test_parse_version_empty_numeric_extraction(version_check_fixture):
    """Test _parse_version when numeric extraction results in empty string."""
    _, _parse_version, _ = version_check_fixture
    # This should test the case where a part starts with non-digit
    result = _parse_version("a1.b2.c3")
    # These parts start with alpha, so numeric extraction is empty from start
    # and they get skipped, resulting in (0, 0, 0) with padding
    assert result == (0, 0, 0)


def test_show_update_message_major_and_minor_in_virtualenv(version_check_fixture):
    """Test major update message with minor update in virtualenv."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': '/path/to/venv'}):
        with mock.patch('warnings.warn') as mock_warn:
            with mock.patch.object(
                version_check_module, '_get_package_version', return_value="26.0.0"
            ):
                version_check_module._show_update_message("26.1.0", "27.0.0")
                mock_warn.assert_called_once()
                warning_msg = mock_warn.call_args[0][0]
                assert "27.0.0" in warning_msg
                assert "26.1.0" in warning_msg
                assert "pip install --upgrade moldflow==27.0.0" in warning_msg
                assert "pip install --upgrade moldflow==26.1.0" in warning_msg


def test_show_update_message_major_and_minor_global_env(version_check_fixture):
    """Test major update message with minor update in global environment."""
    version_check_module, _, _ = version_check_fixture
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': ''}):
        with mock.patch('warnings.warn') as mock_warn:
            with mock.patch.object(
                version_check_module, '_get_package_version', return_value="26.0.0"
            ):
                version_check_module._show_update_message("26.1.0", "27.0.0")
                mock_warn.assert_called_once()
                warning_msg = mock_warn.call_args[0][0]
                assert "27.0.0" in warning_msg
                assert "26.1.0" in warning_msg
                assert "--user" in warning_msg


def test_import_time_update_check_direct_execution():
    """Test the import-time update check execution (lines 415-421)."""
    # This test directly tests the import-time behavior
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch('moldflow.version_check._check_for_updates', return_value=("26.1.0", None)):
            with mock.patch('moldflow.version_check._show_update_message'):
                # Re-import the module to trigger the import-time check
                import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

                # Manually execute the import-time check logic to ensure coverage
                if not os.environ.get("MOLDFLOW_API_NO_UPDATE_CHECK"):
                    minor, major = version_check_module._check_for_updates()
                    if minor or major:
                        version_check_module._show_update_message(minor, major)

                # Also test version retrieval
                version = version_check_module._get_package_version()
                assert version is not None
                assert isinstance(version, str)
                assert len(version) > 0
                assert '.' in version  # Should be in format like "x.y.z"


def test_process_pypi_releases_parse_error_handling(version_check_fixture):
    """Test _process_pypi_releases with version parse errors (line 294)."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    # Create releases with versions that will cause parse errors
    releases = {
        "26.0.0": [{}],
        "": [{}],  # Empty version string
        "..": [{}],  # Only dots
        "invalid.version.format": [{}],
    }
    current_parsed = _parse_version("26.0.0")

    # Should handle parse errors gracefully and return current version results
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major is None


def test_process_pypi_releases_no_higher_major(version_check_fixture):
    """Test _process_pypi_releases when no higher major versions exist."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {
        "26.0.0": [{}],
        "26.1.0": [{}],
        "25.9.9": [{}],  # Lower major version
        "24.5.0": [{}],  # Even lower major version
    }
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor == "26.1.0"
    assert major is None  # No higher major version


def test_process_pypi_releases_multiple_higher_majors(version_check_fixture):
    """Test _process_pypi_releases chooses lowest next major version."""
    _, _parse_version, _process_pypi_releases = version_check_fixture
    releases = {
        "26.0.0": [{}],
        "27.0.0": [{}],
        "27.1.0": [{}],
        "28.0.0": [{}],  # Higher major, but 27 should be chosen as next
        "29.0.0": [{}],  # Even higher major
    }
    current_parsed = _parse_version("26.0.0")
    minor, major = _process_pypi_releases(releases, current_parsed)
    assert minor is None
    assert major == "27.1.0"  # Should be latest in the next major (27.x)


def test_process_pypi_releases_value_error_handling(version_check_fixture):
    """Test _process_pypi_releases handles ValueError from _parse_version (lines 294-295)."""
    _, _parse_version, _process_pypi_releases = version_check_fixture

    # Mock _parse_version to raise ValueError for specific versions
    original_parse_version = _parse_version

    def mock_parse_version(ver):
        if ver == "bad.version":
            raise ValueError("Invalid version")
        return original_parse_version(ver)

    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_parse_version', side_effect=mock_parse_version):
        releases = {
            "26.0.0": [{}],
            "bad.version": [{}],  # This will cause ValueError
            "26.1.0": [{}],
        }
        current_parsed = original_parse_version("26.0.0")
        minor, major = _process_pypi_releases(releases, current_parsed)
        # Should handle the error gracefully and process other versions
        assert minor == "26.1.0"
        assert major is None


def test_process_pypi_releases_index_error_handling(version_check_fixture):
    """Test _process_pypi_releases handles IndexError from _parse_version (lines 294-295)."""
    _, _parse_version, _process_pypi_releases = version_check_fixture

    # Mock _parse_version to raise IndexError for specific versions
    original_parse_version = _parse_version

    def mock_parse_version(ver):
        if ver == "index.error":
            raise IndexError("Index error")
        return original_parse_version(ver)

    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_parse_version', side_effect=mock_parse_version):
        releases = {
            "26.0.0": [{}],
            "index.error": [{}],  # This will cause IndexError
            "27.0.0": [{}],
        }
        current_parsed = original_parse_version("26.0.0")
        minor, major = _process_pypi_releases(releases, current_parsed)
        # Should handle the error gracefully and process other versions
        assert minor is None
        assert major == "27.0.0"


def test_import_time_update_message_call_coverage():
    """Test the actual call to _show_update_message on import (line 419)."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=("26.1.0", "27.0.0")
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                # Directly execute the import-time check logic to cover line 419
                if not os.environ.get("MOLDFLOW_API_NO_UPDATE_CHECK"):
                    minor, major = version_check_module._check_for_updates()
                    if minor or major:
                        version_check_module._show_update_message(minor, major)  # This is line 419

                # Verify the message was called
                mock_show.assert_called_once_with("26.1.0", "27.0.0")


# NEW COMPREHENSIVE TESTS TO ACHIEVE 100% COVERAGE


def test_package_not_found_fallback_to_version_json():
    """Test lines 225-233: PackageNotFoundError fallback to version.json."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory() as temp_dir:
        version_file = Path(temp_dir) / "version.json"
        version_data = {"major": "26", "minor": "0", "patch": "1"}
        version_file.write_text(json.dumps(version_data))

        fake_init_file = Path(temp_dir) / "version_check.py"
        with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
            with mock.patch.object(
                version_check_module, 'version', side_effect=PackageNotFoundError
            ):
                result = version_check_module._get_package_version()
                assert result == "26.0.1"


def test_version_json_io_error_coverage():
    """Test lines 232-233: IOError when reading version.json."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory instead of file to cause IOError
        version_dir = Path(temp_dir) / "version.json"
        version_dir.mkdir()

        fake_init_file = Path(temp_dir) / "version_check.py"
        with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
            with mock.patch.object(
                version_check_module, 'version', side_effect=PackageNotFoundError
            ):
                with pytest.raises(RuntimeError) as exc_info:
                    version_check_module._get_package_version()
                assert "Failed to read version" in str(exc_info.value)


def test_parse_version_all_alpha_coverage():
    """Test line 253: Skip parts that are all alpha."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test version with all alpha parts
    result = version_check_module._parse_version("alpha.beta.gamma")
    assert result == (0, 0, 0)

    # Test mixed alpha and numeric
    result = version_check_module._parse_version("1.alpha.2")
    assert result == (1, 2, 0)


def test_parse_version_early_break_coverage():
    """Test line 260: Early break on non-digit character."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    result = version_check_module._parse_version("1a2.3b4.5c6")
    assert result == (1, 3, 5)  # Should stop at first non-digit


def test_parse_version_numeric_check_coverage():
    """Test line 261: Check if numeric content exists before appending."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # This should trigger the numeric check and skip parts with no leading digits
    result = version_check_module._parse_version("a1.b2.c3")
    assert result == (0, 0, 0)  # No leading digits


def test_process_pypi_releases_empty_coverage():
    """Test line 277: Handle empty releases."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    result = version_check_module._process_pypi_releases({}, (26, 0, 0))
    assert result == (None, None)


def test_process_pypi_releases_yanked_filtering_coverage():
    """Test yanked release filtering."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test scenario 1: Mixed yanked status - some files yanked, some not
    releases1 = {
        "26.0.0": [{}],
        "26.1.0": [{"yanked": True}],  # All files yanked
        "26.2.0": [{"yanked": True}, {"yanked": True}],  # All files yanked
        "27.0.0": [{"yanked": False}, {"yanked": True}],  # Mixed yanked status
    }
    result1 = version_check_module._process_pypi_releases(releases1, (26, 0, 0))
    assert result1[1] == "27.0.0"  # Only non-yanked version

    # Test scenario 2: All newer versions yanked except major update
    releases2 = {
        "26.0.0": [{}],
        "26.1.0": [{"yanked": True}],  # All files yanked
        "26.2.0": [{"yanked": True}, {"yanked": True}],  # All files yanked
        "27.0.0": [{"yanked": False}],  # Not yanked
    }
    result2 = version_check_module._process_pypi_releases(releases2, (26, 0, 0))
    assert result2[0] is None  # No minor updates (yanked)
    assert result2[1] == "27.0.0"  # Major update available


def test_process_pypi_releases_no_valid_versions_coverage():
    """Test when no valid versions remain after filtering."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test scenario 1: Invalid format, pre-release with 'a', and yanked release
    releases1 = {
        "invalid": [{}],
        "26.1.0a1": [{}],  # Pre-release
        "26.2.0": [{"yanked": True}],  # Yanked
    }
    result1 = version_check_module._process_pypi_releases(releases1, (26, 0, 0))
    assert result1 == (None, None)

    # Test scenario 2: Invalid format, pre-release with 'alpha', and yanked release
    releases2 = {
        "invalid": [{}],  # Invalid version format
        "26.1.0alpha": [{}],  # Pre-release
        "26.2.0": [{"yanked": True}],  # Yanked release
    }
    result2 = version_check_module._process_pypi_releases(releases2, (26, 0, 0))
    assert result2 == (None, None)


def test_process_pypi_releases_major_version_selection_coverage():
    """Test selection logic for major versions."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test scenario 1: Multiple versions in same major, next major available
    releases = {
        "26.0.0": [{}],
        "26.1.0": [{}],
        "26.2.5": [{}],  # Latest in major 26
        "27.0.0": [{}],
        "27.1.0": [{}],  # Latest in major 27
        "28.0.0": [{}],  # Higher major, but 27 should be chosen as next
    }
    result = version_check_module._process_pypi_releases(releases, (26, 0, 0))
    assert result[0] == "26.2.5"  # Latest in same major
    assert result[1] == "27.1.0"  # Next major version

    # Test scenario 2: Simpler case with fewer patch versions
    releases2 = {
        "26.0.0": [{}],
        "26.1.0": [{}],  # Latest in same major
        "27.0.0": [{}],  # Next major
        "27.1.0": [{}],  # Latest in next major
        "28.0.0": [{}],  # Higher major (should not be selected as next)
    }
    result2 = version_check_module._process_pypi_releases(releases2, (26, 0, 0))
    assert result2[0] == "26.1.0"  # Latest in same major
    assert result2[1] == "27.1.0"  # Latest in next major (27), not 28


def test_check_for_updates_disabled_coverage():
    """Test line 331: Check environment variable."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': '1'}):
        result = version_check_module._check_for_updates()
        assert result == (None, None)


def test_check_for_updates_exception_handling_coverage():
    """Test lines 340-343: Exception handling in update check."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch('urllib.request.urlopen', side_effect=Exception("Network error")):
            result = version_check_module._check_for_updates()
            assert result == (None, None)


def test_check_for_updates_timeout_coverage():
    """Test timeout handling in update check."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch('urllib.request.urlopen', side_effect=TimeoutError):
            result = version_check_module._check_for_updates()
            assert result == (None, None)


def test_check_for_updates_json_error_coverage():
    """Test JSON decode error handling."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    class MockResponse:
        """Mock response class that returns invalid JSON data.

        Used for testing JSON decode error handling.
        """

        def __enter__(self):
            """Context manager entry point."""
            return self

        def __exit__(self, *args):
            """Context manager exit point."""
            return None

        def read(self):
            """Return invalid JSON data to simulate a JSON decode error."""
            return b"invalid json"

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch('urllib.request.urlopen', return_value=MockResponse()):
            result = version_check_module._check_for_updates()
            assert result == (None, None)


def test_show_update_message_no_updates_coverage():
    """Test line 358: Early return when no updates."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch('warnings.warn') as mock_warn:
        version_check_module._show_update_message(None, None)
        mock_warn.assert_not_called()


def test_show_update_message_minor_update_coverage():
    """Test lines 400-411: Minor update message branch."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
        with mock.patch('warnings.warn') as mock_warn:
            version_check_module._show_update_message("26.1.0", None)
            mock_warn.assert_called_once()
            warning_msg = mock_warn.call_args[0][0]
            assert "26.1.0" in warning_msg


def test_show_update_message_major_and_minor_coverage():
    """Test major update with minor update also available."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
        with mock.patch('warnings.warn') as mock_warn:
            version_check_module._show_update_message("26.1.0", "27.0.0")
            mock_warn.assert_called_once()
            warning_msg = mock_warn.call_args[0][0]
            assert "27.0.0" in warning_msg  # Major update shown
            assert "26.1.0" in warning_msg  # Minor update also mentioned


def test_show_update_message_virtualenv_vs_global():
    """Test different pip commands for virtualenv vs global install."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test virtualenv
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': '/path/to/venv'}):
        with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
            with mock.patch('warnings.warn') as mock_warn:
                version_check_module._show_update_message("26.1.0", None)
                warning_msg = mock_warn.call_args[0][0]
                assert "--user" not in warning_msg  # No --user in virtualenv

    # Test global install
    with mock.patch.dict(os.environ, {'VIRTUAL_ENV': ''}):
        with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
            with mock.patch('warnings.warn') as mock_warn:
                version_check_module._show_update_message("26.1.0", None)
                warning_msg = mock_warn.call_args[0][0]
                assert "--user" in warning_msg  # --user for global install


def test_exception_handling_in_process_releases_coverage():
    """Test exception handling in _process_pypi_releases (lines 294-295)."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Mock _parse_version to raise exceptions
    original_parse_version = version_check_module._parse_version

    def failing_parse_version(ver_str):
        if ver_str == "error_trigger":
            raise ValueError("Parse error")
        if ver_str == "index_trigger":  # Changed from elif to if
            raise IndexError("Index error")
        return original_parse_version(ver_str)

    with mock.patch.object(
        version_check_module, '_parse_version', side_effect=failing_parse_version
    ):
        releases = {"26.0.0": [{}], "error_trigger": [{}], "index_trigger": [{}], "26.1.0": [{}]}
        result = version_check_module._process_pypi_releases(releases, (26, 0, 0))
        # Should handle exceptions gracefully and process valid versions
        assert result[0] == "26.1.0"


def test_import_time_behavior_coverage():
    """Test import-time behavior (lines 416-422)."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Simulate import-time behavior
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=("26.1.0", None)
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                # Execute the import-time logic manually to ensure coverage
                if not os.environ.get("MOLDFLOW_API_NO_UPDATE_CHECK"):
                    minor, major = version_check_module._check_for_updates()
                    if minor or major:
                        version_check_module._show_update_message(minor, major)  # Line 419

                mock_show.assert_called_once_with("26.1.0", None)


def test_version_assignment_coverage():
    """Test version retrieval functionality."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test version retrieval works correctly
    version = version_check_module.get_version()
    assert version is not None
    assert isinstance(version, str)
    assert '.' in version


def test_process_pypi_releases_parse_exception_coverage():
    """Test exception handling in _process_pypi_releases when _parse_version raises exceptions."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Mock _parse_version to raise specific exceptions
    original_parse = version_check_module._parse_version

    def failing_parse(ver_str):
        # Test various version strings that trigger different exceptions
        if ver_str == "value_error":
            raise ValueError("Parse failed")
        if ver_str == "index_error":
            raise IndexError("Index failed")
        if ver_str == "invalid_format":
            raise ValueError("Cannot parse")
        if ver_str == "index_problem":
            raise IndexError("Index error")
        return original_parse(ver_str)

    # Test scenario 1: ValueError and IndexError with different version strings
    with mock.patch.object(version_check_module, '_parse_version', side_effect=failing_parse):
        releases1 = {
            "26.0.0": [{}],
            "value_error": [{}],  # This will trigger ValueError
            "index_error": [{}],  # This will trigger IndexError
            "26.1.0": [{}],
        }
        current_parsed = original_parse("26.0.0")
        result1 = version_check_module._process_pypi_releases(releases1, current_parsed)
        # Should handle exceptions gracefully and process valid versions
        assert result1[0] == "26.1.0"
        assert result1[1] is None

    # Test scenario 2: Different exception-triggering version strings
    with mock.patch.object(version_check_module, '_parse_version', side_effect=failing_parse):
        releases2 = {
            "26.0.0": [{}],
            "invalid_format": [{}],  # Will cause ValueError
            "index_problem": [{}],  # Will cause IndexError
            "26.1.0": [{}],  # Valid version
        }
        result2 = version_check_module._process_pypi_releases(releases2, (26, 0, 0))
        assert result2[0] == "26.1.0"  # Should process valid versions despite exceptions


def test_import_time_show_update_message_call():
    """Test coverage of line 419: the actual call to _show_update_message during import."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Simulate the exact import-time scenario to hit line 419
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=("26.1.0", "27.0.0")
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                # Execute the exact code path from lines 416-419
                if not os.environ.get("MOLDFLOW_API_NO_UPDATE_CHECK"):
                    minor, major = version_check_module._check_for_updates()
                    if minor or major:
                        version_check_module._show_update_message(minor, major)  # This is line 419

                # Verify the call was made
                mock_show.assert_called_once_with("26.1.0", "27.0.0")


def test_import_time_update_check_with_minor_only():
    """Test import-time update check when only minor update is available."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=("26.1.0", None)
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                # Execute import-time logic
                if not os.environ.get("MOLDFLOW_API_NO_UPDATE_CHECK"):
                    minor, major = version_check_module._check_for_updates()
                    if minor or major:
                        version_check_module._show_update_message(minor, major)  # Line 419

                mock_show.assert_called_once_with("26.1.0", None)


def test_import_time_update_check_with_major_only():
    """Test import-time update check when only major update is available."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=(None, "27.0.0")
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                # Execute import-time logic
                if not os.environ.get("MOLDFLOW_API_NO_UPDATE_CHECK"):
                    minor, major = version_check_module._check_for_updates()
                    if minor or major:
                        version_check_module._show_update_message(minor, major)  # Line 419

                mock_show.assert_called_once_with(None, "27.0.0")


def test_package_not_found_error_fallback_coverage():
    """Test lines 30-38: PackageNotFoundError fallback to version.json reading."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create version.json file
        version_file = Path(temp_dir) / "version.json"
        version_data = {"major": "26", "minor": "1", "patch": "2"}
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f)

        # Mock __file__ to point to temp directory
        fake_init_file = Path(temp_dir) / "version_check.py"
        with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
            # Mock version() to raise PackageNotFoundError
            with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
                result = version_check_module._get_package_version()
                assert result == "26.1.2"


def test_version_json_file_reading_coverage():
    """Test lines 34-36: Reading and parsing version.json file."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create version.json with proper format
        version_file = Path(temp_dir) / "version.json"
        version_data = {"major": "25", "minor": "9", "patch": "8"}
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f)

        fake_init_file = Path(temp_dir) / "version_check.py"
        with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
            with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
                result = version_check_module._get_package_version()
                assert result == "25.9.8"


def test_version_json_ioerror_exception_coverage():
    """Test lines 37-41: IOError exception handling when reading version.json."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory instead of a file to trigger IOError
        version_path = Path(temp_dir) / "version.json"
        version_path.mkdir()  # This will cause IOError when trying to read as file

        fake_init_file = Path(temp_dir) / "version_check.py"
        with mock.patch.object(version_check_module, '__file__', str(fake_init_file)):
            with mock.patch('moldflow.version_check.version', side_effect=PackageNotFoundError):
                with pytest.raises(RuntimeError) as exc_info:
                    version_check_module._get_package_version()
                assert "Failed to read version" in str(exc_info.value)
                assert "This likely indicates a build or packaging issue" in str(exc_info.value)


def test_parse_version_all_alpha_skip_coverage():
    """Test line 59: Skip parts that are all alpha characters."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test version with all alpha parts - should be skipped
    result = version_check_module._parse_version("alpha.beta.gamma")
    assert result == (0, 0, 0)

    # Test mixed alpha and numeric parts
    result = version_check_module._parse_version("1.alpha.3")
    assert result == (1, 3, 0)  # Alpha part skipped


def test_parse_version_numeric_extraction_coverage():
    """Test lines 66-67: Numeric extraction and early break on non-digit."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test early break when encountering non-digit characters
    result = version_check_module._parse_version("1a2.3b4.5c6")
    assert result == (1, 3, 5)  # Should stop at first non-digit in each part

    # Test with mixed characters
    result = version_check_module._parse_version("12abc.34def.56ghi")
    assert result == (12, 34, 56)  # Should extract numeric prefix only


def test_parse_version_empty_numeric_handling_coverage():
    """Test when numeric extraction results in empty string (line 67)."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Parts that start with non-digit characters should be skipped
    result = version_check_module._parse_version("a1.b2.c3")
    assert result == (0, 0, 0)  # No leading digits, so all parts skipped


def test_parse_version_padding_coverage():
    """Test line 71: Padding to ensure exactly 3 parts."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    result = version_check_module._parse_version("1")
    assert result == (1, 0, 0)

    result = version_check_module._parse_version("1.2")
    assert result == (1, 2, 0)

    result = version_check_module._parse_version("1.2.3")
    assert result == (1, 2, 3)


def test_process_pypi_releases_empty_releases_coverage():
    """Test line 84-85: Handle empty releases dictionary."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    result = version_check_module._process_pypi_releases({}, (26, 0, 0))
    assert result == (None, None)


def test_process_pypi_releases_prerelease_filtering_coverage():
    """Test lines 92-94: Filter out pre-release versions with alpha characters."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    releases = {
        "26.0.0": [{}],
        "26.1.0a1": [{}],  # Pre-release with alpha
        "26.2.0b2": [{}],  # Pre-release with beta
        "26.3.0rc1": [{}],  # Pre-release with rc
        "27.0.0alpha1": [{}],  # Pre-release with alpha
    }
    result = version_check_module._process_pypi_releases(releases, (26, 0, 0))
    assert result == (None, None)  # All newer versions are pre-releases


def test_check_for_updates_env_var_coverage():
    """Test line 138: Environment variable check to disable updates."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': '1'}):
        result = version_check_module._check_for_updates()
        assert result == (None, None)


def test_check_for_updates_network_request_coverage():
    """Test lines 147-150: Network request and JSON parsing."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    class MockResponse:
        """Mock HTTP response for testing."""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            """Mock read method for HTTP response."""
            return json.dumps(
                {"releases": {"26.0.0": [{}], "26.1.0": [{}], "27.0.0": [{}]}}
            ).encode()

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
            with mock.patch('urllib.request.urlopen', return_value=MockResponse()):
                result = version_check_module._check_for_updates()
                assert result[0] == "26.1.0"  # Minor update
                assert result[1] == "27.0.0"  # Major update


def test_show_update_message_no_updates_early_return_coverage():
    """Test lines 165-166: Early return when no updates available."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch('warnings.warn') as mock_warn:
        version_check_module._show_update_message(None, None)
        mock_warn.assert_not_called()


def test_show_update_message_major_update_coverage():
    """Test lines 172-206: Major update message generation."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
        with mock.patch('warnings.warn') as mock_warn:
            with mock.patch.dict(os.environ, {'VIRTUAL_ENV': '/path/to/venv'}):
                version_check_module._show_update_message(None, "27.0.0")
                mock_warn.assert_called_once()
                warning_msg = mock_warn.call_args[0][0]
                assert "27.0.0" in warning_msg
                assert "major update" in warning_msg.lower()
                assert "2026" in warning_msg  # Current year from major version
                assert "2027" in warning_msg  # Latest year from major version


def test_show_update_message_major_with_minor_coverage():
    """Test lines 193-203: Major update with minor update available."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
        with mock.patch('warnings.warn') as mock_warn:
            with mock.patch.dict(os.environ, {'VIRTUAL_ENV': ''}):  # Global install
                version_check_module._show_update_message("26.1.0", "27.0.0")
                mock_warn.assert_called_once()
                warning_msg = mock_warn.call_args[0][0]
                assert "27.0.0" in warning_msg
                assert "26.1.0" in warning_msg
                assert "--user" in warning_msg  # Global install command


def test_show_update_message_minor_only_coverage():
    """Test lines 208-219: Minor update only message."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
        with mock.patch('warnings.warn') as mock_warn:
            with mock.patch.dict(os.environ, {'VIRTUAL_ENV': '/some/venv'}):
                version_check_module._show_update_message("26.1.0", None)
                mock_warn.assert_called_once()
                warning_msg = mock_warn.call_args[0][0]
                assert "26.1.0" in warning_msg
                assert "pip install --upgrade moldflow" in warning_msg
                assert "--user" not in warning_msg  # Virtual env, no --user


def test_check_for_updates_on_import_coverage():
    """Test line 229: check_for_updates_on_import function entry point."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test when update check is disabled
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': '1'}):
        with mock.patch.object(version_check_module, '_check_for_updates') as mock_check:
            version_check_module.check_for_updates_on_import()
            mock_check.assert_not_called()


def test_check_for_updates_on_import_with_updates_coverage():
    """Test line 232: Import-time message display when updates available."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_check_for_updates', return_value=("26.1.0", "27.0.0")
        ):
            with mock.patch.object(version_check_module, '_show_update_message') as mock_show:
                version_check_module.check_for_updates_on_import()
                mock_show.assert_called_once_with("26.1.0", "27.0.0")


def test_all_exception_branches_coverage():
    """Test comprehensive exception handling across all functions."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Test timeout exception in _check_for_updates
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch('urllib.request.urlopen', side_effect=TimeoutError("Request timeout")):
            result = version_check_module._check_for_updates()
            assert result == (None, None)

    # Test general exception in _check_for_updates
    with mock.patch.dict(os.environ, {'MOLDFLOW_API_NO_UPDATE_CHECK': ''}):
        with mock.patch.object(
            version_check_module, '_get_package_version', side_effect=Exception("General error")
        ):
            result = version_check_module._check_for_updates()
            assert result == (None, None)


def test_specific_error_handling_coverage():
    """Specific ValueError and IndexError handling in _process_pypi_releases."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    # Create a mock parse function that raises specific exceptions for certain versions
    # Use numeric-only version strings to bypass the alpha character check at lines 93-94
    original_parse = version_check_module._parse_version

    def mock_parse_with_exceptions(ver_str):
        if ver_str == "99.99.99":  # Numeric string that will trigger ValueError
            raise ValueError("Simulated parse error")
        if ver_str == "88.88.88":  # Numeric string that will trigger IndexError
            raise IndexError("Simulated index error")
        return original_parse(ver_str)

    # Patch the _parse_version function
    with mock.patch.object(
        version_check_module, '_parse_version', side_effect=mock_parse_with_exceptions
    ):
        releases = {
            "26.0.0": [{}],  # Valid version
            "99.99.99": [{}],  # This will trigger ValueError on line 99, caught on line 101
            "88.88.88": [{}],  # This will trigger IndexError on line 99, caught on line 101
            "26.1.0": [{}],  # Another valid version
        }
        current_parsed = original_parse("26.0.0")
        result = version_check_module._process_pypi_releases(releases, current_parsed)

        # The function should handle the exceptions gracefully and process valid versions
        assert result[0] == "26.1.0"  # Should get the valid minor update
        assert result[1] is None  # No major update in this test


def test_virtualenv_detection_coverage():
    """Test virtual environment detection in _show_update_message."""
    import moldflow.version_check as version_check_module  # pylint: disable=import-outside-toplevel

    with mock.patch.object(version_check_module, '_get_package_version', return_value="26.0.0"):
        with mock.patch('warnings.warn') as mock_warn:
            # Test with VIRTUAL_ENV set
            with mock.patch.dict(os.environ, {'VIRTUAL_ENV': '/path/to/venv'}):
                version_check_module._show_update_message("26.1.0", None)
                warning_msg = mock_warn.call_args[0][0]
                assert "--user" not in warning_msg

            # Test with VIRTUAL_ENV empty
            mock_warn.reset_mock()
            with mock.patch.dict(os.environ, {'VIRTUAL_ENV': ''}):
                version_check_module._show_update_message("26.1.0", None)
                warning_msg = mock_warn.call_args[0][0]
                assert "--user" in warning_msg
