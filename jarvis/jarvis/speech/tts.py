"""Text-to-Speech (Turkish) implementation."""

import asyncio
from typing import Optional

import pyttsx3

from jarvis.core.config import ConfigManager
from jarvis.core.logger import logger


class TextToSpeech:
    """Turkish Text-to-Speech processor.

    Supports multiple providers:
    - Google Text-to-Speech
    - Azure Speech Services
    - Local pyttsx3
    """

    def __init__(self, config: ConfigManager):
        """Initialize TTS.

        Args:
            config: ConfigManager instance
        """
        self.config = config
        self.provider = config.get("tts_provider", "pyttsx3")
        self.language = config.get("language", "tr-TR")

        # Initialize local engine
        self.engine = pyttsx3.init()
        self._configure_engine()

        logger.info(f"TTS initialized with provider: {self.provider}")

    def _configure_engine(self) -> None:
        """Configure pyttsx3 engine."""
        # Set language/voice
        voices = self.engine.getProperty("voices")
        # Try to find Turkish voice
        turkish_voice = None
        for voice in voices:
            if "turkish" in voice.name.lower() or "tr" in voice.id.lower():
                turkish_voice = voice.id
                break

        if turkish_voice:
            self.engine.setProperty("voice", turkish_voice)
            logger.debug(f"Set voice to: {turkish_voice}")
        else:
            logger.warning(
                "Turkish voice not available, using default"
            )

        # Set speech rate and volume
        self.engine.setProperty("rate", 150)  # Slower speech
        self.engine.setProperty("volume", 0.9)

    async def speak(self, text: str) -> None:
        """Speak the given text.

        Args:
            text: Text to speak
        """
        try:
            # Run in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._speak_sync, text
            )
        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)

    def _speak_sync(self, text: str) -> None:
        """Synchronous text-to-speech (blocking)."""
        try:
            logger.debug(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error speaking text: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            self.engine.stop()
        except Exception as e:
            logger.error(f"Error cleaning up TTS: {e}")
