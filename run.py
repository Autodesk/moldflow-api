#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302

"""
Usage:
    run.py clean-up
    run.py build [-P | --publish] [-i | --install]
    run.py build-docs [-t <target> | --target=<target>] [-s | --skip-build] [-l | --local]
        [--skip-switcher] [--include-current] [--incremental]
    run.py format [--check]
    run.py generate-expected-data [<markers>...]
    run.py generate-switcher [--include-current]
    run.py install [-s | --skip-build]
    run.py install-package-requirements
    run.py lint [-s | --skip-build]
    run.py publish [-s | --skip-build] [(--testpypi | --repo-url=<url>)]
    run.py release [--github-api-url=<url>]
    run.py report [-c | --cli] [-h | --html] [-x | --xml]
    run.py test [<tests>...] [-m <marker> | --marker=<marker>] [-s | --skip-build]
        [-k | --keep-files] [-q | --quiet] [--unit] [--integration] [--core] [--all]

Commands:
    clean-up                        Clean up build artifacts.
    build                           Build and optionally publish the moldflow-api package.
    build-docs                      Build the documentation.
    format                          Format all Python files in the repository using black.
    generate-expected-data          Generate expected data for integration tests.
    generate-switcher               Generate switcher.json from git tags (vX.Y.Z format).
    install                         Install the moldflow-api package.
    install-package-requirements    Install package dependencies.
    lint                            Lint all Python files in the repository.
    publish                         Publish the package to PyPI or TestPyPI.
    release                         Create a Git tag and GitHub release using PyGithub.
    report                          Generate coverage reports.
    test                            Run unit and integration tests.

Options:
    -s, --skip-build                Skip building the package before running the command.
    -k, --keep-files                Keep the coverage file after running tests.
    -q, --quiet                     Run tests with minimal output,
                                    showing only test names and status.
    --check                         Check the code formatting without making changes.
    -i, --install                   Install the package after building.
    -m, --marker=<marker>           Run only tests with the specified marker.
    <marker>                        Marker to filter tests by: unit, integration, core.
    -t, --target=<target>           Documentation target format [default: html].
    <tests>                         Test files, directories, or functions to run.
    -c, --cli                       Generate a CLI coverage report.
    -h, --html                      Generate an HTML coverage report.
    -x, --xml                       Generate an XML coverage report.
    --core                          Run only core tests.
    --unit                          Run only unit tests.
    --integration                   Run only integration tests.
    --all                           Run all tests.
    --repo-url=<url>                Custom PyPI repository URL.
    --github-api-url=<url>          Custom GitHub API URL.
    -l, --local                     Build documentation locally (single version).
    --skip-switcher                 Skip generating switcher.json for documentation.
    --include-current               Build current working tree version from version.json
                                    (useful during development before tagging).
    --incremental                   Only build versions that don't have existing output directories
                                    (speeds up development by skipping already-built versions).
    <markers>                       Markers to filter data generation by: mesh_summary, etc.
"""

import os
import re
import sys
import json
import logging
import platform
import subprocess
import shutil
import glob
from urllib.parse import urlparse
import docopt
import git as gitpython
from github import Github
import polib
from packaging.version import InvalidVersion, Version

WINDOWS = platform.system() == 'Windows'
ENCODING = 'utf-8'
SITE_PACKAGES = 'moldflow-site-packages'
VERSION_JSON = 'version.json'
VERSION = ''

# FILE TYPES
PY_FILES_EXT = '.py'
PO_FILES_EXT = '.po'
MO_FILES_EXT = '.mo'

# Directory Paths
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
GIT_REPO = gitpython.Repo(ROOT_DIR)
MOLDFLOW_DIR = os.path.join(ROOT_DIR, 'src', 'moldflow')
TEST_DIR = os.path.join(ROOT_DIR, 'tests')
LOCALE_DIR = os.path.join(MOLDFLOW_DIR, 'locale')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')
DOCS_SOURCE_DIR = os.path.join(DOCS_DIR, 'source')
DOCS_STATIC_DIR = os.path.join(DOCS_SOURCE_DIR, '_static')
DOCS_BUILD_DIR = os.path.join(DOCS_DIR, 'build')
DOCS_HTML_DIR = os.path.join(DOCS_BUILD_DIR, 'html')
COVERAGE_HTML_DIR = os.path.join(ROOT_DIR, 'htmlcov')
DIST_DIR = os.path.join(ROOT_DIR, 'dist')

