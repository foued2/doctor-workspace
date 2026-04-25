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
- parser_fail: statement never produced a model
- matcher_miss: parsed correctly, matched wrong or None when should match
- false_accept: matched when should reject  
- validation_leak: validation passed but match was wrong
- unresolved: failure mode unclear after trace inspection
"""

import os
import json
from datetime import datetime

os.environ['GROQ_API_KEY'] = os.environ.get('GROQ_API_KEY', '')
os.environ['LLM_PROVIDER'] = os.environ.get('LLM_PROVIDER', 'groq')

from doctor.ingest.problem_parser import parse_problem
from doctor.ingest.registry_matcher import match_to_registry


def run_phase3(statement: str, user_id: str) -> dict:
    """Run single statement through Doctor."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "statement": statement,  # Raw for analysis
        "status": None,
        "failure_tag": None,
        "parsed_model": None,
        "matched": None,
        "decision_trace": {},
    }
    
    # Parse
    try:
        model = parse_problem(statement)
        result["parsed_model"] = model
        result["status"] = "parsed"
    except Exception as e:
        result["status"] = "parse_error"
        result["failure_tag"] = "parser_fail"
        # Store error for analysis
        result["error"] = str(e)
        return result
    
    # Match
    try:
        match_id, justification, trace = match_to_registry(model)
        result["matched"] = match_id
        result["decision_trace"] = trace
        
        # Determine failure tag
        # If matched and we don't expect reject → potential false accept
        # If None and expected match → matcher_miss  
        # validation leak would be visible in trace
        
        if trace.get("final") == "accept":
            result["status"] = "success"
            result["failure_tag"] = None
        else:
            result["status"] = "rejected"
            result["failure_tag"] = "matcher_miss"
            
    except Exception as e:
        result["status"] = "match_error"
        result["failure_tag"] = "unresolved"
        result["error"] = str(e)
    
    return result


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