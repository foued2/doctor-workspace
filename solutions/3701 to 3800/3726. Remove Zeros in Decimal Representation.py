"""
LeetCode 3726. Remove Zeros in Decimal Representation
============================================================

Problem Number: 3726
Difficulty Rating: 1175.64 (ZeroTrac)
Contest: weekly-contest-473
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/remove-zeros-in-decimal-representation/

Problem Slug: remove-zeros-in-decimal-representation
Chinese Title: 移除十进制表示中的所有零

PROBLEM STATEMENT:
============================================================
You are given a **positive** integer `n`.

Return the integer obtained by removing all zeros from the decimal representation of `n`.

 

Example 1:**

**Input:** n = 1020030

**Output:** 123

**Explanation:**

After removing all zeros from 1**0**2**00**3**0**, we get 123.

Example 2:**

**Input:** n = 1

**Output:** 1

**Explanation:**

1 has no zero in its decimal representation. Therefore, the answer is 1.

 

**Constraints:**

	
• `1 <= n <= 1015`

DIFFICULTY: Easy
LIKES: 44 | DISLIKES: 2
TOPICS: Math, Simulation


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3726`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

============================================================
TODO #3 - COMPLEXITY:
Time Complexity: O(?)  — replace with actual complexity (e.g., O(n log n))
Space Complexity: O(?) — replace with actual complexity (e.g., O(n) for hash map)
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve() -> None:
        """
        TODO #4a — Implement the solution for Remove Zeros in Decimal Representation

        Args:
            TODO: Add parameters based on the problem statement

        Returns:
            TODO: Add return type based on the problem statement
        """
        # TODO: Implement your solution here
        pass


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()

    # Example 1:
    # Input: TODO
    # Expected: TODO

    # Example 2:
    # Input: TODO
    # Expected: TODO

    # Edge case:
    # Input: TODO
    # Expected: TODO

    result = solution.solve()
    print(f"Result: {result}")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
