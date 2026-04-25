import os
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

from doctor.ingest.unified_engine import analyze_statement, _check_contradiction, _check_operation_restriction

# Test p4_09
print("=== p4_09 ===")
result = analyze_statement("Given an array, find the subarray with the maximum product.")
print(f"Full result keys: {list(result.keys())}")
print(f"Status: {result['status']}")
print(f"Matched: {result.get('matched')}")
print(f"Error: {result.get('error')}")
print(f"Trace final: {result.get('decision_trace', {}).get('final')}")
print(f"Trace rejection_reason: {result.get('decision_trace', {}).get('rejection_reason')}")

# Manual check
obj = result.get('parsed_model', {}).get('objective', '')
print(f"\nManual contradiction check for '{obj}' + max_subarray:")
is_con, reason = _check_contradiction(obj, 'max_subarray')
print(f"  Result: {is_con}, {reason}")

print("\n=== p4_12 ===")
result2 = analyze_statement("Given two strings, find the minimum edits to make them equal using only insertions and deletions.")
print(f"Status: {result2['status']}")
print(f"Matched: {result2.get('matched')}")
print(f"Constraints: {result2.get('parsed_model', {}).get('constraints')}")
print(f"Trace rejection_reason: {result2.get('decision_trace', {}).get('rejection_reason')}")

# Manual check
obj2 = result2.get('parsed_model', {}).get('objective', '')
constraints2 = result2.get('parsed_model', {}).get('constraints', [])
print(f"\nManual operation check for '{obj2[:40]}...' constraints={constraints2}:")
is_restricted, reason = _check_operation_restriction(obj2, constraints2, 'min_distance')
print(f"  Result: {is_restricted}, {reason}")