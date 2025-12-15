# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.2] - 2025-12-15

### Changed

- **CI/CD**: Migrated PyPI publishing from API tokens to OIDC (OpenID Connect) trusted publishing
  - More secure: Short-lived tokens instead of long-lived API tokens
  - No secret management: GitHub Actions authenticates directly with PyPI
  - Uses official `pypa/gh-action-pypi-publish` action

## [1.1.1] - 2025-12-15

### Added
- **Upgrade Executor**: New `execute_upgrade()` function for safely executing upgrade commands
  - Automatic handling of compound commands with `&&` (e.g., `brew update && brew upgrade pkg`)
  - Proper command parsing using `shlex.split()` to prevent shell injection
  - Configurable output display and timeout settings
  - Returns (success, error_message) tuple for easy error handling
- **UpgradeError**: New exception class for upgrade failures with command details
- **execute_upgrade_raise()**: Convenience wrapper that raises exceptions instead of returning tuples

### Changed
- Exported upgrade utilities from main package: `execute_upgrade`, `execute_upgrade_raise`, `UpgradeError`

## [1.1.0] - 2025-12-15

### Added
- **Changelog Parser**: New `changelog_parser.py` utility module for parsing CHANGELOG.md files
  - Fetch and format changelogs from GitHub repositories
  - Highlight breaking changes and version-specific updates
  - Support for filtering by version range
- **CLAUDE.md**: Development guidance for Claude Code integration

## [1.0.0] - 2024-12-14

### Added
- Multi-source version checking (PyPI, Homebrew, GitHub formula parsing)
- Smart installation detection for 7 methods: Homebrew, pipx, uv, pip-user, pip, dev, unknown
- Homebrew-first strategy: prioritizes Homebrew source for brew installations
- Background async checking with daemon threads (non-blocking)
- Smart caching with 24-hour TTL
- Environment variable opt-out support (`NO_UPDATE_NOTIFIER`, package-specific vars)
- Rich and Simple notifiers with graceful fallback
- Optional changelog plugin for parsing version highlights
- GitHub Actions workflows for automated testing and PyPI publishing
- Comprehensive test suite (139 tests, 64% coverage)

### Features
- **UpdateChecker**: Main orchestrator for update checking
- **VersionSource**: Pluggable architecture for PyPI, Homebrew, GitHub
- **InstallDetector**: Automatic installation method detection
- **Notifier**: Simple (stdlib) and Rich (enhanced) notification formats
- **ChangelogPlugin**: Parse and display version highlights from CHANGELOG.md
- **CacheManager**: Smart caching with TTL and automatic expiration
- **Version Comparison**: Dev version filtering with semantic versioning

### Dependencies
- Required: `packaging>=23.0`
- Optional: `rich>=13.0`, `httpx>=0.25.0`

### Python Support
- Python 3.9, 3.10, 3.11, 3.12

[1.0.0]: https://github.com/HenriquesLab/henriqueslab-updater/releases/tag/v1.0.0
