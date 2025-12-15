# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`henriqueslab-updater` is a centralized update checking library for HenriquesLab Python packages. It provides a pluggable architecture for detecting updates from multiple sources (PyPI, Homebrew, GitHub), automatically detecting installation methods (brew, pipx, uv, pip), and displaying notifications to users.

## Development Commands

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[all,dev]"
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_update_checker.py

# Run specific test function
pytest tests/unit/test_update_checker.py::test_function_name

# Run without coverage report
pytest --no-cov
```

### Code Quality
```bash
# Format and lint (Ruff handles both)
ruff check src tests
ruff format src tests

# Type checking
mypy src
```

### Building
```bash
# Build distribution packages
pip install build
python -m build
```

## Architecture

### Core Components

The codebase follows a **pluggable architecture** with clear separation of concerns:

1. **UpdateChecker** (`core/update_checker.py`) - Main orchestrator that coordinates all components
2. **VersionSources** (`sources/`) - Fetch latest version from different sources (PyPI, Homebrew, GitHub)
3. **InstallDetector** (`detectors/install_detector.py`) - Detects how package was installed and provides upgrade commands
4. **CacheManager** (`core/cache_manager.py`) - Manages update check cache with 24-hour TTL
5. **Notifiers** (`notifiers/`) - Display update notifications (Simple text or Rich formatted)
6. **Plugins** (`plugins/`) - Extend functionality (e.g., ChangelogPlugin for release notes)

### Key Design Patterns

**Singleton Pattern**: The `convenience.py` module provides singleton access to UpdateChecker via `get_update_checker()`, allowing multiple parts of an application to check for updates without creating multiple checkers.

**Priority System**: VersionSources have priorities (lower = higher priority). When multiple sources are configured, they're tried in priority order until one succeeds.

**Non-blocking Checks**: The `check_async()` method uses `create_async_task()` to run checks in background without blocking CLI execution. Results are cached for later display via `show_notification()`.

**Plugin Architecture**: Plugins receive update info and can augment it (e.g., ChangelogPlugin fetches and parses CHANGELOG.md to add highlights).

### Module Dependencies

- **Core** depends on: sources, detectors, notifiers, utils
- **Convenience functions** depend on: core only
- **Plugins** depend on: core (receive update_info dict)
- **Sources/Notifiers/Detectors** are independent and can be used standalone

### Optional Dependencies

The library minimizes required dependencies (only `packaging` is required):
- `rich>=13.0` - For RichNotifier with colored output
- `httpx>=0.25.0` - For async HTTP requests (changelog fetching)

Code should gracefully handle missing optional dependencies with try/except ImportError blocks.

## Testing Philosophy

- **Unit tests** (`tests/unit/`) test individual components in isolation with mocking
- **Integration tests** (`tests/integration/`) test real network calls (minimal, marked slow)
- Use `pytest-mock` for mocking complex dependencies
- Use `pytest-asyncio` for async code testing
- Target: >60% coverage (currently 64%)

## Version Management

Version is defined in `src/henriqueslab_updater/__version__.py` as a single-line string:
```python
__version__ = "1.0.0"
```

The build system (hatchling) reads this file via `tool.hatch.version.path` in pyproject.toml.

## Supported Python Versions

Minimum: Python 3.9 (as specified in pyproject.toml `requires-python = ">=3.9"`)

CI tests against: 3.9, 3.10, 3.11, 3.12
