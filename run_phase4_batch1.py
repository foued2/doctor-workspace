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

with open('phase4_batch1.json') as f:
    cases = json.load(f)

statements = [c['statement'] for c in cases]
case_ids = [c['user_id'] for c in cases]

print(f"Running Phase 4 batch 1 ({len(statements)} cases)...")
print("=" * 60)

results = run_batch_phase3_runner(statements, case_ids)

def is_correct(expected, got, status):
    if expected is None:
        return status == "rejected"
    if status == "rejected":
        return False
    return expected == got

for i, r in enumerate(results):
    expected = cases[i]['expected_match']
    got = r.get('matched')
    status = r.get('status')
    tag = r.get('failure_tag')
    
    r['expected_match'] = expected
    r['expected_type'] = cases[i]['expected_type']
    r['note'] = cases[i].get('note', '')
    
    status_check = "PASS" if is_correct(expected, got, status) else "FAIL"
    print(f"  {status_check} {r['user_id']}: expected={expected}, got={got}, status={status}")

pass_count = sum(1 for r in results if is_correct(r['expected_match'], r['matched'], r['status']))
fail_count = len(results) - pass_count
print(f"\nTotal: {pass_count}/{len(results)} pass, {fail_count}/{len(results)} fail")

with open('phase4_batch1_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to phase4_batch1_results.json")