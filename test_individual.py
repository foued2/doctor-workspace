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

cases = [
    ("p4b2_06", "Given a string containing just brackets, determine if it is valid."),
    ("p4b2_09", "A warehouse has daily profit/loss records. Find the period with highest total gain."),
    ("p4b2_10", "Given transaction amounts, find the contiguous block with maximum total value."),
]

statements = [c[1] for c in cases]
case_ids = [c[0] for c in cases]

print("Individual verification")
print("=" * 60)

for i, (stmt, cid) in enumerate(zip(statements, case_ids)):
    results = run_batch_phase3_runner([stmt], [cid])
    r = results[0]
    trace = r.get('decision_trace', {})
    print(f"\n{cid}: {stmt[:50]}...")
    print(f"  Status: {r.get('status')}, Matched: {r.get('matched')}")
    print(f"  Alignment: {trace.get('alignment_score')}")