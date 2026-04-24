"""Targeted regression test for Phase 2 failure cases."""
import os
os.environ['LLM_PROVIDER'] = 'google'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyC0aQ1naUtDWNqmA0WaRkWmWawrPhFGAeI'

from doctor.ingest.problem_parser import parse_problem
from doctor.ingest.registry_matcher import match_to_registry

cases = [
    ('SIMILAR_MAX_SUM_VS_PRODUCT_OBJ', 'Find the contiguous subarray with the maximum product. (vs maximum SUM would be different)', 'max_subarray'),
    ('SIMILAR_LIS_VS_LCS_OBJ', 'Find the longest common subsequence between two arrays. (vs longest increasing - similar structure, different problem)', 'longest_increasing_subsequence'),
    ('DISGUISE_LIS_TIMESERIES', 'Given daily stock prices over a month, find the longest consecutive period where prices were consistently rising.', 'longest_increasing_subsequence'),
    ('DISGUISE_MAX_SUM_BUDGET', 'Given daily expenses over a week, find the consecutive days with the highest total spending.', 'max_subarray'),
]

print("=" * 60)
print("TARGETED REGRESSION: 4 Failure Cases")
print("=" * 60)

all_passed = True
for case_id, statement, expected in cases:
    print(f"\n--- {case_id} ---")
    print(f"Statement: {statement[:60]}...")
    try:
        m = parse_problem(statement)
        print(f"Parsed objective: {m.get('objective')[:60]}...")
        match_id, justification, trace = match_to_registry(m)
        print(f"Match: {match_id}")
        print(f"Decision trace: contradiction={trace.get('contradiction')}, validation={trace.get('validation')}, fallback={trace.get('fallback')}, final={trace.get('final')}")
        if trace.get('final') == 'reject' and expected is None:
            verdict = 'CORRECT_REJECT'
        elif match_id == expected:
            verdict = 'CORRECT'
        else:
            verdict = 'WRONG'
            all_passed = False
        print(f"Expected: {expected}, Got: {match_id}, Verdict: {verdict}")
    except Exception as e:
        print(f"ERROR: {e}")
        all_passed = False

print("\n" + "=" * 60)
print("REGRESSION RESULT:", "ALL PASSED" if all_passed else "SOME FAILED")
print("=" * 60)