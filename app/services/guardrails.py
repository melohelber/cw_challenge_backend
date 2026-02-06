import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GuardrailResult:
    allowed: bool
    reason: Optional[str] = None
    severity: str = "low"
    should_escalate: bool = False


class GuardrailsService:
    def __init__(self):
        self.blocked_keywords = [
            "illegal", "hack", "fraud", "scam", "steal", "bomb",
            "violence", "weapon", "drug", "terrorism"
        ]

        self.allowed_topics = [
            "payment", "pix", "transfer", "card", "account", "transaction",
            "fee", "limit", "maquininha", "pdv", "tap to pay", "infinitepay",
            "help", "support", "status", "blocked", "failed"
        ]

        self.prompt_injection_patterns = [
            "ignore previous",
            "ignore all",
            "forget everything",
            "new instructions",
            "system prompt",
            "you are now",
            "act as if",
            "pretend you are"
        ]

    def check(self, message: str) -> GuardrailResult:
        message_lower = message.lower()

        if self._check_blocked_content(message_lower):
            logger.warning(f"Blocked message due to inappropriate content: {message[:50]}...")
            return GuardrailResult(
                allowed=False,
                reason="Message contains inappropriate or illegal content",
                severity="high"
            )

        if self._check_prompt_injection(message_lower):
            logger.warning(f"Potential prompt injection detected: {message[:50]}...")
            return GuardrailResult(
                allowed=False,
                reason="Message appears to contain prompt injection attempt",
                severity="high"
            )

        if self._check_spam(message):
            logger.warning(f"Spam-like message detected: {message[:50]}...")
            return GuardrailResult(
                allowed=False,
                reason="Message appears to be spam",
                severity="medium"
            )

        if self._check_excessive_off_topic(message_lower):
            logger.info(f"Off-topic message detected: {message[:50]}...")
            return GuardrailResult(
                allowed=True,
                reason="Message is off-topic but allowed",
                severity="low"
            )

        logger.debug("Message passed all guardrail checks")
        return GuardrailResult(allowed=True)

    def _check_blocked_content(self, message_lower: str) -> bool:
        return any(keyword in message_lower for keyword in self.blocked_keywords)

    def _check_prompt_injection(self, message_lower: str) -> bool:
        return any(pattern in message_lower for pattern in self.prompt_injection_patterns)

    def _check_spam(self, message: str) -> bool:
        if len(message) > 2000:
            return True

        repeated_chars = any(char * 10 in message for char in "!@#$%*")
        if repeated_chars:
            return True

        return False

    def _check_excessive_off_topic(self, message_lower: str) -> bool:
        has_any_relevant_topic = any(
            topic in message_lower for topic in self.allowed_topics
        )

        if not has_any_relevant_topic and len(message_lower) > 100:
            return True

        return False
