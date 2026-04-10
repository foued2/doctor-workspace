from typing import List


class Solution:
    @staticmethod
    def minimumSum(nums: List[int]) -> int:
        # Check if the length of the input list is less than 3
        if len(nums) < 3:
            return -1

        # Initialize the minimum sum with positive infinity
        min_sum = float('inf')

        # Iterate through the indices of the input list, excluding the first and last elements
        for i in range(1, len(nums) - 1):
            # Find the minimum element on the left side of the current index
            left_min = min(nums[:i])  # Maximum element on the right side
            # Find the minimum element on the right side of the current index
            right_min = min(nums[i + 1:])  # Maximum element on the left side

            # Check if the current element is greater than both left_min and right_min
            if nums[i] > left_min and nums[i] > right_min:
                # Update the minimum sum if a valid combination is found
                min_sum = min(min_sum, left_min + nums[i] + right_min)

        # Check if a valid minimum sum was found
        if min_sum != float("inf"):
            return min_sum
        else:
            return -1
