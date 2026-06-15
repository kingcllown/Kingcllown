"""Application management (launch, kill, list)."""

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional

import psutil

from jarvis.core.logger import logger


@dataclass
class AppInfo:
    """Information about a running application."""

    pid: int
    name: str
    exe_path: str
    memory_mb: float


class AppManager:
    """Manage applications - launch, kill, list, monitor."""

    def __init__(self):
        """Initialize app manager."""
        self.platform = sys.platform
        logger.info(f"AppManager initialized for platform: {self.platform}")

    async def launch_app(self, app_name: str) -> bool:
        """Launch an application.

        Args:
            app_name: Application name or path to executable

        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._launch_app_sync, app_name
            )
            logger.info(f"Launched application: {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch app {app_name}: {e}")
            return False

    def _launch_app_sync(self, app_name: str) -> None:
        """Synchronously launch an application."""
        try:
            if self.platform == "win32":
                subprocess.Popen(
                    app_name, shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            elif self.platform == "darwin":  # macOS
                subprocess.Popen(
                    ["open", "-a", app_name]
                )
            else:  # Linux
                subprocess.Popen([app_name])
        except Exception as e:
            raise RuntimeError(f"Failed to launch {app_name}: {e}")

    async def kill_app(self, app_name_or_pid: str) -> bool:
        """Kill a running application.

        Args:
            app_name_or_pid: Application name or PID

        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._kill_app_sync, app_name_or_pid
            )
            logger.info(f"Killed application: {app_name_or_pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to kill app {app_name_or_pid}: {e}")
            return False

    def _kill_app_sync(self, app_name_or_pid: str) -> None:
        """Synchronously kill an application."""
        try:
            # Try as PID first
            if app_name_or_pid.isdigit():
                pid = int(app_name_or_pid)
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)
                return

            # Search by process name
            for proc in psutil.process_iter(["pid", "name"]):
                if app_name_or_pid.lower() in proc.info["name"].lower():
                    process = psutil.Process(proc.info["pid"])
                    process.terminate()
                    process.wait(timeout=5)
                    return

            raise RuntimeError(f"Process not found: {app_name_or_pid}")
        except Exception as e:
            raise RuntimeError(f"Failed to kill {app_name_or_pid}: {e}")

    async def list_running_apps(self) -> List[AppInfo]:
        """List all running applications.

        Returns:
            List of AppInfo objects
        """
        try:
            loop = asyncio.get_event_loop()
            apps = await loop.run_in_executor(
                None, self._list_running_apps_sync
            )
            return apps
        except Exception as e:
            logger.error(f"Failed to list running apps: {e}")
            return []

    def _list_running_apps_sync(self) -> List[AppInfo]:
        """Synchronously list running applications."""
        apps = []
        try:
            for proc in psutil.process_iter(["pid", "name", "exe"]):
                try:
                    info = proc.as_dict()
                    memory = proc.memory_info().rss / (1024 * 1024)  # MB

                    apps.append(
                        AppInfo(
                            pid=info["pid"],
                            name=info["name"],
                            exe_path=info["exe"] or "N/A",
                            memory_mb=memory,
                        )
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"Error listing processes: {e}")

        return apps
