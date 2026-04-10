"""
LeetCode 3467. Transform Array by Parity
============================================================

Problem Number: 3467
Difficulty Rating: 1165.83 (ZeroTrac)
Contest: biweekly-contest-151
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/transform-array-by-parity/

Problem Slug: transform-array-by-parity
Chinese Title: 将数组按照奇偶性转化

PROBLEM STATEMENT:
============================================================
You are given an integer array `nums`. Transform `nums` by performing the following operations in the **exact** order specified:

	
• Replace each even number with 0.
	
• Replace each odd numbers with 1.
	
• Sort the modified array in **non-decreasing** order.

Return the resulting array after performing these operations.

 

Example 1:**

**Input:** nums = [4,3,2,1]

**Output:** [0,0,1,1]

**Explanation:**

	
• Replace the even numbers (4 and 2) with 0 and the odd numbers (3 and 1) with 1. Now, `nums = [0, 1, 0, 1]`.
	
• After sorting `nums` in non-descending order, `nums = [0, 0, 1, 1]`.

Example 2:**

**Input:** nums = [1,5,1,4,2]

**Output:** [0,0,1,1,1]

**Explanation:**

	
• Replace the even numbers (4 and 2) with 0 and the odd numbers (1, 5 and 1) with 1. Now, `nums = [1, 1, 1, 0, 0]`.
	
• After sorting `nums` in non-descending order, `nums = [0, 0, 1, 1, 1]`.

 

**Constraints:**

	
• `1 <= nums.length <= 100`
	
• `1 <= nums[i] <= 1000`

DIFFICULTY: Easy
LIKES: 103 | DISLIKES: 7
TOPICS: Array, Sorting, Counting


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3467`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

============================================================
TODO #3 - COMPLEXITY:
Time Complexity: O(n) — single pass to transform elements + O(n log n) for sorting
Space Complexity: O(1) — in-place transformation (excluding output array)
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve(nums: List[int]) -> List[int]:
        """
        Transform array by replacing even numbers with 0 and odd with 1, then sort.

        Args:
            nums: input array of integers

        Returns:
            transformed and sorted array
        """
        transformed = [0 if x % 2 == 0 else 1 for x in nums]
        return sorted(transformed)


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()
    passed = 0
    failed = 0

    def check(nums, expected, label=""):
        nonlocal passed, failed
        result = solution.solve(nums)
        if result == expected:
            passed += 1
            print(f"  PASS: {label} -> solve({nums}) = {result}")
        else:
            failed += 1
            print(f"  FAIL: {label} -> solve({nums}) = {result}, expected {expected}")

    # Example 1
    check([4, 3, 2, 1], [0, 0, 1, 1], "Example 1")

    # Example 2
    check([1, 5, 1, 4, 2], [0, 0, 1, 1, 1], "Example 2")

    # Edge case: single element (even)
    check([2], [0], "Edge: single even")

    # Edge case: single element (odd)
    check([3], [1], "Edge: single odd")

    # Edge case: all even
    check([4, 2, 6], [0, 0, 0], "Edge: all even")

    # Edge case: all odd
    check([1, 3, 5], [1, 1, 1], "Edge: all odd")

    print(f"\nResults: {passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        raise AssertionError(f"{failed} test(s) failed")
    print("All tests passed!")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
