from typing import List


class Solution:
    @staticmethod
    def minSubArrayLen(target: int, nums: List[int]) -> int:
        # Check if the list is empty, return 0 if so
        if not nums:
            return 0

        # Initialize left and right pointers, current sum, and minimum length
        left, right = 0, 0
        current_sum = nums[0]
        min_length = float('inf')

        # Iterate through the list using the sliding window approach
        while right < len(nums):
            # If the current sum is greater than or equal to the target
            if current_sum >= target:
                # Update the minimum length if needed
                min_length = min(min_length, right - left + 1)
                # Move the left pointer to the right and update the current sum
                current_sum -= nums[left]
                left += 1
            else:
                # If the current sum is less than the target, move the right pointer to the right
                right += 1
                # If the right pointer is within the bounds of the list, update the current sum
                if right < len(nums):
                    current_sum += nums[right]

        # Return the minimum length if it's not infinity, otherwise return 0
        return min_length if min_length != float('inf') else 0


# Test the function
print(Solution.minSubArrayLen(target=7, nums=[2, 3, 1, 2, 4, 3]))
