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

print(f"Extracted problem (first 100): {repr(problem[:100])}")
print(f"Expected problem name: Two Sum")
print()

executor = TestExecutor()
# Call with extracted problem description
report1 = executor.verify(problem, code)
print(f"With extracted problem: verdict={report1.verdict} pass_rate={report1.pass_rate} error={report1.error}")

# Call with proper name
report2 = executor.verify("Two Sum", code)
print(f"With 'Two Sum': verdict={report2.verdict} pass_rate={report2.pass_rate} error={report2.error}")
