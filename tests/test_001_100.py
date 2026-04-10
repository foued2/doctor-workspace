"""
Tests for LeetCode problems 1-100.

Run with: python -m pytest tests/test_001_100.py -v
"""

import pytest
import sys
from pathlib import Path

# Import main solution as example
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_add_two_numbers():
    """Test adding two numbers represented as linked lists (LeetCode #2)"""
    from main import Solution
    
    solution = Solution()
    
    # Test case 1: [9,9,9,9,9,9,9] + [9,9,9,9] = [8,9,9,9,0,0,0,1]
    list1 = [9, 9, 9, 9, 9, 9, 9]
    list2 = [9, 9, 9, 9]
    result = solution.addTwoNumbers(list1, list2)
    assert result == [8, 9, 9, 9, 0, 0, 0, 1]
    
    # Test case 2: [0] + [0] = [0]
    list1 = [0]
    list2 = [0]
    result = solution.addTwoNumbers(list1, list2)
    assert result == [0]
    
    # Test case 3: [9,9] + [1] = [0,0,1]
    list1 = [9, 9]
    list2 = [1]
    result = solution.addTwoNumbers(list1, list2)
    assert result == [0, 0, 1]


@pytest.mark.skip(reason="Add tests for problems as solutions are created")
def test_problem_1_two_sum():
    """Test Two Sum (LeetCode #1) - Add test when solution exists"""
    pass
