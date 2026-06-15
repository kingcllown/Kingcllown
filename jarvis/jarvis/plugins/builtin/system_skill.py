"""System control skill - app launching, volume, diagnostics."""

from typing import Any, Dict

from jarvis.os_control.app_manager import AppManager
from jarvis.os_control.audio_manager import AudioManager
from jarvis.os_control.system_info import SystemInfo
from jarvis.plugins.base_skill import BaseSkill, SkillResult


class SystemSkill(BaseSkill):
    """Built-in skill for system-level operations.

    Supports:
    - Launch/kill applications
    - Volume control
    - System diagnostics (CPU, RAM, disk)
    """

    def __init__(self):
        """Initialize system skill."""
        super().__init__(
            name="system_skill",
            description="System control operations (apps, volume, diagnostics)",
            version="1.0.0",
            author="Jarvis Framework",
        )
        self.app_manager = AppManager()
        self.audio_manager = AudioManager()
        self.system_info = SystemInfo()

    async def execute(
        self,
        intent: Any,
        parameters: Dict[str, Any],
    ) -> SkillResult:
        """Execute system operation.

        Args:
            intent: Matched intent
            parameters: Extracted parameters

        Returns:
            SkillResult with execution status
        """
        action = intent.action

        if action == "launch_app":
            return await self._launch_app(parameters)
        elif action == "kill_app":
            return await self._kill_app(parameters)
        elif action == "set_volume":
            return await self._set_volume(parameters)
        elif action == "get_volume":
            return await self._get_volume(parameters)
        elif action == "get_system_stats":
            return await self._get_system_stats(parameters)
        else:
            return SkillResult(
                success=False,
                message=f"Unknown action: {action}",
            )

    async def _launch_app(self, parameters: Dict) -> SkillResult:
        """Launch an application."""
        app_name = parameters.get("app_name")
        if not app_name:
            return SkillResult(
                success=False,
                message="App name not specified",
            )

        success = await self.app_manager.launch_app(app_name)
        message = (
            f"{app_name} açılıyor..."
            if success
            else f"{app_name} açılamadı"
        )
        return SkillResult(success=success, message=message)

    async def _kill_app(self, parameters: Dict) -> SkillResult:
        """Kill an application."""
        app_name = parameters.get("app_name")
        if not app_name:
            return SkillResult(
                success=False,
                message="App name not specified",
            )

        success = await self.app_manager.kill_app(app_name)
        message = (
            f"{app_name} kapatıldı"
            if success
            else f"{app_name} kapatılamadı"
        )
        return SkillResult(success=success, message=message)

    async def _set_volume(self, parameters: Dict) -> SkillResult:
        """Set system volume."""
        level = parameters.get("level")
        if level is None:
            return SkillResult(
                success=False,
                message="Volume level not specified",
            )

        try:
            level = int(level)
            success = await self.audio_manager.set_volume(level)
            message = (
                f"Ses seviyesi {level}% olarak ayarlandı"
                if success
                else "Ses seviyesi ayarlanamadı"
            )
            return SkillResult(success=success, message=message)
        except ValueError:
            return SkillResult(
                success=False,
                message="Invalid volume level",
            )

    async def _get_volume(self, parameters: Dict) -> SkillResult:
        """Get current volume level."""
        volume = await self.audio_manager.get_volume()
        if volume is not None:
            message = f"Ses seviyesi: {volume}%"
            return SkillResult(success=True, message=message)
        return SkillResult(
            success=False,
            message="Ses seviyesi alınamadı",
        )

    async def _get_system_stats(self, parameters: Dict) -> SkillResult:
        """Get system diagnostics."""
        stats = await self.system_info.get_stats()
        if not stats:
            return SkillResult(
                success=False,
                message="Sistem bilgisi alınamadı",
            )

        message = (
            f"CPU: {stats.cpu_percent}%, "
            f"RAM: {stats.ram_percent}% "
            f"({stats.ram_used_mb:.0f}MB/{stats.ram_available_mb:.0f}MB), "
            f"Disk: {stats.disk_percent}%"
        )
        if stats.battery_percent is not None:
            message += f", Pil: {stats.battery_percent}%"

        return SkillResult(
            success=True,
            message=message,
            data={
                "cpu_percent": stats.cpu_percent,
                "ram_percent": stats.ram_percent,
                "disk_percent": stats.disk_percent,
                "battery_percent": stats.battery_percent,
            },
        )
