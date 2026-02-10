import logging
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.core.database import get_db
from app.utils.logging import mask_user_key

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Validate JWT and return user_key (UUID)"""
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        logger.warning("JWT validation failed: invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_key = payload.get("sub")
    if user_key is None:
        logger.warning("JWT validation failed: missing user_key in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate UUID format
    try:
        uuid.UUID(user_key)
    except (ValueError, AttributeError):
        logger.warning(f"JWT validation failed: invalid user_key format: {mask_user_key(user_key)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"JWT validated successfully: user_key={mask_user_key(user_key)}")
    return user_key
