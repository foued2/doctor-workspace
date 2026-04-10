from typing import List


class Solution:
    @staticmethod
    def smallestRangeI(nums: List[int], k: int) -> int:
        # Find the maximum value in the list
        max_num = max(nums)
        # Find the minimum value in the list
        min_num = min(nums)

        # Calculate the adjusted range after increasing the minimum and decreasing the maximum by k
        adjusted_range = (max_num - k) - (min_num + k)

        # Ensure the result is non-negative by taking the maximum of 0 and the adjusted range
        result = max(0, adjusted_range)

        # Return the final result
        return result


# Example usage:
nums = [2, 7, 2]
k = 1
solution = Solution()
print(solution.smallestRangeI(nums, k))  # Output should be 3
