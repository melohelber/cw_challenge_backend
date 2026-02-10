import logging
from typing import Dict
from datetime import datetime
from app.utils.logging import mask_user_key

logger = logging.getLogger(__name__)

MOCKED_ACCOUNT_STATUS = {
    "user_leo": {
        "user_id": "user_leo",
        "account_status": "active",
        "can_send": True,
        "can_receive": True,
        "daily_send_limit": 10000.00,
        "daily_receive_limit": 50000.00,
        "used_today": 1750.00,
        "remaining_today": 8250.00,
        "currency": "BRL",
        "last_transaction": (datetime.now()).isoformat(),
        "restrictions": []
    },
    "user_luiz": {
        "user_id": "user_luiz",
        "account_status": "active",
        "can_send": True,
        "can_receive": True,
        "daily_send_limit": 50000.00,
        "daily_receive_limit": 100000.00,
        "used_today": 2000.00,
        "remaining_today": 48000.00,
        "currency": "BRL",
        "last_transaction": (datetime.now()).isoformat(),
        "restrictions": []
    },
    "user_test": {
        "user_id": "user_test",
        "account_status": "active",
        "can_send": True,
        "can_receive": True,
        "daily_send_limit": 1000.00,
        "daily_receive_limit": 5000.00,
        "used_today": 200.00,
        "remaining_today": 800.00,
        "currency": "BRL",
        "last_transaction": (datetime.now()).isoformat(),
        "restrictions": ["needs_verification_for_higher_limits"]
    },
    "user_blocked": {
        "user_id": "user_blocked",
        "account_status": "blocked",
        "can_send": False,
        "can_receive": False,
        "daily_send_limit": 0.00,
        "daily_receive_limit": 0.00,
        "used_today": 0.00,
        "remaining_today": 0.00,
        "currency": "BRL",
        "last_transaction": None,
        "restrictions": ["account_blocked"],
        "block_reason": "Suspicious activity detected",
        "blocked_since": "2025-11-05"
    }
}


def account_status(user_key: str) -> Dict[str, any]:
    logger.info(f"Tool [account_status] called with user_key={mask_user_key(user_key)}")

    # For mocked data, still use user_key to lookup
    status_data = MOCKED_ACCOUNT_STATUS.get(user_key)

    if not status_data:
        logger.warning(f"Tool [account_status] no status found for user: {mask_user_key(user_key)}")
        return {
            "user_key": user_key,
            "found": False,
            "error": "Account not found"
        }

    logger.info(f"Tool [account_status] returned status for user: {mask_user_key(user_key)} (status={status_data['account_status']})")

    return {
        "found": True,
        **status_data
    }


def get_account_status_description() -> str:
    return """
    Use this tool when user asks about:
    - Account limits (daily send/receive limits)
    - Why they can't transfer money
    - If account is blocked or suspended
    - How much they can still transfer today
    - Account restrictions

    Example queries:
    - "Why can't I send money?"
    - "What's my daily limit?"
    - "Is my account blocked?"
    - "How much can I transfer today?"
    - "Check my account status"

    Input: user_key (string - UUID)
    Output: Account status, limits, restrictions, and usage information
    """
