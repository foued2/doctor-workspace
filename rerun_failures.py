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

from phase3_runner import run_phase3

test_cases = [
    {"user_id": "p4_09", "statement": "Given an array, find the subarray with the maximum product.", "expected": None},
    {"user_id": "p4_12", "statement": "Given two strings, find the minimum edits to make them equal using only insertions and deletions.", "expected": None},
]

print("Rerunning failed cases...")
for tc in test_cases:
    print(f"\n{tc['user_id']}: {tc['statement'][:50]}...")
    result = run_phase3(tc['statement'], tc['user_id'])
    got = result.get('matched')
    tag = result.get('failure_tag')
    contradiction = result.get('decision_trace', {}).get('contradiction')
    op_restriction = result.get('decision_trace', {}).get('operation_restriction')
    
    status = "PASS" if (tc['expected'] is None and got is None) or (tc['expected'] == got) else "FAIL"
    print(f"  {status}: expected={tc['expected']}, got={got}, tag={tag}")
    print(f"  Trace: contradiction={contradiction}, operation_restriction={op_restriction}")
    print(f"  Error: {result.get('error')}")