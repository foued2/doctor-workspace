#!/usr/bin/env python3
"""
Phase 2 Perturbation Runner - One perturbation per base case, tagged by type.

Run with: py phase2_runner.py
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

os.environ['GROQ_API_KEY'] = os.environ.get('GROQ_API_KEY', '')

CACHE_DIR = Path("doctor/.llm_cache")
if CACHE_DIR.exists():
    print(f"[CLEARING CACHE] {CACHE_DIR}")
    shutil.rmtree(CACHE_DIR)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from doctor.ingest.problem_parser import parse_problem
from doctor.ingest.registry_matcher import match_to_registry
from doctor.registry.problem_registry import get_problems


PERTURBATION_PACK = [
    ("PARAPHRASE_TWO_SUM_ALPHA_LEXICAL", "two_sum", "lexical", "Provided an array along with a target value, output indices of the two entries whose sum equals the target. Exactly one valid combination exists."),
    ("PARAPHRASE_TWO_SUM_BETA_LEXICAL", "two_sum", "lexical", "Inputs: a collection of integers together with a goal sum. Outputs: index positions of two elements that together reach the goal. No alternative pairs are possible."),
    ("PARAPHRASE_LONGEST_PREFIX_LEXICAL", "longest_common_prefix", "lexical", "Receiving several text strings, determine the longest common prefix that begins every string. Return empty string when no match."),
    ("PARAPHRASE_VALID_PARENS_LEXICAL", "valid_parentheses", "lexical", "Check that every opening bracket has a matching closing bracket in proper nesting order. Respond true or false."),
    ("PARAPHRASE_MERGE_LISTS_LEXICAL", "merge_two_sorted_lists", "lexical", "Combine two already-sorted sequences into one sorted sequence. Maintain the ordering."),
    ("SIMILAR_MAX_SUM_VS_PRODUCT_OBJ", "max_subarray", "objective_swap", "Find the contiguous subarray with the maximum product. (vs maximum SUM would be different)"),
    ("SIMILAR_TWO_SUM_VS_THREE_SUM_OBJ", "three_sum", "objective_swap", "Find three numbers in the array that add up to zero. (vs Two Sum - different count)"),
    ("SIMILAR_CLIMBING_WAYS_VS_COST_OBJ", "climbing_stairs", "objective_swap", "Find the minimum cost to reach the top. (vs number of ways would be different)"),
    ("SIMILAR_LIS_VS_LCS_OBJ", "longest_increasing_subsequence", "objective_swap", "Find the longest common subsequence between two arrays. (vs longest increasing - similar structure, different problem)"),
    ("SIMILAR_DFS_VS_BFS_TRAVERSAL_OBJ", None, "objective_swap", "Visit all nodes in the structure below using breadth-first order:\n    1\n   / \\\n  2   3"),
    ("AMBIG_SHORTEST_PATH_CONSTRAINT", None, "constraint_ambiguity", "Find the shortest path from start to end. You may move in any cardinal direction on an infinite grid."),
    ("AMBIG_MAX_ELEMENT_CONSTRAINT", None, "constraint_ambiguity", "Find the maximum element in the array."),
    ("AMBIG_FIND_PAIRS_CONSTRAINT", None, "constraint_ambiguity", "Find all pairs of elements that satisfy the condition (elements must sum to an even number)."),
    ("AMBIG_SORTED_OUTPUT_CONSTRAINT", None, "constraint_ambiguity", "Return a sorted version of the input using merge sort."),
    ("AMBIG_TRAVERSE_CONSTRAINT", None, "constraint_ambiguity", "Traverse the binary tree below in depth-first order:\n    1\n   / \\\n  2   3"),
    ("DISGUISE_TWO_SUM_SHOPPING", "two_sum", "domain_disguise", "Given a shopping list with item prices and a budget, identify which two items can be purchased together without exceeding the budget."),
    ("DISGUISE_LIS_TIMESERIES", "longest_increasing_subsequence", "domain_disguise", "Given daily stock prices over a month, find the longest consecutive period where prices were consistently rising."),
    ("DISGUISE_MAX_SUM_BUDGET", "max_subarray", "domain_disguise", "Given daily expenses over a week, find the consecutive days with the highest total spending."),
    ("DISGUISE_VALID_PARENS_BRACKETS", "valid_parentheses", "domain_disguise", "Verify that all opening brackets [ and { have matching closing brackets ] and } in the correct sequence in an expression."),
]

EXPECTED = {
    "PARAPHRASE_TWO_SUM_ALPHA_LEXICAL": ("two_sum", "match"),
    "PARAPHRASE_TWO_SUM_BETA_LEXICAL": ("two_sum", "match"),
    "PARAPHRASE_LONGEST_PREFIX_LEXICAL": ("longest_common_prefix", "match"),
    "PARAPHRASE_VALID_PARENS_LEXICAL": ("valid_parentheses", "match"),
    "PARAPHRASE_MERGE_LISTS_LEXICAL": ("merge_two_sorted_lists", "match"),
    "SIMILAR_MAX_SUM_VS_PRODUCT_OBJ": ("max_subarray", "match"),
    "SIMILAR_TWO_SUM_VS_THREE_SUM_OBJ": ("three_sum", "match"),
    "SIMILAR_CLIMBING_WAYS_VS_COST_OBJ": ("climbing_stairs", "match_or_reject"),
    "SIMILAR_LIS_VS_LCS_OBJ": ("longest_increasing_subsequence", "match"),
    "SIMILAR_DFS_VS_BFS_TRAVERSAL_OBJ": (None, "reject"),
    "AMBIG_SHORTEST_PATH_CONSTRAINT": (None, "reject"),
    "AMBIG_MAX_ELEMENT_CONSTRAINT": (None, "reject"),
    "AMBIG_FIND_PAIRS_CONSTRAINT": (None, "reject"),
    "AMBIG_SORTED_OUTPUT_CONSTRAINT": (None, "reject"),
    "AMBIG_TRAVERSE_CONSTRAINT": (None, "reject"),
    "DISGUISE_TWO_SUM_SHOPPING": ("two_sum", "match"),
    "DISGUISE_LIS_TIMESERIES": ("longest_increasing_subsequence", "match"),
    "DISGUISE_MAX_SUM_BUDGET": ("max_subarray", "match"),
    "DISGUISE_VALID_PARENS_BRACKETS": ("valid_parentheses", "match"),
}


def main():
    results = []
    
    print("=" * 60)
    print("PHASE 2 - Perturbation Pack with Decision Trace")
    print("=" * 60)
    
    for i, (case_id, expected_match, perturb_type, statement) in enumerate(PERTURBATION_PACK, 1):
        print(f"\n[{i}] {case_id} ({perturb_type}):")
        print(f"  Input: {statement[:50]}...")
        
        parse_retry_count = 0
        
        try:
            model = parse_problem(statement)
            print(f"  Parsed: {model.get('input_type')} -> {model.get('output_type')}")
            print(f"  Parse retries: {parse_retry_count}")
            parse_ok = True
            gate_fired = model.get('_gate_fired')
            infer_confidence = model.get('_inferred', {}).get('infer_confidence', 'unknown')
        except Exception as e:
            print(f"  PARSE ERROR: {e}")
            parse_ok = False
            error_msg = str(e)
            gate_fired = getattr(e, 'gate_fired', 'unknown' if '429' in error_msg else None)
            parse_retry_count = 1 if '429' in error_msg else 0
            model = {"_gate_fired": gate_fired}
            infer_confidence = 'unknown'
        
        if not parse_ok:
            results.append({
                "case": case_id, "statement": statement, "perturbation_type": perturb_type,
                "status": "parse_error", "expected": EXPECTED[case_id],
                "gate_fired": gate_fired, "infer_confidence": infer_confidence,
                "parse_retry_count": parse_retry_count, "decision_trace": {},
            })
            continue
        
        try:
            match_id, justification, decision_trace = match_to_registry(model)
            retry_count = decision_trace.get("retry_count", 0)
            print(f"  Matched: {match_id}")
            print(f"  Decision trace: contradiction={decision_trace.get('contradiction')}, validation={decision_trace.get('validation')}, fallback={decision_trace.get('fallback')}, final={decision_trace.get('final')}")
            match_ok = match_id is not None
        except Exception as e:
            print(f"  MATCH ERROR: {e}")
            match_id, justification, decision_trace = None, str(e), {"contradiction": False, "validation": True, "fallback": False, "final": "error"}
            match_ok = False
            retry_count = 1 if '429' in str(e) else 0
        
        expected_match_val, expected_type = EXPECTED[case_id]
        
        if expected_type == "reject":
            correct = match_id is None or match_id == "no match"
            verdict = "CORRECT_REJECT" if correct else "INCORRECT_GUESS"
        elif expected_type == "match_or_reject":
            correct = match_id == expected_match_val or match_id is None
            verdict = "CORRECT" if correct else "WRONG"
        else:
            correct = match_id == expected_match_val
            verdict = "CORRECT" if correct else "WRONG"
        
        print(f"  Expected: {expected_match_val} ({expected_type})")
        print(f"  Result: {match_id}")
        print(f"  Verdict: {verdict}")
        
        results.append({
            "case": case_id, "statement": statement, "perturbation_type": perturb_type,
            "status": "success", "parsed_model": model, "matched": match_id,
            "justification": justification, "expected": expected_match_val, "expected_type": expected_type,
            "correct": correct, "verdict": verdict, "gate_fired": gate_fired,
            "infer_confidence": infer_confidence, "parse_retry_count": parse_retry_count,
            "matcher_retry_count": retry_count, "decision_trace": decision_trace,
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("PHASE 2 RESULTS")
    print("=" * 60)
    
    total = len(results)
    parse_errors = len([r for r in results if r.get("status") == "parse_error"])
    correct = len([r for r in results if r.get("correct")])
    
    print(f"Total: {total}, Parse errors: {parse_errors}, Correct: {correct}/{total - parse_errors}")
    
    # Metrics
    rejects = len([r for r in results if r.get("expected_type") == "reject" and r.get("status") == "parse_error"])
    accepted = total - parse_errors
    correct_accepts = len([r for r in results if r.get("status") == "success" and r.get("correct")])
    correct_rejects = len([r for r in results if r.get("expected_type") == "reject" and r.get("status") == "parse_error"])
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    results.append({
        "_summary": {
            "timestamp": ts, "phase": "phase2", "total": total, "parse_errors": parse_errors,
            "rejects": rejects, "accepted": accepted, "correct_accepts": correct_accepts,
            "correct_rejects": correct_rejects,
            "correctness_conditional_on_accept": correct_accepts / accepted if accepted > 0 else 0,
            "correctness_unconditional": (correct_accepts + correct_rejects) / total,
            "decision_trace_summary": {
                "contradictions_triggered": len([r for r in results if r.get("decision_trace", {}).get("contradiction")]),
                "fallbacks_triggered": len([r for r in results if r.get("decision_trace", {}).get("fallback")]),
                "validation_failures": len([r for r in results if not r.get("decision_trace", {}).get("validation", True)]),
            }
        }
    })
    
    with open(f"phase2_results_{ts}.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to phase2_results_{ts}.json")


if __name__ == "__main__":
    main()