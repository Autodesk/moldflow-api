# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Tests for scripts/generate_switcher.py"""

import json
import os
import sys
from unittest.mock import patch

import pytest

# Ensure the scripts directory is importable, but avoid leaking sys.path changes
_scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
_original_sys_path = list(sys.path)
try:
    sys.path.insert(0, _scripts_dir)
    from generate_switcher import (
        parse_version_tags,
        sort_versions,
        generate_switcher_json,
        get_version_from_json,
        _validate_version_progression,
    )
finally:
    sys.path[:] = _original_sys_path

MOCK_VERSION_JSON = 'generate_switcher.get_version_from_json'


# ---------------------------------------------------------------------------
# parse_version_tags
# ---------------------------------------------------------------------------


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestParseVersionTags:
    """Tests for tag filtering against the sphinx-multiversion whitelist."""

    def test_accepts_v_prefixed_tags(self):
        tags = ['v1.0.0', 'v2.3.4', 'v27.0.0']
        assert parse_version_tags(tags) == tags

    def test_accepts_tags_without_v_prefix(self):
        tags = ['1.0.0', '2.3.4', '27.0.0']
        assert parse_version_tags(tags) == tags

    def test_accepts_mixed_prefix_tags(self):
        tags = ['v1.0.0', '2.0.0', 'v3.1.2']
        assert parse_version_tags(tags) == tags

    def test_rejects_prerelease_tags(self):
        tags = ['v1.0.0rc1', 'v1.0.0a1', 'v1.0.0b2']
        assert parse_version_tags(tags) == []

    def test_rejects_post_release_tags(self):
        assert parse_version_tags(['v1.0.0.post1']) == []

    def test_rejects_dev_tags(self):
        assert parse_version_tags(['v1.0.0.dev3']) == []

    def test_rejects_local_tags(self):
        assert parse_version_tags(['v1.0.0+local']) == []

    def test_rejects_non_version_tags(self):
        tags = ['release-1', 'latest', 'foo', 'docs-v2']
        assert parse_version_tags(tags) == []

    def test_filters_mixed_valid_and_invalid(self):
        tags = ['v1.0.0', 'v2.0.0rc1', 'latest', '3.0.0', 'v4.0.0.dev1']
        assert parse_version_tags(tags) == ['v1.0.0', '3.0.0']

    def test_empty_input(self):
        assert parse_version_tags([]) == []


# ---------------------------------------------------------------------------
# sort_versions
# ---------------------------------------------------------------------------


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestSortVersions:
    """Tests for descending version sort."""

    def test_descending_order(self):
        tags = ['v1.0.0', 'v3.0.0', 'v2.0.0']
        assert sort_versions(tags) == ['v3.0.0', 'v2.0.0', 'v1.0.0']

    def test_patch_ordering(self):
        tags = ['v1.0.2', 'v1.0.0', 'v1.0.1']
        assert sort_versions(tags) == ['v1.0.2', 'v1.0.1', 'v1.0.0']

    def test_mixed_prefix_ordering(self):
        tags = ['1.0.0', 'v2.0.0', '3.0.0']
        assert sort_versions(tags) == ['3.0.0', 'v2.0.0', '1.0.0']

    def test_single_tag(self):
        assert sort_versions(['v1.0.0']) == ['v1.0.0']


# ---------------------------------------------------------------------------
# generate_switcher_json — basic structure (no include_current)
# ---------------------------------------------------------------------------


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestGenerateSwitcherJsonStructure:
    """Tests for output format and latest-flag logic."""

    def test_empty_tags_returns_empty(self):
        assert generate_switcher_json([]) == []

    @patch(MOCK_VERSION_JSON, return_value='v1.0.0')
    def test_single_tag_is_latest(self, _):
        result = generate_switcher_json(['v1.0.0'])
        assert len(result) == 1
        assert result[0]['version'] == 'v1.0.0'
        assert result[0]['is_latest'] is True
        assert '(latest)' in result[0]['name']

    @patch(MOCK_VERSION_JSON, return_value='v3.0.0')
    def test_latest_flag_only_on_first(self, _):
        result = generate_switcher_json(['v1.0.0', 'v2.0.0', 'v3.0.0'])
        assert result[0]['is_latest'] is True
        assert result[0]['version'] == 'v3.0.0'
        for entry in result[1:]:
            assert entry['is_latest'] is False

    @patch(MOCK_VERSION_JSON, return_value='v1.0.0')
    def test_url_uses_tag_name(self, _):
        result = generate_switcher_json(['v1.0.0'])
        assert result[0]['url'] == '../v1.0.0/'

    @patch(MOCK_VERSION_JSON, return_value='1.0.0')
    def test_url_preserves_no_v_prefix(self, _):
        result = generate_switcher_json(['1.0.0'])
        assert result[0]['url'] == '../1.0.0/'

    @patch(MOCK_VERSION_JSON, return_value='v2.0.0')
    def test_all_entries_have_required_keys(self, _):
        result = generate_switcher_json(['v1.0.0', 'v2.0.0'])
        for entry in result:
            assert 'version' in entry
            assert 'name' in entry
            assert 'url' in entry
            assert 'is_latest' in entry


