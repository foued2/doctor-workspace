import json
import os
import shutil
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY', '')

cache_dir = Path("doctor/ingest/.llm_cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
cache_dir.mkdir(exist_ok=True)

from phase3_runner import run_batch_phase3_runner

with open('phase4_batch2.json') as f:
    cases = json.load(f)

statements = [c['statement'] for c in cases]
case_ids = [c['user_id'] for c in cases]

print("Phase 4 Batch 2 Test (10 cases)")
print("=" * 60)

results = run_batch_phase3_runner(statements, case_ids)

def is_correct(expected_type, got_match, status):
    if expected_type == "reject":
        return status == "rejected"
    return expected_type == "accept" and status == "success" and got_match is not None

print("\nResults:")
for i, r in enumerate(results):
    expected_type = cases[i]['expected_type']
    expected_match = cases[i]['expected_match']
    status = r.get('status')
    got_match = r.get('matched')
    
    status_check = "PASS" if is_correct(expected_type, got_match, status) else "FAIL"
    
    print(f"\n{status_check} {r['user_id']}: {cases[i]['statement'][:50]}...")
    print(f"  Expected: {expected_type} ({expected_match})")
    print(f"  Got: {status} ({got_match})")
    print(f"  Alignment: {r['decision_trace'].get('alignment_score')}")
    print(f"  Constraint: {r['decision_trace'].get('constraint_consistency')}")
    print(f"  Structural: {r['decision_trace'].get('structural_compatibility')}")

print("\n" + "=" * 60)

pass_count = sum(1 for r in results if is_correct(cases[i]['expected_type'], r.get('matched'), r.get('status')))
fail_count = len(results) - pass_count
print(f"\nPhase 4 Batch 2: {pass_count}/{len(results)} pass, {fail_count}/{len(results)} fail")

with open('phase4_batch2_results.json', 'w') as f:
    json.dump(results, f, indent=2)