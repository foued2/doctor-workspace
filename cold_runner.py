#!/usr/bin/env python3
"""
Cold Runner - Forces live API calls, no cache.

Run with: py cold_runner.py
"""

import os
import json
import shutil
from pathlib import Path

os.environ['GROQ_API_KEY'] = os.environ.get('GROQ_API_KEY', '')

# Clear cache before running - forces cold API calls
CACHE_DIR = Path("doctor/.llm_cache")
if CACHE_DIR.exists():
    print(f"[CLEARING CACHE] {CACHE_DIR}")
    shutil.rmtree(CACHE_DIR)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from doctor.ingest.problem_parser import parse_problem
from doctor.ingest.registry_matcher import match_to_registry
from doctor.registry.problem_registry import get_problems


COLD_PACK = [
    ("PARAPHRASE_TWO_SUM_ALPHA", "Given a list and a value, return the positions of a pair whose combination reaches the target. Only one such pair exists."),
    ("PARAPHRASE_TWO_SUM_BETA", "Input: numbers and a goal. Output: indices of two items that produce the goal when combined. No other pair works."),
    ("PARAPHRASE_LONGEST_PREFIX", "Given multiple text sequences, return the longest shared prefix appearing at the start of each. Empty string if nothing matches."),
    ("PARAPHRASE_VALID_PARENS", "Verify that all opening delimiters have corresponding closing delimiters in the correct sequence. Return true/false."),
    ("PARAPHRASE_MERGE_LISTS", "Join two sorted sequences into a single sorted result. Preserve the ordering."),
    ("AMBIG_SHORTEST_PATH", "Find the shortest path from start to end. No grid or graph structure specified."),
    ("AMBIG_MAX_ELEMENT", "Find the maximum element in a data structure. No indication whether it's an array, BST, or heap."),
    ("AMBIG_FIND_PAIRS", "Find all pairs of elements that satisfy a condition. Unclear whether sum, difference, or product."),
    ("AMBIG_SORTED_OUTPUT", "Return a sorted version of the input. No algorithm specified (merge sort, quick sort, heap sort?)."),
    ("AMBIG_TRAVERSE", "Traverse the nodes in the data structure. Could be depth-first or breadth-first."),
    ("SIMILAR_MAX_SUM_VS_PRODUCT", "Find the contiguous subarray with the maximum sum. (vs maximum PRODUCT would be different)"),
    ("SIMILAR_TWO_SUM_VS_THREE_SUM", "Find three numbers in the array that add up to zero. (vs Two Sum - same structure, different count)"),
    ("SIMILAR_CLIMBING_WAYS_VS_COST", "Find the number of ways to reach the top."),
    ("SIMILAR_LIS_VS_LCS", "Find the longest increasing subsequence. (vs Longest Common Subsequence - similar DP pattern)"),
    ("SIMILAR_DFS_VS_BFS_TRAVERSAL", "Visit all nodes in the structure below:\n    1\n   / \\\n  2   3"),
]


EXPECTED = {
    "PARAPHRASE_TWO_SUM_ALPHA": ("two_sum", "match"),
    "PARAPHRASE_TWO_SUM_BETA": ("two_sum", "match"),
    "PARAPHRASE_LONGEST_PREFIX": ("longest_common_prefix", "match"),
    "PARAPHRASE_VALID_PARENS": ("valid_parentheses", "match"),
    "PARAPHRASE_MERGE_LISTS": ("merge_two_sorted_lists", "match"),
    "AMBIG_SHORTEST_PATH": (None, "reject"),
    "AMBIG_MAX_ELEMENT": (None, "reject"),
    "AMBIG_FIND_PAIRS": (None, "reject"),
    "AMBIG_SORTED_OUTPUT": (None, "reject"),
    "AMBIG_TRAVERSE": (None, "reject"),
    "SIMILAR_MAX_SUM_VS_PRODUCT": ("max_subarray", "match"),
    "SIMILAR_TWO_SUM_VS_THREE_SUM": ("three_sum", "match"),
    "SIMILAR_CLIMBING_WAYS_VS_COST": ("climbing_stairs", "match_or_reject"),
    "SIMILAR_LIS_VS_LCS": ("longest_increasing_subsequence", "match"),
    "SIMILAR_DFS_VS_BFS_TRAVERSAL": (None, "reject"),
}


def main():
    results = []
    
    print("=" * 60)
    print("COLD RUN - 15 cases, no cache")
    print("=" * 60)
    
    for i, (case_id, statement) in enumerate(COLD_PACK, 1):
        print(f"\n[{i}] {case_id}:")
        print(f"  Input: {statement[:50]}...")
        
        # Parse - forces live API call
        try:
            model = parse_problem(statement)
            print(f"  Parsed: {model.get('input_type')} -> {model.get('output_type')}")
            parse_ok = True
        except Exception as e:
            print(f"  PARSE ERROR: {e}")
            parse_ok = False
            model = None
        
        if not parse_ok:
            results.append({"case": case_id, "status": "parse_error", "expected": EXPECTED[case_id]})
            continue
        
        # Match - forces live API call
        try:
            match_id, justification = match_to_registry(model)
            print(f"  Matched: {match_id}")
            match_ok = True
        except Exception as e:
            print(f"  MATCH ERROR: {e}")
            match_id, justification = None, str(e)
            match_ok = False
        
        # Evaluate
        expected_match, expected_type = EXPECTED[case_id]
        
        if expected_type == "reject":
            correct = match_id is None or match_id == "no match"
            verdict = "CORRECT_REJECT" if correct else "INCORRECT_GUESS"
        elif expected_type == "match_or_reject":
            correct = match_id == expected_match or match_id is None
            verdict = "CORRECT" if correct else "WRONG"
        else:
            correct = match_id == expected_match
            verdict = "CORRECT" if correct else "WRONG"
        
        print(f"  Expected: {expected_match} ({expected_type})")
        print(f"  Result: {match_id}")
        print(f"  Verdict: {verdict}")
        
        results.append({
            "case": case_id,
            "statement": statement,  # Full input
            "status": "success",
            "parsed_model": model,  # Full parser output
            "matched": match_id,
            "justification": justification,  # Matcher reasoning
            "expected": expected_match,
            "expected_type": expected_type,
            "correct": correct,
            "verdict": verdict,
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("COLD RUN RESULTS")
    print("=" * 60)
    
    total = len(results)
    correct = len([r for r in results if r.get("correct")])
    parse_errors = len([r for r in results if r.get("status") == "parse_error"])
    
    print(f"Total: {total}")
    print(f"Parse errors: {parse_errors}")
    print(f"Correct: {correct}/{total - parse_errors}")
    
    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"cold_results_{ts}.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to cold_results_{ts}.json")


if __name__ == "__main__":
    from datetime import datetime
    main()
