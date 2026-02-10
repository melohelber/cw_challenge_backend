import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.database.conversation import Conversation
from app.config import settings

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for retrieving and formatting conversation history"""

    def __init__(self, db: Session):
        self.db = db

    def get_session_history(
        self,
        session_id: str,
        limit_pairs: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session ID to retrieve history for
            limit_pairs: Number of message pairs to retrieve (default: settings.CONVERSATION_HISTORY_PAIRS)

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        limit = limit_pairs or settings.CONVERSATION_HISTORY_PAIRS

        # Get last N conversations for this session
        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(
            Conversation.created_at.desc()
        ).limit(limit).all()

        if not conversations:
            return []

        # Reverse to get chronological order
        conversations = list(reversed(conversations))

        # Format as message pairs
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
        """
        Format conversation history as a string for inclusion in agent prompts.

        Args:
            session_id: Session ID to retrieve history for
            limit_pairs: Number of message pairs to retrieve

        Returns:
            Formatted string with conversation history
        """
        history = self.get_session_history(session_id, limit_pairs)

        if not history:
            return ""

        # Build formatted string
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
        """Get the last user message in a session"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(
            Conversation.created_at.desc()
        ).first()

        return conversation.message if conversation else None

    def get_conversation_count(self, session_id: str) -> int:
        """Get total number of conversations in a session"""
        return self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).count()

    def archive_session_conversations(self, session_id: str) -> int:
        """
        Archive all conversations for a session (future feature).
        Currently just returns count.

        Returns:
            Number of conversations in the session
        """
        count = self.get_conversation_count(session_id)
        logger.info(f"Session {session_id[:8]}... has {count} conversations")
        return count
