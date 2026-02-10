import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.database.conversation import Conversation
from app.config import settings

logger = logging.getLogger(__name__)


class ConversationService:

    def __init__(self, db: Session):
        self.db = db

    def get_session_history(
        self,
        session_id: str,
        limit_pairs: Optional[int] = None
    ) -> List[Dict[str, str]]:
        limit = limit_pairs or settings.CONVERSATION_HISTORY_PAIRS

        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(
            Conversation.created_at.desc()
        ).limit(limit).all()

        if not conversations:
            return []

        conversations = list(reversed(conversations))

        history = []
        for conv in conversations:
            history.append({
                "role": "user",
                "content": conv.message
            })
            history.append({
                "role": "assistant",
                "content": conv.response
            })

        logger.debug(f"Retrieved {len(conversations)} conversation pairs for session {session_id[:8]}...")
        return history

    def format_history_for_prompt(
        self,
        session_id: str,
        limit_pairs: Optional[int] = None
    ) -> str:
        history = self.get_session_history(session_id, limit_pairs)

        if not history:
            return ""

        lines = ["[CONVERSATION HISTORY - Use ONLY if relevant to current question]"]

        for message in history:
            role = message["role"].capitalize()
            content = message["content"]
            lines.append(f"{role}: {content}")

        lines.append("[END OF HISTORY]")

        formatted = "\n".join(lines)
        logger.debug(f"Formatted history: {len(formatted)} characters")
        return formatted

    def get_last_user_message(self, session_id: str) -> Optional[str]:
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(
            Conversation.created_at.desc()
        ).first()

        return conversation.message if conversation else None

    def get_conversation_count(self, session_id: str) -> int:
        return self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).count()

    def archive_session_conversations(self, session_id: str) -> int:
        count = self.get_conversation_count(session_id)
        logger.info(f"Session {session_id[:8]}... has {count} conversations")
        return count
