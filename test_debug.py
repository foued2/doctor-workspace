import os
import shutil
import json
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = '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'

statement = "A warehouse has daily profit/loss records. Find the period with highest total gain."

print("Testing canonicalization with debug")
print("=" * 60)

cache_dir = Path("doctor/ingest/.llm_cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
cache_dir.mkdir(exist_ok=True)

from phase3_runner import run_batch_phase3_runner
results = run_batch_phase3_runner([statement], ["debug"])
r = results[0]

trace = r.get('decision_trace', {})
print(f"\nStatus: {r.get('status')}")
print(f"Matched: {r.get('matched')}")
print(f"Alignment: {trace.get('alignment_score')}")
print(f"Objective canonical: {trace.get('objective_canonical')}")
print(f"Parsing: {r.get('parsed_model')}")

for f in cache_dir.glob("*.json"):
    with open(f) as fh:
        cached = json.load(fh)
        print(f"\nCached response:")
        print(json.dumps(cached, indent=2)[:1500])