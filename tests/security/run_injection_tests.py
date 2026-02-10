#!/usr/bin/env python3
"""
Automated Prompt Injection Test Runner

This script loads test cases from prompt_injection_test_cases.json
and runs them against the GuardrailsService to validate detection.

Usage:
    python tests/security/run_injection_tests.py
    python tests/security/run_injection_tests.py --verbose
    python tests/security/run_injection_tests.py --category basic_injection
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.guardrails import GuardrailsService


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class InjectionTestRunner:
    def __init__(self, test_cases_path: str, verbose: bool = False):
        self.test_cases_path = test_cases_path
        self.verbose = verbose
        self.guardrails = GuardrailsService()
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "failures": []
        }

    def load_test_cases(self) -> Dict:
        """Load test cases from JSON file"""
        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run_single_test(self, test: Dict, category: str) -> Tuple[bool, str]:
        """Run a single test case and return (passed, reason)"""
        message = test["message"]
        expected_blocked = test["expected_blocked"]
        test_id = test["id"]

        # Special handling for boundary test with repeat
        if "repeat" in message:
            # This is a placeholder for programmatically generated long strings
            # In real implementation, would need to generate it properly
            message = "a" * 2500

        result = self.guardrails.check(message)
        actual_blocked = not result.allowed

        passed = (actual_blocked == expected_blocked)

        if self.verbose or not passed:
            status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
            expected_str = "BLOCK" if expected_blocked else "ALLOW"
            actual_str = "BLOCKED" if actual_blocked else "ALLOWED"

            print(f"\n{status} [{category}] {test_id}")
            print(f"  Message: {message[:80]}{'...' if len(message) > 80 else ''}")
            print(f"  Expected: {expected_str} | Actual: {actual_str}")

            if not passed:
                reason = result.reason if result.reason else "No reason provided"
                print(f"  {Colors.YELLOW}Reason: {reason}{Colors.END}")

        failure_reason = ""
        if not passed:
            if expected_blocked and not actual_blocked:
                failure_reason = "False negative: Attack not detected"
            else:
                failure_reason = "False positive: Legitimate message blocked"

        return passed, failure_reason

    def run_category(self, category_data: Dict) -> Dict:
        """Run all tests in a category"""
        category_name = category_data["category"]
        description = category_data["description"]
        tests = category_data["tests"]

        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Category: {category_name}{Colors.END}")
        print(f"Description: {description}")
        print(f"Tests: {len(tests)}")
        print(f"{Colors.BLUE}{'='*70}{Colors.END}")

        category_passed = 0
        category_failed = 0

        for test in tests:
            passed, failure_reason = self.run_single_test(test, category_name)

            if passed:
                category_passed += 1
            else:
                category_failed += 1
                self.results["failures"].append({
                    "category": category_name,
                    "test_id": test["id"],
                    "message": test["message"],
                    "expected_blocked": test["expected_blocked"],
                    "reason": failure_reason
                })

        pass_rate = (category_passed / len(tests)) * 100 if tests else 0
        print(f"\n{Colors.BOLD}Category Results:{Colors.END} {category_passed}/{len(tests)} passed ({pass_rate:.1f}%)")

        return {
            "passed": category_passed,
            "failed": category_failed,
            "total": len(tests),
            "pass_rate": pass_rate
        }

    def run_all_tests(self, filter_category: str = None):
        """Run all test cases"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("=" * 70)
        print(" PROMPT INJECTION TEST SUITE")
        print("=" * 70)
        print(f"{Colors.END}")

        data = self.load_test_cases()
        test_cases = data["test_cases"]
        metadata = data.get("metadata", {})

        print(f"Version: {metadata.get('version', 'N/A')}")
        print(f"Total Categories: {len(test_cases)}")
        print(f"Expected Pass Rate: {metadata.get('expected_pass_rate', 0.90) * 100:.0f}%")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        category_results = []

        for category_data in test_cases:
            # Skip if filtering by category
            if filter_category and category_data["category"] != filter_category:
                continue

            result = self.run_category(category_data)
            category_results.append({
                "category": category_data["category"],
                **result
            })

            self.results["passed"] += result["passed"]
            self.results["failed"] += result["failed"]
            self.results["total"] += result["total"]

        self.print_summary(category_results, metadata)

    def print_summary(self, category_results: List[Dict], metadata: Dict):
        """Print final test summary"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}FINAL SUMMARY{Colors.END}")
        print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

        # Category breakdown
        print(f"{Colors.BOLD}Results by Category:{Colors.END}")
        for result in category_results:
            status_icon = "✓" if result["pass_rate"] == 100 else "✗" if result["pass_rate"] < 50 else "⚠"
            color = Colors.GREEN if result["pass_rate"] >= 90 else Colors.YELLOW if result["pass_rate"] >= 70 else Colors.RED

            print(f"  {status_icon} {result['category']:.<40} {color}{result['passed']}/{result['total']} ({result['pass_rate']:.1f}%){Colors.END}")

        # Overall statistics
        total_pass_rate = (self.results["passed"] / self.results["total"]) * 100 if self.results["total"] > 0 else 0
        expected_pass_rate = metadata.get("expected_pass_rate", 0.90) * 100

        print(f"\n{Colors.BOLD}Overall Statistics:{Colors.END}")
        print(f"  Total Tests: {self.results['total']}")
        print(f"  Passed: {Colors.GREEN}{self.results['passed']}{Colors.END}")
        print(f"  Failed: {Colors.RED}{self.results['failed']}{Colors.END}")

        # Pass rate with color coding
        if total_pass_rate >= expected_pass_rate:
            rate_color = Colors.GREEN
            status = "✓ PASSED"
        elif total_pass_rate >= 70:
            rate_color = Colors.YELLOW
            status = "⚠ WARNING"
        else:
            rate_color = Colors.RED
            status = "✗ FAILED"

        print(f"  Pass Rate: {rate_color}{total_pass_rate:.1f}%{Colors.END} (Expected: {expected_pass_rate:.0f}%)")
        print(f"\n  {Colors.BOLD}Status: {rate_color}{status}{Colors.END}")

        # Failures detail
        if self.results["failures"]:
            print(f"\n{Colors.BOLD}{Colors.RED}Failed Tests:{Colors.END}")
            for failure in self.results["failures"]:
                print(f"\n  [{failure['category']}] {failure['test_id']}")
                print(f"    Message: {failure['message'][:60]}{'...' if len(failure['message']) > 60 else ''}")
                print(f"    {failure['reason']}")

        print(f"\n{Colors.BLUE}{'='*70}{Colors.END}\n")

        # Exit code
        if total_pass_rate >= expected_pass_rate:
            sys.exit(0)
        else:
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run prompt injection tests against GuardrailsService"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all test results (not just failures)"
    )
    parser.add_argument(
        "--category", "-c",
        type=str,
        help="Run tests for a specific category only"
    )
    parser.add_argument(
        "--test-file",
        type=str,
        default="tests/security/prompt_injection_test_cases.json",
        help="Path to test cases JSON file"
    )

    args = parser.parse_args()

    runner = InjectionTestRunner(
        test_cases_path=args.test_file,
        verbose=args.verbose
    )

    try:
        runner.run_all_tests(filter_category=args.category)
    except FileNotFoundError:
        print(f"{Colors.RED}Error: Test cases file not found: {args.test_file}{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error running tests: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
