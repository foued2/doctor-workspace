import os
import shutil
import json
from pathlib import Path

os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY', '')

statement = "A warehouse has daily profit/loss records. Find the period with highest total gain."

print("Debug - 3 runs with parse")
print("=" * 60)

for i in range(3):
    cache_dir = Path("doctor/ingest/.llm_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(exist_ok=True)
    
    from doctor.ingest.unified_engine import analyze_statement
    result = analyze_statement(statement)
    trace = result.get('decision_trace', {})
    model = result.get('parsed_model', {})
    
    orig = model.get('objective', '')
    canon = model.get('objective_canonical', '')
    
    print(f"\nRun {i+1}:")
    print(f"  Status: {result.get('status')}")
    print(f"  Matched: {result.get('matched')}")
    print(f"  Original: {orig}")
    print(f"  Canonical: {canon}")
    print(f"  Alignment: {trace.get('alignment_score')}")
    print(f"  Constraint: {trace.get('constraint_consistency')}")
    print(f"  Structural: {trace.get('structural_compatibility')}")