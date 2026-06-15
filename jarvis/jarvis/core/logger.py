"""Centralized logging configuration for Jarvis."""

import sys
from pathlib import Path
from loguru import logger

# Create logs directory
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Console handler (stdout)
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)

# File handler
logger.add(
    logs_dir / "jarvis.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="500 MB",
    retention="10 days",
)

# Error file handler
logger.add(
    logs_dir / "jarvis_errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="500 MB",
)

__all__ = ["logger"]
