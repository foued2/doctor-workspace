from typing import List


class Solution:
    @staticmethod
    def maximizeSum(nums: List[int], k: int) -> int:
        # Find the maximum value in the list
        max_num = max(nums)

        # Calculate the sum of the maximum value repeated k times
        max_sum = k * max_num

        # Calculate the sum of the first (k - 1) natural numbers
        # This is done using the formula n * (n + 1) // 2, where n = k - 1
        natural_sum = ((k - 1) * k) // 2

        # Return the total sum
        return max_sum + natural_sum


# Example usage:
solution = Solution()
print(solution.maximizeSum([1, 2, 3, 4], 3))  # Output: 16

print(Solution.maximizeSum(nums=[5, 5, 5], k=8))
