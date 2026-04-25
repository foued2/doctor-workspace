import os
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

from doctor.ingest.unified_engine import analyze_batch

# Test cases that should trigger explicit gates
test_cases = [
    "Find the maximum product of any subarray in the array.",  # product vs sum
    "Calculate the minimum edits between strings using only insertions and deletions.",  # operation restriction
]

results = analyze_batch(test_cases, ["gate_test_1", "gate_test_2"])

for r in results:
    print(f"\n{r['user_id']}: {r['statement'][:50]}...")
    print(f"  Status: {r['status']}")
    print(f"  Matched: {r.get('matched')}")
    print(f"  Contradiction: {r['decision_trace'].get('contradiction')}")
    print(f"  Operation_restriction: {r['decision_trace'].get('operation_restriction')}")
    print(f"  Rejection_reason: {r['decision_trace'].get('rejection_reason')}")