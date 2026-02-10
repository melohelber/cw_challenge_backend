import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.agents import RouterAgent, KnowledgeAgent, SupportAgent, SlackAgent
from app.services.guardrails import GuardrailsService
from app.services.user_store import UserStore
from app.services.session_service import SessionService
from app.services.conversation_service import ConversationService
from app.models.database.conversation import Conversation
from app.utils.logging import sanitize_message_for_log, mask_user_key

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

    async def process_message(self, message: str, user_key: str, db: Session) -> Dict[str, Any]:
        user_store = UserStore(db)
        user_id = user_store.get_user_id_from_key(user_key)

        if not user_id:
            logger.error(f"User not found for key: {mask_user_key(user_key)}")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Processing message for user {mask_user_key(user_key)}: {sanitize_message_for_log(message, 100)}")

        session_service = SessionService(db)
        conversation_service = ConversationService(db)

        session = session_service.get_or_create_active_session(user_id)
        session_id = session.session_id

        history_formatted = conversation_service.format_history_for_prompt(session_id)

        logger.info(f"Session {session_id[:8]}... | History length: {len(history_formatted)} chars")

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

        routing_result = await self.router.process(message, user_key)

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

        if target_route == "ESCALATE":
            logger.info("User requested escalation, calling Slack Agent directly")
            escalation_result = await self.slack.process(
                message,
                user_key,
                context={
                    "reason": "user_request",
                    "history": history_formatted,
                    "session_id": session_id
                }
            )
            response_text = escalation_result.response
            agent_used = "slack_escalation"
            metadata = escalation_result.metadata
        else:
            target_agent = self.agents.get(target_route)
            if not target_agent:
                logger.error(f"Unknown route: {target_route}")
                target_agent = self.agents["GENERAL"]

            agent_result = await target_agent.process(
                message,
                user_key,
                context={
                    "route": target_route,
                    "history": history_formatted,
                    "session_id": session_id
                }
            )

            if not agent_result.success:
                logger.error(f"Agent {target_route} failed: {agent_result.error}")

                escalation_result = await self.slack.process(
                    message,
                    user_key,
                    context={
                        "reason": "technical_failure",
                        "original_error": agent_result.error,
                        "history": history_formatted,
                        "session_id": session_id
                    }
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
            session_id=session_id,
            user_id=user_id,
            message=message,
            response=response_text,
            agent_used=agent_used
        )

        session_service.update_session_activity(session_id)

        return {
            "response": response_text,
            "agent_used": agent_used,
            "confidence": routing_result.metadata.get("confidence"),
            "metadata": {
                **metadata,
                "session_id": session_id[:8] + "..."
            }
        }

    def _save_conversation(
        self,
        db: Session,
        session_id: str,
        user_id: int,
        message: str,
        response: str,
        agent_used: str
    ) -> None:
        try:
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id,
                message=message,
                response=response,
                agent_used=agent_used
            )
            db.add(conversation)
            db.commit()
            logger.info(f"Conversation saved | session={session_id[:8]}... | user_id={user_id}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            db.rollback()
