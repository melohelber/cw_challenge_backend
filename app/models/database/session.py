import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        """Initialize session with expiration time (default 5 minutes from creation)"""
        timeout_minutes = kwargs.pop('timeout_minutes', 5)
        super().__init__(*args, **kwargs)

        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)

    def is_expired(self) -> bool:
        """Check if session is expired based on expires_at timestamp"""
        return datetime.utcnow() > self.expires_at

    def update_activity(self, timeout_minutes: int = 5):
        """Update last activity timestamp and extend expiration"""
        self.last_activity_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)

    def end(self):
        """Mark session as inactive"""
        self.is_active = False

    def __repr__(self):
        return f"<Session(session_id={self.session_id[:8]}..., user_id={self.user_id}, is_active={self.is_active})>"
