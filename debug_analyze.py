import os
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

from doctor.ingest.unified_engine import analyze_statement

# Test p4_09
print("=== p4_09 ===")
result = analyze_statement("Given an array, find the subarray with the maximum product.")
print(f"Status: {result['status']}")
print(f"Matched: {result.get('matched')}")
print(f"Objective: {result.get('parsed_model', {}).get('objective')}")
print(f"Trace contradiction: {result.get('decision_trace', {}).get('contradiction')}")
print(f"Trace final: {result.get('decision_trace', {}).get('final')}")

print("\n=== p4_12 ===")
result2 = analyze_statement("Given two strings, find the minimum edits to make them equal using only insertions and deletions.")
print(f"Status: {result2['status']}")
print(f"Matched: {result2.get('matched')}")
print(f"Objective: {result2.get('parsed_model', {}).get('objective')}")
print(f"Constraints: {result2.get('parsed_model', {}).get('constraints')}")
print(f"Trace operation_restriction: {result2.get('decision_trace', {}).get('operation_restriction')}")
print(f"Trace final: {result2.get('decision_trace', {}).get('final')}")