"""Intent matching and routing system."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

from jarvis.core.config import ConfigManager
from jarvis.core.logger import logger


@dataclass
class Intent:
    """Represents a matched intent."""

    name: str
    skill_name: str
    action: str
    confidence: float
    parameters: Dict = field(default_factory=dict)


class IntentMatcher:
    """Match user input to intents using pattern matching.

    Supports:
    - Regex pattern matching
    - Parameter extraction
    - Confidence scoring
    - Local LLM integration (optional)
    """

    def __init__(self, config: ConfigManager):
        """Initialize intent matcher.

        Args:
            config: ConfigManager instance
        """
        self.config = config
        self.intents = config.intents
        self.use_llm = config.get("use_local_llm", False)

        if self.use_llm:
            logger.info("Local LLM intent matching enabled")
            self._initialize_llm()

    def _initialize_llm(self) -> None:
        """Initialize local LLM if configured."""
        # TODO: Implement local LLM initialization
        pass

    def match(self, text: str) -> Optional[Intent]:
        """Match input text to an intent.

        Args:
            text: User input text

        Returns:
            Intent object if matched, None otherwise
        """
        text_lower = text.lower().strip()

        best_match = None
        best_score = 0.0

        # Try pattern matching for each intent
        for intent_key, intent_config in self.intents.items():
            score, parameters = self._match_patterns(
                text_lower, intent_config
            )

            if score > best_score:
                best_score = score
                best_match = (intent_key, intent_config, parameters)

        # Check confidence threshold
        if best_score >= self.config.get("intent_confidence_threshold", 0.7):
            intent_key, intent_config, parameters = best_match
            return Intent(
                name=intent_key,
                skill_name=intent_config.get("skill", "unknown"),
                action=intent_config.get("action", "execute"),
                confidence=best_score,
                parameters=parameters,
            )

        logger.debug(
            f"Best match score {best_score} below threshold "
            f"({self.config.get('intent_confidence_threshold')})"
        )
        return None

    def _match_patterns(self, text: str, intent_config: dict) -> tuple:
        """Match text against intent patterns.

        Args:
            text: Input text to match
            intent_config: Intent configuration with patterns

        Returns:
            Tuple of (confidence_score, extracted_parameters)
        """
        patterns = intent_config.get("patterns", [])

        if not patterns:
            return 0.0, {}

        best_score = 0.0
        best_params = {}

        for pattern in patterns:
            score, params = self._match_pattern(text, pattern)
            if score > best_score:
                best_score = score
                best_params = params

        return best_score, best_params

    def _match_pattern(self, text: str, pattern: str) -> tuple:
        """Match text against a single pattern.

        Pattern syntax:
        - {param_name}: Named parameter (captured)
        - [option1|option2]: Optional alternatives
        - Literal text: Exact match required

        Args:
            text: Input text
            pattern: Pattern string

        Returns:
            Tuple of (confidence_score, extracted_parameters)
        """
        # Convert pattern to regex
        regex_pattern, param_names = self._pattern_to_regex(pattern)

        try:
            match = re.search(regex_pattern, text, re.IGNORECASE)
            if match:
                # Extract parameters from groups
                parameters = {}
                for i, param_name in enumerate(param_names, 1):
                    try:
                        parameters[param_name] = match.group(i)
                    except IndexError:
                        pass

                # Confidence based on match quality
                match_ratio = len(match.group(0)) / len(text)
                confidence = min(1.0, match_ratio * 1.2)

                return confidence, parameters
        except Exception as e:
            logger.debug(f"Pattern matching error: {e}")

        return 0.0, {}

    def _pattern_to_regex(self, pattern: str) -> tuple:
        """Convert pattern string to regex.

        Args:
            pattern: Pattern string with {params} and [options]

        Returns:
            Tuple of (regex_pattern, parameter_names)
        """
        param_names = []
        regex_pattern = pattern

        # Extract and replace {param_name}
        for match in re.finditer(r"\{(\w+)\}", pattern):
            param_names.append(match.group(1))
            regex_pattern = regex_pattern.replace(
                match.group(0), r"(\w+)", 1
            )

        # Replace [option1|option2]
        regex_pattern = re.sub(r"\[([^\]]+)\]", r"(?:\1)?", regex_pattern)
        regex_pattern = re.sub(r"\|", r"|" , regex_pattern)

        # Escape special regex chars (but keep our replacements)
        regex_pattern = regex_pattern.replace(r"\w+", "PARAM_PLACEHOLDER")
        regex_pattern = re.escape(regex_pattern)
        regex_pattern = regex_pattern.replace("PARAM_PLACEHOLDER", r"\w+")

        return regex_pattern, param_names
