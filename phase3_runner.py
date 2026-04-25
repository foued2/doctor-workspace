#!/usr/bin/env python3
"""
Phase 3 Runner - Real user submissions

Protocol:
1. Collect raw statement from user
2. Run through Doctor (parse + match)
3. Tag failure by layer using schema
4. Log before anonymization
5. Push results

Failure tagging schema:
- parser_fail: statement never produced a model (logic error)
- rate_limit: infrastructure noise, statement never reached parser (excluded from analysis)
- matcher_miss: parsed correctly, matched wrong or None when should match
- false_accept: matched when should reject  
- validation_leak: validation passed but match was wrong
- unresolved: failure mode unclear after trace inspection

IMPORTANT: Batch evaluation is not a valid scoring mode. Use atomic evaluation
only. Batch mode is preserved for infrastructure testing only and must not be used
for threshold calibration or Phase 4 metrics. Multi-statement evaluation creates
inter-statement interference that violates determinism guarantees.
"""

import os
import json
from datetime import datetime

os.environ['GROQ_API_KEY'] = os.environ.get('GROQ_API_KEY', '')
os.environ['LLM_PROVIDER'] = os.environ.get('LLM_PROVIDER', 'groq')

from doctor.ingest.unified_engine import run_phase3_unified, run_batch_phase3


def run_phase3(statement: str, user_id: str) -> dict:
    """Run single statement through Doctor unified engine."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "statement": statement,
        "status": None,
        "failure_tag": None,
        "parsed_model": None,
        "matched": None,
        "decision_trace": {},
    }
    
    try:
        analysis = run_phase3_unified(statement, user_id)
        result.update(analysis)
    except Exception as e:
        result["status"] = "error"
        result["failure_tag"] = "parser_fail"
        result["error"] = str(e)
    
    return result


def run_batch_phase3_runner(statements: list, case_ids: list) -> list:
    """Run batch of statements through unified engine."""
    results = run_batch_phase3(statements, case_ids)
    
    for r in results:
        if r.get('failure_tag'):
            failure = r['failure_tag']
        elif r['status'] == 'success' and r.get('matched'):
            failure = None
        elif r['status'] == 'success' and not r.get('matched'):
            failure = 'false_accept'
        elif r['status'] == 'rejected' and r.get('matched'):
            failure = 'matcher_miss'
        else:
            failure = 'unresolved'
        
        r['failure_tag'] = failure
    
    return results


def main():
    results = []
    
    print("=" * 60)
    print("PHASE 3 - Real User Submissions")
    print("=" * 60)
    print("Waiting for user statements...")
    print("Failure tags: parser_fail, matcher_miss, false_accept, validation_leak, unresolved")
    print()
    
    # Example: would be called per user submission
    # results.append(run_phase3(user_statement, user_id))


if __name__ == "__main__":
    main()