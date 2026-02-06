import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.agents import RouterAgent, KnowledgeAgent, SupportAgent, SlackAgent
from app.services.guardrails import GuardrailsService
from app.models.database.conversation import Conversation

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self):
        self.guardrails = GuardrailsService()
        self.router = RouterAgent()
        self.agents = {
            "KNOWLEDGE": KnowledgeAgent(),
            "SUPPORT": SupportAgent(),
            "GENERAL": KnowledgeAgent(),
        }
        self.slack = SlackAgent()

    async def process_message(self, message: str, user_id: str, db: Session) -> Dict[str, Any]:
        logger.info(f"Processing message for user {user_id}: {message[:100]}...")

        guardrail_result = self.guardrails.check(message)
        if not guardrail_result.allowed:
            logger.warning(f"Message blocked by guardrails: {guardrail_result.reason}")
            return {
                "response": f"Desculpe, não posso processar esta mensagem. Motivo: {guardrail_result.reason}",
                "agent_used": "guardrails",
                "confidence": None,
                "metadata": {
                    "blocked": True,
                    "reason": guardrail_result.reason,
                    "severity": guardrail_result.severity
                }
            }

        routing_result = await self.router.process(message, user_id)

        if not routing_result.success:
            logger.error(f"Routing failed: {routing_result.error}")
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.",
                "agent_used": "error",
                "confidence": None,
                "metadata": {"error": routing_result.error}
            }

        target_route = routing_result.response
        logger.info(f"Routed to: {target_route}")

        target_agent = self.agents.get(target_route)
        if not target_agent:
            logger.error(f"Unknown route: {target_route}")
            target_agent = self.agents["GENERAL"]

        agent_result = await target_agent.process(message, user_id)

        if not agent_result.success:
            logger.error(f"Agent {target_route} failed: {agent_result.error}")

            escalation_result = await self.slack.process(
                message,
                user_id,
                context={"reason": "technical_failure", "original_error": agent_result.error}
            )

            response_text = escalation_result.response
            agent_used = "slack_escalation"
            metadata = escalation_result.metadata
        else:
            response_text = agent_result.response
            agent_used = target_route.lower()
            metadata = agent_result.metadata or {}

        self._save_conversation(
            db=db,
            user_id=user_id,
            message=message,
            response=response_text,
            agent_used=agent_used
        )

        return {
            "response": response_text,
            "agent_used": agent_used,
            "confidence": routing_result.metadata.get("confidence"),
            "metadata": metadata
        }

    def _save_conversation(
        self,
        db: Session,
        user_id: str,
        message: str,
        response: str,
        agent_used: str
    ) -> None:
        try:
            conversation = Conversation(
                user_id=int(user_id),
                message=message,
                response=response,
                agent_used=agent_used
            )
            db.add(conversation)
            db.commit()
            logger.info(f"Conversation saved for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            db.rollback()