# ---------------------------------------------------------------------------
# generate_switcher_json — include_current with version.json
# ---------------------------------------------------------------------------


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestIncludeCurrent:
    """Tests for the include_current flag and version.json integration."""

    @patch(MOCK_VERSION_JSON, return_value='v2.0.1')
    def test_newer_version_added_as_latest(self, _):
        result = generate_switcher_json(['v2.0.0', 'v1.0.0'], include_current=True)
        assert result[0]['version'] == 'v2.0.1'
        assert result[0]['is_latest'] is True
        assert result[1]['is_latest'] is False

    @patch(MOCK_VERSION_JSON, return_value='v2.0.0')
    def test_same_version_not_added(self, _):
        result = generate_switcher_json(['v2.0.0', 'v1.0.0'], include_current=True)
        assert result[0]['version'] == 'v2.0.0'
        assert len(result) == 2

    @patch(MOCK_VERSION_JSON, return_value='v1.0.0')
    def test_older_version_not_added(self, _):
        result = generate_switcher_json(['v2.0.0', 'v1.0.0'], include_current=True)
        assert result[0]['version'] == 'v2.0.0'
        assert len(result) == 2

    @patch(MOCK_VERSION_JSON, return_value=None)
    def test_none_version_json_no_effect(self, _):
        result = generate_switcher_json(['v2.0.0'], include_current=True)
        assert len(result) == 1
        assert result[0]['is_latest'] is True

    @patch(MOCK_VERSION_JSON, return_value='v2.0.1')
    def test_newer_version_not_added_without_include_current(self, _):
        """version.json is read and validated, but not added to output."""
        result = generate_switcher_json(['v2.0.0', 'v1.0.0'], include_current=False)
        assert len(result) == 2
        assert result[0]['version'] == 'v2.0.0'
        assert result[0]['is_latest'] is True

    @patch(MOCK_VERSION_JSON, return_value='v2.0.0')
    def test_same_version_without_include_current(self, _):
        """Same version in version.json is harmless regardless of flag."""
        result = generate_switcher_json(['v2.0.0'], include_current=False)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Version progression rules
