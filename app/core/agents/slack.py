import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.agents.base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


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
        escalation_reason = context.get("reason", "complex_issue") if context else "complex_issue"
        reason_description = ESCALATION_REASONS.get(escalation_reason, "Unknown reason")

        self.logger.warning(
            f"ESCALATION TO HUMAN SUPPORT - "
            f"User: {user_id}, "
            f"Reason: {reason_description}, "
            f"Message: {message[:100]}..."
        )

        ticket_id = self._generate_ticket_id(user_id)

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
⏱️ **Tempo estimado de resposta:** 1-2 horas

Nossa equipe entrará em contato em breve. Obrigado pela paciência!"""
