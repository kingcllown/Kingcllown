"""Base class for all Jarvis skills/plugins."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict

from jarvis.core.logger import logger


@dataclass
class SkillResult:
    """Result of skill execution."""

    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


class BaseSkill(ABC):
    """Base class for all Jarvis skills.

    All custom skills must inherit from this class and implement
    the execute() method.

    Example:
        class MySkill(BaseSkill):
            def __init__(self):
                super().__init__(
                    name="my_skill",
                    description="My custom skill"
                )

            async def execute(self, intent, parameters):
                # Your implementation
                return SkillResult(success=True, message="Done")
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        author: str = "Unknown",
    ):
        """Initialize skill.

        Args:
            name: Unique skill identifier
            description: Human-readable description
            version: Semantic version string
            author: Skill author name
        """
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self._enabled = True

        logger.debug(
            f"Skill initialized: {name} v{version} by {author}"
        )

    @abstractmethod
    async def execute(
        self,
        intent: Any,
        parameters: Dict[str, Any],
    ) -> SkillResult:
        """Execute the skill.

        Args:
            intent: Intent object matched by NLU
            parameters: Extracted parameters from user input

        Returns:
            SkillResult with success status and message
        """
        pass

    def enable(self) -> None:
        """Enable this skill."""
        self._enabled = True
        logger.info(f"Skill enabled: {self.name}")

    def disable(self) -> None:
        """Disable this skill."""
        self._enabled = False
        logger.info(f"Skill disabled: {self.name}")

    def is_enabled(self) -> bool:
        """Check if skill is enabled."""
        return self._enabled

    def get_info(self) -> Dict[str, str]:
        """Get skill metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "enabled": self._enabled,
        }
