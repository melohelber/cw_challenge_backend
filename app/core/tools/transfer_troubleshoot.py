import logging
from typing import Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

MOCKED_TRANSFER_ISSUES = {
    "tx_leo_pending_001": {
        "transfer_id": "tx_leo_pending_001",
        "user_id": "user_leo",
        "status": "pending",
        "amount": 5000.00,
        "recipient": "João Silva",
        "created_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "issue_detected": True,
        "issue_type": "recipient_bank_processing_delay",
        "issue_description": "Transfer is being processed by recipient's bank. Expected completion in 1-2 hours.",
        "can_cancel": True,
        "estimated_completion": (datetime.now() + timedelta(hours=1)).isoformat(),
        "recommendations": [
            "Wait for recipient bank to process the transfer",
            "If not completed in 2 hours, contact support"
        ]
    },
    "tx_test_failed_001": {
        "transfer_id": "tx_test_failed_001",
        "user_id": "user_test",
        "status": "failed",
        "amount": 1500.00,
        "recipient": "Maria Santos",
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "issue_detected": True,
        "issue_type": "daily_limit_exceeded",
        "issue_description": "Transfer failed because it would exceed your daily send limit of R$ 1000.00. You have already used R$ 200.00 today.",
        "can_retry": False,
        "recommendations": [
            "Wait until tomorrow to retry",
            "Request a limit increase in your account settings",
            "Split the transfer into smaller amounts over multiple days"
        ]
    },
    "tx_blocked_001": {
        "transfer_id": "tx_blocked_001",
        "user_id": "user_blocked",
        "status": "blocked",
        "amount": 500.00,
        "recipient": "Leonardo Frizzo",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "issue_detected": True,
        "issue_type": "account_blocked",
        "issue_description": "Transfer blocked due to suspicious activity on your account. Account is currently under review.",
        "can_retry": False,
        "can_cancel": False,
        "recommendations": [
            "Contact support immediately to resolve account block",
            "Provide identity verification documents",
            "Review recent account activity for unauthorized transactions"
        ],
        "support_ticket": "SUP-2025-001234"
    }
}


def transfer_troubleshoot(transfer_id: str) -> Dict[str, any]:
    logger.info(f"Tool [transfer_troubleshoot] called with transfer_id={transfer_id}")

    transfer_data = MOCKED_TRANSFER_ISSUES.get(transfer_id)

    if not transfer_data:
        logger.info(f"Tool [transfer_troubleshoot] no issues found for transfer: {transfer_id}")
        return {
            "transfer_id": transfer_id,
            "found": True,
            "issue_detected": False,
            "status": "completed",
            "message": "Transfer completed successfully with no issues detected"
        }

    logger.warning(f"Tool [transfer_troubleshoot] issue detected for transfer: {transfer_id} (type={transfer_data['issue_type']})")

    return {
        "found": True,
        **transfer_data
    }


def get_transfer_troubleshoot_description() -> str:
    return """
    Use this tool when user asks about:
    - Why a transfer failed
    - Transfer status (pending/failed/stuck)
    - Problems with sending money
    - Troubleshooting payment issues
    - Why money hasn't arrived

    Example queries:
    - "Why did my transfer fail?"
    - "My Pix is stuck, what happened?"
    - "Transfer not completed"
    - "Why can't I send money to João?"
    - "Check transfer tx_leo_pending_001"

    Input: transfer_id (string)
    Output: Transfer diagnostics including status, issue type, description, and recommendations
    """
