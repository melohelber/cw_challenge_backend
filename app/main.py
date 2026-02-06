import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logging import setup_logging, mask_api_key
from app.core.database import create_tables
from app.models.database import User, Conversation
from app.api.routes import auth, chat

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.LOG_LEVEL)

    logger.info("=" * 60)
    logger.info("CloudWalk Agent Swarm - Starting up...")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    try:
        settings.validate_required_keys()
        logger.info(f"Anthropic API Key: {mask_api_key(settings.ANTHROPIC_API_KEY)}")
        logger.info(f"Tavily API Key: {mask_api_key(settings.TAVILY_API_KEY)}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise

    try:
        create_tables()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    logger.info("=" * 60)
    logger.info("Application started successfully!")
    logger.info(f"API Documentation: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    logger.info("Shutting down CloudWalk Agent Swarm...")


app = FastAPI(
    title="CloudWalk Agent Swarm API",
    description="Multi-agent system for InfinitePay customer support and knowledge management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "CloudWalk Agent Swarm API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
