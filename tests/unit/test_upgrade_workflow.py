"""Unit tests for upgrade workflow."""

from typing import Optional
from unittest.mock import Mock, patch, MagicMock
import pytest

from henriqueslab_updater.workflows.upgrade_workflow import (
    handle_upgrade_workflow,
    UpgradeNotifier,
    SimpleUpgradeNotifier,
)


class MockNotifier:
    """Mock notifier for testing."""

    def __init__(self):
        self.calls = {
            "show_checking": [],
            "show_version_check": [],
            "show_update_info": [],
            "show_installer_info": [],
            "show_success": [],
            "show_error": [],
            "show_manual_instructions": [],
            "confirm_upgrade": [],
        }
        self.confirm_response = True

    def show_checking(self):
        self.calls["show_checking"].append(())

    def show_version_check(self, current: str, latest: str, available: bool):
        self.calls["show_version_check"].append((current, latest, available))

    def show_update_info(self, current: str, latest: str, release_url: str):
        self.calls["show_update_info"].append((current, latest, release_url))

    def show_installer_info(self, friendly_name: str, command: str):
        self.calls["show_installer_info"].append((friendly_name, command))

    def show_success(self, version: str):
        self.calls["show_success"].append((version,))

    def show_error(self, error: Optional[str]):
        self.calls["show_error"].append((error,))

    def show_manual_instructions(self, install_method: str):
        self.calls["show_manual_instructions"].append((install_method,))

    def confirm_upgrade(self, version: str) -> bool:
        self.calls["confirm_upgrade"].append((version,))
        return self.confirm_response


