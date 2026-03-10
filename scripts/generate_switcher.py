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
import subprocess
import sys
import docopt
from packaging.version import InvalidVersion, Version


# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCS_STATIC_DIR = os.path.join(ROOT_DIR, 'docs', 'source', '_static')
SWITCHER_JSON = os.path.join(DOCS_STATIC_DIR, 'switcher.json')
VERSION_JSON = os.path.join(ROOT_DIR, 'version.json')


def get_git_tags():
    """Fetch all git tags from the repository."""
    try:
        result = subprocess.run(
            ['git', 'tag', '-l'], cwd=ROOT_DIR, capture_output=True, text=True, check=True
        )
        tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
        return tags
    except subprocess.CalledProcessError as err:
        logging.error("Failed to fetch git tags: %s", err)
        raise


def parse_version_tags(tags):
    """
    Parse version tags and return a list of valid version strings.

    Filters tags that start with 'v' and can be parsed as valid versions.
    """
    version_tags = []

    for tag in tags:
        if not tag.startswith('v'):
            continue

        version_str = tag[1:]  # Remove 'v' prefix

        try:
            # Validate that it's a proper version
            Version(version_str)
            version_tags.append(tag)
        except InvalidVersion:
            logging.warning("Skipping invalid version tag: %s", tag)
            continue

    return version_tags


def get_version_from_json():
    """
    Read version from version.json file.

    Returns version string in format 'vX.Y.Z' or None if file doesn't exist.
    """
    try:
        with open(VERSION_JSON, 'r', encoding='utf-8') as f:
            version_data = json.load(f)

        # Validate that major, minor, patch exist and are valid
        required_fields = ['major', 'minor', 'patch']
        for field in required_fields:
            if field not in version_data:
                logging.error("version.json is missing required field: %s", field)
                return None

        # Validate that values can be converted to integers
        try:
            major = int(version_data['major'])
            minor = int(version_data['minor'])
            patch = int(version_data['patch'])

            # Validate they are non-negative
            if major < 0 or minor < 0 or patch < 0:
                logging.error(
                    "version.json contains negative version numbers: %s.%s.%s", major, minor, patch
                )
                return None

        except (ValueError, TypeError) as err:
            logging.error(
                "version.json contains non-numeric version values: major=%s, minor=%s, patch=%s. Error: %s",
                version_data.get('major'),
                version_data.get('minor'),
                version_data.get('patch'),
                err,
            )
            return None

        version_str = f"v{major}.{minor}.{patch}"

        # Validate it's a proper semantic version
        try:
            Version(version_str.lstrip('v'))
            return version_str
        except InvalidVersion as err:
            logging.error(
                "Invalid semantic version in version.json: %s. Error: %s", version_str, err
            )
            return None

    except FileNotFoundError:
        logging.warning("version.json file not found at: %s", VERSION_JSON)
        return None
    except KeyError as err:
        logging.error("version.json is missing required field: %s", err)
        return None
    except json.JSONDecodeError as err:
        logging.error("version.json is not valid JSON: %s", err)
        return None


def sort_versions(version_tags):
    """Sort version tags in descending order (latest first)."""

    def version_key(tag):
        try:
            return Version(tag.lstrip('v'))
        except InvalidVersion:
            return Version("0.0.0")

    return sorted(version_tags, key=version_key, reverse=True)


