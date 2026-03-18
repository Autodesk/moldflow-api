#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate switcher.json for documentation version switcher.

Usage:
    generate_switcher.py [--include-current]

Options:
    --include-current   Include the current version from version.json if it is
                        newer than the latest tag.
"""

import json
import logging
import os
import re
import sys
import docopt
import git
from packaging.version import InvalidVersion, Version


# Must match smv_tag_whitelist in docs/source/conf.py
SMV_TAG_PATTERN = re.compile(r'^v\d+\.\d+\.\d+$')


# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCS_STATIC_DIR = os.path.join(ROOT_DIR, 'docs', 'source', '_static')
SWITCHER_JSON = os.path.join(DOCS_STATIC_DIR, 'switcher.json')
VERSION_JSON = os.path.join(ROOT_DIR, 'version.json')


def get_git_tags():
    """Fetch all git tags from the repository."""
    try:
        repo = git.Repo(ROOT_DIR)
        return [tag.name for tag in repo.tags]
    except git.InvalidGitRepositoryError as err:
        logging.error("Not a valid git repository: %s", err)
        raise
    except git.GitCommandError as err:
        logging.error("Failed to fetch git tags: %s", err)
        raise


def parse_version_tags(tags):
    """
    Filter tags to those matching strict X.Y.Z releases.

    Uses the same pattern as smv_tag_whitelist in docs/source/conf.py
    so that switcher.json stays in sync with the versions that
    sphinx-multiversion actually builds.  Accepts both vX.Y.Z and X.Y.Z.

    Returns the original tag strings (preserving any 'v' prefix).
    """
    version_tags = []

    for tag in tags:
        if not SMV_TAG_PATTERN.match(tag):
            continue

        version_str = tag.lstrip('v')

        try:
            Version(version_str)
            version_tags.append(tag)
        except InvalidVersion:
            logging.warning("Skipping invalid version tag: %s", tag)
            continue

    return version_tags


def get_version_from_json():
    """
    Read version from version.json file.

    Returns version string in format 'vX.Y.Z', or None if the file does not
    exist.  Raises ValueError if the file exists but is invalid (malformed
    JSON, missing fields, non-numeric values, etc.) so that a broken
    version.json is always a hard failure rather than a silent skip.
    """
    try:
        with open(VERSION_JSON, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
    except FileNotFoundError:
        logging.warning("version.json file not found at: %s", VERSION_JSON)
        return None
    except json.JSONDecodeError as err:
        raise ValueError(f"version.json is not valid JSON: {err}") from err

    required_fields = ['major', 'minor', 'patch']
    for field in required_fields:
        if field not in version_data:
            raise ValueError(f"version.json is missing required field: {field}")

    try:
        major = int(version_data['major'])
        minor = int(version_data['minor'])
        patch = int(version_data['patch'])
    except (ValueError, TypeError) as err:
        raise ValueError(
            f"version.json contains non-numeric version values: "
            f"major={version_data.get('major')}, "
            f"minor={version_data.get('minor')}, "
            f"patch={version_data.get('patch')}"
        ) from err

    if major < 0 or minor < 0 or patch < 0:
        raise ValueError(
            f"version.json contains negative version numbers: " f"{major}.{minor}.{patch}"
        )

    version_str = f"v{major}.{minor}.{patch}"

    try:
        Version(version_str.lstrip('v'))
    except InvalidVersion as err:
        raise ValueError(f"Invalid semantic version in version.json: {version_str}") from err

    return version_str


def sort_versions(version_tags):
    """Sort version tags in descending order (latest first)."""

    def version_key(tag):
        try:
            return Version(tag.lstrip('v'))
        except InvalidVersion:
            return Version("0.0.0")

    return sorted(version_tags, key=version_key, reverse=True)


def _validate_version_progression(json_version, latest_tag_version):
    """
    Validate that version.json is a legal next version after the latest tag.

    Raises ValueError if the progression skips versions or violates reset
    rules (e.g. patch must be 0 when bumping minor).
    """
    json_ver = Version(json_version.lstrip('v'))
    tag_ver = Version(latest_tag_version.lstrip('v'))

    if json_ver <= tag_ver:
        return

    j_major, j_minor, j_patch = json_ver.release[:3]
    t_major, t_minor, t_patch = tag_ver.release[:3]

    if j_major == t_major and j_minor == t_minor:
        if j_patch > t_patch + 1:
            logging.error(
                "version.json (%s) skips patch versions from latest "
                "tag (%s). Expected v%d.%d.%d",
                json_version,
                latest_tag_version,
                t_major,
                t_minor,
                t_patch + 1,
            )
            raise ValueError(
                f"Invalid version progression: "
                f"{latest_tag_version} -> {json_version}. "
                f"Cannot skip versions. "
                f"Expected v{t_major}.{t_minor}.{t_patch + 1}"
            )
    elif j_major == t_major and j_minor == t_minor + 1:
        if j_patch != 0:
            logging.error(
                "version.json (%s) has non-zero patch when bumping "
                "minor version. Expected v%d.%d.0",
                json_version,
                j_major,
                j_minor,
            )
            raise ValueError(
                f"Invalid version: {json_version}. "
                f"When bumping minor version from "
                f"{latest_tag_version}, patch must be 0. "
                f"Expected v{j_major}.{j_minor}.0"
            )
    elif j_major == t_major and j_minor > t_minor + 1:
        logging.error(
            "version.json (%s) skips minor versions from latest " "tag (%s). Expected v%d.%d.0",
            json_version,
            latest_tag_version,
            t_major,
            t_minor + 1,
        )
        raise ValueError(
            f"Invalid version progression: "
            f"{latest_tag_version} -> {json_version}. "
            f"Cannot skip versions. "
            f"Expected v{t_major}.{t_minor + 1}.0"
        )
    elif j_major == t_major + 1:
        if j_minor != 0 or j_patch != 0:
            logging.error(
                "version.json (%s) has non-zero minor/patch when "
                "bumping major version. Expected v%d.0.0",
                json_version,
                j_major,
            )
            raise ValueError(
                f"Invalid version: {json_version}. "
                f"When bumping major version from "
                f"{latest_tag_version}, minor and patch must be 0. "
                f"Expected v{j_major}.0.0"
            )
    elif j_major > t_major + 1:
        logging.error(
            "version.json (%s) skips major versions from latest " "tag (%s). Expected v%d.0.0",
            json_version,
            latest_tag_version,
            t_major + 1,
        )
        raise ValueError(
            f"Invalid version progression: "
            f"{latest_tag_version} -> {json_version}. "
            f"Cannot skip versions. "
            f"Expected v{t_major + 1}.0.0"
        )


def generate_switcher_json(version_tags, include_current=False):
    """
    Generate the switcher.json structure.

    Returns a list of version entries with the format expected by
    pydata-sphinx-theme's version switcher.

    Always reads version.json and validates its progression against the
    latest git tag (to catch skipped versions early, even in CI).
    When include_current is True and version.json is newer than the latest
    tag, that version is also added to the switcher output.
    """
    if not version_tags:
        logging.warning("No version tags found!")
        return []

    sorted_tags = sort_versions(version_tags)
    switcher_data = []

    latest_tag_version = sorted_tags[0]
    json_version = get_version_from_json()

    add_json_version = False
    if json_version and latest_tag_version:
        try:
            json_ver = Version(json_version.lstrip('v'))
            tag_ver = Version(latest_tag_version.lstrip('v'))
            version_json_is_newer = json_ver > tag_ver

            if version_json_is_newer:
                _validate_version_progression(json_version, latest_tag_version)
                if include_current:
                    add_json_version = True

        except InvalidVersion:
            pass

    if add_json_version:
        logging.info(
            "version.json (%s) is newer than latest tag (%s), " "adding as latest",
            json_version,
            latest_tag_version,
        )
        switcher_data.append(
            {
                "version": json_version,
                "name": f"{json_version} (latest)",
                "url": f"../{json_version}/",
                "is_latest": True,
            }
        )

    for i, tag in enumerate(sorted_tags):
        is_latest = (i == 0) and not add_json_version

        switcher_data.append(
            {
                "version": tag,
                "name": f"{tag} (latest)" if is_latest else tag,
                "url": f"../{tag}/",
                "is_latest": is_latest,
            }
        )

    return switcher_data


def write_switcher_json(switcher_data):
    """Write the switcher data to switcher.json file."""
    # Ensure the directory exists
    os.makedirs(DOCS_STATIC_DIR, exist_ok=True)

    with open(SWITCHER_JSON, 'w', encoding='utf-8') as f:
        json.dump(switcher_data, f, indent=2)

    logging.info("Generated switcher.json with %d versions", len(switcher_data))
    logging.info("Latest version: %s", switcher_data[0]['version'] if switcher_data else 'None')


def main():
    """Main entry point."""
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    args = docopt.docopt(__doc__)
    include_current = args.get('--include-current')

    try:
        logging.info("Fetching git tags...")
        tags = get_git_tags()

        if not tags:
            logging.error("No git tags found in the repository!")
            return 1

        logging.info("Found %d total tags", len(tags))

        logging.info("Parsing version tags...")
        version_tags = parse_version_tags(tags)

        if not version_tags:
            logging.error("No valid version tags found!")
            return 1

        logging.info("Found %d version tags", len(version_tags))

        logging.info("Generating switcher.json...")
        switcher_data = generate_switcher_json(version_tags, include_current=include_current)

        logging.info("Writing switcher.json to %s", SWITCHER_JSON)
        write_switcher_json(switcher_data)

        logging.info("Successfully generated switcher.json!")
        return 0

    except Exception as err:
        logging.error("Failed to generate switcher.json: %s", err, exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
