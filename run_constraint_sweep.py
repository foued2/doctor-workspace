import json
import os
import shutil
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

cache_dir = Path("doctor/ingest/.llm_cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
cache_dir.mkdir(exist_ok=True)

from phase3_runner import run_batch_phase3_runner

with open('constraint_sweep.json') as f:
    cases = json.load(f)

statements = [c['statement'] for c in cases]
case_ids = [c['user_id'] for c in cases]

print("Constraint Sweep Test (5 non-strict LIS variants)")
print("=" * 60)

results = run_batch_phase3_runner(statements, case_ids)

def is_correct(expected, got, status):
    if expected is None:
        return status == "rejected"
    return expected == got and status == "success"

print("\nResults:")
for i, r in enumerate(results):
    expected = cases[i]['expected_match']
    status = r.get('status')
    
    status_check = "PASS" if is_correct(expected, r.get('matched'), status) else "FAIL"
    
    print(f"\n{status_check} {r['user_id']}: {cases[i]['statement'][:50]}...")
    print(f"  Final status: {status}")
    print(f"  Gate fired: contradiction={r['decision_trace'].get('contradiction')}, constraint_violation={r['decision_trace'].get('constraint_consistency_violation')}")

print("\n" + "=" * 60)

pass_count = sum(1 for r in results if is_correct(r.get('expected_match'), r.get('matched'), r.get('status')))
fail_count = len(results) - pass_count
print(f"\nConstraint Sweep: {pass_count}/{len(results)} pass, {fail_count}/{len(results)} fail")

with open('constraint_sweep_results.json', 'w') as f:
    json.dump(results, f, indent=2)