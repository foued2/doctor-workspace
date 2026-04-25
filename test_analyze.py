import os
import shutil
import json
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY', '')

statement = "A warehouse has daily profit/loss records. Find the period with highest total gain."

print("Testing decision logic")
print("=" * 60)

cache_dir = Path("doctor/ingest/.llm_cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
cache_dir.mkdir(exist_ok=True)

from doctor.ingest.unified_engine import analyze_statement

result = analyze_statement(statement)
print(f"\nResult keys: {result.keys()}")
print(f"Status: {result.get('status')}")
print(f"Matched: {result.get('matched')}")
print(f"Parsed model: {result.get('parsed_model')}")

trace = result.get('decision_trace', {})
print(f"\nTrace keys: {trace.keys()}")
print(f"LLM match: {trace.get('llm_match')}")
print(f"Alignment raw: {trace.get('alignment_score')}")
print(f"Objective canonical: {trace.get('objective_canonical')}")
print(f"Constraint: {trace.get('constraint_consistency')}")
print(f"Structural: {trace.get('structural_compatibility')}")
print(f"Final: {trace.get('final')}")
print(f"Contract: {trace.get('decision_contract')}")