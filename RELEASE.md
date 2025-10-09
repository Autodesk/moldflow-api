# Release steps (minimal)

This file documents the minimal, explicit steps to bump the version and publish a release for moldflow-api.

Summary (short):

- Edit the root `version.json` (only this file).
- Commit on a branch named `release/MAJOR.MINOR.PATCH` and push.
- Wait for CI to pass on that branch.
- Trigger the manual "Publish package (manual)" workflow in GitHub Actions and confirm.

Why this works (important notes):

- The canonical version source for releases is the root `version.json` in the repository root.
- The `run.py` script (used for building and releasing locally and by many repo commands)
  reads the `patch` value directly from the root `version.json` and will raise a
  RuntimeError if `patch` is missing.
- The workflow only publishes when run on a branch whose name starts with `release/` and when
  you confirm the manual workflow dispatch.
- The release workflow checks PyPI for an existing version and will skip publishing if that
  exact version already exists.

Minimal step-by-step

1. Decide the new major/minor/patch values.

   - Always set a numeric `patch` value in the root `version.json`.

2. Edit `version.json` at the repository root. Example (bumping to MAJOR.MINOR.PATCH, e.g. 1.2.0):

```json
{
  "major": "27",
  "minor": "0",
  "patch": "0"
}
```

3. Commit and push on a `release/` branch. Example (use the placeholder branch name below and replace with your version):

```bash
# create branch using the target version (branch name must start with 'release/')
# use a placeholder like 'release/MAJOR.MINOR.PATCH' and replace with your values
git checkout -b release/MAJOR.MINOR.PATCH  # e.g. release/1.2.0
git add version.json
git commit -m "Bump version to MAJOR.MINOR.PATCH"  # e.g. "Bump version to 1.2.0"
git push -u origin release/MAJOR.MINOR.PATCH
```

4. Wait for CI to pass on that branch.

   - The publish workflow has a guard that requires the `ci.yml` workflow to have completed
     successfully for the same commit before allowing publish.

5. Trigger the publish workflow manually in the GitHub Actions UI for the repository.

   - Open the `Publish package (manual)` workflow, choose `Run workflow`, set `confirm` to
     `true`, and run it on your `release/MAJOR.MINOR.PATCH` branch (replace the placeholder
     with the actual version).
   - Alternatively, you can use the GitHub CLI (if you have it configured). Example using a
     placeholder branch name (replace with your actual branch):
```bash
# example (replace with the correct workflow file name and branch if needed)
# gh workflow run publish.yml --ref release/MAJOR.MINOR.PATCH -f confirm=true
# e.g. --ref release/1.2.0
```

6. What the workflow does (high level):

- Ensures CI (`ci.yml`) passed for the commit.
- Computes the release version using `version.json`.
- If the computed version already exists on PyPI the workflow will skip the publish.
- If not present, it builds the package, uploads to PyPI (requires the repo to have
  `PYPI_API_TOKEN` in secrets), creates a GitHub release (tag `vMAJOR.MINOR.PATCH`) and
  deploys documentation to GitHub Pages.

Local testing and notes

- You can build the package locally to smoke test the build step:

```bash
python run.py build
```

- Publishing to PyPI is intentionally restricted to the manual GitHub Actions workflow.
  If you need to test publishing to TestPyPI locally, you can use `python -m twine upload`
  with TestPyPI credentials, but this is separate from the CI-based publish flow.

Edge cases and tips

- `run.py` now requires a `patch` value in the root `version.json`. It will raise a
  RuntimeError if that key is missing. Do not rely on `run.py` falling back to any
  environment variable.
- If you want CI to inject a monotonic build number into the patch segment, make the CI
  step explicitly update `version.json` (or generate a temporary `version.json`) with the
  desired `patch` before running the build and publish steps. That keeps `run.py` and the
  workflow in agreement.
- The `run.py` script will write a package-local `src/moldflow/version.json` at build time;
  you do not need to edit that file directly (it is generated and typically ignored by Git).

Cleanup (optional)

- After a successful release you may merge the `release/` branch to `main` (if you use merge
  workflow) and delete the `release/` branch.

Contact

If anything in CI behaves unexpectedly, check the logs for the `publish` workflow and the
`ci` workflow; feel free to open an issue or ask a maintainer.
