import logging
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from app.core.agents.base import BaseAgent, AgentResponse
from app.config import settings
from app.utils.logging import sanitize_message_for_log, mask_user_key

logger = logging.getLogger(__name__)


ROUTING_PROMPT = """You are a routing assistant for InfinitePay, a Brazilian payment processing company.

Analyze the user's message and classify it into ONE of these categories:

1. KNOWLEDGE - Questions about InfinitePay products, services, features, or general information
   Examples:
   - "What are the fees for Pix transactions?"
   - "How does the maquininha work?"
   - "Tell me about InfinitePay's payment solutions"
   - "What is Tap to Pay?"
   - "How do I integrate with the API?"

2. SUPPORT - Customer support requests, account issues, troubleshooting
   Examples:
   - "Why can't I send money?"
   - "My transfer failed"
   - "What's my account status?"
   - "Show my transaction history"
   - "Is my account blocked?"

3. ESCALATE - User explicitly wants to talk to a human agent or open a support ticket
   Examples:
   - "I want to talk to a human"
   - "Speak with a support agent"
   - "Open a ticket"
   - "Escalate this issue"
   - "I need urgent help"
   - "Connect me to technical support"
   - "Let me talk to someone"

4. GENERAL - Off-topic questions not related to InfinitePay or payments
   Examples:
   - "What's the weather?"
   - "Who won the game?"
   - "Tell me a joke"
   - "What's 2+2?"

User message: {message}

Respond with ONLY ONE WORD: KNOWLEDGE, SUPPORT, ESCALATE, or GENERAL

Your response:"""


class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="router")
        self.llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.0,
            max_tokens=10
        )
        self.prompt = ChatPromptTemplate.from_template(ROUTING_PROMPT)
        self.chain = self.prompt | self.llm

    async def process(self, message: str, user_key: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        self.logger.info(f"Routing message for user {mask_user_key(user_key)}: {sanitize_message_for_log(message, 100)}")

        try:
            result = await self.chain.ainvoke({"message": message})
            route = result.content.strip().upper()

            if route not in ["KNOWLEDGE", "SUPPORT", "ESCALATE", "GENERAL"]:
                self.logger.warning(f"Invalid route returned: {route}, defaulting to GENERAL")
                route = "GENERAL"

            self.logger.info(f"Routed to: {route}")

            return self._create_success_response(
                response=route,
                metadata={
                    "route": route,
                    "confidence": "high"
                }
            )

        except Exception as e:
            self.logger.error(f"Error routing message: {str(e)}")
            return self._create_error_response(
                error=f"Routing failed: {str(e)}",
                metadata={"fallback_route": "GENERAL"}
            )
