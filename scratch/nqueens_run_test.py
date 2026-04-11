"""Run N-Queens solutions to see actual outputs."""
import sys
sys.path.insert(0, r'F:\pythonProject')

from tests.verify_code_only_baseline import SOLUTIONS

for sol_type in ['correct', 'partial', 'incorrect']:
    key = f'N-Queens::{sol_type}'
    code = SOLUTIONS[key]['code']
    namespace = {}
    exec(code, namespace)
    func = namespace['solveNQueens']
    
    for n in [1, 4, 0]:
        try:
            result = func(n)
            print(f"N-Queens::{sol_type}  n={n}  -> {len(result) if isinstance(result, list) else result} solutions")
        except Exception as e:
            print(f"N-Queens::{sol_type}  n={n}  -> ERROR: {e}")
    print()
