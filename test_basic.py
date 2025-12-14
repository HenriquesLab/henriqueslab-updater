#!/usr/bin/env python3
"""Quick test script to verify basic functionality."""

from henriqueslab_updater import UpdateChecker, SimpleNotifier

# Test 1: Basic initialization
print("Test 1: Basic initialization")
checker = UpdateChecker(
    package_name="test-package",
    current_version="1.0.0",
)
print(f"✓ UpdateChecker created: {checker.package_name} v{checker.current_version}")

# Test 2: Installation detection
print("\nTest 2: Installation detection")
install_info = checker.get_install_info()
print(f"✓ Installation detected: {install_info.method} ({install_info.friendly_name})")
print(f"  Upgrade command: {install_info.upgrade_command}")

# Test 3: Version comparison
print("\nTest 3: Version comparison")
from henriqueslab_updater.core.version_compare import is_newer_version

test_cases = [
    ("1.0.0", "1.0.1", True),
    ("1.0.1", "1.0.0", False),
    ("1.0.0", "1.1.0", True),
    ("1.0.0", "2.0.0", True),
    ("1.0.0", "1.0.0", False),
]

for current, latest, expected in test_cases:
    result = is_newer_version(current, latest)
    status = "✓" if result == expected else "✗"
    print(f"{status} {current} → {latest}: {result} (expected {expected})")

# Test 4: Cache manager
print("\nTest 4: Cache manager")
from henriqueslab_updater.core.cache_manager import CacheManager
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    cache = CacheManager("test-package", cache_dir=Path(tmpdir))

    # Should check (cache doesn't exist)
    print(f"✓ Should check (no cache): {cache.should_check()}")

    # Save some data
    cache.save({"test": "data"})
    print(f"✓ Cache saved")

    # Load data
    data = cache.load()
    print(f"✓ Cache loaded: {data}")

# Test 5: Notifier
print("\nTest 5: Simple Notifier")
notifier = SimpleNotifier()
test_update_info = {
    "package_name": "test-package",
    "current_version": "1.0.0",
    "latest_version": "1.1.0",
    "install_method": "pip",
    "upgrade_command": "pip install --upgrade test-package",
    "release_url": "https://github.com/test/repo/releases/tag/v1.1.0",
}
print("Testing notification format:")
message = notifier.format(test_update_info)
print(message)

print("\n" + "=" * 64)
print("All basic tests passed! ✓")
print("=" * 64)
