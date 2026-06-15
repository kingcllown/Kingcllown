"""Speech-to-Text (Turkish) implementation."""

import asyncio
from typing import Optional

import speech_recognition as sr

from jarvis.core.config import ConfigManager
from jarvis.core.logger import logger


class SpeechToText:
    """Turkish Speech-to-Text processor.

    Supports multiple providers:
    - Google Cloud Speech
    - Azure Speech Services
    - Offline recognition (PocketSphinx)
    """

    def __init__(self, config: ConfigManager):
        """Initialize STT.

        Args:
            config: ConfigManager instance
        """
        self.config = config
        self.recognizer = sr.Recognizer()
        self.provider = config.get("stt_provider", "google")
        self.language = config.get("language", "tr-TR")
        self.timeout = config.get("speech_timeout", 10.0)
        self.microphone = sr.Microphone()

        logger.info(f"STT initialized with provider: {self.provider}")

    async def listen(self) -> Optional[str]:
        """Listen for speech input and convert to text.

        Returns:
            Recognized text or None if failed/timeout
        """
        try:
            # Run in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None, self._listen_sync
            )
            return text
        except asyncio.TimeoutError:
            logger.warning("Speech recognition timeout")
            return None
        except Exception as e:
            logger.error(f"STT error: {e}", exc_info=True)
            return None

    def _listen_sync(self) -> Optional[str]:
        """Synchronous speech listening (blocking)."""
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(
                    source, duration=1
                )

                # Listen for audio
                audio = self.recognizer.listen(
                    source, timeout=self.timeout
                )

            # Recognize speech
            if self.provider == "google":
                text = self.recognizer.recognize_google(
                    audio, language=self.language
                )
            elif self.provider == "azure":
                # Azure implementation (requires API key)
                text = self._recognize_azure(audio)
            else:
                # Fallback to Google
                text = self.recognizer.recognize_google(
                    audio, language=self.language
                )

            logger.debug(f"Recognized: {text}")
            return text

        except sr.UnknownValueError:
            logger.warning("Speech not understood")
            return None
        except sr.RequestError as e:
            logger.error(f"STT service error: {e}")
            return None

    def _recognize_azure(self, audio) -> Optional[str]:
        """Recognize speech using Azure Speech Services."""
        # TODO: Implement Azure Speech Services integration
        logger.warning("Azure STT not implemented yet")
        return None

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            self.microphone.__exit__(None, None, None)
        except Exception as e:
            logger.error(f"Error cleaning up STT: {e}")
