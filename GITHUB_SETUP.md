# GitHub Repository Setup Guide

## Overview

This guide walks you through creating the GitHub repository and configuring automated PyPI releases.

## Step 1: Create GitHub Repository

1. **Go to GitHub**: https://github.com/organizations/HenriquesLab/repositories/new

2. **Repository Settings**:
   - **Repository name**: `henriqueslab-updater`
   - **Description**: `Centralized update checking library for HenriquesLab Python packages`
   - **Visibility**: ✅ Public
   - **Initialize**: ❌ Do NOT add README, .gitignore, or license (we have these locally)

3. **Click "Create repository"**

## Step 2: Configure PyPI API Token for GitHub Actions

### 2.1 Create PyPI API Token

1. Go to PyPI: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. **Token name**: `github-actions-henriqueslab-updater`
4. **Scope**:
   - Select "Project: henriqueslab-updater" (specific to this package)
   - OR select "Entire account" (if you want to reuse for other packages)
5. **Copy the token** (starts with `pypi-...`)
6. ⚠️ **IMPORTANT**: Save this token immediately - you won't be able to see it again!

### 2.2 Add Token to GitHub Secrets

1. Go to repository settings: https://github.com/HenriquesLab/henriqueslab-updater/settings/secrets/actions
2. Click "New repository secret"
3. **Name**: `PYPI_API_TOKEN` (exactly as shown, case-sensitive)
4. **Value**: Paste your PyPI token (the full `pypi-...` string)
5. Click "Add secret"

## Step 3: Push Code to GitHub

```bash
cd /Users/paxcalpt/Documents/GitHub/henriqueslab_updater

# Add and commit the GitHub Actions workflows
git add .github/workflows/
git commit -m "ci: Add GitHub Actions workflows for tests and PyPI publishing"

# Push code and tag
git push -u origin main
git push origin v1.0.0
```

## Step 4: Create GitHub Release (Triggers Automated PyPI Publishing)

### Option A: Via GitHub Web Interface (Recommended)

1. Go to: https://github.com/HenriquesLab/henriqueslab-updater/releases/new

2. **Choose tag**: v1.0.0 (from dropdown)

3. **Release title**: `v1.0.0 - Initial Stable Release`

4. **Description**:
   ```markdown
   ## 🚀 Initial Stable Release

   First production release of henriqueslab-updater - a centralized update checking library for HenriquesLab Python packages.

   ### ✨ Features

   - Multi-source version checking (PyPI, Homebrew, GitHub)
   - Smart installation detection (7 methods)
   - Homebrew-first strategy for brew installations
   - Background async checking (non-blocking)
   - Smart caching with 24-hour TTL
   - Environment variable opt-out support
   - Rich and simple notifiers
   - Optional changelog plugin

   ### 📦 Installation

   ```bash
   pip install henriqueslab-updater
   ```

   ### 🔗 Links

   - **PyPI**: https://pypi.org/project/henriqueslab-updater/1.0.0/
   - **Documentation**: See README.md
   - **Issues**: https://github.com/HenriquesLab/henriqueslab-updater/issues

   ### 📊 Test Coverage

   - 139 unit tests (all passing)
   - 64% code coverage
   - Python 3.9 - 3.12 supported
   ```

5. ✅ Click "Publish release"

6. **Watch the automated workflow**:
   - Go to: https://github.com/HenriquesLab/henriqueslab-updater/actions
   - The "Publish to PyPI" workflow will run automatically
   - It will build the package and publish to PyPI
   - Check the workflow logs to verify success

### Option B: Via GitHub CLI (gh)

```bash
cd /Users/paxcalpt/Documents/GitHub/henriqueslab_updater

gh release create v1.0.0 \
  --title "v1.0.0 - Initial Stable Release" \
  --notes "See PYPI_SUCCESS.md for detailed release notes" \
  dist/*
```

## Step 5: Verify Automated Publishing

After creating the release, the GitHub Actions workflow will automatically:

1. ✅ Build the package
2. ✅ Run `twine check`
3. ✅ Publish to PyPI

**Monitor the workflow**:
- Go to: https://github.com/HenriquesLab/henriqueslab-updater/actions
- Click on the "Publish to PyPI" workflow run
- Verify all steps completed successfully (green checkmarks)

**If the workflow fails**:
- Check the workflow logs for error messages
- Common issues:
  - `PYPI_API_TOKEN` secret not set or incorrect
  - Version already exists on PyPI (can't republish same version)
  - Build errors (should have been caught locally)

## GitHub Actions Workflows

### 1. `publish-to-pypi.yml`

**Trigger**: When a GitHub release is published

**What it does**:
- Checks out code from the release tag
- Sets up Python 3.12
- Installs build tools
- Builds wheel and sdist
- Validates package with `twine check`
- Publishes to PyPI using the `PYPI_API_TOKEN` secret

**Usage**: Create a GitHub release (with tag) to trigger automated publishing

### 2. `tests.yml`

**Trigger**: On push to main or pull requests

**What it does**:
- Runs tests on Python 3.9, 3.10, 3.11, 3.12
- Reports test results
- Uploads coverage to Codecov (optional)

**Usage**: Automatic on every push/PR

## Future Releases

For future versions:

1. **Update version** in `src/henriqueslab_updater/__version__.py`
2. **Commit changes**: `git commit -am "chore: bump version to X.Y.Z"`
3. **Create tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. **Push**: `git push && git push --tags`
5. **Create GitHub release** from the new tag
6. **GitHub Actions automatically publishes to PyPI** 🎉

## Troubleshooting

### Workflow fails with "Token invalid"
- Regenerate PyPI token
- Update `PYPI_API_TOKEN` secret in GitHub

### Workflow fails with "Version already exists"
- You cannot republish the same version to PyPI
- Bump version number and create a new release

### Tests fail in CI but pass locally
- Check Python version compatibility
- Verify dependencies are correctly specified in `pyproject.toml`

### Want to test workflow without publishing?
- Change workflow trigger from `release: [published]` to `workflow_dispatch` (manual trigger)
- Or use TestPyPI:
  ```yaml
  - name: Publish to TestPyPI
    env:
      TWINE_REPOSITORY_URL: https://test.pypi.org/legacy/
      TWINE_USERNAME: __token__
      TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
    run: twine upload dist/*
  ```

## Security Best Practices

✅ **Use scoped tokens**: Create project-specific PyPI tokens, not account-wide
✅ **Use GitHub Secrets**: Never commit API tokens to git
✅ **Enable 2FA**: Required on PyPI for publishing
✅ **Review workflows**: Check workflow runs for unexpected behavior
✅ **Pin actions versions**: Use `@v4` not `@main` for stability

## Summary Checklist

Before first release:
- [ ] Create GitHub repository
- [ ] Create PyPI API token (scoped to henriqueslab-updater)
- [ ] Add `PYPI_API_TOKEN` to GitHub Secrets
- [ ] Push code to GitHub (`main` branch)
- [ ] Push tag to GitHub (`v1.0.0`)
- [ ] Create GitHub release (triggers automated publishing)
- [ ] Verify workflow succeeded
- [ ] Check package on PyPI

For subsequent releases:
- [ ] Update version in `__version__.py`
- [ ] Commit and create git tag
- [ ] Push code and tag
- [ ] Create GitHub release
- [ ] Workflow publishes automatically 🚀

---

**Note**: Since v1.0.0 is already published to PyPI manually, the automated workflow will fail if you create a v1.0.0 release. This is expected - start using the workflow from v1.0.1 onwards.
