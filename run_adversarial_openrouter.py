import json
import os
import time
import shutil
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY', '')

cache_dir = Path("doctor/ingest/.llm_cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
cache_dir.mkdir(exist_ok=True)

from phase3_runner import run_batch_phase3_runner

with open('phase3_batch3.json') as f:
    cases = json.load(f)

statements = [c['statement'] for c in cases]
case_ids = [c['user_id'] for c in cases]

print(f"Running {len(statements)} adversarial cases via OpenRouter...")
print("=" * 60)

results = run_batch_phase3_runner(statements, case_ids)

for i, r in enumerate(results):
    expected = cases[i]['expected_match']
    got = r.get('matched')
    tag = r.get('failure_tag')
    
    r['expected_match'] = expected
    r['expected_type'] = cases[i]['expected_type']
    r['note'] = cases[i].get('note', '')
    
    status = "PASS" if (expected == got) or (expected is None and got is None) else "FAIL"
    print(f"  {status} {r['user_id']}: expected={expected}, got={got}, tag={tag}")

with open('phase3_batch3_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 60)
print("Adversarial batch complete.")