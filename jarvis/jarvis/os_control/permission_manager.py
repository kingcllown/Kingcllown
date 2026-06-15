"""Permission and security management for OS operations."""

from typing import Set

from jarvis.core.config import ConfigManager
from jarvis.core.logger import logger


class PermissionManager:
    """Manage permissions for OS-level operations.

    Implements a permission-based access control system where each
    OS operation requires explicit permission before execution.
    """

    def __init__(self, config: ConfigManager):
        """Initialize permission manager.

        Args:
            config: ConfigManager instance
        """
        self.config = config
        self.permissions = config.permissions
        self._permission_log: list = []

        logger.info("Permission Manager initialized")
        self._log_permissions()

    def _log_permissions(self) -> None:
        """Log current permissions."""
        logger.debug("Current permissions:")
        for action, allowed in self.permissions.items():
            status = "✓ ALLOWED" if allowed else "✗ DENIED"
            logger.debug(f"  {action}: {status}")

    def check_permission(self, action: str) -> bool:
        """Check if an action is permitted.

        Args:
            action: Action identifier (e.g., 'app_launch', 'volume_control')

        Returns:
            True if action is permitted, False otherwise
        """
        allowed = self.permissions.get(action, False)

        # Log all permission checks (including denials)
        self._permission_log.append(
            {"action": action, "allowed": allowed}
        )

        if not allowed:
            logger.warning(f"Permission denied for action: {action}")
        else:
            logger.debug(f"Permission granted for action: {action}")

        return allowed

    def grant_permission(self, action: str) -> None:
        """Grant permission for an action.

        Args:
            action: Action identifier
        """
        self.permissions[action] = True
        logger.info(f"Permission granted: {action}")

    def revoke_permission(self, action: str) -> None:
        """Revoke permission for an action.

        Args:
            action: Action identifier
        """
        self.permissions[action] = False
        logger.info(f"Permission revoked: {action}")

    def get_permission_log(self) -> list:
        """Get permission access log.

        Returns:
            List of permission check records
        """
        return self._permission_log.copy()

    def clear_permission_log(self) -> None:
        """Clear permission log."""
        self._permission_log.clear()
        logger.debug("Permission log cleared")
