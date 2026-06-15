"""System diagnostics and information gathering."""

import asyncio
from dataclasses import dataclass

import psutil

from jarvis.core.logger import logger


@dataclass
class SystemStats:
    """System statistics snapshot."""

    cpu_percent: float
    ram_percent: float
    ram_used_mb: float
    ram_available_mb: float
    disk_percent: float
    temperature_celsius: float = None
    battery_percent: float = None


class SystemInfo:
    """Gather system diagnostics and statistics."""

    def __init__(self):
        """Initialize system info gatherer."""
        logger.info("SystemInfo initialized")

    async def get_stats(self) -> SystemStats:
        """Get current system statistics.

        Returns:
            SystemStats object with CPU, RAM, disk, etc.
        """
        try:
            loop = asyncio.get_event_loop()
            stats = await loop.run_in_executor(
                None, self._get_stats_sync
            )
            return stats
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return None

    def _get_stats_sync(self) -> SystemStats:
        """Synchronously gather system statistics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # RAM usage
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_used_mb = ram.used / (1024 * 1024)
            ram_available_mb = ram.available / (1024 * 1024)

            # Disk usage (root)
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Temperature (platform-dependent)
            temp_celsius = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature
                    first_temp_list = list(temps.values())[0]
                    if first_temp_list:
                        temp_celsius = first_temp_list[0].current
            except Exception:
                pass

            # Battery (if available)
            battery_percent = None
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_percent = battery.percent
            except Exception:
                pass

            return SystemStats(
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                ram_used_mb=ram_used_mb,
                ram_available_mb=ram_available_mb,
                disk_percent=disk_percent,
                temperature_celsius=temp_celsius,
                battery_percent=battery_percent,
            )
        except Exception as e:
            logger.error(f"Error gathering system stats: {e}")
            return None

    async def get_cpu_count(self) -> int:
        """Get number of CPU cores."""
        return psutil.cpu_count(logical=True)

    async def get_hostname(self) -> str:
        """Get system hostname."""
        return psutil.os.uname().nodename
