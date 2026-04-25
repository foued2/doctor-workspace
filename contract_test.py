import json
import os

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

from phase3_runner import run_phase3

test_cases = [
    {"statement": "find two numbers that add up to X", "expected": "two_sum", "expected_type": "accept"},
    {"statement": "find the longest stretch of consecutive increases", "expected": None, "expected_type": "reject"},
    {"statement": "count minimum coins for amount", "expected": "coin_change", "expected_type": "accept"},
    {"statement": "find duplicate characters in string", "expected": None, "expected_type": "reject"},
    {"statement": "how many ways to climb n stairs", "expected": "climbing_stairs", "expected_type": "accept"},
]

print("Contract Minimality Test")
print("=" * 60)

all_pass = True
for i, tc in enumerate(test_cases, 1):
    print(f"\nCase {i}: {tc['statement'][:50]}...")
    result = run_phase3(tc['statement'], f"contract_test_{i}")
    
    expected = tc['expected']
    got = result.get('matched')
    
    is_match = (expected == got) or (expected is None and (got is None or got == "no match"))
    
    if is_match:
        print(f"  PASS: expected={expected}, got={got}")
    else:
        print(f"  FAIL: expected={expected}, got={got}")
        all_pass = False

print("\n" + "=" * 60)
if all_pass:
    print("Contract minimality test: PASS (no hidden branches detected)")
else:
    print("Contract minimality test: FAIL (contract has undeclared branches)")