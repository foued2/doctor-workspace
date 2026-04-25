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

statements = ["A warehouse has daily profit/loss records. Find the period with highest total gain."]
case_ids = ["p4b2_09"]

print("Testing p4b2_09 after prompt update")
print("=" * 60)

results = run_batch_phase3_runner(statements, case_ids)
r = results[0]
trace = r.get('decision_trace', {})

print(f"\np4b2_09: {r['statement']}")
print(f"  Status: {r.get('status')}")
print(f"  Matched: {r.get('matched')}")
print(f"  Alignment: {trace.get('alignment_score')}")
print(f"  Constraint: {trace.get('constraint_consistency')}")
print(f"  Structural: {trace.get('structural_compatibility')}")
print(f"  Decision: {trace.get('final')}")

alignment = trace.get('alignment_score', 0)
status = r.get('status')

if alignment >= 0.85 and status == 'success':
    print(f"\nPASS: Alignment {alignment} >= 0.85, accepted")
else:
    print(f"\nFAIL: Alignment {alignment} < 0.85 or status {status}")