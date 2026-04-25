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

with open('gate_test.json') as f:
    cases = json.load(f)

statements = [c['statement'] for c in cases]
case_ids = [c['user_id'] for c in cases]

print("Gate Validation Test (5 cases)")
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
    got = r.get('matched')
    
    status_check = "PASS" if is_correct(expected, got, status) else "FAIL"
    
    print(f"\n{status_check} {r['user_id']}: {cases[i]['statement'][:50]}...")
    print(f"  Final status: {status}")
    print(f"  LLM match_candidate: {r['decision_trace'].get('llm_match')}")
    print(f"  Gate fired: contradiction={r['decision_trace'].get('contradiction')}, operation_restriction={r['decision_trace'].get('operation_restriction')}")
    print(f"  Final rejection_reason: {r['decision_trace'].get('rejection_reason')}")
    
    r['expected_match'] = expected
    r['expected_type'] = cases[i]['expected_type']
    r['note'] = cases[i].get('note', '')

print("\n" + "=" * 60)

pass_count = sum(1 for r in results if is_correct(r['expected_match'], r['matched'], r['status']))
fail_count = len(results) - pass_count

print(f"\nGate Test: {pass_count}/{len(results)} final verdict = reject")

llm_accepts = [r for r in results if r['decision_trace'].get('llm_match') and r['decision_trace'].get('llm_match') != 'no match']
print(f"LLM initial accepts: {len(llm_accepts)}")
print(f"Gate caught: {sum(1 for r in llm_accepts if r['status'] == 'rejected')}")

with open('gate_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)