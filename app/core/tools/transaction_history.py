import logging
from typing import Dict, List
from datetime import datetime, timedelta
from app.utils.logging import mask_user_key

logger = logging.getLogger(__name__)

MOCKED_TRANSACTIONS = {
    "user_leo": [
        {
            "id": "tx_leo_001",
            "type": "payment_received",
            "amount": 1250.00,
            "currency": "BRL",
            "method": "credit_card",
            "merchant": "CloudWalk Store",
            "status": "completed",
            "date": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "id": "tx_leo_002",
            "type": "pix_sent",
            "amount": 500.00,
            "currency": "BRL",
            "method": "pix",
            "recipient": "Maria Santos",
            "status": "completed",
            "date": (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            "id": "tx_leo_003",
            "type": "payment_received",
            "amount": 3500.00,
            "currency": "BRL",
            "method": "debit_card",
            "merchant": "Tech Solutions",
            "status": "completed",
            "date": (datetime.now() - timedelta(days=5)).isoformat()
        }
    ],
    "user_luiz": [
        {
            "id": "tx_luiz_001",
            "type": "payment_received",
            "amount": 15000.00,
            "currency": "BRL",
            "method": "credit_card",
            "merchant": "InfinitePay Consulting",
            "status": "completed",
            "date": (datetime.now() - timedelta(hours=12)).isoformat()
        },
        {
            "id": "tx_luiz_002",
            "type": "pix_sent",
            "amount": 2000.00,
            "currency": "BRL",
            "method": "pix",
            "recipient": "Leonardo Frizzo",
            "status": "completed",
            "date": (datetime.now() - timedelta(days=2)).isoformat()
        }
    ],
    "user_test": [
        {
            "id": "tx_test_001",
            "type": "payment_received",
            "amount": 150.00,
            "currency": "BRL",
            "method": "debit_card",
            "merchant": "Padaria São Paulo",
            "status": "completed",
            "date": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "id": "tx_test_002",
            "type": "payment_received",
            "amount": 50.00,
            "currency": "BRL",
            "method": "credit_card",
            "merchant": "Uber",
            "status": "completed",
            "date": (datetime.now() - timedelta(days=2)).isoformat()
        }
    ]
}


def transaction_history(user_key: str, limit: int = 5) -> Dict[str, any]:
    logger.info(f"Tool [transaction_history] called with user_key={mask_user_key(user_key)}, limit={limit}")

    transactions = MOCKED_TRANSACTIONS.get(user_key)

    if transactions is None:
        logger.info(f"Tool [transaction_history] using default mock data for user: {mask_user_key(user_key)}")
        transactions = MOCKED_TRANSACTIONS.get("user_test", [])

    if not transactions:
        logger.warning(f"Tool [transaction_history] no transactions found for user: {mask_user_key(user_key)}")
        return {
            "user_key": user_key,
            "transactions": [],
            "total_count": 0,
            "message": "No transactions found"
        }

    limited_transactions = transactions[:limit]
    total_amount = sum(tx["amount"] for tx in limited_transactions)

    logger.info(f"Tool [transaction_history] returned {len(limited_transactions)} transactions for user: {mask_user_key(user_key)}")

    return {
        "user_key": user_key,
        "transactions": limited_transactions,
        "total_count": len(transactions),
        "returned_count": len(limited_transactions),
        "total_amount": total_amount,
        "currency": "BRL"
    }
