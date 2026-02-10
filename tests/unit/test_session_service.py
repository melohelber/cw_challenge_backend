import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.database.user import User
from app.models.database.session import Session as SessionModel
from app.models.database.conversation import Conversation
from app.services.session_service import SessionService
from app.services.conversation_service import ConversationService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create a test user
    user = User(
        username="testuser",
        hashed_password="hashedpassword123",
        is_active=True
    )
    session.add(user)
    session.commit()

    yield session

    session.close()


class TestSessionService:
    def test_create_new_session(self, db_session):
        """Test creating a new session for a user"""
        service = SessionService(db_session)

        # Get user_id
        user = db_session.query(User).filter(User.username == "testuser").first()

        # Create session
        session = service.get_or_create_active_session(user.id, timeout_minutes=5)

        assert session is not None
        assert session.user_id == user.id
        assert session.is_active is True
        assert session.session_id is not None
        assert session.expires_at > datetime.utcnow()

    def test_reuse_active_session(self, db_session):
        """Test that active session is reused instead of creating new one"""
        service = SessionService(db_session)
        user = db_session.query(User).first()

        # Create first session
        session1 = service.get_or_create_active_session(user.id)
        session1_id = session1.session_id

        # Try to get session again
        session2 = service.get_or_create_active_session(user.id)

        assert session2.session_id == session1_id
        assert session2.id == session1.id

    def test_session_expiration(self, db_session):
        """Test that expired sessions are not reused"""
        service = SessionService(db_session)
        user = db_session.query(User).first()

        # Create session with very short timeout
        session1 = service.get_or_create_active_session(user.id, timeout_minutes=0)

        # Manually expire the session
        session1.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db_session.commit()

        # Get session again - should create new one
        session2 = service.get_or_create_active_session(user.id)

        assert session2.session_id != session1.session_id

    def test_update_session_activity(self, db_session):
        """Test updating session activity timestamp"""
        service = SessionService(db_session)
        user = db_session.query(User).first()

        # Create session
        session = service.get_or_create_active_session(user.id)
        original_activity = session.last_activity_at
        original_expires = session.expires_at

        # Wait a tiny bit and update activity
        import time
        time.sleep(0.1)

        success = service.update_session_activity(session.session_id)

        assert success is True

        # Refresh from DB
        db_session.refresh(session)

        assert session.last_activity_at > original_activity
        assert session.expires_at > original_expires

    def test_end_session(self, db_session):
        """Test explicitly ending a session"""
        service = SessionService(db_session)
        user = db_session.query(User).first()

        # Create session
        session = service.get_or_create_active_session(user.id)
        session_id = session.session_id

        # End session
        success = service.end_session(session_id)
        assert success is True

        # Verify session is inactive
        db_session.refresh(session)
        assert session.is_active is False

    def test_cleanup_expired_sessions(self, db_session):
        """Test cleanup of expired sessions"""
        service = SessionService(db_session)
        user = db_session.query(User).first()

        # Create multiple sessions
        session1 = service.get_or_create_active_session(user.id)
        session1.is_active = True
        session1.expires_at = datetime.utcnow() - timedelta(minutes=10)  # Expired

        # Create another active but not expired session
        session2 = SessionModel(user_id=user.id, timeout_minutes=5)
        session2.is_active = True
        db_session.add(session2)
        db_session.commit()

        # Run cleanup
        cleaned_count = service.cleanup_expired_sessions()

        assert cleaned_count == 1

        # Verify session1 is now inactive
        db_session.refresh(session1)
        assert session1.is_active is False

        # Verify session2 is still active
        db_session.refresh(session2)
        assert session2.is_active is True


class TestConversationService:
    def test_get_session_history_empty(self, db_session):
        """Test getting history for session with no conversations"""
        service = ConversationService(db_session)

        history = service.get_session_history("nonexistent-session-id")

        assert history == []

    def test_get_session_history_with_conversations(self, db_session):
        """Test getting conversation history for a session"""
        user = db_session.query(User).first()

        # Create session
        session = SessionModel(user_id=user.id, timeout_minutes=5)
        db_session.add(session)
        db_session.commit()

        # Add conversations
        conv1 = Conversation(
            session_id=session.session_id,
            user_id=user.id,
            message="What is Pix?",
            response="Pix is a Brazilian payment system.",
            agent_used="knowledge"
        )
        conv2 = Conversation(
            session_id=session.session_id,
            user_id=user.id,
            message="What is the fee?",
            response="The fee is R$0.99.",
            agent_used="knowledge"
        )
        db_session.add_all([conv1, conv2])
        db_session.commit()

        # Get history
        service = ConversationService(db_session)
        history = service.get_session_history(session.session_id, limit_pairs=5)

        assert len(history) == 4  # 2 pairs = 4 messages (user + assistant × 2)
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "What is Pix?"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Pix is a Brazilian payment system."

    def test_format_history_for_prompt(self, db_session):
        """Test formatting history as string for prompts"""
        user = db_session.query(User).first()

        # Create session
        session = SessionModel(user_id=user.id, timeout_minutes=5)
        db_session.add(session)
        db_session.commit()

        # Add conversation
        conv = Conversation(
            session_id=session.session_id,
            user_id=user.id,
            message="Hello",
            response="Hi there!",
            agent_used="knowledge"
        )
        db_session.add(conv)
        db_session.commit()

        # Format history
        service = ConversationService(db_session)
        formatted = service.format_history_for_prompt(session.session_id)

        assert "[CONVERSATION HISTORY" in formatted
        assert "[END OF HISTORY]" in formatted
        assert "User: Hello" in formatted
        assert "Assistant: Hi there!" in formatted

    def test_history_limit(self, db_session):
        """Test that history respects limit_pairs parameter"""
        user = db_session.query(User).first()

        # Create session
        session = SessionModel(user_id=user.id, timeout_minutes=5)
        db_session.add(session)
        db_session.commit()

        # Add 5 conversation pairs (10 messages)
        for i in range(5):
            conv = Conversation(
                session_id=session.session_id,
                user_id=user.id,
                message=f"Question {i}",
                response=f"Answer {i}",
                agent_used="knowledge"
            )
            db_session.add(conv)
        db_session.commit()

        # Get history with limit of 2 pairs
        service = ConversationService(db_session)
        history = service.get_session_history(session.session_id, limit_pairs=2)

        # Should return last 2 pairs = 4 messages
        assert len(history) == 4
