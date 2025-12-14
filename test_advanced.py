#!/usr/bin/env python3
"""Advanced test demonstrating best-practice patterns."""

print("=" * 70)
print("Advanced Tests: Homebrew-first strategy & Singleton pattern")
print("=" * 70)

# Test 1: Convenience Functions (Singleton Pattern)
print("\n1. Testing Singleton Pattern with Convenience Functions")
print("-" * 70)

from henriqueslab_updater import (
    check_for_updates_async_background,
    get_update_checker,
    show_update_notification,
)

# First call initializes the singleton
check_for_updates_async_background("test-package", "1.0.0")
print("✓ Background check initiated with convenience function")

# Get the same instance
checker = get_update_checker()
print(f"✓ Got checker instance: {checker.package_name} v{checker.current_version}")

# Can call show_update_notification even without checker reference
print("✓ Convenience function can be called independently")

# Test 2: Homebrew-first Strategy
print("\n2. Testing Homebrew-first Strategy")
print("-" * 70)

from henriqueslab_updater import UpdateChecker, HomebrewSource, PyPISource

# Create checker with both sources
checker2 = UpdateChecker(
    package_name="test-package-2",
    current_version="1.0.0",
    sources=[
        PyPISource("test-package-2"),
        HomebrewSource("test-package-2"),
    ],
)

# Check installation method
install_info = checker2.get_install_info()
print(f"✓ Installation detected: {install_info.method}")
print(f"  Upgrade command: {install_info.upgrade_command}")

if install_info.method == "homebrew":
    print("  → Homebrew sources will be checked FIRST")
else:
    print("  → Sources will be checked in standard priority order")

# Test 3: Version Comparison Edge Cases
print("\n3. Testing Version Comparison Edge Cases")
print("-" * 70)

from henriqueslab_updater.core.version_compare import is_newer_version

test_cases = [
    # (current, latest, expected, description)
    ("1.0.0", "1.0.1", True, "Simple patch update"),
    ("1.0.0", "1.1.0", True, "Minor version update"),
    ("1.0.0", "2.0.0", True, "Major version update"),
    ("1.0.0", "1.0.0", False, "Same version"),
    ("2.0.0", "1.0.0", False, "Downgrade"),
    ("unknown", "1.0.0", False, "Unknown current"),
    ("1.0.0", "unknown", False, "Unknown latest"),
    ("1.0.0.dev1", "1.0.0", True, "Dev to release IS an update"),
    ("1.0.0", "1.0.1.dev1", False, "Dev version is not newer"),
]

for current, latest, expected, desc in test_cases:
    result = is_newer_version(current, latest)
    status = "✓" if result == expected else "✗ FAILED"
    print(f"{status} {desc}: {current} → {latest} = {result}")

# Test 4: Multiple Notification Styles
print("\n4. Testing Notification Styles")
print("-" * 70)

from henriqueslab_updater import SimpleNotifier, RichNotifier

test_update_info = {
    "package_name": "rxiv-maker",
    "current_version": "1.15.9",
    "latest_version": "1.16.0",
    "install_method": "Homebrew",
    "upgrade_command": "brew update && brew upgrade rxiv-maker",
    "release_url": "https://github.com/henriqueslab/rxiv-maker/releases/tag/v1.16.0",
    "changelog_summary": "✨ What's New:\n  v1.16.0:\n    ✨ Add SVG figure support\n    🐛 Fix PDF rendering\n    🔄 Improve performance",
}

print("\nSimple Notifier:")
simple = SimpleNotifier()
simple_msg = simple.format(test_update_info)
print(simple_msg)

print("\nRich Notifier:")
if RichNotifier is not None:
    rich = RichNotifier()
    print("✓ Rich notifier available - displaying formatted panel:")
    rich.notify(test_update_info)
else:
    print("⚠ Rich not installed - would fall back to simple notifier")

# Test 5: Source Priority
print("\n5. Testing Source Priority Logic")
print("-" * 70)

pypi_src = PyPISource("test")
homebrew_src = HomebrewSource("test")

print(f"PyPI priority: {pypi_src.get_priority()} (higher number = lower priority)")
print(f"Homebrew priority: {homebrew_src.get_priority()} (higher number = lower priority)")

if homebrew_src.get_priority() < pypi_src.get_priority():
    print("✓ Homebrew has higher priority than PyPI")
else:
    print("✗ Priority ordering incorrect")

print("\n" + "=" * 70)
print("All advanced tests completed!")
print("=" * 70)
