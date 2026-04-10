"""
LeetCode 3783. Mirror Distance of an Integer
============================================================

Problem Number: 3783
Difficulty Rating: 1170.79 (ZeroTrac)
Contest: weekly-contest-481
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/mirror-distance-of-an-integer/

Problem Slug: mirror-distance-of-an-integer
Chinese Title: 整数的镜像距离

PROBLEM STATEMENT:
============================================================
You are given an integer `n`.

Define its **mirror distance** as: `abs(n - reverse(n))`​​​​​​​ where `reverse(n)` is the integer formed by reversing the digits of `n`.

Return an integer denoting the mirror distance of `n`​​​​​​​.

`abs(x)` denotes the absolute value of `x`.

 

Example 1:**

**Input:** n = 25

**Output:** 27

**Explanation:**

	
• `reverse(25) = 52`.
	
• Thus, the answer is `abs(25 - 52) = 27`.

Example 2:**

**Input:** n = 10

**Output:** 9

**Explanation:**

	
• `reverse(10) = 01` which is 1.
	
• Thus, the answer is `abs(10 - 1) = 9`.

Example 3:**

**Input:** n = 7

**Output:** 0

**Explanation:**

	
• `reverse(7) = 7`.
	
• Thus, the answer is `abs(7 - 7) = 0`.

 

**Constraints:**

	
• `1 <= n <= 109`

DIFFICULTY: Easy
LIKES: 61 | DISLIKES: 2
TOPICS: Math


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3783`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
I will convert the integer n to a string, reverse the string, convert it back to an integer, and then compute abs(n - reversed_n).
This leverages Python's string slicing [::-1] to reverse digits efficiently.
Steps:
1. Convert n to string: str(n)
2. Reverse the string: str(n)[::-1]
3. Convert back to int: int(str(n)[::-1])
4. Return absolute difference: abs(n - reversed_n)

============================================================
TODO #3 - COMPLEXITY:
Time Complexity: O(log n) — where log n is the number of digits in n (since we reverse a string of length proportional to log₁₀(n))
Space Complexity: O(log n) — to store the string representation of n and its reverse
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve(n: int) -> int:
        """
        TODO #4a — Implement the solution for Mirror Distance of an Integer

        Args:
            n: A positive integer (1 <= n <= 10^9)

        Returns:
            The mirror distance: abs(n - reverse(n))
        """
        reversed_n = int(str(n)[::-1])
        return abs(n - reversed_n)


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()

    # Example 1:
    # Input: n = 25
    # Expected: 27
    result1 = solution.solve(25)
    assert result1 == 27, f"Example 1 failed: expected 27, got {result1}"
    print(f"Example 1: n=25 -> {result1} ✓")

    # Example 2:
    # Input: n = 10
    # Expected: 9
    result2 = solution.solve(10)
    assert result2 == 9, f"Example 2 failed: expected 9, got {result2}"
    print(f"Example 2: n=10 -> {result2} ✓")

    # Example 3:
    # Input: n = 7
    # Expected: 0
    result3 = solution.solve(7)
    assert result3 == 0, f"Example 3 failed: expected 0, got {result3}"
    print(f"Example 3: n=7 -> {result3} ✓")

    # Edge case: single digit
    result4 = solution.solve(1)
    assert result4 == 0, f"Edge case 1 failed: expected 0, got {result4}"
    print(f"Edge case: n=1 -> {result4} ✓")

    # Edge case: palindrome
    result5 = solution.solve(121)
    assert result5 == 0, f"Edge case 2 failed: expected 0, got {result5}"
    print(f"Edge case: n=121 -> {result5} ✓")

    # Edge case: large number (constraint boundary)
    result6 = solution.solve(1000000000)
    assert result6 == 999999999, f"Edge case 3 failed: expected 999999999, got {result6}"
    print(f"Edge case: n=1000000000 -> {result6} ✓")

    print("\nAll tests passed! ✓✓✓")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
