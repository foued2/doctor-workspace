"""
LeetCode 3861. Minimum Capacity Box
============================================================

Problem Number: 3861
Difficulty Rating: 1154.16 (ZeroTrac)
Contest: weekly-contest-492
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/minimum-capacity-box/

Problem Slug: minimum-capacity-box
Chinese Title: 容量最小的箱子

PROBLEM STATEMENT:
============================================================
You are given an integer array `capacity`, where `capacity[i]` represents the capacity of the `ith` box, and an integer `itemSize` representing the size of an item.

The `ith` box can store the item if `capacity[i] >= itemSize`.

Return an integer denoting the index of the box with the **minimum** capacity that can store the item. If multiple such boxes exist, return the **smallest index**.

If no box can store the item, return -1.

 

Example 1:**

**Input:** capacity = [1,5,3,7], itemSize = 3

**Output:** 2

**Explanation:**

The box at index 2 has a capacity of 3, which is the minimum capacity that can store the item. Thus, the answer is 2.

Example 2:**

**Input:** capacity = [3,5,4,3], itemSize = 2

**Output:** 0

**Explanation:**

The minimum capacity that can store the item is 3, and it appears at indices 0 and 3. Thus, the answer is 0.

Example 3:**

**Input:** capacity = [4], itemSize = 5

**Output:** -1

**Explanation:**

No box has enough capacity to store the item, so the answer is -1.

 

**Constraints:**

	
• `1 <= capacity.length <= 100`
	
• `1 <= capacity[i] <= 100`
	
• `1 <= itemSize <= 100`

DIFFICULTY: Easy
LIKES: 49 | DISLIKES: 2
TOPICS: Array


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3861`
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
        TODO #4a — Implement the solution for Minimum Capacity Box

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

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
