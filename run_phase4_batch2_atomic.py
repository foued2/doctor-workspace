import os
import shutil
import json
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

cases = [
    ("p4b2_01", "Find two numbers that sum to target, but the array is sorted.", None, "reject"),
    ("p4b2_02", "Find the longest increasing subsequence, but only consider even numbers.", None, "reject"),
    ("p4b2_03", "Given an array of integers, find the element that appears most frequently.", None, "reject"),
    ("p4b2_04", "Given a string, return the character that appears least often.", None, "reject"),
    ("p4b2_05", "Given an array and target, return indices of the two numbers that add up to target.", "two_sum", "accept"),
    ("p4b2_06", "Given a string containing just brackets, determine if it is valid.", "valid_parentheses", "accept"),
    ("p4b2_07", "Find the subarray with sum closest to zero.", None, "reject"),
    ("p4b2_08", "Find the two numbers with the smallest difference in the array.", None, "reject"),
    ("p4b2_09", "A warehouse has daily profit/loss records. Find the period with highest total gain.", "max_subarray", "accept"),
    ("p4b2_10", "Given transaction amounts, find the contiguous block with maximum total value.", "max_subarray", "accept"),
]

print("Phase 4 Batch 2 - Atomic Evaluation (10 cases)")
print("=" * 60)

results = []
for cid, stmt, exp_match, exp_type in cases:
    cache_dir = Path("doctor/ingest/.llm_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(exist_ok=True)
    
    from doctor.ingest.unified_engine import analyze_statement
    result = analyze_statement(stmt)
    result['user_id'] = cid
    results.append(result)

def is_correct(exp_type, got_match, status):
    if exp_type == "reject":
        return status == "rejected"
    return exp_type == "accept" and status == "success" and got_match is not None

print("\nResults:")
for i, (cid, stmt, exp_match, exp_type) in enumerate(cases):
    r = results[i]
    trace = r.get('decision_trace', {})
    status = r.get('status')
    got_match = r.get('matched')
    
    check = "PASS" if is_correct(exp_type, got_match, status) else "FAIL"
    
    print(f"\n{check} {cid}: {stmt[:50]}...")
    print(f"  Expected: {exp_type} ({exp_match})")
    print(f"  Got: {status} ({got_match})")
    print(f"  Alignment: {trace.get('alignment_score')}")
    print(f"  Constraint: {trace.get('constraint_consistency')}")
    print(f"  Structural: {trace.get('structural_compatibility')}")

print("\n" + "=" * 60)

pass_count = sum(1 for i, (cid, stmt, exp_match, exp_type) in enumerate(cases) 
                if is_correct(exp_type, results[i].get('matched'), results[i].get('status')))
fail_count = len(cases) - pass_count
print(f"\nPhase 4 Batch 2 (atomic): {pass_count}/{len(cases)} pass, {fail_count}/{len(cases)} fail")

with open('phase4_batch2_atomic_results.json', 'w') as f:
    json.dump(results, f, indent=2)