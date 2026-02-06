import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.tools.user_lookup import user_lookup
from app.core.tools.transaction_history import transaction_history
from app.core.tools.account_status import account_status
from app.core.tools.transfer_troubleshoot import transfer_troubleshoot


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_user_lookup():
    print_section("Testing user_lookup tool")

    print("1. Looking up Leonardo Frizzo (user_leo):")
    result = user_lookup("user_leo")
    print(f"   Found: {result.get('found')}")
    print(f"   Name: {result.get('name')}")
    print(f"   Role: {result.get('role')}")
    print(f"   Status: {result.get('account_status')}")

    print("\n2. Looking up non-existent user:")
    result = user_lookup("user_nonexistent")
    print(f"   Found: {result.get('found')}")
    print(f"   Error: {result.get('error')}")


def test_transaction_history():
    print_section("Testing transaction_history tool")

    print("1. Getting Leo's last 3 transactions:")
    result = transaction_history("user_leo", limit=3)
    print(f"   User: {result.get('user_id')}")
    print(f"   Total transactions: {result.get('total_count')}")
    print(f"   Returned: {result.get('returned_count')}")
    print(f"   Total amount: R$ {result.get('total_amount'):.2f}")
    print(f"\n   Transactions:")
    for tx in result.get('transactions', []):
        print(f"     - {tx['id']}: {tx['type']} R$ {tx['amount']:.2f} ({tx['method']})")

    print("\n2. Getting transactions for user with no history:")
    result = transaction_history("user_nonexistent")
    print(f"   Total: {result.get('total_count')}")
    print(f"   Message: {result.get('message')}")


def test_account_status():
    print_section("Testing account_status tool")

    print("1. Checking active account (user_leo):")
    result = account_status("user_leo")
    print(f"   Status: {result.get('account_status')}")
    print(f"   Can send: {result.get('can_send')}")
    print(f"   Daily limit: R$ {result.get('daily_send_limit'):.2f}")
    print(f"   Used today: R$ {result.get('used_today'):.2f}")
    print(f"   Remaining: R$ {result.get('remaining_today'):.2f}")

    print("\n2. Checking blocked account (user_blocked):")
    result = account_status("user_blocked")
    print(f"   Status: {result.get('account_status')}")
    print(f"   Can send: {result.get('can_send')}")
    print(f"   Block reason: {result.get('block_reason')}")
    print(f"   Restrictions: {result.get('restrictions')}")


def test_transfer_troubleshoot():
    print_section("Testing transfer_troubleshoot tool")

    print("1. Checking pending transfer:")
    result = transfer_troubleshoot("tx_leo_pending_001")
    print(f"   Transfer ID: {result.get('transfer_id')}")
    print(f"   Status: {result.get('status')}")
    print(f"   Issue type: {result.get('issue_type')}")
    print(f"   Description: {result.get('issue_description')}")
    print(f"   Can cancel: {result.get('can_cancel')}")
    print(f"   Recommendations:")
    for rec in result.get('recommendations', []):
        print(f"     - {rec}")

    print("\n2. Checking failed transfer (limit exceeded):")
    result = transfer_troubleshoot("tx_test_failed_001")
    print(f"   Status: {result.get('status')}")
    print(f"   Issue: {result.get('issue_type')}")
    print(f"   Can retry: {result.get('can_retry')}")

    print("\n3. Checking successful transfer (no issues):")
    result = transfer_troubleshoot("tx_success_001")
    print(f"   Issue detected: {result.get('issue_detected')}")
    print(f"   Message: {result.get('message')}")


def main():
    print("\n" + "="*60)
    print("  CLOUDWALK SUPPORT TOOLS - TEST SUITE")
    print("="*60)

    test_user_lookup()
    test_transaction_history()
    test_account_status()
    test_transfer_troubleshoot()

    print("\n" + "="*60)
    print("  ALL TESTS COMPLETED ✅")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
