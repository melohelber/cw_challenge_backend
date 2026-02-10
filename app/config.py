from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"
    TAVILY_API_KEY: str
    TAVILY_SEARCH_DEPTH: str = "advanced"
    SECRET_KEY: str

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./data/app.db"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    AGENT_TIMEOUT_SECONDS: int = 30
    CACHE_TTL_HOURS: int = 1

    SESSION_TIMEOUT_MINUTES: int = 5
    SESSION_CLEANUP_INTERVAL_MINUTES: int = 30
    CONVERSATION_HISTORY_PAIRS: int = 5

    TELEGRAM_BOT_TOKEN: str = ""
    BOT_PASSWORD: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def validate_required_keys(self) -> None:
        if not self.ANTHROPIC_API_KEY or self.ANTHROPIC_API_KEY == "sk-ant-your-key-here":
            raise ValueError("ANTHROPIC_API_KEY is required and must be set in .env file")

        if not self.TAVILY_API_KEY or self.TAVILY_API_KEY == "tvly-your-key-here":
            raise ValueError("TAVILY_API_KEY is required and must be set in .env file")

        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")


settings = Settings()
