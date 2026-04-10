from typing import List


class Solution:
    @staticmethod
    def arrayPairSum(nums: List[int]) -> int:
        # Sort the array in non-decreasing order
        nums.sort()

        # Get the length of the array
        n = len(nums)

        # If the array contains only two elements, return the minimum of the two
        if n == 2:
            return nums[0]

        # Sum the elements at even indices (0-indexed), which are the minimum elements in each pair
        return sum(nums[::2])


# Test the solution with the given example
print(Solution.arrayPairSum([6, 2, 6, 5, 1, 2]))
