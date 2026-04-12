import sys
sys.path.insert(0, r'F:\pythonProject')
from tests.verify_code_only_baseline import build_cases
cases = build_cases()
for c in cases:
    if c.ground_truth == 'incorrect':
        prob = c.problem_name
        sol = c.solution_code[:300] if c.solution_code else 'None'
        print(f'=== {prob} (GT=incorrect) ===')
        print(sol)
        print()