# Files
PYLINT_CONFIG_FILE = os.path.join(ROOT_DIR, '.pylint.toml')
SETUP_CONFIG_FILE = os.path.join(ROOT_DIR, 'setup.cfg')
SETUP_CONFIG_IN_FILE = os.path.join(ROOT_DIR, 'setup.cfg.in')
COVERAGE_FILE = os.path.join(ROOT_DIR, '.coverage')
COVERAGE_CONFIG_FILE = os.path.join(ROOT_DIR, '.coverage-config')
COVERAGE_XML_FILE_NAME = 'coverage.xml'
VERSION_FILE = os.path.join(ROOT_DIR, VERSION_JSON)
DIST_FILES = os.path.join(ROOT_DIR, 'dist', '*')
PYTHON_FILES = [MOLDFLOW_DIR, DOCS_SOURCE_DIR, TEST_DIR, "run.py"]
SWITCHER_JSON = os.path.join(DOCS_STATIC_DIR, 'switcher.json')

# Must match smv_tag_whitelist in docs/source/conf.py
VERSION_TAG_RE = re.compile(r'^v\d+\.\d+\.\d+$')


def _is_version_tag(name):
    """Return True if *name* matches the vX.Y.Z version tag format."""
    return VERSION_TAG_RE.match(name) is not None


def run_command(args, cwd=os.getcwd(), extra_env=None):
    """Runs native executable command, args is an array of strings"""

    logging.info(
        "Running command: '%s' in '%s'%s",
        ' '.join(args),
        cwd,
        f' with extra env: {extra_env}' if extra_env else '',
    )

    command_env = {**os.environ, **extra_env} if extra_env else os.environ

    with subprocess.Popen(args, cwd=cwd, shell=WINDOWS, env=command_env) as proc:
        proc.wait()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, ' '.join(args))


def build_package(install=True):
    """Build package"""

    logging.info('Attempting to build moldflow-api package')

    build_mo()

    with open(SETUP_CONFIG_IN_FILE, 'r', encoding=ENCODING) as f:
        template = f.read()

    output = template.format(VERSION=VERSION)

    with open(SETUP_CONFIG_FILE, 'w', encoding=ENCODING) as f:
        f.write(output)

    try:
        run_command([sys.executable] + '-m build'.split(' '), ROOT_DIR)
    except Exception as err:
        logging.error(
            "Failed to build package: '%s'.\n"
            'Error: %s\n'
            'You may need to run `git clean -fXd` to clean up your repository',
            ROOT_DIR,
            err,
        )

    if install:
        install_package()


def publish(skip_build=False, testpypi=False, repo_url=None):
    """Publish package"""

    # Restrict publishing to GitHub Actions workflow
    if os.environ.get('GITHUB_ACTIONS') != 'true' and not testpypi:
        raise RuntimeError(
            'Publishing to PyPI is restricted to the GitHub Actions manual workflow.'
            'Please use the "Publish to PyPI (manual)" workflow.'
        )
    # Defensive check: don't allow both testpypi and explicit repo_url
    if testpypi and repo_url:
        raise RuntimeError('Options testpypi and repo_url are mutually exclusive.')

    if not skip_build:
        build_package()

    logging.info('Attempting to publish moldflow-api package to PyPI')

    # First check the package
    logging.info('Checking package validity')

    # Expand distribution files using glob to avoid shell globbing
    dist_files_list = glob.glob(DIST_FILES)
    if not dist_files_list:
        raise RuntimeError(f'No distribution files found in {DIST_DIR}')

    # Use explicit args to avoid shell interpolation for the check step
    run_command([sys.executable, '-m', 'twine', 'check', '--strict'] + dist_files_list, ROOT_DIR)

    logging.info('Package is valid')

    # Validate repo URL if provided
    if repo_url:
        parsed = urlparse(repo_url)
        # Only allow secure HTTPS URLs for repository uploads
        if parsed.scheme != 'https' or not parsed.netloc:
            raise RuntimeError(f'Invalid repository URL: {repo_url}. Only HTTPS URLs are allowed.')

    # Build twine upload args safely as a list
    twine_cmd = [sys.executable, '-m', 'twine', 'upload', '--verbose']

    if repo_url:
        twine_cmd += ['--repository-url', repo_url]
    elif testpypi:
        twine_cmd += ['--repository', 'testpypi']

    twine_cmd += dist_files_list

    run_command(
        twine_cmd,
        ROOT_DIR,
        {
            'TWINE_USERNAME': os.environ.get('TWINE_USERNAME', ''),
            'TWINE_PASSWORD': os.environ.get('TWINE_PASSWORD', ''),
        },
    )


