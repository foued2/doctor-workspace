"""Deep trace: why does Two_Sum_partial fail no_index_out_of_bounds?"""
import sys, ast
sys.path.insert(0, r'F:\pythonProject')

from tests.verify_code_only_baseline import SOLUTIONS
from doctor.code_analyzer import _safe_parse, _has_index_out_of_bounds_risk

code = SOLUTIONS['Two Sum::partial']['code']
tree = _safe_parse(code)

print("Code:")
print(code)
print()
print(f"_has_index_out_of_bounds_risk: {_has_index_out_of_bounds_risk(tree)}")

# Trace the function
print("\n--- Tracing _has_index_out_of_bounds_risk ---")
# Check 1: range(len(...)) loop
for n in ast.walk(tree):
    if isinstance(n, ast.For):
        iter_src = ast.dump(n.iter)
        print(f"  For loop iter: {iter_src}")
        has_range = "range" in iter_src
        has_len = "len" in iter_src
        print(f"    has range: {has_range}, has len: {has_len}")
        if has_range and has_len:
            print("  -> All index access is bounded by range(len(...)) -> SAFE")
