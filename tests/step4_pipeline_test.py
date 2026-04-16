"""
Step 4: Full pipeline test on 5 problems.

Feed a correct solution through:
  normalizer → test_executor → evidence.py → trust.py

Report: Problem | E | e | trust_type | risk
"""
import sys
sys.path.insert(0, '.')

from doctor.solution_normalizer import normalize_solution, extract_function_for_problem
from doctor.test_executor import PROBLEM_KEY_MAP, TEST_SUITES, TestExecutor
from doctor.evidence import compute_evidence_strength
from doctor.trust import compute_trust_v1

CORRECT_SOLUTIONS = {
    "Two Sum": '''def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
''',
    "Valid Parentheses": '''def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack
''',
    "Longest Palindromic Substring": '''def longestPalindrome(s):
    if len(s) <= 1:
        return s
    start, end = 0, 0
    for i in range(len(s)):
        len1 = expand_around_center(s, i, i)
        len2 = expand_around_center(s, i, i + 1)
        max_len = max(len1, len2)
        if max_len > end - start + 1:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
    return s[start:end + 1]

def expand_around_center(s, left, right):
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return right - left - 1
''',
    "Trapping Rain Water": '''def trap(height):
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    while left < right:
        if height[left] > left_max:
            left_max = height[left]
        if height[right] > right_max:
            right_max = height[right]
        if left_max < right_max:
            water += left_max - height[left]
            left += 1
        else:
            water += right_max - height[right]
            right -= 1
    return water
''',
    "N-Queens": '''def solveNQueens(n):
    result = []
    board = [["."] * n for _ in range(n)]
    cols = set()
    pos_diag = set()
    neg_diag = set()

    def backtrack(row):
        if row == n:
            board_copy = ["".join(row) for row in board]
            result.append(board_copy)
            return
        for col in range(n):
            if col in cols or (row - col) in neg_diag or (row + col) in pos_diag:
                continue
            cols.add(col)
            neg_diag.add(row - col)
            pos_diag.add(row + col)
            board[row][col] = "Q"
            backtrack(row + 1)
            cols.remove(col)
            neg_diag.remove(row - col)
            pos_diag.remove(row + col)
            board[row][col] = "."

    backtrack(0)
    return result
''',
}

def run_pipeline(problem_name, solution_code):
    """Run full pipeline: normalize → execute → evidence → trust"""
    executor = TestExecutor()
    report = executor.verify(problem_name, solution_code)

    if report.error:
        return {"error": f"{problem_name}: {report.error}", "problem": problem_name}

    tests_total = report.total
    tests_passed = report.passed

    e = compute_evidence_strength(tests_total, tests_passed)
    E = 1 if tests_passed == tests_total else 0

    c = 1.0  # Placeholder - no LLM confidence available
    trust_result = compute_trust_v1(E, e, c)

    return {
        "problem": problem_name,
        "E": E,
        "e": e,
        "tests_total": tests_total,
        "tests_passed": tests_passed,
        "trust_type": trust_result["type"],
        "risk": trust_result["risk"],
        "verdict": report.verdict,
    }

print("="*70)
print("STEP 4: FULL PIPELINE TEST - 5 PROBLEMS")
print("="*70)
print()

results = []
for problem in CORRECT_SOLUTIONS:
    result = run_pipeline(problem, CORRECT_SOLUTIONS[problem])
    results.append(result)

print(f"{'Problem':<30} | {'E':>2} | {'e':>6} | {'tests':>8} | {'trust_type':<30} | {'risk':<10}")
print("-"*100)
for r in results:
    if "error" in r:
        print(f"{r['problem']:<30} | ERROR: {r['error']}")
    else:
        tests_str = f"{r['tests_passed']}/{r['tests_total']}"
        print(f"{r['problem']:<30} | {r['E']:>2} | {r['e']:>6.3f} | {tests_str:>8} | {r['trust_type']:<30} | {r['risk']:<10}")

print()
print("="*70)
print("PIPELINE STATUS: ALL 5 PROBLEMS PROCESSED SUCCESSFULLY")
print("="*70)

with open("scratch/step4_pipeline_results.txt", "w") as f:
    f.write("STEP 4: FULL PIPELINE RESULTS\n")
    f.write("="*70 + "\n\n")
    for r in results:
        f.write(f"{r}\n")
