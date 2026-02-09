import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.agents.base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

recent_escalations = {}


ESCALATION_REASONS = {
    "complex_issue": "Issue requires human expertise",
    "user_frustrated": "User appears frustrated or unsatisfied",
    "blocked_account": "Account blocked - requires manual review",
    "high_value": "High-value transaction requires approval",
    "compliance": "Compliance or regulatory issue detected",
    "technical_failure": "Technical failure in automated systems"
}


class SlackAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="slack_escalation")
        self.escalation_channel = "#support-escalations"

    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        global recent_escalations

        now = datetime.now()
        cooldown_minutes = 5

        if user_id in recent_escalations:
            last_escalation = recent_escalations[user_id]
            time_since_last = now - last_escalation["timestamp"]

            if time_since_last < timedelta(minutes=cooldown_minutes):
                self.logger.info(f"User {user_id} already has recent ticket: {last_escalation['ticket_id']}")
                response = f"""Sua chamada já foi enviada para nossa equipe de suporte.

📋 **Número do ticket:** {last_escalation['ticket_id']}
⏱️ **Tempo estimado de resposta:** 2 - 3 minutos

Nossa equipe entrará em contato em breve. Por favor, aguarde um momento."""

                return self._create_success_response(
                    response=response,
                    metadata={
                        "escalated": False,
                        "duplicate_prevented": True,
                        "original_ticket_id": last_escalation["ticket_id"],
                        "time_since_last": str(time_since_last)
                    }
                )

        escalation_reason = context.get("reason", "complex_issue") if context else "complex_issue"
        reason_description = ESCALATION_REASONS.get(escalation_reason, "Unknown reason")

        self.logger.warning(
            f"ESCALATION TO HUMAN SUPPORT - "
            f"User: {user_id}, "
            f"Reason: {reason_description}, "
            f"Message: {message[:100]}..."
        )

        ticket_id = self._generate_ticket_id(user_id)

        recent_escalations[user_id] = {
            "ticket_id": ticket_id,
            "timestamp": now
        }

        if len(recent_escalations) > 1000:
            cutoff_time = now - timedelta(hours=24)
            recent_escalations = {
                uid: data for uid, data in recent_escalations.items()
                if data["timestamp"] > cutoff_time
            }
            self.logger.info("Cleaned up old escalations from cache")

        slack_message = self._format_slack_message(
            user_id=user_id,
            message=message,
            reason=reason_description,
            ticket_id=ticket_id,
            metadata=context or {}
        )

        self.logger.info(f"[MOCKED] Would send to Slack {self.escalation_channel}:")
        self.logger.info(slack_message)

        response_to_user = self._generate_user_response(ticket_id, reason_description)

        return self._create_success_response(
            response=response_to_user,
            metadata={
                "escalated": True,
                "ticket_id": ticket_id,
                "reason": escalation_reason,
                "slack_channel": self.escalation_channel,
                "mocked": True
            }
        )

    def _generate_ticket_id(self, user_id: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"SUP-{timestamp}-{user_id[:8]}"

    def _format_slack_message(self, user_id: str, message: str, reason: str, ticket_id: str, metadata: Dict) -> str:
        return f"""
🚨 **Support Escalation** 🚨

**Ticket ID:** {ticket_id}
**User ID:** {user_id}
**Reason:** {reason}
**Timestamp:** {datetime.now().isoformat()}

**User Message:**
{message}

**Metadata:**
{metadata}

**Action Required:**
Please review and respond to this escalation within 1 hour.

---
_Escalated by: CloudWalk Agent Swarm_
"""

    def _generate_user_response(self, ticket_id: str, reason: str) -> str:
        return f"""Entendi sua solicitação. Para garantir o melhor atendimento, estou encaminhando seu caso para nossa equipe de suporte especializada.

📋 **Número do ticket:** {ticket_id}
⏱️ **Tempo estimado de resposta:** 2 - 3 minutos

Nossa equipe entrará em contato em breve. Obrigado pela paciência!"""
