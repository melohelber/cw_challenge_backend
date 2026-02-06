import logging
import sys
from typing import Any, Dict, Optional


def setup_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def mask_api_key(api_key: str) -> str:
    if not api_key or len(api_key) < 8:
        return "***"
    return f"{api_key[:7]}***{api_key[-4:]}"


def log_request(user_id: str, endpoint: str, **kwargs: Any) -> None:
    logger = logging.getLogger("api")

    context_parts = [f"{k}={v}" for k, v in kwargs.items() if v is not None]
    context = f" ({', '.join(context_parts)})" if context_parts else ""

    logger.info(f"User [{user_id}] called {endpoint}{context}")


def log_error(user_id: str, endpoint: str, error: Exception) -> None:
    logger = logging.getLogger("api")
    logger.error(f"User [{user_id}] failed {endpoint}: {str(error)}")
