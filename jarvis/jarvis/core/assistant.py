"""Main Jarvis Assistant orchestration and async event loop."""

import asyncio
from typing import Optional

from jarvis.core.config import ConfigManager, get_config
from jarvis.core.logger import logger
from jarvis.nlu.intent_matcher import IntentMatcher
from jarvis.os_control.permission_manager import PermissionManager
from jarvis.plugins.skill_registry import SkillRegistry
from jarvis.speech.stt import SpeechToText
from jarvis.speech.tts import TextToSpeech


class JarvisAssistant:
    """Main Jarvis Assistant class.

    Orchestrates all components:
    - Speech I/O (STT/TTS)
    - NLU (Intent matching)
    - Permission management
    - Skill execution
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Jarvis Assistant.

        Args:
            config_path: Path to configuration YAML file
        """
        self.config = get_config(config_path)
        self.permission_manager = PermissionManager(self.config)
        self.intent_matcher = IntentMatcher(self.config)
        self.skill_registry = SkillRegistry(config=self.config)
        self.stt = SpeechToText(config=self.config)
        self.tts = TextToSpeech(config=self.config)

        self._running = False
        self._tasks: set = set()

        logger.info("Jarvis Assistant initialized")

    async def start(self) -> None:
        """Start the assistant.

        Begins the main event loop and background tasks.
        """
        if self._running:
            logger.warning("Assistant is already running")
            return

        self._running = True
        logger.info("Starting Jarvis Assistant")

        try:
            # Load built-in plugins
            await self.skill_registry.load_builtin_skills()
            logger.info(f"Loaded {len(self.skill_registry.skills)} skills")

            # Start main event loop
            await self._event_loop()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error in main event loop: {e}", exc_info=True)
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the assistant and cleanup resources."""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping Jarvis Assistant")

        # Cancel all running tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Cleanup resources
        await self.stt.cleanup()
        await self.tts.cleanup()

        logger.info("Jarvis Assistant stopped")

    async def _event_loop(self) -> None:
        """Main event loop.

        Continuously listens for voice input and processes intents.
        """
        logger.info("Entering main event loop")
        await self.tts.speak("Jarvis başlatıldı. Size nasıl yardımcı olabilirim?")

        while self._running:
            try:
                # Listen for voice input
                logger.debug("Listening for voice input...")
                text = await self.stt.listen()

                if not text:
                    continue

                logger.info(f"Heard: {text}")

                # Process intent
                await self._process_input(text)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event loop: {e}", exc_info=True)
                await self.tts.speak("Bir hata oluştu. Lütfen tekrar deneyin.")

    async def _process_input(self, text: str) -> None:
        """Process user input through the NLU pipeline.

        Args:
            text: User's spoken or typed input
        """
        try:
            # Step 1: Match intent
            intent = self.intent_matcher.match(text)

            if not intent:
                logger.warning(f"No intent matched for: {text}")
                await self.tts.speak(
                    "Anlamadım. Lütfen tekrar deneyiniz."
                )
                return

            logger.info(f"Matched intent: {intent.name} (confidence: {intent.confidence})")

            # Step 2: Check permissions
            if not self.permission_manager.check_permission(intent.action):
                logger.warning(
                    f"Permission denied for action: {intent.action}"
                )
                await self.tts.speak(
                    f"Bu işlem için yetkiniz yok: {intent.action}"
                )
                return

            # Step 3: Get skill and execute
            skill = self.skill_registry.get_skill(intent.skill_name)

            if not skill:
                logger.error(f"Skill not found: {intent.skill_name}")
                await self.tts.speak(
                    f"Beceri bulunamadı: {intent.skill_name}"
                )
                return

            logger.info(
                f"Executing skill: {skill.name} with action: {intent.action}"
            )

            # Execute skill
            result = await skill.execute(intent, intent.parameters)

            # Provide feedback
            if result.success:
                logger.info(f"Skill execution successful: {result.message}")
                await self.tts.speak(result.message)
            else:
                logger.error(f"Skill execution failed: {result.message}")
                await self.tts.speak(
                    f"Hata: {result.message}"
                )

        except Exception as e:
            logger.error(f"Error processing input: {e}", exc_info=True)
            await self.tts.speak(
                "İşlemi gerçekleştirirken hata oluştu."
            )

    def register_skill(self, skill) -> None:
        """Register a custom skill.

        Args:
            skill: Skill instance (must inherit from BaseSkill)
        """
        self.skill_registry.register(skill)
        logger.info(f"Registered skill: {skill.name}")
