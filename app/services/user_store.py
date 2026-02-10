import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.database import User
from app.core.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserStore:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, password: str) -> Optional[User]:
        try:
            hashed_password = hash_password(password)

            user = User(
                username=username,
                hashed_password=hashed_password
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"User created successfully: {username}")
            return user

        except IntegrityError:
            self.db.rollback()
            logger.warning(f"User creation failed: username already exists: {username}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"User creation failed: {str(e)}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_key(self, user_key: str) -> Optional[User]:
        """Get user by public UUID key"""
        return self.db.query(User).filter(User.user_key == user_key).first()

    def get_user_id_from_key(self, user_key: str) -> Optional[int]:
        """Convert public UUID to internal ID for database operations"""
        user = self.get_user_by_key(user_key)
        return user.id if user else None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)

        if not user:
            logger.warning(f"Authentication failed: user not found: {username}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password: {username}")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user
