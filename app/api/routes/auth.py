import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.services.user_store import UserStore
from app.models.schemas import UserCreate, UserResponse, UserLogin, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"User registration attempt: username={user_data.username}")

    user_store = UserStore(db)

    existing_user = user_store.get_user_by_username(user_data.username)
    if existing_user:
        logger.warning(f"Registration failed: username already exists: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    user = user_store.create_user(
        username=user_data.username,
        password=user_data.password
    )

    if not user:
        logger.error(f"Registration failed: user creation error: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )

    logger.info(f"User registered successfully: id={user.id}, username={user.username}")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"User login attempt: username={credentials.username}")

    user_store = UserStore(db)

    user = user_store.authenticate_user(
        username=credentials.username,
        password=credentials.password
    )

    if not user:
        logger.warning(f"Login failed: invalid credentials: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={
        "sub": str(user.id),
        "username": user.username
    })

    logger.info(f"User logged in successfully: id={user.id}, username={user.username}")
    return TokenResponse(access_token=access_token)
