#!/usr/bin/env python3
"""
Format JSON response to readable text

Usage:
    python scripts/format_response.py
    (then paste your JSON response and press Ctrl+D)

Or:
    echo '{"response": "text\\nwith\\nnewlines"}' | python scripts/format_response.py
"""

import json
import sys


def format_response():
    try:
        # Read from stdin
        raw_input = sys.stdin.read()

        # Try to parse as JSON
        try:
            data = json.loads(raw_input)

            if isinstance(data, dict) and 'response' in data:
                response_text = data['response']
            elif isinstance(data, str):
                response_text = data
            else:
                response_text = str(data)
        except json.JSONDecodeError:
            # Not JSON, treat as raw text
            response_text = raw_input

        # Print formatted
        print("\n" + "="*60)
        print("FORMATTED RESPONSE:")
        print("="*60 + "\n")
        print(response_text)
        print("\n" + "="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nAborted.")
        sys.exit(0)


if __name__ == "__main__":
    format_response()
