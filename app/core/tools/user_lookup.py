import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

MOCKED_USERS = {
    "user_leo": {
        "user_id": "user_leo",
        "name": "Leonardo Frizzo",
        "email": "leonardo.frizzo@cloudwalk.io",
        "phone": "+55 11 98765-4321",
        "document": "123.456.789-00",
        "account_status": "active",
        "verification_level": "full",
        "account_type": "business",
        "created_at": "2024-01-15",
        "role": "Head of Engineering"
    },
    "user_luiz": {
        "user_id": "user_luiz",
        "name": "Luiz Silva",
        "email": "luiz.silva@cloudwalk.io",
        "phone": "+55 11 91234-5678",
        "document": "987.654.321-00",
        "account_status": "active",
        "verification_level": "full",
        "account_type": "business",
        "created_at": "2023-06-10",
        "role": "CEO"
    },
    "user_test": {
        "user_id": "user_test",
        "name": "Maria Santos",
        "email": "maria.santos@example.com",
        "phone": "+55 11 99999-8888",
        "document": "111.222.333-44",
        "account_status": "active",
        "verification_level": "basic",
        "account_type": "personal",
        "created_at": "2025-03-20"
    },
    "user_blocked": {
        "user_id": "user_blocked",
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "phone": "+55 11 97777-6666",
        "document": "555.666.777-88",
        "account_status": "blocked",
        "verification_level": "basic",
        "account_type": "personal",
        "created_at": "2025-11-05",
        "block_reason": "Suspicious activity detected"
    }
}


def user_lookup(user_id: str) -> Dict[str, any]:
    logger.info(f"Tool [user_lookup] called with user_id={user_id}")

    user_data = MOCKED_USERS.get(user_id)

    if not user_data:
        logger.info(f"Tool [user_lookup] using default mock data for user: {user_id}")
        user_data = MOCKED_USERS.get("user_test", {}).copy()
        if user_data:
            user_data["user_id"] = user_id

    logger.info(f"Tool [user_lookup] returned data for user: {user_data['name']}")
    return {
        "found": True,
        **user_data
    }


def get_user_info_description() -> str:
    return """
    Use this tool when user asks about:
    - Their account information
    - Profile details
    - Account status (active/blocked)
    - Contact information
    - Verification level

    Example queries:
    - "What's my account status?"
    - "Am I verified?"
    - "Show my profile"
    - "What's my email?"

    Input: user_id (string)
    Output: User profile data including name, email, status, verification level
    """
