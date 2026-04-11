"""Compare all 3 N-Queens solutions against the actual test suite."""
import sys
sys.path.insert(0, r'F:\pythonProject')

from tests.verify_code_only_baseline import SOLUTIONS
from doctor.test_executor import TestExecutor, PROBLEM_KEY_MAP

executor = TestExecutor()

for sol_type in ['correct', 'partial', 'incorrect']:
    key = f'N-Queens::{sol_type}'
    sol = SOLUTIONS[key]
    
    # Build the prompt as the baseline does
    problem_name = 'N-Queens'
    suite_key = PROBLEM_KEY_MAP[problem_name]
    
    report = executor.verify(problem_name, sol['code'])
    
    print(f"\nN-Queens::{sol_type}")
    print(f"  verdict={report.verdict} pass_rate={report.pass_rate} passed={report.passed}/{report.total}")
    print(f"  failure_type={report.failure_type}")
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        got_str = str(r.got)[:60] if r.got is not None else "None"
        exp_str = str(r.expected)[:60]
        print(f"    {status} {r.label}: got={got_str} expected={exp_str}")