def create_release(github_api_url=None):
    """
    Create Git tag and GitHub release via PyGithub.

    Uses environment variables:
    - GITHUB_TOKEN
    - GITHUB_REPOSITORY (owner/repo)
    - GITHUB_SHA (target commit)
    """

    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN not set')

    owner_repo = os.environ.get('GITHUB_REPOSITORY')
    if not owner_repo:
        raise RuntimeError('GITHUB_REPOSITORY not set')

    target_sha = os.environ.get('GITHUB_SHA')
    if not target_sha:
        # Fallback to HEAD when running locally
        target_sha = GIT_REPO.git.rev_parse('HEAD').decode().strip()

    tag = f'v{VERSION}'
    release_name = tag

    logging.info('Creating GitHub release %s on %s', tag, owner_repo)

    if github_api_url:
        logging.info('Using custom GitHub API URL: %s', github_api_url)
        gh = Github(token, base_url=github_api_url)
    else:
        gh = Github(token)

    repo = gh.get_repo(owner_repo)

    release = repo.create_git_tag_and_release(
        tag=tag,
        tag_message=release_name,
        release_name=release_name,
        release_message='',
        object=target_sha,
        type='commit',
        draft=False,
        prerelease=False,
        generate_release_notes=True,
        make_latest='true',
    )

    # Upload artifacts from dist if present
    dist_dir = os.path.join(ROOT_DIR, 'dist')
    if os.path.isdir(dist_dir):
        for name in os.listdir(dist_dir):
            full_path = os.path.join(dist_dir, name)
            if os.path.isfile(full_path):
                logging.info('Uploading asset %s', name)
                with open(full_path, 'rb') as fd:
                    _data = fd.read()
                    release.upload_asset_from_memory(
                        _data,
                        name=name,
                        label=name,
                        content_type='application/octet-stream',
                        file_size=len(_data),
                    )

    logging.info('Release %s created', tag)
    return release


def install_package(target_path=None, build=False):
    """Install moldflow-api package"""

    if build:
        build_package(install=False)

    logging.info('Attempting to install moldflow-api')

    wheel_path = os.path.join(ROOT_DIR, 'dist', f'moldflow-{VERSION}-py3-none-any.whl')

    pip_args = f'install --force-reinstall --upgrade {wheel_path}'
    if target_path:
        pip_args = f'{pip_args} --target={target_path}'

    run_command([sys.executable] + f'-m pip {pip_args}'.split(' '), ROOT_DIR)


def build_mo():
    """Build Localisation Files"""

    logging.info('Attempting to build .mo files')

    try:
        for root, _, files in os.walk(LOCALE_DIR):
            for file in files:
                if file.endswith(PO_FILES_EXT):
                    locale_name = os.path.basename(os.path.dirname(root))
                    logging.info('Building .mo file for %s', locale_name)
                    po_file = os.path.join(root, file)
                    mo_file = po_file.replace(PO_FILES_EXT, MO_FILES_EXT)
                    po = polib.pofile(po_file)
                    po.save_as_mofile(mo_file)

        logging.info('.mo files built successfully.')
    except Exception as err:
        logging.error(
            "Failed to build .mo files: '%s'.\n"
            'Error: %s\n'
            'You may need to check your locale directory.',
            ROOT_DIR,
            err,
        )


def create_root_redirect(build_output: str) -> None:
    """Create an index.html in the versioned HTML build output root that redirects to /latest/."""
    index_path = os.path.join(build_output, 'index.html')
    redirect_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting to latest documentation...</title>
    <meta http-equiv="refresh" content="0; url=./latest/">
    <link rel="canonical" href="./latest/">
    <script>window.location.replace("./latest/");</script>
</head>
<body>
    <p>Redirecting to <a href="./latest/">latest documentation</a>...</p>
