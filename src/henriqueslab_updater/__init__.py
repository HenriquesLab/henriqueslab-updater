"""henriqueslab-updater: Centralized update checking for HenriquesLab packages.

This package provides a unified update checking system that supports multiple
installation methods (Homebrew, pipx, uv, pip) and version sources (PyPI, Homebrew).
"""

from .__version__ import __version__
from .core.update_checker import UpdateChecker
from .notifiers.simple import SimpleNotifier
from .plugins.changelog import ChangelogPlugin

# Try to import Rich notifier (optional dependency)
try:
    from .notifiers.rich import RichNotifier
except ImportError:
    RichNotifier = None  # type: ignore

# Try to import version sources
from .sources.pypi import PyPISource
from .sources.homebrew import HomebrewSource

__all__ = [
    "__version__",
    "UpdateChecker",
    "SimpleNotifier",
    "RichNotifier",
    "ChangelogPlugin",
    "PyPISource",
    "HomebrewSource",
]
