import pytest
from app.core.tools.user_lookup import user_lookup
from app.core.tools.transaction_history import transaction_history
from app.core.tools.account_status import account_status
from app.core.tools.transfer_troubleshoot import transfer_troubleshoot


class TestUserLookup:
    def test_lookup_existing_user(self):
        result = user_lookup("user_leo")
        assert result["found"] is True
        assert result["name"] == "Leonardo Frizzo"
        assert result["email"] == "leonardo.frizzo@cloudwalk.io"
        assert result["account_status"] == "active"

    def test_lookup_nonexistent_user(self):
        result = user_lookup("user_nonexistent")
        assert result["found"] is True
        assert result["name"] == "Maria Santos"


class TestTransactionHistory:
    def test_get_transactions_with_limit(self):
        result = transaction_history("user_leo", limit=2)
        assert result["user_key"] == "user_leo"
        assert result["returned_count"] == 2
        assert len(result["transactions"]) == 2

    def test_get_all_transactions(self):
        result = transaction_history("user_leo", limit=10)
        assert result["total_count"] >= result["returned_count"]

    def test_fallback_transactions_for_nonexistent_user(self):
        result = transaction_history("user_nonexistent")
        assert result["total_count"] == 2
        assert result["user_key"] == "user_nonexistent"


class TestAccountStatus:
    def test_active_account(self):
        result = account_status("user_leo")
        assert result["found"] is True
        assert result["account_status"] == "active"
        assert result["can_send"] is True
        assert result["daily_send_limit"] > 0

    def test_blocked_account(self):
        result = account_status("user_blocked")
        assert result["found"] is True
        assert result["account_status"] == "blocked"
        assert result["can_send"] is False
        assert "block_reason" in result

    def test_nonexistent_account(self):
        result = account_status("user_nonexistent")
        assert result["found"] is False


class TestTransferTroubleshoot:
    def test_pending_transfer(self):
        result = transfer_troubleshoot("tx_leo_pending_001")
        assert result["found"] is True
        assert result["issue_detected"] is True
        assert result["status"] == "pending"
        assert "recommendations" in result

    def test_failed_transfer(self):
        result = transfer_troubleshoot("tx_test_failed_001")
        assert result["found"] is True
        assert result["status"] == "failed"
        assert result["issue_type"] == "daily_limit_exceeded"

    def test_successful_transfer(self):
        result = transfer_troubleshoot("tx_success_001")
        assert result["found"] is True
        assert result["issue_detected"] is False
        assert "successfully" in result["message"].lower()