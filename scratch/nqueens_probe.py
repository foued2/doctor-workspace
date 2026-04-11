"""N-Queens AST probe — check what patterns the checker looks for."""
import sys, ast
sys.path.insert(0, r'F:\pythonProject')

from tests.verify_code_only_baseline import SOLUTIONS

for sol_type in ['correct', 'incorrect', 'partial']:
    key = f'N-Queens::{sol_type}'
    code = SOLUTIONS[key]['code']
    tree = ast.parse(code)
    src = ast.dump(tree)
    print(f"\n=== N-Queens::{sol_type} ===")
    print(f"has 'diag' in AST: {'diag' in src}")
    print(f"has 'd1' in AST: {'d1' in src}")
    print(f"has 'd2' in AST: {'d2' in src}")
    print(f"has 'abs' in code: {'abs(' in code}")
    print(f"has 'Sub' in AST: {'Sub' in src}")
    print(f"has 'Add' in AST: {'Add' in src}")
    print(f"has 'permutations' in code: {'permutations' in code}")
    print(f"has 'backtrack' in code: {'backtrack' in code}")
    print(f"has 'set()' in code: {'set()' in code}")
    print(f"Code snippet:\n{code[:400]}")
