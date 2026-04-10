import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tests.production_87 as p87
from doctor.test_executor import _safe_exec, TEST_SUITES, PROBLEM_KEY_MAP

prob = p87.PROBLEMS[0]  # Two Sum
correct_code = prob["correct"]

print("=== SOLUTION CODE ===")
print(repr(correct_code))
print()

# Test _safe_exec
func = _safe_exec(correct_code)
print(f"Function found: {func}")
print(f"Function name: {func.__name__ if func else None}")
print()

if func:
    result = func([2, 7, 11, 15], 9)
    print(f"Test call result: {result}")
    print()

# Check test suite mapping
suite_key = PROBLEM_KEY_MAP.get("Two Sum")
print(f"Suite key: {suite_key}")
test_cases = TEST_SUITES.get(suite_key, [])
print(f"Number of test cases: {len(test_cases)}")
for tc in test_cases:
    print(f"  {tc.label}: input={tc.input}, expected={tc.expected}")
