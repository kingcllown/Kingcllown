"""Tests for core Jarvis components."""

import asyncio
import pytest

from jarvis.core.config import ConfigManager, get_config
from jarvis.core.assistant import JarvisAssistant


class TestConfig:
    """Test configuration management."""

    def test_default_config_loading(self):
        """Test loading default configuration."""
        config = get_config()
        assert config is not None
        assert config.config.app_name == "Jarvis"

    def test_permissions_loading(self):
        """Test loading permissions."""
        config = get_config()
        assert config.has_permission("app_launch")
        assert not config.has_permission("file_operations")


class TestAssistant:
    """Test Jarvis Assistant."""

    @pytest.mark.asyncio
    async def test_assistant_initialization(self):
        """Test assistant initialization."""
        assistant = JarvisAssistant()
        assert assistant is not None
        assert assistant.config is not None
        assert not assistant._running

    @pytest.mark.asyncio
    async def test_skill_registration(self):
        """Test skill registration."""
        from jarvis.plugins.base_skill import BaseSkill, SkillResult

        class TestSkill(BaseSkill):
            async def execute(self, intent, parameters):
                return SkillResult(success=True, message="Test")

        assistant = JarvisAssistant()
        skill = TestSkill(name="test", description="Test skill")
        assistant.register_skill(skill)

        retrieved = assistant.skill_registry.get_skill("test")
        assert retrieved is not None
        assert retrieved.name == "test"
