from typing import List


class Solution:
    @staticmethod
    def longestMonotonicSubarray(nums: List[int]) -> int:
        # Get the length of the nums list
        n = len(nums)

        # Initialize counters for the current increasing and decreasing subarray lengths
        curr_increasing = 1
        curr_decreasing = 1

        # Initialize variables to store the maximum length of increasing and decreasing subarrays
        max_increase = 1
        max_decrease = 1

        # Iterate through the nums list starting from the second element
        for i in range(1, n):
            if nums[i] > nums[i - 1]:
                # If the current element is greater than the previous one, increment the increasing counter
                curr_increasing += 1
                # Reset the decreasing counter
                curr_decreasing = 1
            elif nums[i] < nums[i - 1]:
                # If the current element is less than the previous one, increment the decreasing counter
                curr_decreasing += 1
                # Reset the increasing counter
                curr_increasing = 1
            else:
                # If the current element is equal to the previous one, reset both counters
                curr_increasing = 1
                curr_decreasing = 1

            # Update the maximum lengths if the current lengths are greater
            max_increase = max(max_increase, curr_increasing)
            max_decrease = max(max_decrease, curr_decreasing)

        # Return the maximum length between increasing and decreasing subarrays
        return max(max_increase, max_decrease)


# Example usage
solution = Solution()
print(solution.longestMonotonicSubarray([1, 4, 3, 3, 2]))  # Output: 4 (the subarray [2, 3, 4, 5] is
# increasing)
