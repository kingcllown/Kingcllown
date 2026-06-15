"""Skill/plugin registration and discovery system."""

import asyncio
import importlib.util
from pathlib import Path
from typing import Dict, Optional

from jarvis.core.config import ConfigManager
from jarvis.core.logger import logger
from jarvis.plugins.base_skill import BaseSkill


class SkillRegistry:
    """Registry for skill discovery, loading, and management."""

    def __init__(self, config: ConfigManager):
        """Initialize skill registry.

        Args:
            config: ConfigManager instance
        """
        self.config = config
        self.skills: Dict[str, BaseSkill] = {}
        logger.info("Skill Registry initialized")

    def register(self, skill: BaseSkill) -> bool:
        """Register a skill.

        Args:
            skill: BaseSkill instance

        Returns:
            True if registered successfully, False otherwise
        """
        if not isinstance(skill, BaseSkill):
            logger.error(f"Invalid skill type: {type(skill)}")
            return False

        if skill.name in self.skills:
            logger.warning(f"Skill already registered: {skill.name}")
            return False

        self.skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")
        return True

    def unregister(self, skill_name: str) -> bool:
        """Unregister a skill.

        Args:
            skill_name: Name of skill to unregister

        Returns:
            True if unregistered, False if not found
        """
        if skill_name in self.skills:
            del self.skills[skill_name]
            logger.info(f"Unregistered skill: {skill_name}")
            return True
        return False

    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """Get a registered skill by name.

        Args:
            skill_name: Name of skill to retrieve

        Returns:
            Skill instance or None if not found
        """
        return self.skills.get(skill_name)

    def list_skills(self) -> Dict[str, dict]:
        """List all registered skills.

        Returns:
            Dictionary of skill metadata
        """
        return {name: skill.get_info() for name, skill in self.skills.items()}

    async def load_builtin_skills(self) -> None:
        """Load built-in skills from plugins/builtin directory."""
        plugin_dir = (
            Path(__file__).parent / "builtin"
        )

        if not plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {plugin_dir}")
            return

        # Dynamically load skill modules
        for skill_file in plugin_dir.glob("*_skill.py"):
            if skill_file.name.startswith("__"):
                continue

            try:
                await self._load_skill_module(skill_file)
            except Exception as e:
                logger.error(
                    f"Failed to load skill {skill_file.name}: {e}",
                    exc_info=True,
                )

    async def _load_skill_module(self, module_path: Path) -> None:
        """Dynamically load a skill module.

        Args:
            module_path: Path to skill module
        """
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self._load_skill_module_sync, module_path
        )

    def _load_skill_module_sync(self, module_path: Path) -> None:
        """Synchronously load skill module."""
        spec = importlib.util.spec_from_file_location(
            module_path.stem, module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find and register skill classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseSkill)
                and attr is not BaseSkill
            ):
                try:
                    skill_instance = attr()
                    self.register(skill_instance)
                except Exception as e:
                    logger.error(
                        f"Failed to instantiate skill {attr_name}: {e}"
                    )
