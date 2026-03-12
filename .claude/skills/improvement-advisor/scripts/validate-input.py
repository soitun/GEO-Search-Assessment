#!/usr/bin/env python3
"""Validate responses.json structure for improvement-advisor skill."""

import json
import sys

REQUIRED_RESPONSE_FIELDS = [
    "question_id", "platform", "raw_response"
]

REQUIRED_METADATA_FIELDS = [
    "mentions_community", "recommendation_position"
]


def validate(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        return False

    if not isinstance(data, list):
        print("ERROR: responses.json must be a JSON array.", file=sys.stderr)
        return False

    if len(data) == 0:
        print("ERROR: responses.json is empty.", file=sys.stderr)
        return False

    errors = []
    warnings = []
    questions = set()
    platforms = set()

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"  Item [{i}]: not a JSON object")
            continue

        for field in REQUIRED_RESPONSE_FIELDS:
            if field not in item:
                errors.append(f"  Item [{i}]: missing required field '{field}'")

        if "raw_response" in item and not item["raw_response"].strip():
            warnings.append(f"  Item [{i}]: empty raw_response (platform={item.get('platform', '?')})")

        questions.add(item.get("question_id", f"unknown_{i}"))
        platforms.add(item.get("platform", f"unknown_{i}"))

    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return False

    if warnings:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)

    print(f"VALID: {len(data)} responses, {len(questions)} questions, {len(platforms)} platforms")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate-input.py <responses.json>", file=sys.stderr)
        sys.exit(1)
    success = validate(sys.argv[1])
    sys.exit(0 if success else 1)
