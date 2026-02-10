import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.database.session import Session as SessionModel
from app.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions with timeout and activity tracking"""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_active_session(
        self,
        user_id: int,
        timeout_minutes: Optional[int] = None
    ) -> SessionModel:
        """
        Get existing active session for user or create a new one.

        Args:
            user_id: Internal user ID
            timeout_minutes: Session timeout in minutes (defaults to settings.SESSION_TIMEOUT_MINUTES)

        Returns:
            Active SessionModel instance
        """
        timeout = timeout_minutes or settings.SESSION_TIMEOUT_MINUTES

        # Try to find active session that hasn't expired
        existing_session = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True,
            SessionModel.expires_at > datetime.utcnow()
        ).first()

        if existing_session:
            logger.info(f"Found active session for user_id={user_id}: {existing_session.session_id[:8]}...")
            # Update activity timestamp and extend expiration
            existing_session.update_activity(timeout_minutes=timeout)
            self.db.commit()
            return existing_session

        # No active session found, create new one
        new_session = SessionModel(
            user_id=user_id,
            timeout_minutes=timeout
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)

        logger.info(f"Created new session for user_id={user_id}: {new_session.session_id[:8]}...")
        return new_session

    def get_session_by_id(self, session_id: str) -> Optional[SessionModel]:
        """Get session by session_id"""
        return self.db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

    def update_session_activity(
        self,
        session_id: str,
        timeout_minutes: Optional[int] = None
    ) -> bool:
        """
        Update session activity timestamp and extend expiration.

        Returns:
            True if session was updated, False if not found
        """
        timeout = timeout_minutes or settings.SESSION_TIMEOUT_MINUTES

        session = self.get_session_by_id(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id[:8]}...")
            return False

        session.update_activity(timeout_minutes=timeout)
        self.db.commit()

        logger.debug(f"Updated activity for session: {session_id[:8]}...")
        return True

    def is_session_expired(self, session_id: str) -> bool:
        """
        Check if session is expired.

        Returns:
            True if expired or not found, False if still active
        """
        session = self.get_session_by_id(session_id)
        if not session:
            return True

        return session.is_expired()

    def end_session(self, session_id: str) -> bool:
        """
        Mark session as inactive (explicit end).

        Returns:
            True if session was ended, False if not found
        """
        session = self.get_session_by_id(session_id)
        if not session:
            logger.warning(f"Cannot end session, not found: {session_id[:8]}...")
            return False

        session.end()
        self.db.commit()

        logger.info(f"Session ended: {session_id[:8]}...")
        return True

    def cleanup_expired_sessions(self) -> int:
        """
        Mark all expired sessions as inactive.

        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()

        expired_sessions = self.db.query(SessionModel).filter(
            SessionModel.is_active == True,
            SessionModel.expires_at <= now
        ).all()

        count = 0
        for session in expired_sessions:
            session.end()
            count += 1

        if count > 0:
            self.db.commit()
            logger.info(f"Cleaned up {count} expired sessions")

        return count

    def get_user_active_session_count(self, user_id: int) -> int:
        """Get count of active sessions for a user"""
        return self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True,
            SessionModel.expires_at > datetime.utcnow()
        ).count()
