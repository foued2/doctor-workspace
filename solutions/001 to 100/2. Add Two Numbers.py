"""
LeetCode 2. Add Two Numbers
============================================================

Problem Number: 2
Difficulty Rating: N/A
Contest: N/A
Problem Index: N/A

LeetCode URL: https://leetcode.com/problems/add-two-numbers/

Problem Slug: add-two-numbers
Chinese Title: 两数相加

PROBLEM STATEMENT:
============================================================
You are given two **non-empty** linked lists representing two non-negative integers. The digits are stored in **reverse order**, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

 

Example 1:**

```

**Input:** l1 = [2,4,3], l2 = [5,6,4]
**Output:** [7,0,8]
**Explanation:** 342 + 465 = 807.

```

Example 2:**

```

**Input:** l1 = [0], l2 = [0]
**Output:** [0]

```

Example 3:**

```

**Input:** l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
**Output:** [8,9,9,9,0,0,0,1]

```

 

**Constraints:**

	
• The number of nodes in each linked list is in the range `[1, 100]`.
	
• `0 <= Node.val <= 9`
	
• It is guaranteed that the list represents a number that does not have leading zeros.

DIFFICULTY: Medium
LIKES: 36673 | DISLIKES: 7234
TOPICS: Linked List, Math, Recursion


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 — PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 — APPROACH                [Describe your algorithm step-by-step]
TODO #3 — COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 — SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 2`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 — APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

============================================================
TODO #3 — COMPLEXITY:
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
        TODO #4a — Implement the solution for Add Two Numbers

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
