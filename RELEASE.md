# Release steps

This file documents how to create a release and publish to PyPI for moldflow-api.

The process is split into two independent stages:
1. **Create a GitHub Release** (produces the wheel and attaches it to a tagged release)
2. **Publish to PyPI** (uploads the wheel from the GitHub Release to PyPI)

You can create the GitHub Release first and publish to PyPI when ready.

## Prerequisites

- The canonical version source is the root `version.json` in the repository root.
- All release workflows only run on branches whose name starts with `release/`.
- CI (`ci.yml`) must pass before either workflow can proceed.

## Step 1: Bump the version

1. Edit `version.json` at the repository root:

```json
{
  "major": "27",
  "minor": "0",
  "patch": "0"
}
```

2. Commit and push on a `release/` branch:

```bash
git checkout -b release/MAJOR  # e.g. release/27
git add version.json
git commit -m "Bump version to MAJOR.MINOR.PATCH"
git push -u origin release/MAJOR
```

3. Wait for CI to pass on that branch.

## Step 2: Create a GitHub Release

Trigger the **"Create GitHub Release (manual)"** workflow:

- Open the workflow in GitHub Actions UI, choose `Run workflow`
- Set `confirm` to `true`
- Run on your `release/` branch

Or via GitHub CLI:

```bash
gh workflow run github-release.yml --ref release/MAJOR -f confirm=true
```

This will:
- Ensure CI passed for the commit
- Build the package (`python run.py build`)
- Create a GitHub Release with tag `vMAJOR.MINOR.PATCH`
- Attach the wheel (`.whl`) and source distribution (`.tar.gz`) as release assets

The wheel is now available from the GitHub Release assets.

## Step 3: Publish to PyPI

When ready to make the package publicly available, trigger the **"Publish to PyPI (manual)"** workflow:

- Open the workflow in GitHub Actions UI, choose `Run workflow`
- Set `tag` to the GitHub Release tag (e.g. `v27.0.0`)
- Set `confirm` to `true`
- Run on your `release/` branch

Or via GitHub CLI:

```bash
gh workflow run pypi-publish.yml --ref release/MAJOR -f tag=v27.0.0 -f confirm=true
```

This will:
- Validate the release tag exists
- Check if the version already exists on PyPI (skip if it does)
- Download the wheel from the GitHub Release assets
- Upload to PyPI using `twine`
- Build and deploy documentation to GitHub Pages

## PyPI publish ordering

Creating a GitHub Release does **not** require older releases to be on PyPI — multiple
GitHub Releases can exist during development.

When you run **Publish to PyPI**, the workflow checks that every **older** GitHub
Release (by version number) is already on PyPI before uploading the tag you selected.
Draft and prerelease GitHub Releases are ignored.

Example — GitHub Releases: `v26.1.0`, `v27.0.0`, `v27.1.0`, `v27.1.1`; PyPI: `26.1.0`, `27.0.0`:

| Publish tag | Result |
|---|---|
| `v27.1.0` | Allowed (older releases are on PyPI) |
| `v27.1.1` | **Blocked** (`v27.1.0` is older and not on PyPI) |

Publish in order. If an intermediate build had issues, publish it to PyPI anyway and
follow with the fix — `pip install --upgrade` resolves to the latest version, so users
are not left on the bad release.

## Local testing

Build the package locally to smoke test:

```bash
python run.py build
```

Publishing to PyPI is restricted to the GitHub Actions workflows. Use `--testpypi`
for local testing if needed:

```bash
python run.py publish --testpypi
```

## Notes

- `run.py` requires a `patch` value in the root `version.json`. It will raise a
  RuntimeError if that key is missing.
- The `run.py` script writes a package-local `src/moldflow/version.json` at build
  time; you do not need to edit that file directly.
- After a successful release and publish, you may merge the `release/` branch back
  to `main` and delete the branch.

## Contact

If anything behaves unexpectedly, check the logs for the `github-release` and
`pypi-publish` workflows; feel free to open an issue or ask a maintainer.
