import os
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

from doctor.ingest.unified_engine import _check_contradiction, _check_operation_restriction

# Test cases
print("=== Contradiction checks ===")
test_con = [
    ("find the subarray with the maximum product", "max_subarray"),
    ("find the max sum subarray", "max_subarray"),
    ("maximum product of subarray", "max_subarray"),
]
for obj, match in test_con:
    result = _check_contradiction(obj, match)
    print(f"  '{obj[:40]}...' + {match}: {result[0]}")

print("\n=== Operation restriction checks ===")
test_op = [
    ("minimum edits to make them equal", ["insertions and deletions only"], "min_distance"),
    ("minimum edits to make them equal", ["only insertions and deletions"], "min_distance"),
    ("minimum edits to make them equal", ["no replacement"], "min_distance"),
]
for obj, constraints, match in test_op:
    result = _check_operation_restriction(obj, constraints, match)
    print(f"  '{obj[:30]}...' + {constraints}: {result[0]}")