# ---------------------------------------------------------------------------


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestVersionProgression:
    """Tests for version skip / progression validation."""

    @patch(MOCK_VERSION_JSON, return_value='v1.0.1')
    def test_valid_patch_bump(self, _):
        result = generate_switcher_json(['v1.0.0'], include_current=True)
        assert result[0]['version'] == 'v1.0.1'

    @patch(MOCK_VERSION_JSON, return_value='v1.1.0')
    def test_valid_minor_bump(self, _):
        result = generate_switcher_json(['v1.0.0'], include_current=True)
        assert result[0]['version'] == 'v1.1.0'

    @patch(MOCK_VERSION_JSON, return_value='v2.0.0')
    def test_valid_major_bump(self, _):
        result = generate_switcher_json(['v1.0.0'], include_current=True)
        assert result[0]['version'] == 'v2.0.0'

    @patch(MOCK_VERSION_JSON, return_value='v1.0.3')
    def test_skipped_patch_raises(self, _):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            generate_switcher_json(['v1.0.0'], include_current=True)

    @patch(MOCK_VERSION_JSON, return_value='v1.3.0')
    def test_skipped_minor_raises(self, _):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            generate_switcher_json(['v1.0.0'], include_current=True)

    @patch(MOCK_VERSION_JSON, return_value='v3.0.0')
    def test_skipped_major_raises(self, _):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            generate_switcher_json(['v1.0.0'], include_current=True)

    @patch(MOCK_VERSION_JSON, return_value='v1.1.1')
    def test_minor_bump_with_nonzero_patch_raises(self, _):
        with pytest.raises(ValueError, match="patch must be 0"):
            generate_switcher_json(['v1.0.0'], include_current=True)

    @patch(MOCK_VERSION_JSON, return_value='v2.1.0')
    def test_major_bump_with_nonzero_minor_raises(self, _):
        with pytest.raises(ValueError, match="minor and patch must be 0"):
            generate_switcher_json(['v1.0.0'], include_current=True)

    @patch(MOCK_VERSION_JSON, return_value='v2.0.1')
    def test_major_bump_with_nonzero_patch_raises(self, _):
        with pytest.raises(ValueError, match="minor and patch must be 0"):
            generate_switcher_json(['v1.0.0'], include_current=True)


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestValidationRunsWithoutIncludeCurrent:
    """Validation fires on the default (CI) path even without include_current."""

    @patch(MOCK_VERSION_JSON, return_value='v1.0.3')
    def test_skipped_patch_raises_without_flag(self, _):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            generate_switcher_json(['v1.0.0'], include_current=False)

    @patch(MOCK_VERSION_JSON, return_value='v1.3.0')
    def test_skipped_minor_raises_without_flag(self, _):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            generate_switcher_json(['v1.0.0'], include_current=False)

    @patch(MOCK_VERSION_JSON, return_value='v3.0.0')
    def test_skipped_major_raises_without_flag(self, _):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            generate_switcher_json(['v1.0.0'], include_current=False)

    @patch(MOCK_VERSION_JSON, return_value='v1.1.1')
    def test_minor_bump_nonzero_patch_raises_without_flag(self, _):
        with pytest.raises(ValueError, match="patch must be 0"):
            generate_switcher_json(['v1.0.0'], include_current=False)

    @patch(MOCK_VERSION_JSON, return_value='v2.1.0')
    def test_major_bump_nonzero_minor_raises_without_flag(self, _):
        with pytest.raises(ValueError, match="minor and patch must be 0"):
            generate_switcher_json(['v1.0.0'], include_current=False)

    @patch(MOCK_VERSION_JSON, return_value='v1.0.1')
    def test_valid_bump_without_flag_does_not_add_to_output(self, _):
        """Valid progression is fine — version just isn't added to output."""
        result = generate_switcher_json(['v1.0.0'], include_current=False)
        assert len(result) == 1
        assert result[0]['version'] == 'v1.0.0'


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestValidateVersionProgressionDirect:
    """Direct tests for the _validate_version_progression helper."""

    def test_valid_patch_bump(self):
        _validate_version_progression('v1.0.1', 'v1.0.0')

    def test_valid_minor_bump(self):
        _validate_version_progression('v1.1.0', 'v1.0.0')

    def test_valid_major_bump(self):
        _validate_version_progression('v2.0.0', 'v1.0.0')

    def test_older_version_is_noop(self):
        _validate_version_progression('v1.0.0', 'v2.0.0')

    def test_same_version_is_noop(self):
        _validate_version_progression('v1.0.0', 'v1.0.0')

    def test_skipped_patch_raises(self):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            _validate_version_progression('v1.0.3', 'v1.0.0')

    def test_skipped_minor_raises(self):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            _validate_version_progression('v1.3.0', 'v1.0.0')

    def test_skipped_major_raises(self):
        with pytest.raises(ValueError, match="Cannot skip versions"):
            _validate_version_progression('v3.0.0', 'v1.0.0')


# ---------------------------------------------------------------------------
# get_version_from_json
# ---------------------------------------------------------------------------


@pytest.mark.core
@pytest.mark.scripts
@pytest.mark.generate_switcher
class TestGetVersionFromJson:
    """Tests for version.json reading and validation."""

    def test_valid_version_json(self, tmp_path):
        version_file = tmp_path / 'version.json'
        version_file.write_text(json.dumps({"major": 1, "minor": 2, "patch": 3}))

        with patch('generate_switcher.VERSION_JSON', str(version_file)):
            assert get_version_from_json() == 'v1.2.3'

    def test_missing_field_raises(self, tmp_path):
        version_file = tmp_path / 'version.json'
        version_file.write_text(json.dumps({"major": 1, "minor": 2}))

        with patch('generate_switcher.VERSION_JSON', str(version_file)):
            with pytest.raises(ValueError, match="missing required field"):
                get_version_from_json()

    def test_non_numeric_values_raises(self, tmp_path):
        version_file = tmp_path / 'version.json'
        version_file.write_text(json.dumps({"major": "abc", "minor": 0, "patch": 0}))

        with patch('generate_switcher.VERSION_JSON', str(version_file)):
            with pytest.raises(ValueError, match="non-numeric"):
                get_version_from_json()

    def test_negative_values_raises(self, tmp_path):
        version_file = tmp_path / 'version.json'
        version_file.write_text(json.dumps({"major": -1, "minor": 0, "patch": 0}))

        with patch('generate_switcher.VERSION_JSON', str(version_file)):
            with pytest.raises(ValueError, match="negative"):
                get_version_from_json()

    def test_missing_file_returns_none(self):
        with patch('generate_switcher.VERSION_JSON', '/nonexistent/version.json'):
            assert get_version_from_json() is None

    def test_invalid_json_raises(self, tmp_path):
        version_file = tmp_path / 'version.json'
        version_file.write_text('not valid json{{{')

        with patch('generate_switcher.VERSION_JSON', str(version_file)):
            with pytest.raises(ValueError, match="not valid JSON"):
                get_version_from_json()
