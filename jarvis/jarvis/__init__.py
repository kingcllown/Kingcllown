"""Jarvis - Advanced Asynchronous Desktop Assistant Framework."""

__version__ = "0.1.0"
__author__ = "Kingcllown"
__description__ = "Professional Turkish desktop assistant with plugin architecture"

from jarvis.core.assistant import JarvisAssistant
from jarvis.plugins.base_skill import BaseSkill

__all__ = ["JarvisAssistant", "BaseSkill"]
