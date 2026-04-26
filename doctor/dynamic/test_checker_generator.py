#!/usr/bin/env python3
"""
Task 3: End-to-end test runner for checker_generator.
Usage: python doctor/dynamic/test_checker_generator.py <schema_json_path>
"""
import json
import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_checker_generator.py <schema_json_path>")
        sys.exit(1)

    schema_path = sys.argv[1]
    if not os.path.exists(schema_path):
        print(f"ERROR: Schema file not found: {schema_path}")
        sys.exit(1)

    if not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("GROQ_API_KEY"):
        print("ERROR: Set OPENROUTER_API_KEY or GROQ_API_KEY")
        sys.exit(1)

    with open(schema_path) as f:
        schema = json.load(f)

    print(f"=== Checker Generator Test ===")
    print(f"Schema   : {schema.get('problem_id', 'unknown')}")
    print(f"Val type : {schema.get('validation_type')}")
    print(f"Samples  : {len(schema.get('sample_cases', []))}")
    print(f"Invariants: {len(schema.get('invariants', []))}")
    print()

    from doctor.dynamic.checker_generator import generate_checker

    print("--- Running generate_checker() ---")
    result = generate_checker(schema)
    print()

    if result is None:
        print("RESULT: FAILED — checker_generator returned None")
        print("Check failure_mode printed above.")
        sys.exit(1)
    else:
        print("RESULT: PASSED — checker generated and all 4 protocol tests passed")
        print()
        print("--- Generated Checker Source ---")
        print(result)
        sys.exit(0)


if __name__ == "__main__":
    main()