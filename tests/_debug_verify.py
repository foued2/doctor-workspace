import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tests.production_87 as p87
from doctor.test_executor import TestExecutor

prob = p87.PROBLEMS[0]  # Two Sum
correct_code = prob["correct"]

executor = TestExecutor()
report = executor.verify("Two Sum", correct_code)
print(f"Verdict: {report.verdict}")
print(f"Pass rate: {report.pass_rate}")
print(f"Total: {report.total}, Passed: {report.passed}")
print(f"Error: {report.error}")
for r in report.results:
    print(f"  {r.label}: passed={r.passed} got={r.got} exp={r.expected} err={r.error}")
