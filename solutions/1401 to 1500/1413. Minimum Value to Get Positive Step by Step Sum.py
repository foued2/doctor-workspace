from typing import List


class Solution:
    @staticmethod
    def minStartValue(nums: List[int]) -> int:
        # Initialize the current prefix sum to zero
        current_prefix_sum = 0

        # Initialize the minimum value of the prefix sum encountered to zero
        min_prefix_sum = 0

        # Iterate through each element in the list
        for i in range(len(nums)):
            # Update the current prefix sum by adding the current element
            current_prefix_sum += nums[i]

            # Update the minimum prefix sum if the current prefix sum is smaller
            min_prefix_sum = min(current_prefix_sum, min_prefix_sum)

        # The minimum start value needed to ensure all prefix sums are positive
        # is the absolute value of the minimum prefix sum plus one
        return 1 - min_prefix_sum


print(Solution.minStartValue(nums=[2, 3, 5, -5, -1]))
