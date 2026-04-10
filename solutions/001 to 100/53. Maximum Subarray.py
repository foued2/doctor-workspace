from typing import List


class Solution:
    @staticmethod
    def maxSubArray(nums: List[int]) -> int:
        max_sum = nums[0]  # Initialize max_sum with the first element
        curr_sum = nums[0]  # Initialize curr_sum with the first element

        # Iterate over the array starting from the second element
        for num in nums[1:]:
            # Update curr_sum to be either the current element or the sum of the current element and the previous
            # subarray
            curr_sum = max(num, curr_sum + num)
            # Update max_sum to be the maximum of the current max_sum and curr_sum
            max_sum = max(max_sum, curr_sum)

        return max_sum


# Test the function
print(Solution.maxSubArray(nums=[-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # Output: 6