class TestHandleUpgradeWorkflow:
    """Test handle_upgrade_workflow function."""

    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_check_only_no_update(self, mock_checker_class):
        """Test check-only mode when no update is available."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": False,
            "latest_version": "1.0.0",
        }

        notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            check_only=True,
            notifier=notifier,
        )

        # Verify
        assert success is True
        assert error is None
        assert len(notifier.calls["show_checking"]) == 1
        assert len(notifier.calls["show_version_check"]) == 1
        assert notifier.calls["show_version_check"][0] == ("1.0.0", "1.0.0", False)

    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_check_only_update_available(self, mock_checker_class):
        """Test check-only mode when update is available."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
        }

        notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            check_only=True,
            notifier=notifier,
        )

        # Verify
        assert success is False  # False indicates update available in check-only mode
        assert error is None
        assert len(notifier.calls["show_checking"]) == 1
        assert len(notifier.calls["show_version_check"]) == 1
        assert notifier.calls["show_version_check"][0] == ("1.0.0", "1.1.0", True)

    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_check_only_check_failed(self, mock_checker_class):
        """Test check-only mode when update check fails."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = None

        notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            check_only=True,
            notifier=notifier,
        )

        # Verify
        assert success is True  # Treat failed check as no update available
        assert error is None
        assert len(notifier.calls["show_version_check"]) == 1

    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_upgrade_no_update_available(self, mock_checker_class):
        """Test upgrade mode when no update is available."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": False,
            "latest_version": "1.0.0",
        }

        notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            notifier=notifier,
        )

        # Verify
        assert success is True
        assert error is None
        assert len(notifier.calls["show_version_check"]) == 1
        assert notifier.calls["show_version_check"][0] == ("1.0.0", "1.0.0", False)
        # Should not show update info or prompt for upgrade
        assert len(notifier.calls["show_update_info"]) == 0
        assert len(notifier.calls["confirm_upgrade"]) == 0

    @patch("henriqueslab_updater.workflows.upgrade_workflow.execute_upgrade")
    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_upgrade_user_cancels(self, mock_checker_class, mock_execute):
        """Test upgrade mode when user cancels confirmation."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
            "install_method": "pipx",
            "friendly_name": "pipx",
            "upgrade_command": "pipx upgrade test-package",
        }

        notifier = MockNotifier()
        notifier.confirm_response = False  # User says no

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            notifier=notifier,
        )

        # Verify
        assert success is False
        assert error == "User cancelled"
        assert len(notifier.calls["confirm_upgrade"]) == 1
        assert notifier.calls["confirm_upgrade"][0] == ("1.1.0",)
        # Should not execute upgrade
        mock_execute.assert_not_called()

    @patch("henriqueslab_updater.workflows.upgrade_workflow.execute_upgrade")
    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_upgrade_success(self, mock_checker_class, mock_execute):
        """Test successful upgrade."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
            "install_method": "pipx",
            "friendly_name": "pipx",
            "upgrade_command": "pipx upgrade test-package",
        }

        mock_execute.return_value = (True, None)  # Success

        notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            skip_confirmation=True,
            notifier=notifier,
        )

        # Verify
        assert success is True
        assert error is None
        assert len(notifier.calls["show_update_info"]) == 1
        assert len(notifier.calls["show_installer_info"]) == 1
        assert len(notifier.calls["show_success"]) == 1
        assert notifier.calls["show_success"][0] == ("1.1.0",)
        # Verify execute_upgrade called with correct params
        mock_execute.assert_called_once_with(
            "pipx upgrade test-package", show_output=False, timeout=300
        )

    @patch("henriqueslab_updater.workflows.upgrade_workflow.execute_upgrade")
    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_upgrade_failure(self, mock_checker_class, mock_execute):
        """Test upgrade failure."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
            "install_method": "pipx",
            "friendly_name": "pipx",
            "upgrade_command": "pipx upgrade test-package",
        }

        error_msg = "Command failed with exit code 1"
        mock_execute.return_value = (False, error_msg)  # Failure

        notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            skip_confirmation=True,
            notifier=notifier,
        )

        # Verify
        assert success is False
        assert error == error_msg
        assert len(notifier.calls["show_error"]) == 1
        assert notifier.calls["show_error"][0] == (error_msg,)
        assert len(notifier.calls["show_manual_instructions"]) == 1
        assert notifier.calls["show_manual_instructions"][0] == ("pipx",)

    @patch("henriqueslab_updater.workflows.upgrade_workflow.execute_upgrade")
    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_upgrade_with_github_release_url(self, mock_checker_class, mock_execute):
        """Test upgrade shows correct GitHub release URL."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
            "install_method": "pipx",
            "friendly_name": "pipx",
            "upgrade_command": "pipx upgrade test-package",
        }

        mock_execute.return_value = (True, None)

        notifier = MockNotifier()

        # Execute with GitHub org/repo
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            skip_confirmation=True,
            notifier=notifier,
            github_org="testorg",
            github_repo="testrepo",
        )

        # Verify GitHub URL was used
        assert success is True
        assert len(notifier.calls["show_update_info"]) == 1
        update_info = notifier.calls["show_update_info"][0]
        assert update_info[2] == "https://github.com/testorg/testrepo/releases/tag/v1.1.0"

    @patch("henriqueslab_updater.workflows.upgrade_workflow.execute_upgrade")
    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_upgrade_with_pypi_url(self, mock_checker_class, mock_execute):
        """Test upgrade shows PyPI URL when no GitHub info provided."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
            "install_method": "pipx",
            "friendly_name": "pipx",
            "upgrade_command": "pipx upgrade test-package",
        }

        mock_execute.return_value = (True, None)

        notifier = MockNotifier()

        # Execute without GitHub org/repo
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            skip_confirmation=True,
            notifier=notifier,
        )

        # Verify PyPI URL was used
        assert success is True
        assert len(notifier.calls["show_update_info"]) == 1
        update_info = notifier.calls["show_update_info"][0]
        assert update_info[2] == "https://pypi.org/project/test-package/1.1.0/"

    @patch("henriqueslab_updater.workflows.upgrade_workflow.execute_upgrade")
    @patch("henriqueslab_updater.workflows.upgrade_workflow.UpdateChecker")
    def test_custom_notifier(self, mock_checker_class, mock_execute):
        """Test that custom notifier is used correctly."""
        # Setup mocks
        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_sync.return_value = {
            "update_available": True,
            "latest_version": "1.1.0",
            "install_method": "pipx",
            "friendly_name": "pipx",
            "upgrade_command": "pipx upgrade test-package",
        }

        mock_execute.return_value = (True, None)

        # Custom notifier
        custom_notifier = MockNotifier()

        # Execute
        success, error = handle_upgrade_workflow(
            package_name="test-package",
            current_version="1.0.0",
            skip_confirmation=True,
            notifier=custom_notifier,
        )

        # Verify custom notifier was called
        assert success is True
        assert len(custom_notifier.calls["show_checking"]) == 1
        assert len(custom_notifier.calls["show_update_info"]) == 1
        assert len(custom_notifier.calls["show_installer_info"]) == 1
        assert len(custom_notifier.calls["show_success"]) == 1

    def test_simple_upgrade_notifier_instantiation(self):
        """Test that SimpleUpgradeNotifier can be instantiated."""
        notifier = SimpleUpgradeNotifier()
        assert notifier is not None

    @patch("builtins.print")
    def test_simple_upgrade_notifier_show_checking(self, mock_print):
        """Test SimpleUpgradeNotifier.show_checking."""
        notifier = SimpleUpgradeNotifier()
        notifier.show_checking()
        mock_print.assert_called_once_with("Checking for updates...")

    @patch("builtins.print")
    def test_simple_upgrade_notifier_show_version_check_no_update(self, mock_print):
        """Test SimpleUpgradeNotifier.show_version_check when no update."""
        notifier = SimpleUpgradeNotifier()
        notifier.show_version_check("1.0.0", "1.0.0", False)

        # Should print current version and "already latest"
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Current version: v1.0.0" in str(call) for call in calls)
        assert any("already using the latest version" in str(call) for call in calls)

    @patch("builtins.print")
    def test_simple_upgrade_notifier_show_version_check_update_available(
        self, mock_print
    ):
        """Test SimpleUpgradeNotifier.show_version_check when update available."""
        notifier = SimpleUpgradeNotifier()
        notifier.show_version_check("1.0.0", "1.1.0", True)

        # Should print current, latest, and "update available"
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Current version: v1.0.0" in str(call) for call in calls)
        assert any("Latest version: v1.1.0" in str(call) for call in calls)
        assert any("Update available!" in str(call) for call in calls)

    @patch("builtins.input", return_value="y")
    def test_simple_upgrade_notifier_confirm_yes(self, mock_input):
        """Test SimpleUpgradeNotifier.confirm_upgrade with 'y' response."""
        notifier = SimpleUpgradeNotifier()
        result = notifier.confirm_upgrade("1.1.0")

        assert result is True
        mock_input.assert_called_once_with("Upgrade to v1.1.0? [Y/n]: ")

    @patch("builtins.input", return_value="n")
    def test_simple_upgrade_notifier_confirm_no(self, mock_input):
        """Test SimpleUpgradeNotifier.confirm_upgrade with 'n' response."""
        notifier = SimpleUpgradeNotifier()
        result = notifier.confirm_upgrade("1.1.0")

        assert result is False

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("builtins.print")
    def test_simple_upgrade_notifier_confirm_keyboard_interrupt(
        self, mock_print, mock_input
    ):
        """Test SimpleUpgradeNotifier.confirm_upgrade with KeyboardInterrupt."""
        notifier = SimpleUpgradeNotifier()
        result = notifier.confirm_upgrade("1.1.0")

        assert result is False
        # Should print cancellation message
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Upgrade cancelled" in str(call) for call in calls)


class TestUpgradeNotifierProtocol:
    """Test that notifiers properly implement the UpgradeNotifier protocol."""

    def test_simple_notifier_implements_protocol(self):
        """Test that SimpleUpgradeNotifier implements UpgradeNotifier protocol."""
        notifier = SimpleUpgradeNotifier()

        # Check that all protocol methods exist
        assert hasattr(notifier, "show_checking")
        assert hasattr(notifier, "show_version_check")
        assert hasattr(notifier, "show_update_info")
        assert hasattr(notifier, "show_installer_info")
        assert hasattr(notifier, "show_success")
        assert hasattr(notifier, "show_error")
        assert hasattr(notifier, "show_manual_instructions")
        assert hasattr(notifier, "confirm_upgrade")

        # Check that methods are callable
        assert callable(notifier.show_checking)
        assert callable(notifier.show_version_check)
        assert callable(notifier.show_update_info)
        assert callable(notifier.show_installer_info)
        assert callable(notifier.show_success)
        assert callable(notifier.show_error)
        assert callable(notifier.show_manual_instructions)
        assert callable(notifier.confirm_upgrade)
