"""Centralized upgrade workflow for CLI applications."""

from typing import Optional, Protocol, Tuple

from ..core.update_checker import UpdateChecker
from ..utils.upgrade_executor import execute_upgrade


class UpgradeNotifier(Protocol):
    """Protocol for custom upgrade notifiers."""

    def show_checking(self) -> None:
        """Show 'checking for updates' message."""
        ...

    def show_version_check(
        self, current: str, latest: str, available: bool
    ) -> None:
        """Show version check results."""
        ...

    def show_update_info(
        self, current: str, latest: str, release_url: str
    ) -> None:
        """Show update available information."""
        ...

    def show_installer_info(self, friendly_name: str, command: str) -> None:
        """Show detected installer information."""
        ...

    def show_success(self, version: str) -> None:
        """Show successful upgrade message."""
        ...

    def show_error(self, error: Optional[str]) -> None:
        """Show upgrade error message."""
        ...

    def show_manual_instructions(self, install_method: str) -> None:
        """Show manual upgrade instructions."""
        ...

    def confirm_upgrade(self, version: str) -> bool:
        """Prompt user to confirm upgrade. Returns True if confirmed."""
        ...


class SimpleUpgradeNotifier:
    """Simple text-based upgrade notifier (no dependencies)."""

    def show_checking(self) -> None:
        print("Checking for updates...")

    def show_version_check(
        self, current: str, latest: str, available: bool
    ) -> None:
        print(f"Current version: v{current}")
        if available:
            print(f"Latest version: v{latest}")
            print("Update available!")
        else:
            print("✓ You are already using the latest version")

    def show_update_info(
        self, current: str, latest: str, release_url: str
    ) -> None:
        print()
        print(f"Update available: v{current} → v{latest}")
        print(f"Release notes: {release_url}")
        print()

    def show_installer_info(self, friendly_name: str, command: str) -> None:
        print(f"\nDetected installer: {friendly_name}")
        print(f"Running: {command}")
        print()

    def show_success(self, version: str) -> None:
        print()
        print(f"✓ Successfully upgraded to v{version}")
        print()
        print("Please restart your terminal or reload your shell")
        print("to ensure the new version is loaded.")

    def show_error(self, error: Optional[str]) -> None:
        print()
        print("✗ Upgrade failed")
        print()
        if error:
            print("Error:")
            print(error)
            print()

    def show_manual_instructions(self, install_method: str) -> None:
        print("Manual upgrade:")
        if install_method == "homebrew":
            print("  brew update && brew upgrade <package>")
        elif install_method == "pipx":
            print("  pipx upgrade <package>")
        elif install_method == "uv":
            print("  uv tool upgrade <package>")
        elif install_method == "dev":
            print("  cd <repo> && git pull && uv sync")
        else:
            print("  pip install --upgrade <package>")
            print("  # Or with --user flag:")
            print("  pip install --upgrade --user <package>")

    def confirm_upgrade(self, version: str) -> bool:
        """Prompt user for confirmation."""
        try:
            response = input(f"Upgrade to v{version}? [Y/n]: ")
            return response.lower() in ("", "y", "yes")
        except (KeyboardInterrupt, EOFError):
            print("\nUpgrade cancelled.")
            return False


def handle_upgrade_workflow(
    package_name: str,
    current_version: str,
    check_only: bool = False,
    skip_confirmation: bool = False,
    notifier: Optional[UpgradeNotifier] = None,
    github_org: Optional[str] = None,
    github_repo: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Complete upgrade workflow for CLI applications.

    Args:
        package_name: Name of the package (e.g., "folder2md4llms")
        current_version: Current installed version
        check_only: If True, only check for updates without upgrading
        skip_confirmation: If True, skip confirmation prompt
        notifier: Custom notifier for CLI output (uses SimpleUpgradeNotifier if None)
        github_org: GitHub organization name (for release notes URL)
        github_repo: GitHub repository name (for release notes URL)

    Returns:
        Tuple of (success, error_message)
        - check_only mode: (True, None) if already latest, (False, None) if update available
        - upgrade mode: (True, None) on success, (False, error_msg) on failure
    """
    if notifier is None:
        notifier = SimpleUpgradeNotifier()

    # Step 1: Check for updates
    notifier.show_checking()
    checker = UpdateChecker(package_name, current_version)
    update_info = checker.check_sync(force=True)

    if not update_info:
        # Check failed - treat as no update available
        notifier.show_version_check(current_version, current_version, False)
        return (True, None) if check_only else (False, "Update check failed")

    update_available = update_info.get("update_available", False)
    latest_version = update_info.get("latest_version", current_version)

    # Step 2: Handle check-only mode
    if check_only:
        notifier.show_version_check(current_version, latest_version, update_available)
        return (True, None) if not update_available else (False, None)

    # Step 3: Check if update available
    if not update_available or latest_version == current_version:
        notifier.show_version_check(current_version, current_version, False)
        return (True, None)

    # Step 4: Show update information
    if github_org and github_repo:
        release_url = f"https://github.com/{github_org}/{github_repo}/releases/tag/v{latest_version}"
    else:
        release_url = f"https://pypi.org/project/{package_name}/{latest_version}/"

    notifier.show_update_info(current_version, latest_version, release_url)

    # Step 5: Confirm upgrade
    if not skip_confirmation:
        if not notifier.confirm_upgrade(latest_version):
            return (False, "User cancelled")

    # Step 6: Get installer info
    install_method = update_info.get("install_method", "unknown")
    friendly_name = update_info.get("friendly_name", install_method)
    upgrade_command = update_info.get(
        "upgrade_command", f"pip install --upgrade {package_name}"
    )

    notifier.show_installer_info(friendly_name, upgrade_command)

    # Step 7: Execute upgrade
    success, error = execute_upgrade(upgrade_command, show_output=False, timeout=300)

    # Step 8: Show result
    if success:
        notifier.show_success(latest_version)
        return (True, None)
    else:
        notifier.show_error(error)
        notifier.show_manual_instructions(install_method)
        return (False, error or "Upgrade failed")
