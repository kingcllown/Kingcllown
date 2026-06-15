#!/usr/bin/env python3
"""Jarvis Desktop Assistant - Entry Point."""

import asyncio
import sys
from pathlib import Path

from jarvis.core.assistant import JarvisAssistant
from jarvis.core.logger import logger


async def main():
    """Main entry point."""
    try:
        # Initialize assistant
        config_path = Path(__file__).parent / "config" / "default.yaml"
        assistant = JarvisAssistant(config_path=str(config_path))

        # Register custom skills here
        # example: assistant.register_skill(MyCustomSkill())

        # Start the assistant
        await assistant.start()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
