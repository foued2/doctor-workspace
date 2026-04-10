import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from doctor.llm_doctor import _extract_problem_and_solution

# Simulate what production_87.py does
problem = "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order."
code = """def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i"""

prompt = f"PROBLEM: {problem}\n\nSOLUTION:\n{code}"

print("=== PROMPT (first 200 chars) ===")
print(prompt[:200])
print()

extracted_problem, extracted_code = _extract_problem_and_solution(prompt)
print("=== EXTRACTED PROBLEM (first 100 chars) ===")
print(repr(extracted_problem[:100]) if extracted_problem else None)
print()
print("=== EXTRACTED CODE ===")
print(repr(extracted_code) if extracted_code else None)
print()

# Now test with the actual prompt format from production_87.py
# Looking at the code: prompt = f"PROBLEM: {problem}\n\nSOLUTION:\n{code}"
# But the code has leading whitespace from the list indentation!

# Let me check the actual code from production_87.py
import tests.production_87 as p87
prob = p87.PROBLEMS[0]  # Two Sum
correct_code = prob["correct"]
print("=== ACTUAL CODE FROM PRODUCTION_87 ===")
print(repr(correct_code[:200]))
print()

actual_prompt = f"PROBLEM: {prob['problem']}\n\nSOLUTION:\n{correct_code}"
print("=== ACTUAL PROMPT (first 300 chars) ===")
print(repr(actual_prompt[:300]))
print()

ext_p, ext_c = _extract_problem_and_solution(actual_prompt)
print("=== ACTUAL EXTRACTED CODE ===")
print(repr(ext_c) if ext_c else None)
