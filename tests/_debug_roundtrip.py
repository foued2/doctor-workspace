import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tests.production_87 as p87
from doctor.llm_doctor import _extract_problem_and_solution
from doctor.test_executor import TestExecutor

prob = p87.PROBLEMS[0]  # Two Sum
correct_code = prob["correct"]
prompt = f"PROBLEM: {prob['problem']}\n\nSOLUTION:\n{correct_code}"

problem, code = _extract_problem_and_solution(prompt)
print("=== EXTRACTED CODE ===")
print(repr(code))
print()
print("=== DIRECT CODE ===")
print(repr(correct_code))
print()
print("=== MATCH ===", code == correct_code)
print()

# Now run executor on extracted code
executor = TestExecutor()
report = executor.verify(problem, code)
print(f"Extracted code - Verdict: {report.verdict}, Pass rate: {report.pass_rate}")
for r in report.results:
    print(f"  {r.label}: passed={r.passed} got={r.got} exp={r.expected} err={r.error}")

# Now run executor on direct code
report2 = executor.verify("Two Sum", correct_code)
print(f"\nDirect code - Verdict: {report2.verdict}, Pass rate: {report2.pass_rate}")
