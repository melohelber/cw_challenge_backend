import logging
import sys
import re
from typing import Any, Dict, Optional


def setup_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    for name in list(logging.Logger.manager.loggerDict.keys()):
        existing_logger = logging.getLogger(name)
        existing_logger.handlers.clear()
        existing_logger.propagate = True

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
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


def sanitize_message_for_log(message: str, max_length: int = 100) -> str:
    clean_message = re.sub(
        r'\[User\'?s?\s+real\s+first\s+name\s+is:.*?\]',
        '',
        message,
        flags=re.IGNORECASE | re.DOTALL
    ).strip()

    if len(clean_message) > max_length:
        return f"{clean_message[:max_length]}..."
    return clean_message


def mask_user_key(user_key: str) -> str:
    if not user_key or len(user_key) < 12:
        return "***"
    return f"{user_key[:6]}***"