def generate_switcher_json(version_tags, include_current=False):
    """
    Generate the switcher.json structure.

    Returns a list of version entries with the format expected by
    pydata-sphinx-theme's version switcher.

    When include_current is True, checks version.json to see if there's a
    newer version that hasn't been tagged yet (e.g., working on a branch/PR).
    If so, that version is added as the latest at the top of the list.
    """
    if not version_tags:
        logging.warning("No version tags found!")
        return []

    sorted_tags = sort_versions(version_tags)
    switcher_data = []

    version_json_is_newer = False
    json_version = None
    latest_tag_version = sorted_tags[0] if sorted_tags else None

    if include_current:
        json_version = get_version_from_json()

    if json_version and latest_tag_version:
        try:
            json_ver = Version(json_version.lstrip('v'))
            tag_ver = Version(latest_tag_version.lstrip('v'))
            version_json_is_newer = json_ver > tag_ver

            # Check if version.json is skipping versions (this is an ERROR)
            if version_json_is_newer:
                # Parse version components to check for skipped versions
                json_parts = str(json_ver).split('.')
                tag_parts = str(tag_ver).split('.')

                if len(json_parts) >= 3 and len(tag_parts) >= 3:
                    j_major, j_minor, j_patch = (
                        int(json_parts[0]),
                        int(json_parts[1]),
                        int(json_parts[2]),
                    )
                    t_major, t_minor, t_patch = (
                        int(tag_parts[0]),
                        int(tag_parts[1]),
                        int(tag_parts[2]),
                    )

                    # Check if we're skipping versions inappropriately
                    if j_major == t_major and j_minor == t_minor:
                        # Same major.minor, check patch difference
                        if j_patch > t_patch + 1:
                            logging.error(
                                "version.json (%s) skips patch versions from latest tag (%s). "
                                "Expected next version would be v%d.%d.%d",
                                json_version,
                                latest_tag_version,
                                t_major,
                                t_minor,
                                t_patch + 1,
                            )
                            raise ValueError(
                                f"Invalid version progression: {latest_tag_version} -> {json_version}. "
                                f"Cannot skip versions. Expected v{t_major}.{t_minor}.{t_patch + 1}"
                            )
                    elif j_major == t_major and j_minor == t_minor + 1:
                        # Valid minor bump, but patch must be 0
                        if j_patch != 0:
                            logging.error(
                                "version.json (%s) has non-zero patch when bumping minor version. "
                                "When incrementing minor version, patch must reset to 0. Expected v%d.%d.0",
                                json_version,
                                j_major,
                                j_minor,
                            )
                            raise ValueError(
                                f"Invalid version: {json_version}. "
                                f"When bumping minor version from {latest_tag_version}, patch must be 0. Expected v{j_major}.{j_minor}.0"
                            )
                    elif j_major == t_major and j_minor > t_minor + 1:
                        # Skipping minor versions
                        logging.error(
                            "version.json (%s) skips minor versions from latest tag (%s). "
                            "Expected next version would be v%d.%d.0",
                            json_version,
                            latest_tag_version,
                            t_major,
                            t_minor + 1,
                        )
                        raise ValueError(
                            f"Invalid version progression: {latest_tag_version} -> {json_version}. "
                            f"Cannot skip versions. Expected v{t_major}.{t_minor + 1}.0"
                        )
                    elif j_major == t_major + 1:
                        # Valid major bump, but minor and patch must be 0
                        if j_minor != 0 or j_patch != 0:
                            logging.error(
                                "version.json (%s) has non-zero minor/patch when bumping major version. "
                                "When incrementing major version, minor and patch must reset to 0. Expected v%d.0.0",
                                json_version,
                                j_major,
                            )
                            raise ValueError(
                                f"Invalid version: {json_version}. "
                                f"When bumping major version from {latest_tag_version}, minor and patch must be 0. Expected v{j_major}.0.0"
                            )
                    elif j_major > t_major + 1:
                        # Skipping major versions
                        logging.error(
                            "version.json (%s) skips major versions from latest tag (%s). "
                            "Expected next version would be v%d.0.0",
                            json_version,
                            latest_tag_version,
                            t_major + 1,
                        )
                        raise ValueError(
                            f"Invalid version progression: {latest_tag_version} -> {json_version}. "
                            f"Cannot skip versions. Expected v{t_major + 1}.0.0"
                        )

        except InvalidVersion:
            pass

    # If version.json has a newer version, add it as the latest
    if version_json_is_newer:
        logging.info(
            "version.json (%s) is newer than latest tag (%s), adding as latest",
            json_version,
            latest_tag_version,
        )
        entry = {
            "version": json_version,
            "name": f"{json_version} (latest)",
            "url": f"../{json_version}/",
            "is_latest": True,
        }
        switcher_data.append(entry)

    # Add all tagged versions
    for i, tag in enumerate(sorted_tags):
        # If version.json was added as latest, no tag is latest
        # Otherwise, the first tag (index 0) is latest
        is_latest = (i == 0) and not version_json_is_newer

        entry = {
            "version": tag,
            "name": f"{tag} (latest)" if is_latest else tag,
            "url": f"../{tag}/",
            "is_latest": is_latest,
        }

        switcher_data.append(entry)

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
