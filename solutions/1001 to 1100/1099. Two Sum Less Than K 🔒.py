from typing import List


class Solution:
    @staticmethod
    def two_sum_less_than_target(nums: List[int], target: int) -> int:
        """
        Two pointers
        """
        # Sort the numbers in non-decreasing order
        nums.sort()

        # Initialize pointers
        left, right = 0, len(nums) - 1

        # Initialize the maximum sum found
        max_sum = -1

        # Use two pointers to find pairs with the sum less than target
        while left < right:
            current_sum = nums[left] + nums[right]
            if current_sum < target:
                # If the sum is less than the target, update max_sum if needed
                max_sum = max(max_sum, current_sum)
                left += 1  # Move the left pointer to the right to try increasing the sum
            else:
                # If the sum is greater than or equal to the target, move the right pointer to the left
                right -= 1

        return max_sum


# Test cases
print(Solution.two_sum_less_than_target([34, 23, 1, 24, 75, 33, 54, 8], 60))  # Output: 58
print(Solution.two_sum_less_than_target([10, 20, 30], 15))  # Output: -1