</body>
</html>
"""
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(redirect_html)
        logging.info("Created root redirect: index.html -> latest/")
    except Exception as err:
        logging.warning("Could not create root redirect index.html: %s", err)


def create_latest_alias(build_output: str) -> None:
    """Create a 'latest' alias pointing to the newest version using symlinks when possible."""
    version_dirs = [d for d in os.listdir(build_output) if _is_version_tag(d)]
    if not version_dirs:
        return

    def version_key(v):
        try:
            return Version(v.lstrip('v'))
        except InvalidVersion:
            return Version("0.0.0")

    sorted_versions = sorted(version_dirs, key=version_key, reverse=True)
    latest_version = sorted_versions[0]
    latest_src = os.path.join(build_output, latest_version)
    latest_dest = os.path.join(build_output, 'latest')

    # Verify source exists before proceeding
    if not os.path.exists(latest_src):
        logging.error("Source directory for 'latest' alias does not exist: %s", latest_src)
        return

    # Clean up any existing 'latest' entry first
    if os.path.islink(latest_dest):
        os.unlink(latest_dest)
    elif os.path.isdir(latest_dest):
        shutil.rmtree(latest_dest)
    elif os.path.exists(latest_dest):
        os.remove(latest_dest)

    # Try creating a symbolic link first (most efficient)
    logging.info("Creating 'latest' alias for %s", latest_version)
    try:
        os.symlink(latest_src, latest_dest, target_is_directory=True)
        logging.info("Created symbolic link: latest -> %s", latest_version)
    except (OSError, NotImplementedError) as err:
        # Fall back to copying if symlinks aren't supported
        logging.warning(
            "Could not create symbolic link for 'latest' alias (%s); "
            "falling back to copying documentation.",
            err,
        )
        shutil.copytree(latest_src, latest_dest)


def _build_html_docs_full(build_output, skip_switcher, include_current):
    """Build all tagged HTML docs using sphinx-multiversion."""
    if not skip_switcher:
        generate_switcher(include_current=include_current)

    try:
        # fmt: off
        run_command(
            [
                sys.executable, '-m', 'sphinx_multiversion',
                DOCS_SOURCE_DIR, build_output
            ],
            ROOT_DIR,
        )
    except Exception as err:
        logging.error(
            "Failed to build documentation with "
            "sphinx_multiversion.\n"
            "This can happen if no Git tags or branches match "
            "the required vX.Y.Z version pattern.\n"
            "Try running 'git fetch --tags' and ensure version "
            "tags (e.g. v1.2.3) exist in the repo.\n"
            "Underlying error: %s",
            str(err),
        )
        raise
    # fmt: on


def _get_missing_version_tags(build_output):
    """Return version tags that have no existing build output directory."""
    existing_versions = set()
    if os.path.exists(build_output):
        for item in os.listdir(build_output):
            item_path = os.path.join(build_output, item)
            if os.path.isdir(item_path) and _is_version_tag(item):
                existing_versions.add(item)

    all_tags = {tag.name for tag in GIT_REPO.tags if _is_version_tag(tag.name)}

    missing = list(all_tags - existing_versions)

    if missing:
        logging.info(
            'Incremental build: found %d existing versions, %d tags need building: %s',
            len(existing_versions),
            len(missing),
            ', '.join(sorted(missing)),
        )
    else:
        logging.info(
            'Incremental build: all %d tagged versions already built, skipping tag builds',
            len(all_tags),
        )

    return missing


def _check_clean_working_tree():
    """Raise if the git working tree has uncommitted changes."""
    if GIT_REPO.is_dirty(untracked_files=True):
        raise RuntimeError(
            "Incremental docs build requires a clean working tree. "
            "Please commit or stash your changes first."
        )


def _build_tags_incrementally(missing_tags, build_output):
    """Check out each missing tag, build its docs, then restore the original ref."""
    logging.info('Building %d missing version(s) incrementally...', len(missing_tags))

    # Capture the branch name if on a branch, otherwise fall back to the
    # commit SHA so we can reliably restore even from a detached HEAD.
    if GIT_REPO.head.is_detached:
        original_ref = GIT_REPO.head.commit.hexsha
    else:
        original_ref = GIT_REPO.active_branch.name

    os.makedirs(build_output, exist_ok=True)

    try:
        for tag in sorted(missing_tags):
            logging.info('Checking out and building tag: %s', tag)
            GIT_REPO.git.checkout(tag)
            tag_output = os.path.join(build_output, tag)
            run_command(
                [sys.executable, '-m', 'sphinx', '-b', 'html', DOCS_SOURCE_DIR, tag_output],
                ROOT_DIR,
            )
            logging.info('Successfully built documentation for %s', tag)
    finally:
        if original_ref:
            logging.info('Restoring original ref: %s', original_ref)
            GIT_REPO.git.checkout(original_ref)


def _distribute_switcher_json(build_output):
    """Copy switcher.json into every version directory under build_output."""
    switcher_src = os.path.join(ROOT_DIR, 'docs', 'source', '_static', 'switcher.json')
    if not os.path.exists(switcher_src):
        logging.warning('switcher.json not found at %s, skipping distribution', switcher_src)
        return

    if not os.path.exists(build_output):
        return

    for item in os.listdir(build_output):
        item_path = os.path.join(build_output, item)
        if not os.path.isdir(item_path):
            continue
        static_dir = os.path.join(item_path, '_static')
        if os.path.isdir(static_dir):
            dest = os.path.join(static_dir, 'switcher.json')
            shutil.copy2(switcher_src, dest)

    logging.info('Distributed switcher.json to all version directories')


def _build_html_docs_incremental(build_output, skip_switcher, include_current):
    """Build HTML docs incrementally: tags, then switcher, then current version."""
    missing_tags = _get_missing_version_tags(build_output)
    if missing_tags:
        _check_clean_working_tree()
        _build_tags_incrementally(missing_tags, build_output)

    if not skip_switcher:
        generate_switcher(include_current=include_current)

    if include_current:
        logging.info('Checking if current version needs to be built...')
        current_version = _get_current_version_if_newer()
        if current_version:
            version_output = os.path.join(build_output, current_version)
            if os.path.exists(version_output):
                logging.info(
                    'Incremental build: current version %s already exists, skipping',
                    current_version,
                )
            else:
                logging.info('Building documentation for current version: %s', current_version)
                run_command(
                    [sys.executable, '-m', 'sphinx', '-b', 'html', DOCS_SOURCE_DIR, version_output],
                    ROOT_DIR,
                )
                logging.info('Current version docs built at %s', version_output)

    if not skip_switcher:
        _distribute_switcher_json(build_output)


# pylint: disable=R0913, R0917
def _run_sphinx_build(target):
    """Run a standard single-version Sphinx build."""
    run_command(
        [sys.executable, '-m', 'sphinx', 'build', '-M', target, DOCS_SOURCE_DIR, DOCS_BUILD_DIR],
        ROOT_DIR,
    )


def _remove_stale_switcher():
    """Remove leftover switcher.json from the source tree.

    Prevents Sphinx from copying a stale version switcher into the build
    output when no version tags exist to populate it.
    """
    if os.path.exists(SWITCHER_JSON):
        os.remove(SWITCHER_JSON)
        logging.info('Removed stale %s', SWITCHER_JSON)


def _clean_multiversion_artifacts(build_output):
    """Selectively remove multi-version artifacts from a previous build.

    Removes vX.Y.Z/ directories, the latest/ alias, the root redirect
    index.html, and any distributed switcher.json copies while preserving
    single-version Sphinx output so that incremental builds remain effective.
    """
    if not os.path.isdir(build_output):
        return

    removed = []

    for item in os.listdir(build_output):
        item_path = os.path.join(build_output, item)
        if os.path.isdir(item_path) and _is_version_tag(item):
            shutil.rmtree(item_path)
            removed.append(item)

    latest_path = os.path.join(build_output, 'latest')
    if os.path.islink(latest_path):
        os.unlink(latest_path)
        removed.append('latest (symlink)')
    elif os.path.isdir(latest_path):
        shutil.rmtree(latest_path)
        removed.append('latest')

    redirect = os.path.join(build_output, 'index.html')
    if os.path.isfile(redirect):
        os.remove(redirect)
        removed.append('index.html')

    for switcher in glob.glob(
        os.path.join(build_output, '**', '_static', 'switcher.json'), recursive=True
    ):
        os.remove(switcher)
        removed.append(os.path.relpath(switcher, build_output))

    if removed:
        logging.info(
            'Cleaned multi-version artifacts from %s: %s', build_output, ', '.join(removed)
        )


# pylint: disable=R0912
def build_docs(
    target, skip_build, local=False, skip_switcher=False, include_current=False, incremental=False
):
    """Build Documentation"""

    if not skip_build:
        build_package()

    logging.info('Attempting to build moldflow-api documentation')

    if not incremental:
        logging.info('Removing existing Sphinx documentation...')
        if os.path.exists(DOCS_BUILD_DIR):
            shutil.rmtree(DOCS_BUILD_DIR)
    else:
        logging.info('Incremental build mode: preserving existing documentation...')

    try:
        has_version_tags = any(_is_version_tag(tag.name) for tag in GIT_REPO.tags)

        if target == 'html' and not local and has_version_tags:
            build_output = os.path.join(DOCS_BUILD_DIR, 'html')

            if incremental:
                _build_html_docs_incremental(build_output, skip_switcher, include_current)
            else:
                _build_html_docs_full(build_output, skip_switcher, include_current)

            create_latest_alias(build_output)
            create_root_redirect(build_output)
        elif target == 'html' and not local and not has_version_tags:
            logging.warning(
                'No version tags matching vX.Y.Z found in the repository. '
                'Falling back to a single-version documentation build.'
            )
            if not skip_switcher:
                _remove_stale_switcher()
            _clean_multiversion_artifacts(os.path.join(DOCS_BUILD_DIR, 'html'))
            _run_sphinx_build(target)
        else:
            if target == 'html' and not skip_switcher:
                if has_version_tags:
                    generate_switcher(include_current=include_current)
                else:
                    logging.warning(
                        'No version tags matching vX.Y.Z found in the repository. '
                        'Skipping switcher.json generation.'
                    )
                    _remove_stale_switcher()
            _run_sphinx_build(target)
        logging.info('Sphinx documentation built successfully.')
    except Exception as err:
        logging.error(
            "Failed to build Sphinx documentation: '%s'.\n"
            'Error: %s\n'
            'You may need to check your Sphinx configuration.',
            ROOT_DIR,
            str(err),
        )
        raise


def format_code(check_only=False):
    """Format all python files in the repository using black"""

    logging.info('Attempting to format python files using black in repo')

    check_args = '--check ' if check_only else ''

    python_files = ' '.join(PYTHON_FILES)

    formatter_args = f'--line-length=100 -S -C {python_files}'

    run_command([sys.executable] + f'-m black {check_args}{formatter_args}'.split(' '), ROOT_DIR)


def lint(skip_build):
    """Lint all python files in the repository"""

    format_code(check_only=True)

    if not skip_build:
        build_package()

    logging.info('Attempting to lint python files in repo')

    python_files = ' '.join(PYTHON_FILES)

    pylint_args = f'--rcfile {PYLINT_CONFIG_FILE} --verbose {python_files}'

    run_command([sys.executable] + f'-m pylint {pylint_args}'.split(' '), ROOT_DIR)


class Report:
    """
    Generate reports for coverage

    Report.cli()        Generates  CLI report
    Report.html()       Generates  HTML report
    Report.xml()        Generates  XML report
    """

    coverage_config_file_arg = f"--rcfile={COVERAGE_CONFIG_FILE}"

    @staticmethod
    def cli():
        """Generate CLI report"""
        run_command(
            [sys.executable] + f'-m coverage report {Report.coverage_config_file_arg}'.split(' '),
            ROOT_DIR,
        )

    @staticmethod
    def html():
        """Generate HTML report"""
        run_command(
            [sys.executable] + f'-m coverage html {Report.coverage_config_file_arg}'.split(' '),
            ROOT_DIR,
        )

    @staticmethod
    def xml():
        """Generate XML report"""
        coverage_xml_file_arg = f"-o {COVERAGE_XML_FILE_NAME}"
        run_command(
            [sys.executable]
            + f'-m coverage xml {coverage_xml_file_arg} {Report.coverage_config_file_arg}'.split(
                ' '
            ),
            ROOT_DIR,
        )


class Test:
    """
    Run Tests

    Test.core_tests(tests)            Run core tests
    Test.unit_tests(tests)            Run unit tests
    Test.integration_tests(tests)     Run integration tests
    Test.all_tests(tests)       Run all tests
    Test.custom_tests(marker, tests)  Run custom tests with a specific marker
    """

    @staticmethod
    def _run_marker(marker, tests, quiet=False):

        coverage_config_file_arg = f"--rcfile={COVERAGE_CONFIG_FILE}"

        verbosity = '-v' if quiet else '-rA -vv'
        pytest_options = f'{verbosity} --override-ini=console_output_style=count'

        test_targets = " ".join(tests) if tests else ROOT_DIR
        marker_option = f"-m {marker}" if marker else ""

        pytest_args = f"{pytest_options} {marker_option} {test_targets}".strip()

        coverage_args = f'coverage run -p {coverage_config_file_arg} -m pytest {pytest_args}'

        run_command([sys.executable] + f'-m {coverage_args}'.split(' '), ROOT_DIR)

    @staticmethod
    def core_tests(tests, quiet=False):
        """Run core tests"""
        Test._run_marker('core', tests, quiet)

    @staticmethod
    def unit_tests(tests, quiet=False):
        """Run unit tests"""
        Test._run_marker('unit', tests, quiet)

    @staticmethod
    def integration_tests(tests, quiet=False):
        """Run integration tests"""
        Test._run_marker('integration', tests, quiet)

    @staticmethod
    def all_tests(tests, quiet=False):
        """Run all tests"""
        Test._run_marker('', tests, quiet)

    @staticmethod
    def custom_tests(marker, tests, quiet=False):
        """Run custom tests with a specific marker"""
        Test._run_marker(marker, tests, quiet)


# pylint: disable=R0913, R0917
def run_tests(
    tests,
    marker,
    skip_build,
    keep_files=False,
    unit=False,
    integration=False,
    core=False,
    all_tests=False,
    quiet=False,
):
    """Runs tests"""

    if not skip_build:
        build_package()

    logging.info('Running moldflow-api tests')

    is_custom_marker = marker and marker not in ['core', 'unit', 'integration']
    no_flags = not any([unit, integration, core, all_tests, is_custom_marker])

    # Run Core
    if core or no_flags:
        logging.info('Running core tests')
        Test.core_tests(tests, quiet)

    # Run Unit
    if unit or no_flags:
        logging.info('Running unit tests')
        Test.unit_tests(tests, quiet)

    # Run Integration
    if integration:
        logging.info('Running integration tests')
        Test.integration_tests(tests, quiet)

    # Run all
    if all_tests:
        logging.info('Running all tests')
        Test.all_tests(tests, quiet)

    # Run Custom Tests
    if is_custom_marker:
        Test.custom_tests(marker, tests, quiet)

    # Coverage Combine
    run_command([sys.executable] + '-m coverage combine'.split(' '), ROOT_DIR)

    # Coverage
    run_command([sys.executable] + '-m run report --cli'.split(' '), ROOT_DIR)

    # Keeping files
    if not keep_files:
        if os.path.exists(COVERAGE_FILE):
            os.remove(COVERAGE_FILE)


def clean_up():
    """Clean up build artifacts"""
    logging.info('Cleaning up build artifacts')

    # Remove built docs
    logging.info("Removing built docs")
    if os.path.exists(DOCS_BUILD_DIR):
        shutil.rmtree(DOCS_BUILD_DIR)

    # Remove build files
    logging.info("Removing build files")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)

    if os.path.exists(SETUP_CONFIG_FILE):
        os.remove(SETUP_CONFIG_FILE)

    # Remove coverage files
    logging.info("Removing coverage files")
    if os.path.exists(COVERAGE_FILE):
        os.remove(COVERAGE_FILE)

    # Remove coverage html files
    logging.info("Removing coverage html files")
    if os.path.exists(COVERAGE_HTML_DIR):
        shutil.rmtree(COVERAGE_HTML_DIR)

    # Remove coverage XML files
    logging.info("Removing coverage XMl files")
    if os.path.exists(COVERAGE_XML_FILE_NAME):
        os.remove(COVERAGE_XML_FILE_NAME)


def generate_expected_data(markers: list[str]):
    """Generate data for integration tests"""
    logging.info('Generating data for integration tests')
    generate_data_module = 'tests.api.integration_tests.data_generation.generate_data'
    run_command([sys.executable, '-m', generate_data_module] + markers, ROOT_DIR)


def _get_current_version_if_newer():
    """
    Check if version.json has a version newer than the latest git tag.

    Returns version string (e.g., 'v27.0.1') if newer, None otherwise.
    """
    try:
        # Read version.json
        with open(VERSION_FILE, 'r', encoding=ENCODING) as f:
            vers_json_dict = json.load(f)
        current_version = (
            f"v{vers_json_dict['major']}.{vers_json_dict['minor']}.{vers_json_dict['patch']}"
        )

        # Get latest git tag
        tags = [tag.name for tag in GIT_REPO.tags if _is_version_tag(tag.name)]

        if not tags:
            return None

        latest_tag = sorted(tags, key=lambda t: Version(t.lstrip('v')), reverse=True)[0]

        # Compare versions

        current_ver = Version(current_version.lstrip('v'))
        latest_ver = Version(latest_tag.lstrip('v'))

        if current_ver > latest_ver:
            return current_version
        return None

    except Exception as err:
        logging.warning("Could not determine if current version is newer: %s", err)
        return None


def generate_switcher(include_current=False):
    """Generate switcher.json from git tags (vX.Y.Z format)."""
    logging.info('Generating switcher.json from git tags (vX.Y.Z)')
    switcher_script = os.path.join(ROOT_DIR, 'scripts', 'generate_switcher.py')
    cmd = [sys.executable, switcher_script]
    if include_current:
        cmd.append('--include-current')
    run_command(cmd, ROOT_DIR)


def set_version():
    """Set current version and write version file to package directory"""

    # Read version info from root version.json
    with open(VERSION_FILE, 'r', encoding=ENCODING) as vers_json:
        vers_json_dict = json.load(vers_json)

    # Set global version for use in other functions
    global VERSION
    VERSION = f"{vers_json_dict['major']}.{vers_json_dict['minor']}.{vers_json_dict['patch']}"

    # Create package version.json with complete version info
    package_version = {
        "major": vers_json_dict['major'],
        "minor": vers_json_dict['minor'],
        "patch": vers_json_dict['patch'],
    }

    # Ensure package directory exists
    os.makedirs(MOLDFLOW_DIR, exist_ok=True)

    # Write version.json to package directory
    package_version_file = os.path.join(MOLDFLOW_DIR, VERSION_JSON)
    with open(package_version_file, 'w', encoding=ENCODING) as f:
        json.dump(package_version, f, indent=2)


# pylint: disable=R0912, R0914, R0915
def main():
    """Main entry point for this script"""

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    args = docopt.docopt(__doc__)

    set_version()

    try:
        if args.get('lint'):
            skip_build = args.get('--skip-build') or args.get('-s')

            lint(skip_build=skip_build)

        elif args.get('generate-expected-data'):
            markers = args.get('<markers>') or []
            generate_expected_data(markers=markers)

        elif args.get('generate-switcher'):
            include_current = args.get('--include-current')
            generate_switcher(include_current=include_current)

        elif args.get('test'):
            tests = args.get('<tests>') or []
            marker = args.get('--marker') or args.get('-m')
            skip_build = args.get('--skip-build') or args.get('-s')
            keep_files = args.get('--keep-files') or args.get('-k')
            quiet = args.get('--quiet') or args.get('-q')
            unit = args.get('--unit')
            integration = args.get('--integration')
            core = args.get('--core')
            all_tests = args.get('--all')

            run_tests(
                tests=tests,
                marker=marker,
                skip_build=skip_build,
                keep_files=keep_files,
                unit=unit,
                integration=integration,
                core=core,
                all_tests=all_tests,
                quiet=quiet,
            )

        elif args.get('report'):
            cli_arg = args.get('--cli') or args.get('-c')
            html_arg = args.get('--html') or args.get('-h')
            xml_arg = args.get('--xml') or args.get('-x')

            if cli_arg:
                Report.cli()
            if html_arg:
                Report.html()
            if xml_arg:
                print(COVERAGE_XML_FILE_NAME)
                Report.xml()

        elif args.get('build'):
            install = args.get('--install') or args.get('-i')

            build_package(install=install)

        elif args.get('build-docs'):
            target = args.get('--target') or args.get('-t') or 'html'
            skip_build = args.get('--skip-build') or args.get('-s')
            local = args.get('--local') or args.get('-l')
            skip_switcher = args.get('--skip-switcher')
            include_current = args.get('--include-current')
            incremental = args.get('--incremental')

            build_docs(
                target=target,
                skip_build=skip_build,
                local=local,
                skip_switcher=skip_switcher,
                include_current=include_current,
                incremental=incremental,
            )

        elif args.get('install-package-requirements'):
            install_package(target_path=os.path.join(ROOT_DIR, SITE_PACKAGES))

        elif args.get('install'):
            install_package(build=True)

        elif args.get('format'):
            check_only = args.get('--check')

            format_code(check_only=check_only)

        elif args.get('publish'):
            skip_build = args.get('--skip-build') or args.get('-s')
            testpypi = args.get('--testpypi')
            repo_url = args.get('--repo-url')

            # Docopt groups are XOR, but validate explicitly and present a
            # user-friendly message rather than a stack trace.
            if testpypi and repo_url:
                logging.error(
                    'Options --testpypi and --repo-url are mutually exclusive. Provide only one.'
                )
                return 2

            publish(skip_build=skip_build, testpypi=testpypi, repo_url=repo_url)

        elif args.get('release'):
            github_api_url = args.get('--github-api-url')
            create_release(github_api_url=github_api_url)

        elif args.get('clean-up'):
            clean_up()

    except Exception as err:
        logging.error('FAILURE: %s', err, exc_info=True)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
